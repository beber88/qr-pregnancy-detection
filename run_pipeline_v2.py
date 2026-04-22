"""
Pipeline V2 — Full extraction: photos + videos + training

Runs:
  1. build_index.py     — Scan PICTURES/, index all files
  2. features_v2        — Extract 32 photo features (with calibration + Layla)
  3. video_features     — Extract 42 temporal features from videos
  4. train_v2           — Train Photo / Video / Combined models

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import logging
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
INDEX_CSV = os.path.join(PROCESSED_DIR, "index.csv")
FEATURES_V2_CSV = os.path.join(PROCESSED_DIR, "features_v2.csv")
VIDEO_FEATURES_CSV = os.path.join(PROCESSED_DIR, "video_features.csv")
PICTURES_DIR = os.path.join(PROJECT_ROOT, "PICTURES - VIDEO")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"pipeline_v2_{ts}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_file


def step1_build_index():
    logging.info("=" * 60)
    logging.info("STEP 1: Build Index")
    logging.info("=" * 60)
    from build_index import build_index
    return build_index()


def step2_extract_photo_features():
    logging.info("\n" + "=" * 60)
    logging.info("STEP 2: Extract Photo Features V2 (32 features)")
    logging.info("=" * 60)

    import pandas as pd
    from features_v2 import extract_features_v2

    index_df = pd.read_csv(INDEX_CSV)
    logging.info(f"Index loaded: {len(index_df)} rows")

    rows = []
    for i, idx_row in index_df.iterrows():
        filepath = idx_row["filepath"]

        # Only process photos and video frames (not raw videos)
        if idx_row["media_type"] not in ("photo", "video_frame"):
            continue

        features = extract_features_v2(filepath)
        if features is None:
            continue

        row = {
            "filepath": filepath,
            "subject_id": idx_row["subject_id"],
            "label": idx_row["label"],
            "media_type": idx_row["media_type"],
            "frame_number": idx_row["frame_number"],
            **features,
        }
        rows.append(row)

        if (i + 1) % 20 == 0 or (i + 1) == len(index_df):
            logging.info(f"  Extracted {i + 1}/{len(index_df)}")

    df = pd.DataFrame(rows)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df.to_csv(FEATURES_V2_CSV, index=False)
    logging.info(f"Saved: {FEATURES_V2_CSV} ({df.shape})")
    return df


def step3_extract_video_features():
    logging.info("\n" + "=" * 60)
    logging.info("STEP 3: Extract Video Temporal Features (42 features)")
    logging.info("=" * 60)

    import pandas as pd
    from video_features import extract_video_features

    rows = []

    for label_dir in ["POSITIVE", "NEGATIVE"]:
        label = 1 if label_dir == "POSITIVE" else 0
        group_path = os.path.join(PICTURES_DIR, label_dir)
        if not os.path.isdir(group_path):
            continue

        for subject_id in sorted(os.listdir(group_path)):
            subject_path = os.path.join(group_path, subject_id)
            if not os.path.isdir(subject_path):
                continue

            for fname in sorted(os.listdir(subject_path)):
                if not fname.lower().endswith(('.mp4', '.mov', '.avi')):
                    continue

                video_path = os.path.join(subject_path, fname)
                logging.info(f"  Processing: {label_dir}/{subject_id}/{fname}")

                features = extract_video_features(video_path)
                if features is None:
                    logging.warning(f"    Failed to extract features")
                    continue

                row = {
                    "subject_id": f"{label_dir}_{subject_id}",
                    "label": label,
                    "video_file": fname,
                    "video_path": video_path,
                    **features,
                }
                rows.append(row)

    if not rows:
        logging.warning("No video features extracted")
        return None

    df = pd.DataFrame(rows)
    # Aggregate per subject if multiple videos
    feature_cols = [c for c in df.columns if c.startswith("t_") or c.startswith("video_")]
    numeric_cols = [c for c in feature_cols if df[c].dtype in ('float64', 'int64', 'float32', 'int32')]
    agg = {col: "mean" for col in numeric_cols}
    agg["label"] = "first"
    subject_df = df.groupby("subject_id").agg(agg).reset_index()

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    subject_df.to_csv(VIDEO_FEATURES_CSV, index=False)
    logging.info(f"Saved: {VIDEO_FEATURES_CSV} ({subject_df.shape})")
    logging.info(f"  Subjects with video: {len(subject_df)}")
    return subject_df


def step4_train():
    logging.info("\n" + "=" * 60)
    logging.info("STEP 4: Train Models (Photo / Video / Combined)")
    logging.info("=" * 60)

    # Check if both classes exist
    import pandas as pd

    has_both = False
    if os.path.exists(FEATURES_V2_CSV):
        df = pd.read_csv(FEATURES_V2_CSV)
        labels = set(df["label"].unique())
        if labels == {0, 1}:
            has_both = True

    if not has_both:
        logging.warning("=" * 60)
        logging.warning("CANNOT TRAIN: Need both POSITIVE and NEGATIVE data.")
        logging.warning("Add NEGATIVE samples to PICTURES/NEGATIVE/ and re-run.")
        logging.warning("=" * 60)
        logging.info("Feature extraction complete. Pipeline waiting for NEGATIVE data.")
        return None

    from train_v2 import train_v2
    return train_v2()


def main():
    log_file = setup_logging()
    logging.info("=" * 60)
    logging.info("PIPELINE V2 — Full Photo + Video Processing")
    logging.info("=" * 60)
    logging.info(f"Project root: {PROJECT_ROOT}")

    step1_build_index()
    step2_extract_photo_features()
    step3_extract_video_features()
    step4_train()

    logging.info(f"\nPipeline complete. Log: {log_file}")


if __name__ == "__main__":
    main()
