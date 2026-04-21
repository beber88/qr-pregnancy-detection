"""
Training Dashboard — CLI Status Report
Prints the current state of the project:
  - POSITIVE / NEGATIVE subject counts
  - Latest model's CV AUC
  - Total models trained
  - Which model is in production
  - Date of last retraining

Usage:
    python src/show_progress.py

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import json

import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
INDEX_CSV = os.path.join(PROCESSED_DIR, "index.csv")
FEATURES_CSV = os.path.join(PROCESSED_DIR, "features.csv")
DEEP_FEATURES_CSV = os.path.join(PROCESSED_DIR, "deep_features.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
REGISTRY_PATH = os.path.join(MODELS_DIR, "registry.json")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."


def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)
    return {"models": [], "production": {"hand_coded": None, "cnn": None}}


def show_progress():
    print("=" * 60)
    print("  PREGNANCY DETECTION AI — Project Status")
    print("=" * 60)

    # --- Data ---
    print("\n  DATA")
    print("  " + "-" * 40)

    n_pos_subjects = 0
    n_neg_subjects = 0
    n_total_images = 0
    n_photos = 0
    n_frames = 0

    if os.path.exists(INDEX_CSV):
        df = pd.read_csv(INDEX_CSV)
        n_total_images = len(df)
        n_photos = len(df[df["media_type"] == "photo"])
        n_frames = len(df[df["media_type"] == "video_frame"])

        pos = df[df["label"] == 1]
        neg = df[df["label"] == 0]
        n_pos_subjects = pos["subject_id"].nunique()
        n_neg_subjects = neg["subject_id"].nunique()

    print(f"  POSITIVE subjects (pregnant):      {n_pos_subjects}")
    print(f"  NEGATIVE subjects (not pregnant):   {n_neg_subjects}")
    print(f"  Total subjects:                     {n_pos_subjects + n_neg_subjects}")
    print(f"  Total images/frames:                {n_total_images}")
    print(f"    Photos:                           {n_photos}")
    print(f"    Video frames:                     {n_frames}")

    has_both = n_pos_subjects > 0 and n_neg_subjects > 0
    if not has_both:
        missing = []
        if n_neg_subjects == 0:
            missing.append("NEGATIVE")
        if n_pos_subjects == 0:
            missing.append("POSITIVE")
        print(f"\n  *** BLOCKED: Missing {', '.join(missing)} data ***")
        print(f"  *** Cannot train until both classes are present ***")

    # --- Features ---
    print("\n  FEATURE EXTRACTION")
    print("  " + "-" * 40)

    if os.path.exists(FEATURES_CSV):
        feat_df = pd.read_csv(FEATURES_CSV)
        feat_cols = [c for c in feat_df.columns
                     if c not in ("filepath", "subject_id", "label", "media_type", "frame_number")]
        print(f"  Hand-coded features:                {len(feat_cols)}")
        print(f"  Rows in features.csv:               {len(feat_df)}")
    else:
        print(f"  Hand-coded features:                not extracted yet")

    if os.path.exists(DEEP_FEATURES_CSV):
        deep_df = pd.read_csv(DEEP_FEATURES_CSV, nrows=1)
        emb_cols = [c for c in deep_df.columns if c.startswith("emb_")]
        print(f"  CNN embedding dimensions:           {len(emb_cols)}")
        deep_full = pd.read_csv(DEEP_FEATURES_CSV, usecols=["subject_id"])
        print(f"  Rows in deep_features.csv:          {len(deep_full)}")
    else:
        print(f"  CNN embeddings:                     not extracted yet")

    # --- Models ---
    print("\n  MODELS")
    print("  " + "-" * 40)

    registry = load_registry()
    n_models = len(registry["models"])
    prod_hc = registry["production"].get("hand_coded")
    prod_cnn = registry["production"].get("cnn")

    print(f"  Total models trained:               {n_models}")

    if n_models > 0:
        # Latest model
        latest = max(registry["models"], key=lambda e: e.get("trained_at", ""))
        print(f"  Latest model:                       {latest['filename']}")
        print(f"  Latest model AUC:                   {latest.get('mean_auc', 'N/A')}")
        print(f"  Latest model classifier:            {latest.get('classifier', 'N/A')}")
        print(f"  Latest model date:                  {latest.get('trained_at', 'N/A')[:19]}")

        # By type
        hc_models = [e for e in registry["models"] if e.get("type") == "hand_coded"]
        cnn_models = [e for e in registry["models"] if e.get("type") == "cnn"]
        print(f"  Hand-coded feature models:          {len(hc_models)}")
        print(f"  CNN models:                         {len(cnn_models)}")
    else:
        print(f"  No models trained yet.")

    # --- Production ---
    print("\n  PRODUCTION")
    print("  " + "-" * 40)

    if prod_hc:
        hc_entry = next((e for e in registry["models"] if e["filename"] == prod_hc), None)
        print(f"  Hand-coded model:                   {prod_hc}")
        if hc_entry:
            print(f"    AUC:                              {hc_entry.get('mean_auc', 'N/A')}")
            print(f"    Promoted:                         {hc_entry.get('promoted_at', 'N/A')[:19] if hc_entry.get('promoted_at') else 'N/A'}")
    else:
        print(f"  Hand-coded model:                   (none)")

    if prod_cnn:
        cnn_entry = next((e for e in registry["models"] if e["filename"] == prod_cnn), None)
        print(f"  CNN model:                          {prod_cnn}")
        if cnn_entry:
            print(f"    AUC:                              {cnn_entry.get('mean_auc', 'N/A')}")
    else:
        print(f"  CNN model:                          (none)")

    # --- Last retraining ---
    print("\n  TIMELINE")
    print("  " + "-" * 40)

    if n_models > 0:
        latest = max(registry["models"], key=lambda e: e.get("trained_at", ""))
        print(f"  Last retraining:                    {latest.get('trained_at', 'N/A')[:19]}")
    else:
        print(f"  Last retraining:                    never")

    # --- Next steps ---
    print(f"\n  NEXT STEPS")
    print("  " + "-" * 40)

    if n_neg_subjects == 0:
        print("  1. Collect NEGATIVE (not pregnant) urine samples")
        print("     python src/add_subject.py --group NEGATIVE --subject_id 1 --folder /path")
        print("  2. Once both classes exist, run: python src/retrain.py")
        print("  3. Review metrics, then: python src/promote_model.py --latest hand_coded")
    elif n_models == 0:
        print("  1. Run retraining: python src/retrain.py")
        print("  2. Review metrics, then promote: python src/promote_model.py --latest hand_coded")
    elif prod_hc is None:
        print("  1. Promote a model: python src/promote_model.py --latest hand_coded")
        print("  2. Restart API: python src/api.py")
    else:
        print("  - Add more subjects to improve accuracy")
        print("  - Retrain: python src/retrain.py")
        print("  - Check models: python src/promote_model.py --list")

    print(f"\n  {DISCLAIMER}")
    print("=" * 60)


if __name__ == "__main__":
    show_progress()
