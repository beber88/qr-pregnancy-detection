"""
Retraining Pipeline — Single Command Full Rebuild
Runs the entire pipeline end to end:
  1. Rebuild index.csv from PICTURES/
  2. Re-extract hand-coded features (features.csv)
  3. Re-extract CNN embeddings (deep_features.csv)
  4. Run sanity check
  5. If sanity check passes and both classes exist, retrain all models
  6. Version new models with timestamp, save to models/
  7. Update models/registry.json with metrics
  8. Warn (but still save) if new model AUC is worse than production

Usage:
    python src/retrain.py

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import json
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
REGISTRY_PATH = os.path.join(MODELS_DIR, "registry.json")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features.csv")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"retrain_{ts}.log")
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


def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r") as f:
            return json.load(f)
    return {"models": [], "production": {"hand_coded": None, "cnn": None}}


def save_registry(registry):
    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


def get_production_auc(registry, model_type):
    """Get the AUC of the current production model for comparison."""
    prod_filename = registry["production"].get(model_type)
    if not prod_filename:
        return None
    for entry in registry["models"]:
        if entry["filename"] == prod_filename:
            return entry.get("mean_auc")
    return None


def next_version(registry, model_type):
    """Compute next version number for a model type."""
    versions = [
        e.get("version_number", 0)
        for e in registry["models"]
        if e.get("type") == model_type
    ]
    return max(versions, default=0) + 1


def retrain():
    log_file = setup_logging()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.info("=" * 60)
    logging.info("RETRAIN PIPELINE — Full Rebuild")
    logging.info(f"Timestamp: {ts}")
    logging.info("=" * 60)

    registry = load_registry()

    # ------------------------------------------------------------------
    # Step 1: Rebuild index
    # ------------------------------------------------------------------
    logging.info("\n[1/5] Rebuilding index.csv from PICTURES/...")
    from build_index import build_index
    build_index()
    logging.info("Index rebuild complete.")

    # ------------------------------------------------------------------
    # Step 2: Re-extract hand-coded features
    # ------------------------------------------------------------------
    logging.info("\n[2/5] Re-extracting hand-coded features...")
    from phase1_extract import run_extraction
    run_extraction()
    logging.info("Hand-coded feature extraction complete.")

    # ------------------------------------------------------------------
    # Step 3: Re-extract CNN embeddings
    # ------------------------------------------------------------------
    logging.info("\n[3/5] Re-extracting CNN embeddings...")
    from deep_features import run_extraction as run_deep_extraction
    run_deep_extraction()
    logging.info("CNN embedding extraction complete.")

    # ------------------------------------------------------------------
    # Step 4: Check if both classes exist
    # ------------------------------------------------------------------
    import pandas as pd
    df = pd.read_csv(FEATURES_CSV)
    labels_present = set(df["label"].unique())
    has_both_classes = labels_present == {0, 1}

    if not has_both_classes:
        logging.warning("\n" + "=" * 60)
        logging.warning("BOTH CLASSES NOT YET PRESENT")
        logging.warning(f"Labels found: {labels_present}")
        logging.warning("Data preparation complete. Skipping sanity check and training.")
        logging.warning("Add NEGATIVE subjects and re-run retrain.py when ready.")
        logging.warning("=" * 60)
        save_registry(registry)
        return

    # ------------------------------------------------------------------
    # Step 5: Sanity check
    # ------------------------------------------------------------------
    logging.info("\n[4/5] Running sanity check...")
    from sanity_check import run_sanity_check
    passed = run_sanity_check()

    if not passed:
        logging.error("\n" + "=" * 60)
        logging.error("SANITY CHECK FAILED — Data collection confound detected.")
        logging.error("Models will NOT be retrained.")
        logging.error("Fix the data collection protocol before retraining.")
        logging.error("=" * 60)
        save_registry(registry)
        return

    logging.info("Sanity check passed.")

    # ------------------------------------------------------------------
    # Step 6: Train hand-coded features model
    # ------------------------------------------------------------------
    logging.info("\n[5/5] Training models...")

    # 6a: Hand-coded features model (train.py)
    logging.info("\n--- Training hand-coded features model ---")
    from train import train as train_hand_coded, aggregate_to_subjects
    from phase1_extract import FEATURE_NAMES

    import numpy as np
    from sklearn.model_selection import GroupKFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import accuracy_score, recall_score, roc_auc_score, confusion_matrix
    import pickle

    # Replicate train.py logic but with versioned output
    raw_df = pd.read_csv(FEATURES_CSV)
    subject_df, feature_cols = aggregate_to_subjects(raw_df)
    n_pos = len(subject_df[subject_df["label"] == 1])
    n_neg = len(subject_df[subject_df["label"] == 0])

    X = subject_df[feature_cols].fillna(0).values
    y = subject_df["label"].values
    groups = subject_df["subject_id"].values

    n_splits = min(5, n_pos, n_neg)
    gkf = GroupKFold(n_splits=n_splits)

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

    all_results = {}
    for name, pipeline in candidates.items():
        fold_metrics = []
        for fold_idx, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            y_proba = pipeline.predict_proba(X_test)[:, 1]

            acc = accuracy_score(y_test, y_pred)
            sens = recall_score(y_test, y_pred, zero_division=0)
            try:
                auc_val = roc_auc_score(y_test, y_proba)
            except ValueError:
                auc_val = float("nan")

            fold_metrics.append({"accuracy": acc, "sensitivity": sens, "auc": auc_val})

        mean_auc = np.nanmean([m["auc"] for m in fold_metrics])
        all_results[name] = {"mean_auc": mean_auc, "per_fold": fold_metrics}
        logging.info(f"  {name}: mean AUC = {mean_auc:.4f}")

    best_name = max(all_results, key=lambda k: all_results[k]["mean_auc"])
    best_auc = all_results[best_name]["mean_auc"]
    logging.info(f"  Best: {best_name} (AUC={best_auc:.4f})")

    # Retrain on full data
    best_pipeline = candidates[best_name]
    best_pipeline.fit(X, y)

    # Version and save
    vn = next_version(registry, "hand_coded")
    hc_filename = f"model_B_v{vn}_{ts}.pkl"
    hc_path = os.path.join(MODELS_DIR, hc_filename)

    model_data = {
        "model": best_pipeline,
        "classifier": best_name,
        "features": feature_cols,
        "version": f"v{vn}",
        "trained_at": datetime.now().isoformat(),
        "n_subjects": len(subject_df),
        "n_positive": n_pos,
        "n_negative": n_neg,
        "cv_scores": {k: {"mean_auc": v["mean_auc"]} for k, v in all_results.items()},
        "cv_folds": n_splits,
        "disclaimer": DISCLAIMER,
    }

    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(hc_path, "wb") as f:
        pickle.dump(model_data, f)

    logging.info(f"  Saved: {hc_filename}")

    # Compare with production
    prod_auc = get_production_auc(registry, "hand_coded")
    if prod_auc is not None and best_auc < prod_auc:
        logging.warning(f"  WARNING: New model AUC ({best_auc:.4f}) is WORSE than "
                        f"production ({prod_auc:.4f}). Model saved but NOT auto-promoted.")
    elif prod_auc is not None:
        logging.info(f"  New AUC ({best_auc:.4f}) >= production ({prod_auc:.4f})")

    # Register
    registry["models"].append({
        "filename": hc_filename,
        "type": "hand_coded",
        "version": f"v{vn}",
        "version_number": vn,
        "trained_at": datetime.now().isoformat(),
        "n_subjects": len(subject_df),
        "n_positive": n_pos,
        "n_negative": n_neg,
        "mean_auc": round(float(best_auc), 4),
        "classifier": best_name,
        "cv_folds": n_splits,
    })

    # 6b: CNN model — skeleton exists but requires both classes
    # train_cnn.py will refuse to run with only one class,
    # so we only attempt it when both classes are present (which we confirmed above)
    logging.info("\n--- CNN fine-tuning ---")
    logging.info("  CNN training skeleton is ready (src/train_cnn.py).")
    logging.info("  To train: python src/train_cnn.py")
    logging.info("  CNN training is computationally expensive and runs separately.")
    logging.info("  It is NOT auto-triggered by retrain.py to keep rebuild times fast.")

    # ------------------------------------------------------------------
    # Save registry
    # ------------------------------------------------------------------
    save_registry(registry)

    logging.info(f"\n{'='*60}")
    logging.info("RETRAIN COMPLETE")
    logging.info(f"{'='*60}")
    logging.info(f"Hand-coded model: {hc_filename} (AUC={best_auc:.4f})")
    logging.info(f"Registry: {REGISTRY_PATH}")
    logging.info(f"Log: {log_file}")
    if registry["production"]["hand_coded"] is None:
        logging.info("\nNo production model set. Run promote_model.py to promote.")
    logging.info(DISCLAIMER)


if __name__ == "__main__":
    retrain()
