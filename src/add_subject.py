"""
Add Subject — Incremental Data Ingestion
Copies a subject's images into the dataset, validates them, and appends
to index.csv, features.csv, and deep_features.csv without rebuilding.

Usage:
    python src/add_subject.py --group POSITIVE --subject_id 16 --folder /path/to/photos
    python src/add_subject.py --group NEGATIVE --subject_id 1 --folder /path/to/photos

Validation:
  - At least 3 photos in the folder
  - Each image >= 500x500 px
  - Cup ROI detectable in each image
  - No duplicate subject_id in existing data

Does NOT retrain. Just prepares data. Run retrain.py when ready.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import shutil
import logging
import argparse
from datetime import datetime

import cv2
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validate_image import validate_image
from phase1_extract import extract_features
from build_index import extract_video_frames, IMAGE_EXT, VIDEO_EXT

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICTURES_DIR = os.path.join(PROJECT_ROOT, "PICTURES")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
INDEX_CSV = os.path.join(PROCESSED_DIR, "index.csv")
FEATURES_CSV = os.path.join(PROCESSED_DIR, "features.csv")
DEEP_FEATURES_CSV = os.path.join(PROCESSED_DIR, "deep_features.csv")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"add_subject_{ts}.log")
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


def validate_source_folder(folder_path):
    """Check that the source folder meets protocol requirements."""
    if not os.path.isdir(folder_path):
        return False, f"Not a directory: {folder_path}"

    files = os.listdir(folder_path)
    image_files = [f for f in files if os.path.splitext(f)[1].lower() in IMAGE_EXT]

    if len(image_files) < 3:
        return False, f"Need at least 3 photos, found {len(image_files)}"

    # Validate each image
    issues = []
    for fname in image_files:
        fpath = os.path.join(folder_path, fname)
        result = validate_image(fpath)
        if not result["is_valid"]:
            issues.append(f"  {fname}: {', '.join(result['issues'])}")

    if issues:
        return False, "Image validation failed:\n" + "\n".join(issues)

    return True, f"{len(image_files)} photos validated OK"


def check_duplicate(subject_id):
    """Check if subject_id already exists in index.csv."""
    if not os.path.exists(INDEX_CSV):
        return False
    df = pd.read_csv(INDEX_CSV)
    return subject_id in df["subject_id"].values


def copy_to_pictures(source_folder, group, subject_num):
    """Copy images and videos to PICTURES/<group>/<subject_num>/."""
    dest_dir = os.path.join(PICTURES_DIR, group, str(subject_num))
    os.makedirs(dest_dir, exist_ok=True)

    copied = []
    for fname in sorted(os.listdir(source_folder)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in IMAGE_EXT or ext in VIDEO_EXT:
            src = os.path.join(source_folder, fname)
            dst = os.path.join(dest_dir, fname)
            shutil.copy2(src, dst)
            copied.append(dst)

    return dest_dir, copied


def append_to_index(new_rows):
    """Append rows to index.csv."""
    new_df = pd.DataFrame(new_rows)
    if os.path.exists(INDEX_CSV):
        existing = pd.read_csv(INDEX_CSV)
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df
    combined.to_csv(INDEX_CSV, index=False)
    return len(new_df)


def append_features(new_rows, csv_path):
    """Append rows to a features CSV (hand-coded or deep)."""
    new_df = pd.DataFrame(new_rows)
    if os.path.exists(csv_path):
        existing = pd.read_csv(csv_path)
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df
    combined.to_csv(csv_path, index=False)
    return len(new_df)


def extract_deep_features_for_images(index_rows):
    """Extract CNN embeddings for new images only."""
    try:
        from deep_features import build_model, build_transform, extract_embedding, EMBEDDING_DIM
        import torch
    except ImportError:
        logging.warning("PyTorch not available. Skipping deep feature extraction.")
        return []

    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    model = build_model().to(device)
    transform = build_transform()
    embedding_cols = [f"emb_{i:04d}" for i in range(EMBEDDING_DIM)]

    rows = []
    for idx_row in index_rows:
        emb = extract_embedding(model, transform, idx_row["filepath"], device)
        if emb is None:
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

    return rows


def add_subject(group, subject_id, folder_path):
    log_file = setup_logging()
    logging.info("=" * 60)
    logging.info("ADD SUBJECT — Incremental Data Ingestion")
    logging.info("=" * 60)
    logging.info(f"Group: {group}")
    logging.info(f"Subject ID: {subject_id}")
    logging.info(f"Source folder: {folder_path}")

    # Derive the canonical subject_id
    subject_num = str(subject_id)
    canonical_id = f"{group}_{subject_num}"
    label = 1 if group == "POSITIVE" else 0

    # Check for duplicates
    if check_duplicate(canonical_id):
        logging.error(f"Subject '{canonical_id}' already exists in index.csv.")
        logging.error("Remove the existing subject first or use a different ID.")
        sys.exit(1)

    # Validate source folder
    logging.info("Validating source images...")
    valid, message = validate_source_folder(folder_path)
    logging.info(f"  {message}")
    if not valid:
        logging.error("Source folder validation FAILED. Subject not added.")
        sys.exit(1)

    # Copy to PICTURES/
    logging.info(f"Copying to PICTURES/{group}/{subject_num}/...")
    dest_dir, copied_files = copy_to_pictures(folder_path, group, subject_num)
    logging.info(f"  Copied {len(copied_files)} files to {dest_dir}")

    # Build index rows
    index_rows = []
    for fpath in copied_files:
        ext = os.path.splitext(fpath)[1].lower()
        if ext in IMAGE_EXT:
            index_rows.append({
                "filepath": fpath,
                "subject_id": canonical_id,
                "label": label,
                "media_type": "photo",
                "frame_number": 0,
            })
        elif ext in VIDEO_EXT:
            frames = extract_video_frames(fpath, subject_num, group)
            for frame_path, frame_num in frames:
                index_rows.append({
                    "filepath": frame_path,
                    "subject_id": canonical_id,
                    "label": label,
                    "media_type": "video_frame",
                    "frame_number": frame_num,
                })

    # Append to index.csv
    n_idx = append_to_index(index_rows)
    logging.info(f"  Appended {n_idx} rows to index.csv")

    # Extract and append hand-coded features
    logging.info("Extracting hand-coded features...")
    feature_rows = []
    for idx_row in index_rows:
        features = extract_features(idx_row["filepath"])
        if features is None:
            continue
        feature_rows.append({**idx_row, **features})

    n_feat = append_features(feature_rows, FEATURES_CSV)
    logging.info(f"  Appended {n_feat} rows to features.csv")

    # Extract and append CNN embeddings
    logging.info("Extracting CNN embeddings...")
    deep_rows = extract_deep_features_for_images(index_rows)
    if deep_rows:
        n_deep = append_features(deep_rows, DEEP_FEATURES_CSV)
        logging.info(f"  Appended {n_deep} rows to deep_features.csv")
    else:
        logging.info("  No deep features extracted (PyTorch may not be available)")

    # Summary
    logging.info(f"\n{'='*60}")
    logging.info("SUBJECT ADDED SUCCESSFULLY")
    logging.info(f"{'='*60}")
    logging.info(f"  Subject: {canonical_id}")
    logging.info(f"  Group: {group} (label={label})")
    logging.info(f"  Images: {n_idx}")
    logging.info(f"  Features: {n_feat}")
    logging.info(f"  Destination: {dest_dir}")
    logging.info(f"\nData is ready. Run retrain.py when you want to train.")
    logging.info(f"Log: {log_file}")
    logging.info(DISCLAIMER)


def main():
    parser = argparse.ArgumentParser(description="Add a new subject to the dataset")
    parser.add_argument("--group", required=True, choices=["POSITIVE", "NEGATIVE"],
                        help="POSITIVE (pregnant) or NEGATIVE (not pregnant)")
    parser.add_argument("--subject_id", required=True,
                        help="Subject identifier (e.g., 16, 001)")
    parser.add_argument("--folder", required=True,
                        help="Path to folder containing subject's images")
    args = parser.parse_args()

    add_subject(args.group, args.subject_id, args.folder)


if __name__ == "__main__":
    main()
