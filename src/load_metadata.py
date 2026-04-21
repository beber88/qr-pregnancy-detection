"""
Metadata CSV Loader
Merges data/metadata.csv with data/processed/features.csv on subject_id.

Handles missing metadata gracefully — fills with NaN so that:
  - Model A (metadata only) trains on subjects that have metadata
  - Model C (combined) uses whatever is available, NaN for the rest

Expected metadata.csv format (flexible — extra columns are kept):
  subject_id, weeks_pregnant, time_of_day, hydration, phone_model, vitamins

If the CSV uses different column names or formats, this script normalizes
them into a consistent schema.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import logging
from datetime import datetime

import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_CSV = os.path.join(PROJECT_ROOT, "data", "metadata.csv")
FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features.csv")
MERGED_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features_with_metadata.csv")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."

# Expected metadata columns and how to encode them for modeling
METADATA_SCHEMA = {
    "subject_id": {"type": "key", "required": True},
    "weeks_pregnant": {"type": "numeric", "default": np.nan},
    "time_of_day": {"type": "time", "default": np.nan},
    "hydration": {"type": "numeric", "default": np.nan},
    "phone_model": {"type": "categorical", "default": "unknown"},
    "vitamins": {"type": "boolean", "default": np.nan},
}

# These are the columns that Model A and Model C will use
METADATA_FEATURE_COLS = [
    "weeks_pregnant",
    "time_of_day_minutes",
    "hydration",
    "vitamins_encoded",
]


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"load_metadata_{ts}.log")
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


def time_to_minutes(t):
    """Convert HH:MM or HH:MM:SS to minutes since midnight."""
    if pd.isna(t):
        return np.nan
    t = str(t).strip()
    try:
        parts = t.replace(".", ":").split(":")
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        return hours * 60 + minutes
    except (ValueError, IndexError):
        return np.nan


def encode_boolean(val):
    """Encode yes/no/true/false to 1/0."""
    if pd.isna(val):
        return np.nan
    val = str(val).strip().lower()
    if val in ("yes", "true", "1", "כן"):
        return 1
    if val in ("no", "false", "0", "לא"):
        return 0
    return np.nan


def normalize_subject_id(sid, label=None):
    """
    Normalize subject_id to match the format used in features.csv.
    features.csv uses: POSITIVE_1, POSITIVE_2, NEGATIVE_1, etc.
    metadata.csv might use: 1, 2, P1, N1, POSITIVE_1, etc.
    """
    sid = str(sid).strip()

    # Already in correct format
    if sid.startswith("POSITIVE_") or sid.startswith("NEGATIVE_"):
        return sid

    # Try to extract the numeric part
    numeric = "".join(c for c in sid if c.isdigit())
    if not numeric:
        return sid  # Can't normalize, return as-is

    # If label is provided, use it to determine prefix
    if label is not None:
        prefix = "POSITIVE" if int(label) == 1 else "NEGATIVE"
        return f"{prefix}_{numeric}"

    return sid


def load_metadata(metadata_path=None):
    """
    Load and normalize metadata CSV.

    Args:
        metadata_path: Path to CSV. Defaults to data/metadata.csv.

    Returns:
        pd.DataFrame with normalized columns, or None if file doesn't exist.
    """
    if metadata_path is None:
        metadata_path = METADATA_CSV

    if not os.path.exists(metadata_path):
        logging.warning(f"Metadata file not found: {metadata_path}")
        return None

    # Read CSV — handle various separators and encodings
    for sep in [",", "\t", ";"]:
        try:
            df = pd.read_csv(metadata_path, sep=sep, encoding="utf-8-sig")
            if len(df.columns) > 1:
                break
        except Exception:
            continue
    else:
        logging.error(f"Could not parse metadata CSV: {metadata_path}")
        return None

    # Strip whitespace from column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    logging.info(f"Loaded metadata: {df.shape}")
    logging.info(f"Columns: {list(df.columns)}")

    # --- Normalize subject_id ---
    if "subject_id" not in df.columns:
        # Try common alternatives
        for alt in ["id", "subject", "participant", "participant_id", "sample_id"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "subject_id"})
                break
        else:
            logging.error("No subject_id column found in metadata. "
                         f"Available columns: {list(df.columns)}")
            return None

    # Normalize subject_id format to match features.csv
    label_col = None
    for alt in ["label", "status", "pregnant", "group"]:
        if alt in df.columns:
            label_col = alt
            break

    df["subject_id"] = df.apply(
        lambda row: normalize_subject_id(
            row["subject_id"],
            row.get(label_col) if label_col else None
        ),
        axis=1,
    )

    # --- Encode time_of_day ---
    if "time_of_day" in df.columns:
        df["time_of_day_minutes"] = df["time_of_day"].apply(time_to_minutes)
        logging.info(f"  time_of_day → time_of_day_minutes (range: "
                    f"{df['time_of_day_minutes'].min():.0f}-{df['time_of_day_minutes'].max():.0f})")

    # --- Encode vitamins ---
    if "vitamins" in df.columns:
        df["vitamins_encoded"] = df["vitamins"].apply(encode_boolean)
        logging.info(f"  vitamins → vitamins_encoded (yes={int((df['vitamins_encoded']==1).sum())}, "
                    f"no={int((df['vitamins_encoded']==0).sum())}, "
                    f"missing={int(df['vitamins_encoded'].isna().sum())})")

    # --- Ensure numeric columns ---
    for col in ["weeks_pregnant", "hydration"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def merge_with_features(metadata_df=None, features_path=None, output_path=None):
    """
    Merge metadata with features.csv on subject_id.
    Missing metadata is filled with NaN — no rows are dropped.

    Args:
        metadata_df: Pre-loaded metadata DataFrame (or None to load from file).
        features_path: Path to features.csv.
        output_path: Where to save the merged CSV.

    Returns:
        Merged DataFrame.
    """
    if features_path is None:
        features_path = FEATURES_CSV
    if output_path is None:
        output_path = MERGED_CSV

    if not os.path.exists(features_path):
        logging.error(f"Features file not found: {features_path}")
        return None

    features_df = pd.read_csv(features_path)
    logging.info(f"Loaded features: {features_df.shape}")

    if metadata_df is None:
        metadata_df = load_metadata()

    if metadata_df is None:
        logging.warning("No metadata available — saving features without metadata columns.")
        # Still add empty metadata columns so downstream code doesn't break
        for col in METADATA_FEATURE_COLS:
            features_df[col] = np.nan
        features_df.to_csv(output_path, index=False)
        logging.info(f"Saved (no metadata): {output_path}")
        return features_df

    # Aggregate metadata to subject level (should already be one row per subject,
    # but handle duplicates gracefully)
    meta_cols = [c for c in metadata_df.columns if c != "subject_id"]
    meta_subject = metadata_df.groupby("subject_id").first().reset_index()

    # Merge — left join to keep all features rows
    merged = features_df.merge(
        meta_subject, on="subject_id", how="left", suffixes=("", "_meta")
    )

    # Report merge stats
    n_features_subjects = features_df["subject_id"].nunique()
    n_meta_subjects = meta_subject["subject_id"].nunique()
    n_matched = merged[merged[METADATA_FEATURE_COLS[0]].notna()]["subject_id"].nunique() \
        if METADATA_FEATURE_COLS[0] in merged.columns else 0

    logging.info(f"Merge results:")
    logging.info(f"  Feature subjects:  {n_features_subjects}")
    logging.info(f"  Metadata subjects: {n_meta_subjects}")
    logging.info(f"  Matched:           {n_matched}")
    logging.info(f"  Unmatched (NaN):   {n_features_subjects - n_matched}")

    # Ensure all expected metadata columns exist
    for col in METADATA_FEATURE_COLS:
        if col not in merged.columns:
            merged[col] = np.nan

    # Save
    merged.to_csv(output_path, index=False)
    logging.info(f"Saved merged file: {output_path} ({merged.shape})")
    logging.info(DISCLAIMER)

    return merged


def run():
    """Main entry point — load metadata and merge with features."""
    setup_logging()
    logging.info("=" * 60)
    logging.info("METADATA LOADER — Merge metadata.csv with features.csv")
    logging.info("=" * 60)

    metadata_df = load_metadata()
    merged_df = merge_with_features(metadata_df)

    if merged_df is not None:
        # Summary of metadata coverage
        logging.info("\nMetadata coverage per column:")
        for col in METADATA_FEATURE_COLS:
            if col in merged_df.columns:
                n_valid = merged_df[col].notna().sum()
                n_total = len(merged_df)
                logging.info(f"  {col}: {n_valid}/{n_total} ({n_valid/n_total:.0%})")

    return merged_df


if __name__ == "__main__":
    run()
