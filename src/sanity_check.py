"""
Sanity Check — Data Collection Confound Detector

Trains a model using ONLY technical metadata that should NOT carry a
pregnancy signal: file size, filename timestamp, image dimensions,
mean brightness.

If this "bogus" model achieves AUC > 0.65, the data collection process
has a systematic difference between POSITIVE and NEGATIVE groups
(e.g., photos taken at different times, different lighting, different
phones). The main Model B results CANNOT be trusted.

This MUST run BEFORE train.py.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import re
import logging
from datetime import datetime

import cv2
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, accuracy_score

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features.csv")
INDEX_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "index.csv")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."

AUC_THRESHOLD = 0.65  # Above this = confound detected


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"sanity_check_{ts}.log")
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


def extract_timestamp_from_filename(filename):
    """
    Parse timestamp from filenames like PHOTO-2026-04-21-20-34-11.jpg
    Returns minutes since midnight, or NaN if unparseable.
    """
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})", filename)
    if match:
        hour = int(match.group(4))
        minute = int(match.group(5))
        return hour * 60 + minute
    return float("nan")


def extract_bogus_features(index_df):
    """
    Extract ONLY technical metadata features that should be unrelated
    to pregnancy status.
    """
    rows = []

    for _, row in index_df.iterrows():
        filepath = row["filepath"]
        fname = os.path.basename(filepath)

        # File size in bytes
        try:
            file_size = os.path.getsize(filepath)
        except OSError:
            file_size = 0

        # Timestamp from filename
        timestamp_minutes = extract_timestamp_from_filename(fname)

        # Image dimensions and brightness (without ROI — raw image)
        img = cv2.imread(filepath)
        if img is None:
            continue

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_brightness = float(np.mean(gray))

        rows.append({
            "subject_id": row["subject_id"],
            "label": row["label"],
            "file_size": file_size,
            "timestamp_minutes": timestamp_minutes,
            "img_height": h,
            "img_width": w,
            "mean_brightness_raw": mean_brightness,
        })

    return pd.DataFrame(rows)


def run_sanity_check():
    log_file = setup_logging()
    logging.info("=" * 60)
    logging.info("SANITY CHECK — Data Collection Confound Detection")
    logging.info("=" * 60)
    logging.info(
        "Testing whether TECHNICAL metadata (file size, timestamp, "
        "dimensions, brightness) can predict pregnancy status."
    )
    logging.info(
        "If AUC > 0.65, the POSITIVE and NEGATIVE samples were "
        "collected differently and main results cannot be trusted."
    )

    # --- Load index ---
    if not os.path.exists(INDEX_CSV):
        logging.error(f"index.csv not found: {INDEX_CSV}. Run build_index.py first.")
        sys.exit(1)

    index_df = pd.read_csv(INDEX_CSV)

    # --- Check both classes ---
    labels = set(index_df["label"].unique())
    if labels != {0, 1}:
        logging.error("Both classes required for sanity check.")
        logging.error(f"Labels found: {labels}")
        if 0 not in labels:
            logging.error("MISSING: NEGATIVE samples. Add to PICTURES/NEGATIVE/ first.")
        sys.exit(1)

    # --- Extract bogus features ---
    logging.info("Extracting technical metadata features...")
    bogus_df = extract_bogus_features(index_df)
    logging.info(f"Extracted from {len(bogus_df)} images")

    # --- Aggregate to subject level ---
    feature_cols = ["file_size", "timestamp_minutes", "img_height", "img_width", "mean_brightness_raw"]
    agg = {col: "mean" for col in feature_cols}
    agg["label"] = "first"

    subject_df = bogus_df.groupby("subject_id").agg(agg).reset_index()
    subject_df = subject_df.dropna(subset=feature_cols)

    n_pos = len(subject_df[subject_df["label"] == 1])
    n_neg = len(subject_df[subject_df["label"] == 0])
    logging.info(f"Subjects: {len(subject_df)} (positive={n_pos}, negative={n_neg})")

    X = subject_df[feature_cols].fillna(0).values
    y = subject_df["label"].values
    groups = subject_df["subject_id"].values

    # --- GroupKFold (same as real training) ---
    n_splits = min(5, n_pos, n_neg)
    if n_splits < 2:
        logging.error("Not enough subjects per class for cross-validation.")
        sys.exit(1)

    gkf = GroupKFold(n_splits=n_splits)
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(n_estimators=100, random_state=42)),
    ])

    aucs = []
    accs = []

    for fold_idx, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        try:
            auc_val = roc_auc_score(y_test, y_proba)
        except ValueError:
            auc_val = float("nan")

        accs.append(acc)
        aucs.append(auc_val)
        logging.info(f"  Fold {fold_idx+1}: acc={acc:.3f} auc={auc_val:.3f}")

    mean_auc = np.nanmean(aucs)
    mean_acc = np.mean(accs)

    logging.info(f"\nBogus model mean AUC: {mean_auc:.4f}")
    logging.info(f"Bogus model mean Acc: {mean_acc:.4f}")

    # --- Verdict ---
    logging.info("\n" + "=" * 60)
    if mean_auc > AUC_THRESHOLD:
        logging.error("*** CONFOUND DETECTED ***")
        logging.error(
            f"Bogus model AUC = {mean_auc:.3f} (threshold = {AUC_THRESHOLD})"
        )
        logging.error(
            "Technical metadata can distinguish POSITIVE from NEGATIVE samples."
        )
        logging.error(
            "This means the two groups were collected differently "
            "(different time, lighting, phone, etc.)."
        )
        logging.error(
            "DO NOT TRUST Model B results until this confound is resolved."
        )
        logging.error(
            "Recommendations:\n"
            "  1. Check if POSITIVE and NEGATIVE were photographed at different times of day\n"
            "  2. Check if different phones were used for each group\n"
            "  3. Check if lighting conditions differ\n"
            "  4. Re-collect data with matched conditions"
        )
        logging.info("=" * 60)
        logging.info(DISCLAIMER)
        return False  # FAIL
    else:
        logging.info("*** SANITY CHECK PASSED ***")
        logging.info(
            f"Bogus model AUC = {mean_auc:.3f} (threshold = {AUC_THRESHOLD})"
        )
        logging.info(
            "Technical metadata cannot distinguish groups — "
            "no obvious collection confound detected."
        )
        logging.info("Safe to proceed with train.py")
        logging.info("=" * 60)
        logging.info(DISCLAIMER)
        return True  # PASS


if __name__ == "__main__":
    passed = run_sanity_check()
    sys.exit(0 if passed else 1)
