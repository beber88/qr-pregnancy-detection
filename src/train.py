"""
Training Script — Model B (Image Features Only)
Trains the classifier using GroupKFold (subject-level splits).

NON-NEGOTIABLE: No image from subject X can appear in both train and test.

Candidates: LogisticRegression, RandomForest, GradientBoosting
Metrics per fold: accuracy, sensitivity, specificity, AUC, confusion matrix

Will NOT run unless both classes (label=0 and label=1) are present.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import pickle
import logging
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, recall_score, roc_auc_score,
    confusion_matrix,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase1_extract import FEATURE_NAMES

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"train_{ts}.log")
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


def specificity(y_true, y_pred):
    """TN / (TN + FP)"""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return tn / (tn + fp) if (tn + fp) > 0 else 0.0


def aggregate_to_subjects(df):
    """
    Average image features per subject.
    Each subject becomes one row — this is the unit for GroupKFold.
    """
    feature_cols = [c for c in FEATURE_NAMES if c in df.columns]
    agg = {col: "mean" for col in feature_cols}
    agg["label"] = "first"

    subject_df = df.groupby("subject_id").agg(agg).reset_index()
    return subject_df, feature_cols


def train():
    log_file = setup_logging()
    logging.info("=" * 60)
    logging.info("TRAINING — Model B (Image Features Only)")
    logging.info("=" * 60)

    # --- Load data ---
    if not os.path.exists(FEATURES_CSV):
        logging.error(f"features.csv not found: {FEATURES_CSV}")
        logging.error("Run build_index.py and phase1_extract.py first.")
        sys.exit(1)

    raw_df = pd.read_csv(FEATURES_CSV)
    logging.info(f"Loaded features: {raw_df.shape}")

    # --- Check both classes exist ---
    labels_present = set(raw_df["label"].unique())
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

    # --- Aggregate to subject level ---
    subject_df, feature_cols = aggregate_to_subjects(raw_df)
    n_pos = len(subject_df[subject_df["label"] == 1])
    n_neg = len(subject_df[subject_df["label"] == 0])
    logging.info(f"Subjects: {len(subject_df)} (positive={n_pos}, negative={n_neg})")
    logging.info(f"Features: {len(feature_cols)}")

    X = subject_df[feature_cols].fillna(0).values
    y = subject_df["label"].values
    groups = subject_df["subject_id"].values

    # --- GroupKFold ---
    n_splits = min(5, n_pos, n_neg)
    if n_splits < 2:
        logging.error(f"Not enough subjects per class for GroupKFold (need >=2, got pos={n_pos} neg={n_neg})")
        sys.exit(1)

    gkf = GroupKFold(n_splits=n_splits)
    logging.info(f"Cross-validation: GroupKFold with {n_splits} folds")
    logging.info("Guarantee: no subject appears in both train and test within any fold.")

    # --- Candidate models ---
    candidates = {
        "LogisticRegression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, random_state=42)),
        ]),
        "RandomForest": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(n_estimators=200, random_state=42)),
        ]),
        "GradientBoosting": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", GradientBoostingClassifier(n_estimators=200, random_state=42)),
        ]),
    }

    # --- Train and evaluate each candidate ---
    all_results = {}

    for name, pipeline in candidates.items():
        logging.info(f"\n--- {name} ---")
        fold_metrics = []

        for fold_idx, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            groups_test = groups[test_idx]

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            y_proba = pipeline.predict_proba(X_test)[:, 1]

            acc = accuracy_score(y_test, y_pred)
            sens = recall_score(y_test, y_pred, zero_division=0)
            spec = specificity(y_test, y_pred)
            try:
                auc_val = roc_auc_score(y_test, y_proba)
            except ValueError:
                auc_val = float("nan")
            cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

            fold_metrics.append({
                "fold": fold_idx + 1,
                "accuracy": acc,
                "sensitivity": sens,
                "specificity": spec,
                "auc": auc_val,
                "confusion_matrix": cm.tolist(),
                "test_subjects": list(groups_test),
            })

            logging.info(
                f"  Fold {fold_idx+1}: acc={acc:.3f} sens={sens:.3f} "
                f"spec={spec:.3f} auc={auc_val:.3f} | test_subjects={list(groups_test)}"
            )

        # Aggregate across folds
        mean_acc = np.mean([m["accuracy"] for m in fold_metrics])
        mean_sens = np.mean([m["sensitivity"] for m in fold_metrics])
        mean_spec = np.mean([m["specificity"] for m in fold_metrics])
        mean_auc = np.nanmean([m["auc"] for m in fold_metrics])

        all_results[name] = {
            "mean_accuracy": mean_acc,
            "mean_sensitivity": mean_sens,
            "mean_specificity": mean_spec,
            "mean_auc": mean_auc,
            "per_fold": fold_metrics,
        }

        logging.info(
            f"  MEAN: acc={mean_acc:.3f} sens={mean_sens:.3f} "
            f"spec={mean_spec:.3f} auc={mean_auc:.3f}"
        )

    # --- Select best model by AUC ---
    best_name = max(all_results, key=lambda k: all_results[k]["mean_auc"])
    best_auc = all_results[best_name]["mean_auc"]
    logging.info(f"\n{'='*60}")
    logging.info(f"BEST MODEL: {best_name} (mean AUC={best_auc:.4f})")
    logging.info(f"{'='*60}")

    # --- Retrain best on full data ---
    best_pipeline = candidates[best_name]
    best_pipeline.fit(X, y)

    # --- Save model ---
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "model_B_v1.pkl")

    model_data = {
        "model": best_pipeline,
        "classifier": best_name,
        "features": feature_cols,
        "version": "v1",
        "trained_at": datetime.now().isoformat(),
        "n_subjects": len(subject_df),
        "n_positive": n_pos,
        "n_negative": n_neg,
        "cv_scores": all_results,
        "cv_folds": n_splits,
        "disclaimer": DISCLAIMER,
    }

    with open(model_path, "wb") as f:
        pickle.dump(model_data, f)

    logging.info(f"Model saved: {model_path}")
    logging.info(f"Log: {log_file}")
    logging.info(DISCLAIMER)

    # --- Print comparison table ---
    logging.info(f"\n{'='*60}")
    logging.info("MODEL COMPARISON")
    logging.info(f"{'='*60}")
    logging.info(f"{'Model':<25} {'Accuracy':>10} {'Sensitivity':>12} {'Specificity':>12} {'AUC':>8}")
    logging.info("-" * 70)
    for name, res in all_results.items():
        marker = " <-- BEST" if name == best_name else ""
        logging.info(
            f"{name:<25} {res['mean_accuracy']:>10.4f} {res['mean_sensitivity']:>12.4f} "
            f"{res['mean_specificity']:>12.4f} {res['mean_auc']:>8.4f}{marker}"
        )

    return model_path, all_results


if __name__ == "__main__":
    train()
