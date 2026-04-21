"""
Deep Feature Extraction — CNN Embeddings
Loads a pre-trained CNN (EfficientNet-B0, ImageNet weights) and extracts
a dense embedding vector from each image in index.csv.

Saves deep_features.csv alongside features.csv with the same subject_id
column so the two can be joined for ensemble modelling.

Does NOT train the CNN. This is inference-only feature extraction using
frozen ImageNet weights as a general-purpose visual encoder.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import torch
from torchvision import models, transforms
from PIL import Image

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
INDEX_CSV = os.path.join(PROCESSED_DIR, "index.csv")
DEEP_FEATURES_CSV = os.path.join(PROCESSED_DIR, "deep_features.csv")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."

# ImageNet normalization
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# EfficientNet-B0 produces 1280-dim embeddings
EMBEDDING_DIM = 1280


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"deep_features_{ts}.log")
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


def build_model():
    """
    Load EfficientNet-B0 with ImageNet weights, remove the classifier head,
    and return the feature extractor in eval mode.
    """
    weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1
    model = models.efficientnet_b0(weights=weights)

    # Remove the classifier — keep only the feature backbone + pooling
    # EfficientNet forward: features -> avgpool -> classifier
    # We want the output of avgpool (1280-dim)
    model.classifier = torch.nn.Identity()

    model.eval()
    return model


def build_transform():
    """
    Standard ImageNet preprocessing for EfficientNet-B0:
    resize to 256, center-crop to 224, normalize.
    """
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def extract_embedding(model, transform, image_path, device):
    """
    Extract a single embedding vector from one image.
    Returns a numpy array of shape (EMBEDDING_DIM,) or None on failure.
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        logging.warning(f"Cannot open {image_path}: {e}")
        return None

    tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = model(tensor)

    return embedding.squeeze(0).cpu().numpy()


def run_extraction():
    log_file = setup_logging()
    logging.info("=" * 60)
    logging.info("DEEP FEATURE EXTRACTION — EfficientNet-B0 Embeddings")
    logging.info("=" * 60)

    if not os.path.exists(INDEX_CSV):
        logging.error(f"index.csv not found at {INDEX_CSV}. Run build_index.py first.")
        sys.exit(1)

    index_df = pd.read_csv(INDEX_CSV)
    logging.info(f"Loaded index: {len(index_df)} rows")

    # Device selection
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    logging.info(f"Device: {device}")

    # Load model
    logging.info("Loading EfficientNet-B0 (ImageNet weights)...")
    model = build_model().to(device)
    transform = build_transform()
    logging.info(f"Model loaded. Embedding dim: {EMBEDDING_DIM}")

    # Extract embeddings
    embedding_cols = [f"emb_{i:04d}" for i in range(EMBEDDING_DIM)]
    rows = []
    failed = 0

    for i, idx_row in index_df.iterrows():
        emb = extract_embedding(model, transform, idx_row["filepath"], device)
        if emb is None:
            failed += 1
            continue

        row = {
            "filepath": idx_row["filepath"],
            "subject_id": idx_row["subject_id"],
            "label": idx_row["label"],
            "media_type": idx_row["media_type"],
            "frame_number": idx_row["frame_number"],
        }
        for j, val in enumerate(emb):
            row[embedding_cols[j]] = round(float(val), 6)
        rows.append(row)

        if (i + 1) % 20 == 0 or (i + 1) == len(index_df):
            logging.info(f"  Extracted {i + 1}/{len(index_df)}")

    df = pd.DataFrame(rows)
    df.to_csv(DEEP_FEATURES_CSV, index=False)

    logging.info(f"\nSaved: {DEEP_FEATURES_CSV}")
    logging.info(f"Shape: {df.shape}")
    logging.info(f"Embedding columns: {len(embedding_cols)}")
    logging.info(f"Subjects: {df['subject_id'].nunique()}")
    logging.info(f"Failed images: {failed}")
    logging.info(f"Log: {log_file}")
    logging.info(DISCLAIMER)

    return df


if __name__ == "__main__":
    run_extraction()
