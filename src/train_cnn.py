"""
CNN Fine-Tuning Skeleton — Binary Pregnancy Classifier
Takes a pre-trained EfficientNet-B0, replaces the final layer with a
binary classifier, and fine-tunes on our data using GroupKFold by subject_id.

DO NOT RUN YET — NEGATIVE data is still missing.
This code is ready to execute the moment both classes exist.

GroupKFold guarantee: no subject appears in both train and test.
The model always returns its actual computed probability — no hardcoded
minimum confidence. We iterate on architecture and data until real
measured accuracy reaches the target.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, SubsetRandomSampler
from torchvision import models, transforms
from PIL import Image
from sklearn.model_selection import GroupKFold
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score, confusion_matrix

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
INDEX_CSV = os.path.join(PROCESSED_DIR, "index.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."

# ImageNet normalization
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Training hyperparameters — starting points, tune later
BATCH_SIZE = 16
LEARNING_RATE = 1e-4
NUM_EPOCHS = 20
WEIGHT_DECAY = 1e-4
N_FOLDS = 5


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"train_cnn_{ts}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.info(DISCLAIMER)
    return log_file


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class UrineImageDataset(Dataset):
    """
    Loads images from index.csv. Each item returns (image_tensor, label, subject_id).
    """

    def __init__(self, index_df, transform=None):
        self.df = index_df.reset_index(drop=True)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img = Image.open(row["filepath"]).convert("RGB")
        if self.transform:
            img = self.transform(img)
        label = int(row["label"])
        subject_id = row["subject_id"]
        return img, label, subject_id


def get_train_transform():
    """Training augmentation: random crop, flip, color jitter."""
    return transforms.Compose([
        transforms.Resize(256),
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_val_transform():
    """Validation: deterministic resize + center crop."""
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

def build_model(freeze_backbone=True):
    """
    EfficientNet-B0 with a new binary classification head.
    Optionally freeze the backbone for initial training.
    """
    weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1
    model = models.efficientnet_b0(weights=weights)

    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False

    # Replace classifier: EfficientNet-B0 has 1280-dim features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(1280, 1),
    )

    return model


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------

def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    all_labels = []
    all_probs = []

    for images, labels, _ in loader:
        images = images.to(device)
        labels = labels.float().to(device)

        optimizer.zero_grad()
        outputs = model(images).squeeze(1)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        probs = torch.sigmoid(outputs).detach().cpu().numpy()
        all_probs.extend(probs)
        all_labels.extend(labels.cpu().numpy())

    epoch_loss = running_loss / len(all_labels)
    return epoch_loss, np.array(all_labels), np.array(all_probs)


def evaluate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_labels = []
    all_probs = []

    with torch.no_grad():
        for images, labels, _ in loader:
            images = images.to(device)
            labels = labels.float().to(device)

            outputs = model(images).squeeze(1)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            probs = torch.sigmoid(outputs).cpu().numpy()
            all_probs.extend(probs)
            all_labels.extend(labels.cpu().numpy())

    epoch_loss = running_loss / len(all_labels)
    return epoch_loss, np.array(all_labels), np.array(all_probs)


def specificity(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return tn / (tn + fp) if (tn + fp) > 0 else 0.0


def compute_metrics(labels, probs, threshold=0.5):
    preds = (probs >= threshold).astype(int)
    acc = accuracy_score(labels, preds)
    sens = recall_score(labels, preds, zero_division=0)
    spec = specificity(labels, preds)
    try:
        auc = roc_auc_score(labels, probs)
    except ValueError:
        auc = float("nan")
    return {"accuracy": acc, "sensitivity": sens, "specificity": spec, "auc": auc}


# ---------------------------------------------------------------------------
# Main training with GroupKFold
# ---------------------------------------------------------------------------

def train_cnn():
    log_file = setup_logging()
    logging.info("=" * 60)
    logging.info("CNN FINE-TUNING — EfficientNet-B0 Binary Classifier")
    logging.info("=" * 60)

    if not os.path.exists(INDEX_CSV):
        logging.error(f"index.csv not found at {INDEX_CSV}. Run build_index.py first.")
        sys.exit(1)

    index_df = pd.read_csv(INDEX_CSV)
    logging.info(f"Loaded index: {len(index_df)} rows")

    # Check both classes exist
    labels_present = set(index_df["label"].unique())
    if labels_present != {0, 1}:
        logging.error("=" * 60)
        logging.error("CANNOT TRAIN: Both classes required.")
        logging.error(f"  Labels found: {labels_present}")
        if 0 not in labels_present:
            logging.error("  MISSING: label=0 (NEGATIVE / not pregnant)")
            logging.error("  Add NEGATIVE samples to PICTURES/NEGATIVE/ and re-run pipeline.")
        if 1 not in labels_present:
            logging.error("  MISSING: label=1 (POSITIVE / pregnant)")
        logging.error("=" * 60)
        sys.exit(1)

    # Device
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    logging.info(f"Device: {device}")

    # Subject-level groups for GroupKFold
    subjects = index_df["subject_id"].values
    labels = index_df["label"].values
    unique_subjects = index_df["subject_id"].unique()
    subject_labels = index_df.groupby("subject_id")["label"].first().values

    n_pos = sum(subject_labels == 1)
    n_neg = sum(subject_labels == 0)
    n_splits = min(N_FOLDS, n_pos, n_neg)
    if n_splits < 2:
        logging.error(f"Not enough subjects per class (pos={n_pos}, neg={n_neg})")
        sys.exit(1)

    logging.info(f"Subjects: {len(unique_subjects)} (positive={n_pos}, negative={n_neg})")
    logging.info(f"GroupKFold: {n_splits} folds")
    logging.info(f"Hyperparameters: lr={LEARNING_RATE}, epochs={NUM_EPOCHS}, batch={BATCH_SIZE}")

    # Build GroupKFold over subject indices
    subject_df = index_df.groupby("subject_id")["label"].first().reset_index()
    gkf = GroupKFold(n_splits=n_splits)

    all_fold_results = []

    for fold_idx, (train_subj_idx, val_subj_idx) in enumerate(
        gkf.split(subject_df["subject_id"], subject_df["label"], subject_df["subject_id"])
    ):
        train_subjects = set(subject_df.iloc[train_subj_idx]["subject_id"])
        val_subjects = set(subject_df.iloc[val_subj_idx]["subject_id"])

        logging.info(f"\n--- Fold {fold_idx + 1}/{n_splits} ---")
        logging.info(f"  Train subjects: {sorted(train_subjects)}")
        logging.info(f"  Val subjects:   {sorted(val_subjects)}")

        # Image-level indices for this fold
        train_mask = index_df["subject_id"].isin(train_subjects)
        val_mask = index_df["subject_id"].isin(val_subjects)
        train_indices = index_df[train_mask].index.tolist()
        val_indices = index_df[val_mask].index.tolist()

        # Datasets and loaders
        train_dataset = UrineImageDataset(index_df, transform=get_train_transform())
        val_dataset = UrineImageDataset(index_df, transform=get_val_transform())

        train_loader = DataLoader(
            train_dataset, batch_size=BATCH_SIZE,
            sampler=SubsetRandomSampler(train_indices),
        )
        val_loader = DataLoader(
            val_dataset, batch_size=BATCH_SIZE,
            sampler=SubsetRandomSampler(val_indices),
        )

        # Fresh model each fold
        model = build_model(freeze_backbone=True).to(device)
        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.AdamW(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY,
        )

        best_val_auc = 0.0
        best_state = None

        for epoch in range(NUM_EPOCHS):
            train_loss, _, _ = train_one_epoch(model, train_loader, criterion, optimizer, device)
            val_loss, val_labels, val_probs = evaluate(model, val_loader, criterion, device)
            metrics = compute_metrics(val_labels, val_probs)

            if not np.isnan(metrics["auc"]) and metrics["auc"] > best_val_auc:
                best_val_auc = metrics["auc"]
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

            if (epoch + 1) % 5 == 0 or epoch == 0:
                logging.info(
                    f"  Epoch {epoch+1:>3d}: train_loss={train_loss:.4f} "
                    f"val_loss={val_loss:.4f} acc={metrics['accuracy']:.3f} "
                    f"auc={metrics['auc']:.3f}"
                )

        # Evaluate best checkpoint
        if best_state is not None:
            model.load_state_dict(best_state)
        _, val_labels, val_probs = evaluate(model, val_loader, criterion, device)
        fold_metrics = compute_metrics(val_labels, val_probs)
        fold_metrics["fold"] = fold_idx + 1
        fold_metrics["val_subjects"] = sorted(val_subjects)
        all_fold_results.append(fold_metrics)

        logging.info(
            f"  BEST: acc={fold_metrics['accuracy']:.3f} "
            f"sens={fold_metrics['sensitivity']:.3f} "
            f"spec={fold_metrics['specificity']:.3f} "
            f"auc={fold_metrics['auc']:.3f}"
        )

    # Summary
    mean_acc = np.mean([r["accuracy"] for r in all_fold_results])
    mean_sens = np.mean([r["sensitivity"] for r in all_fold_results])
    mean_spec = np.mean([r["specificity"] for r in all_fold_results])
    mean_auc = np.nanmean([r["auc"] for r in all_fold_results])

    logging.info(f"\n{'='*60}")
    logging.info("CNN CROSS-VALIDATION RESULTS")
    logging.info(f"{'='*60}")
    logging.info(f"Mean accuracy:    {mean_acc:.4f}")
    logging.info(f"Mean sensitivity: {mean_sens:.4f}")
    logging.info(f"Mean specificity: {mean_spec:.4f}")
    logging.info(f"Mean AUC:         {mean_auc:.4f}")

    # Save final model (retrained on all data)
    logging.info("\nRetraining on full dataset...")
    full_dataset = UrineImageDataset(index_df, transform=get_train_transform())
    full_loader = DataLoader(full_dataset, batch_size=BATCH_SIZE, shuffle=True)

    final_model = build_model(freeze_backbone=True).to(device)
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, final_model.parameters()),
        lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY,
    )

    for epoch in range(NUM_EPOCHS):
        train_loss, _, _ = train_one_epoch(final_model, full_loader, criterion, optimizer, device)
        if (epoch + 1) % 5 == 0:
            logging.info(f"  Full retrain epoch {epoch+1}: loss={train_loss:.4f}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "model_cnn_v1.pt")
    torch.save({
        "model_state_dict": final_model.state_dict(),
        "architecture": "efficientnet_b0",
        "embedding_dim": 1280,
        "trained_at": datetime.now().isoformat(),
        "n_folds": n_splits,
        "cv_results": all_fold_results,
        "mean_auc": mean_auc,
        "disclaimer": DISCLAIMER,
    }, model_path)

    logging.info(f"Model saved: {model_path}")
    logging.info(f"Log: {log_file}")
    logging.info(DISCLAIMER)

    return model_path, all_fold_results


if __name__ == "__main__":
    train_cnn()
