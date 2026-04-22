"""
Training V2 — Unified Photo + Video Model

Three model tiers:
  Model A: Photo features only (32 features from features_v2)
  Model B: Video features only (42 temporal features from video_features)
  Model C: Combined photo + video (74 features — the full brain)

Each tier trained with GroupKFold (subject-level splits).
Best model selected by AUC across all tiers.

The system learns to find whatever visual signature distinguishes
pregnancy urine — we don't tell it what to look for.

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

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_V2_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features_v2.csv")
VIDEO_FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "video_features.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."

# Feature groups
PHOTO_FEATURES = [
    # Original 15
    "r_mean", "g_mean", "b_mean", "brightness", "turbidity",
    "dominant_hue", "hue_spread", "texture_score", "edge_intensity",
    "bubble_count", "contrast", "saturation", "color_variance",
    "yellowness", "gy_ratio",
    # Calibration (4)
    "cal_card_found", "cal_delta_e", "cal_quality_ok", "cal_cct_estimate",
    # Layla-range (6)
    "layla_r_ratio", "layla_rg_ratio", "layla_rb_ratio",
    "layla_r_ratio_std", "layla_r_skew", "layla_r_dominant",
    # CIELAB (4)
    "lab_L", "lab_a", "lab_b", "lab_chroma",
    # Concentration proxy (3)
    "conc_proxy_sv", "conc_proxy_yellow_sat", "conc_darkness",
]

VIDEO_FEATURES = [
    # Color dynamics (18)
    "t_r_ratio_mean", "t_r_ratio_std", "t_r_ratio_trend",
    "t_rg_ratio_mean", "t_rg_ratio_std", "t_rg_ratio_trend",
    "t_rb_ratio_mean", "t_rb_ratio_std", "t_rb_ratio_trend",
    "t_hue_mean", "t_hue_std", "t_hue_trend",
    "t_saturation_mean", "t_saturation_std", "t_saturation_trend",
    "t_value_mean", "t_value_std", "t_value_trend",
    # Turbidity dynamics (4)
    "t_turb_mean", "t_turb_std", "t_turb_trend", "t_turb_settling",
    # Optical flow (7)
    "t_flow_mean", "t_flow_std", "t_flow_trend", "t_flow_decay",
    "t_flow_coherence_mean", "t_flow_peak", "t_flow_peak_time",
    # Texture dynamics (3)
    "t_texture_mean", "t_texture_std", "t_texture_trend",
    # Spectral dynamics (2)
    "t_layla_r_stability", "t_layla_r_autocorr",
    # Settling behavior (3)
    "t_activity_mean", "t_activity_trend", "t_time_to_calm",
    # Statistical (2)
    "t_overall_dynamism", "t_r_ratio_complexity",
    # Metadata (3)
    "video_duration", "video_frames_sampled", "video_fps",
]


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"train_v2_{ts}.log")
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
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return tn / (tn + fp) if (tn + fp) > 0 else 0.0


def load_photo_features():
    """Load and aggregate photo features to subject level."""
    if not os.path.exists(FEATURES_V2_CSV):
        return None
    df = pd.read_csv(FEATURES_V2_CSV)
    available = [c for c in PHOTO_FEATURES if c in df.columns]
    agg = {col: "mean" for col in available}
    agg["label"] = "first"
    subject_df = df.groupby("subject_id").agg(agg).reset_index()
    return subject_df, available


def load_video_features():
    """Load video features (already one row per subject)."""
    if not os.path.exists(VIDEO_FEATURES_CSV):
        return None
    df = pd.read_csv(VIDEO_FEATURES_CSV)
    available = [c for c in VIDEO_FEATURES if c in df.columns]
    return df, available


def train_tier(name, X, y, groups, feature_names, n_splits):
    """Train and evaluate one model tier."""
    logging.info(f"\n{'='*60}")
    logging.info(f"TIER: {name} ({len(feature_names)} features)")
    logging.info(f"{'='*60}")

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

    gkf = GroupKFold(n_splits=n_splits)
    tier_results = {}

    for clf_name, pipeline in candidates.items():
        fold_metrics = []

        for fold_idx, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            # Need both classes in train
            if len(set(y_train)) < 2 or len(set(y_test)) < 2:
                continue

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            y_proba = pipeline.predict_proba(X_test)[:, 1]

            try:
                auc_val = roc_auc_score(y_test, y_proba)
            except ValueError:
                auc_val = float("nan")

            fold_metrics.append({
                "fold": fold_idx + 1,
                "accuracy": accuracy_score(y_test, y_pred),
                "sensitivity": recall_score(y_test, y_pred, zero_division=0),
                "specificity": specificity(y_test, y_pred),
                "auc": auc_val,
            })

        if not fold_metrics:
            continue

        mean_auc = np.nanmean([m["auc"] for m in fold_metrics])
        mean_sens = np.mean([m["sensitivity"] for m in fold_metrics])
        mean_spec = np.mean([m["specificity"] for m in fold_metrics])

        tier_results[clf_name] = {
            "mean_auc": mean_auc,
            "mean_sensitivity": mean_sens,
            "mean_specificity": mean_spec,
            "per_fold": fold_metrics,
        }

        logging.info(
            f"  {clf_name}: AUC={mean_auc:.4f} sens={mean_sens:.3f} spec={mean_spec:.3f}"
        )

    if not tier_results:
        return None, None

    best_clf = max(tier_results, key=lambda k: tier_results[k]["mean_auc"])
    best_auc = tier_results[best_clf]["mean_auc"]

    # Retrain best on full data
    best_pipeline = candidates[best_clf]
    best_pipeline.fit(X, y)

    logging.info(f"  BEST for {name}: {best_clf} (AUC={best_auc:.4f})")

    return {
        "tier": name,
        "best_classifier": best_clf,
        "best_auc": best_auc,
        "pipeline": best_pipeline,
        "features": feature_names,
        "all_results": tier_results,
    }, best_pipeline


def train_v2():
    log_file = setup_logging()
    logging.info("=" * 60)
    logging.info("TRAINING V2 — Photo + Video + Combined")
    logging.info("=" * 60)

    photo_data = load_photo_features()
    video_data = load_video_features()

    if photo_data is None and video_data is None:
        logging.error("No feature files found. Run pipeline first.")
        sys.exit(1)

    tiers = {}

    # --- Tier A: Photo features ---
    if photo_data is not None:
        photo_df, photo_cols = photo_data
        labels = set(photo_df["label"].unique())
        if labels == {0, 1}:
            X = photo_df[photo_cols].fillna(0).values
            y = photo_df["label"].values
            groups = photo_df["subject_id"].values
            n_pos = sum(y == 1)
            n_neg = sum(y == 0)
            n_splits = min(5, n_pos, n_neg)
            if n_splits >= 2:
                result, pipeline = train_tier("Photo_V2", X, y, groups, photo_cols, n_splits)
                if result:
                    tiers["Photo_V2"] = result
        else:
            logging.warning(f"Photo features: need both classes, got {labels}")

    # --- Tier B: Video features ---
    if video_data is not None:
        video_df, video_cols = video_data
        labels = set(video_df["label"].unique())
        if labels == {0, 1}:
            X = video_df[video_cols].fillna(0).values
            y = video_df["label"].values
            groups = video_df["subject_id"].values
            n_pos = sum(y == 1)
            n_neg = sum(y == 0)
            n_splits = min(5, n_pos, n_neg)
            if n_splits >= 2:
                result, pipeline = train_tier("Video", X, y, groups, video_cols, n_splits)
                if result:
                    tiers["Video"] = result
        else:
            logging.warning(f"Video features: need both classes, got {labels}")

    # --- Tier C: Combined ---
    if photo_data is not None and video_data is not None:
        photo_df, photo_cols = photo_data
        video_df, video_cols = video_data

        # Merge on subject_id
        combined = pd.merge(photo_df, video_df, on="subject_id", suffixes=("", "_vid"))
        # Use label from photo (should match)
        if "label_vid" in combined.columns:
            combined = combined.drop(columns=["label_vid"])

        labels = set(combined["label"].unique())
        if labels == {0, 1}:
            all_cols = photo_cols + video_cols
            available = [c for c in all_cols if c in combined.columns]
            X = combined[available].fillna(0).values
            y = combined["label"].values
            groups = combined["subject_id"].values
            n_pos = sum(y == 1)
            n_neg = sum(y == 0)
            n_splits = min(5, n_pos, n_neg)
            if n_splits >= 2:
                result, pipeline = train_tier("Combined", X, y, groups, available, n_splits)
                if result:
                    tiers["Combined"] = result

    # --- Select overall best ---
    if not tiers:
        logging.error("No tiers could be trained. Need both POSITIVE and NEGATIVE data.")
        sys.exit(1)

    best_tier_name = max(tiers, key=lambda k: tiers[k]["best_auc"])
    best_tier = tiers[best_tier_name]

    logging.info(f"\n{'='*60}")
    logging.info("FINAL COMPARISON")
    logging.info(f"{'='*60}")
    logging.info(f"{'Tier':<15} {'Classifier':<25} {'AUC':>8}")
    logging.info("-" * 50)
    for name, t in tiers.items():
        marker = " <-- BEST" if name == best_tier_name else ""
        logging.info(f"{name:<15} {t['best_classifier']:<25} {t['best_auc']:>8.4f}{marker}")

    # --- Save models ---
    os.makedirs(MODELS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save each tier
    for name, tier in tiers.items():
        model_path = os.path.join(MODELS_DIR, f"model_{name.lower()}_{ts}.pkl")
        model_data = {
            "model": tier["pipeline"],
            "classifier": tier["best_classifier"],
            "features": tier["features"],
            "tier": name,
            "version": f"v2_{ts}",
            "trained_at": datetime.now().isoformat(),
            "cv_scores": tier["all_results"],
            "best_auc": tier["best_auc"],
            "disclaimer": DISCLAIMER,
        }
        with open(model_path, "wb") as f:
            pickle.dump(model_data, f)
        logging.info(f"Saved: {model_path}")

    # Save combined best as production model
    prod_path = os.path.join(MODELS_DIR, f"model_production_v2.pkl")
    prod_data = {
        "model": best_tier["pipeline"],
        "classifier": best_tier["best_classifier"],
        "features": best_tier["features"],
        "tier": best_tier_name,
        "version": f"v2_prod_{ts}",
        "trained_at": datetime.now().isoformat(),
        "cv_scores": best_tier["all_results"],
        "best_auc": best_tier["best_auc"],
        "disclaimer": DISCLAIMER,
    }
    with open(prod_path, "wb") as f:
        pickle.dump(prod_data, f)

    logging.info(f"\nProduction model: {prod_path}")
    logging.info(f"Best tier: {best_tier_name} (AUC={best_tier['best_auc']:.4f})")
    logging.info(f"Log: {log_file}")

    return prod_path, tiers


if __name__ == "__main__":
    train_v2()
