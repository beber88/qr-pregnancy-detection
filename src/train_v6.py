"""
Training V6 — Production Model (Pure Urine Signal)

Architecture:
  - GradientBoostingClassifier(n_estimators=200, max_depth=2, learning_rate=0.05)
  - SelectKBest(mutual_info_classif, k=90)
  - GroupKFold(n_splits=5) by subject_id
  - Rich per-subject aggregation: mean/std/min/max/range/CV + interaction features
  - NO survey features (format-artifact leakage — see HANDOFF_SESSION_20260504.md)
  - N57 excluded (ambiguous label)

Validated metrics (101 subjects, N57 excluded):
  - V6 Production: AUC=0.749, Sensitivity=0.602, Specificity=0.734
  - V6 Fusion: AUC=0.770 (68 subjects with video, 0.7*photo + 0.3*video)

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import json
import pickle
import logging
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.metrics import roc_auc_score, recall_score, confusion_matrix

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_V2_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features_v2.csv")
VIDEO_FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "video_features.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."

# ── Production hyperparameters (do not change without nested CV justification) ──
N_ESTIMATORS = 200
MAX_DEPTH = 2
LEARNING_RATE = 0.05
K_BEST = 90
N_SPLITS = 5
RANDOM_STATE = 42

# Subjects to exclude
EXCLUDED_SUBJECTS = ["NEGATIVE_57"]  # Ambiguous label — see HANDOFF_SESSION_20260504.md

# ── Photo features to aggregate per subject ───────────────────────────────
PHOTO_FEATURES = [
    "r_mean", "g_mean", "b_mean", "brightness", "turbidity",
    "dominant_hue", "hue_spread", "texture_score", "edge_intensity",
    "bubble_count", "contrast", "saturation", "color_variance",
    "yellowness", "gy_ratio",
    "layla_r_ratio", "layla_rg_ratio", "layla_rb_ratio",
    "layla_r_ratio_std", "layla_r_skew", "layla_r_dominant",
    "lab_L", "lab_a", "lab_b", "lab_chroma",
    "conc_proxy_sv", "conc_proxy_yellow_sat", "conc_darkness",
]

# ── Video features (already per-subject) ──────────────────────────────────
VIDEO_FEATURES = [
    "t_r_ratio_mean", "t_r_ratio_std", "t_r_ratio_trend",
    "t_rg_ratio_mean", "t_rg_ratio_std", "t_rg_ratio_trend",
    "t_rb_ratio_mean", "t_rb_ratio_std", "t_rb_ratio_trend",
    "t_hue_mean", "t_hue_std", "t_hue_trend",
    "t_saturation_mean", "t_saturation_std", "t_saturation_trend",
    "t_value_mean", "t_value_std", "t_value_trend",
    "t_turb_mean", "t_turb_std", "t_turb_trend", "t_turb_settling",
    "t_flow_mean", "t_flow_std", "t_flow_trend", "t_flow_decay",
    "t_flow_coherence_mean", "t_flow_peak", "t_flow_peak_time",
    "t_texture_mean", "t_texture_std", "t_texture_trend",
    "t_layla_r_stability", "t_layla_r_autocorr",
    "t_activity_mean", "t_activity_trend", "t_time_to_calm",
    "t_overall_dynamism", "t_r_ratio_complexity",
]


def setup_logging():
    """Configure file + console logging, return log file path."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"train_v6_{ts}.log")

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

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
    """Compute specificity = TN / (TN + FP)."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return tn / (tn + fp) if (tn + fp) > 0 else 0.0


def mi_scorer(X, y):
    """Mutual information feature scoring (module-level function for pickling)."""
    return mutual_info_classif(X, y, random_state=RANDOM_STATE, n_neighbors=5)


# ── Feature engineering ───────────────────────────────────────────────────

def rich_aggregate(df, feature_cols):
    """
    Aggregate photo features per subject: mean/std/min/max/range/CV.
    Captures within-subject variability — the strongest genuine signal found in V4-V6.
    """
    agg_dict = {}
    for col in feature_cols:
        if col not in df.columns:
            continue
        agg_dict[col] = ["mean", "std", "min", "max"]

    agg_dict["label"] = "first"
    agg_dict["subject_id"] = "first"

    subject_df = df.groupby("subject_id").agg(agg_dict)

    # Flatten multi-level columns
    new_cols = []
    for col in subject_df.columns:
        if isinstance(col, tuple):
            if col[1] == "first":
                new_cols.append(col[0])
            else:
                new_cols.append(f"{col[0]}_{col[1]}")
        else:
            new_cols.append(col)

    subject_df.columns = new_cols
    subject_df = subject_df.reset_index(drop=True)

    # Derived: CV (coefficient of variation) and range
    for col in feature_cols:
        if col not in df.columns:
            continue
        mean_col = f"{col}_mean"
        std_col = f"{col}_std"
        min_col = f"{col}_min"
        max_col = f"{col}_max"

        if mean_col in subject_df.columns and std_col in subject_df.columns:
            subject_df[f"{col}_cv"] = np.where(
                subject_df[mean_col].abs() > 1e-8,
                subject_df[std_col] / subject_df[mean_col].abs(),
                0,
            )
        if min_col in subject_df.columns and max_col in subject_df.columns:
            subject_df[f"{col}_range"] = subject_df[max_col] - subject_df[min_col]

    agg_feature_cols = [c for c in subject_df.columns if c not in ("label", "subject_id")]
    return subject_df, agg_feature_cols


def add_interaction_features(df, feature_cols):
    """
    Add pairwise interaction features between top discriminators from V4/V5 analysis.
    """
    interactions = []

    # Product interactions
    pair_candidates = [
        ("g_mean_std", "brightness_std"),
        ("g_mean_std", "lab_L_std"),
        ("gy_ratio_mean", "conc_darkness_std"),
        ("brightness_std", "conc_darkness_std"),
        ("brightness_cv", "saturation_std"),
        ("lab_L_std", "lab_b_std"),
        ("r_mean_std", "b_mean_std"),
        ("yellowness_mean", "conc_darkness_mean"),
        ("saturation_mean", "brightness_mean"),
        ("lab_chroma_mean", "turbidity_mean"),
    ]

    for col_a, col_b in pair_candidates:
        if col_a in df.columns and col_b in df.columns:
            name = f"ix_{col_a}_x_{col_b}"
            df[name] = df[col_a] * df[col_b]
            interactions.append(name)

    # Ratio interactions
    ratio_candidates = [
        ("brightness_std", "brightness_mean", "brightness_ratio_std_mean"),
        ("saturation_std", "saturation_mean", "saturation_ratio_std_mean"),
        ("lab_L_std", "lab_L_mean", "lab_L_ratio_std_mean"),
        ("conc_darkness_std", "conc_darkness_mean", "conc_dark_ratio_std_mean"),
    ]

    for num, denom, name in ratio_candidates:
        if num in df.columns and denom in df.columns:
            df[name] = np.where(
                df[denom].abs() > 1e-8,
                df[num] / df[denom].abs(),
                0,
            )
            interactions.append(name)

    return df, feature_cols + interactions


# ── Data loading ──────────────────────────────────────────────────────────

def load_and_prepare_data(exclude_subjects=None):
    """
    Load photo + video features, aggregate per subject, merge, return arrays.
    Survey features are NOT loaded (format-artifact leakage).
    """
    if exclude_subjects is None:
        exclude_subjects = []

    # Photo features → rich aggregation
    logging.info("Loading photo features...")
    photo_raw = pd.read_csv(FEATURES_V2_CSV)
    if exclude_subjects:
        photo_raw = photo_raw[~photo_raw["subject_id"].isin(exclude_subjects)]

    available_photo = [c for c in PHOTO_FEATURES if c in photo_raw.columns]
    photo_df, photo_agg_cols = rich_aggregate(photo_raw, available_photo)
    logging.info(f"  Photo: {len(photo_df)} subjects, {len(photo_agg_cols)} aggregated features")

    # Interaction features
    photo_df, photo_agg_cols = add_interaction_features(photo_df, photo_agg_cols)
    logging.info(f"  After interactions: {len(photo_agg_cols)} features")

    # Video features (already per-subject)
    video_cols = []
    if os.path.exists(VIDEO_FEATURES_CSV):
        logging.info("Loading video features...")
        vf = pd.read_csv(VIDEO_FEATURES_CSV)
        if exclude_subjects:
            vf = vf[~vf["subject_id"].isin(exclude_subjects)]
        video_cols = [c for c in VIDEO_FEATURES if c in vf.columns]
        photo_df = photo_df.merge(vf[["subject_id"] + video_cols], on="subject_id", how="left")
        logging.info(f"  Video: {len(vf)} subjects, {len(video_cols)} features")

    all_feature_cols = list(dict.fromkeys(photo_agg_cols + video_cols))
    photo_df = photo_df.fillna(0)

    n_pos = int((photo_df["label"] == 1).sum())
    n_neg = int((photo_df["label"] == 0).sum())
    logging.info(f"Merged: {len(photo_df)} subjects ({n_pos}P + {n_neg}N), {len(all_feature_cols)} features")

    X = photo_df[all_feature_cols].values.astype(np.float64)
    y = photo_df["label"].values.astype(int)
    groups = photo_df["subject_id"].values

    return X, y, groups, all_feature_cols, photo_df


# ── Cross-validation ──────────────────────────────────────────────────────

def make_production_pipeline(k_best=None, n_features=None):
    """Build the production pipeline: Scaler → SelectKBest(MI) → GBM."""
    k = min(k_best or K_BEST, n_features or K_BEST)
    return Pipeline([
        ("scaler", StandardScaler()),
        ("select", SelectKBest(mi_scorer, k=k)),
        ("clf", GradientBoostingClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            learning_rate=LEARNING_RATE,
            random_state=RANDOM_STATE,
        )),
    ])


def run_cv(X, y, groups, feature_names):
    """
    Run 5-fold GroupKFold cross-validation. Returns aggregate metrics and
    per-fold detail records for saving.
    """
    n_splits = min(N_SPLITS, int(sum(y == 1)), int(sum(y == 0)))
    gkf = GroupKFold(n_splits=n_splits)

    fold_records = []
    all_y_true = []
    all_y_proba = []

    for fold_idx, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        groups_test = groups[test_idx]

        if len(set(y_train)) < 2 or len(set(y_test)) < 2:
            logging.warning(f"  Fold {fold_idx}: skipped (single class in train or test)")
            continue

        pipeline = make_production_pipeline(n_features=X.shape[1])
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        try:
            auc = roc_auc_score(y_test, y_proba)
        except ValueError:
            auc = float("nan")

        sens = recall_score(y_test, y_pred, zero_division=0)
        spec = specificity(y_test, y_pred)
        n_test_pos = int(sum(y_test == 1))
        n_test_neg = int(sum(y_test == 0))

        fold_records.append({
            "fold": fold_idx,
            "auc": round(auc, 4),
            "sensitivity": round(sens, 4),
            "specificity": round(spec, 4),
            "n_test": len(y_test),
            "n_test_pos": n_test_pos,
            "n_test_neg": n_test_neg,
            "test_subjects": ",".join(sorted(set(groups_test))),
        })

        all_y_true.extend(y_test.tolist())
        all_y_proba.extend(y_proba.tolist())

        logging.info(
            f"  Fold {fold_idx}: AUC={auc:.4f}  sens={sens:.3f}  spec={spec:.3f}  "
            f"(n={len(y_test)}: {n_test_pos}P+{n_test_neg}N)"
        )

    if not fold_records:
        logging.error("All folds skipped — cannot evaluate.")
        return None, None

    aucs = [r["auc"] for r in fold_records]
    mean_auc = np.nanmean(aucs)
    std_auc = np.nanstd(aucs)
    mean_sens = np.mean([r["sensitivity"] for r in fold_records])
    mean_spec = np.mean([r["specificity"] for r in fold_records])

    summary = {
        "mean_auc": round(float(mean_auc), 4),
        "std_auc": round(float(std_auc), 4),
        "mean_sensitivity": round(float(mean_sens), 4),
        "mean_specificity": round(float(mean_spec), 4),
        "per_fold_auc": aucs,
        "n_folds": len(fold_records),
    }

    return summary, fold_records


# ── Feature importance ────────────────────────────────────────────────────

def log_feature_importance(pipeline, feature_names, top_n=20):
    """Log top features from the trained production pipeline."""
    selector = pipeline.named_steps.get("select")
    clf = pipeline.named_steps.get("clf")

    if not (selector and hasattr(selector, "get_support") and hasattr(clf, "feature_importances_")):
        return []

    selected_mask = selector.get_support()
    selected_features = [f for f, s in zip(feature_names, selected_mask) if s]
    importances = clf.feature_importances_
    top_idx = np.argsort(importances)[::-1][:top_n]

    logging.info(f"\nTOP {top_n} FEATURES:")
    records = []
    for rank, idx in enumerate(top_idx):
        fname = selected_features[idx]
        imp = float(importances[idx])
        logging.info(f"  {rank+1:2d}. {fname:<45} {imp:.4f}")
        records.append({"rank": rank + 1, "feature": fname, "importance": round(imp, 4)})

    return records


# ── Main training ─────────────────────────────────────────────────────────

def train_v6():
    log_file = setup_logging()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    logging.info("=" * 60)
    logging.info("V6 PRODUCTION TRAINING")
    logging.info(f"  Pipeline: StandardScaler → SelectKBest(MI, k={K_BEST}) → GBM({N_ESTIMATORS}, depth={MAX_DEPTH}, lr={LEARNING_RATE})")
    logging.info(f"  CV: {N_SPLITS}-fold GroupKFold by subject_id")
    logging.info(f"  Excluded: {EXCLUDED_SUBJECTS}")
    logging.info(f"  Survey features: EXCLUDED (format-artifact leakage)")
    logging.info(f"  Timestamp: {ts}")
    logging.info("=" * 60)

    # Load data
    X, y, groups, feature_names, merged_df = load_and_prepare_data(
        exclude_subjects=EXCLUDED_SUBJECTS,
    )

    n_pos = int(sum(y == 1))
    n_neg = int(sum(y == 0))

    # Cross-validation
    logging.info(f"\nRunning {N_SPLITS}-fold GroupKFold CV...")
    summary, fold_records = run_cv(X, y, groups, feature_names)

    if summary is None:
        logging.error("Training failed — no valid folds.")
        return None, None

    logging.info(f"\n{'='*60}")
    logging.info(f"CV RESULTS:")
    logging.info(f"  AUC:         {summary['mean_auc']:.4f} ± {summary['std_auc']:.4f}")
    logging.info(f"  Sensitivity: {summary['mean_sensitivity']:.4f}")
    logging.info(f"  Specificity: {summary['mean_specificity']:.4f}")
    logging.info(f"  Per-fold AUC: {summary['per_fold_auc']}")
    logging.info(f"{'='*60}")

    # Save fold-level results to CSV
    os.makedirs(RESULTS_DIR, exist_ok=True)
    fold_csv_path = os.path.join(RESULTS_DIR, f"v6_fold_results_{ts}.csv")
    pd.DataFrame(fold_records).to_csv(fold_csv_path, index=False)
    logging.info(f"Fold results saved: {fold_csv_path}")

    # Retrain on ALL data for production model
    logging.info("\nRetraining on all data for production model...")
    final_pipeline = make_production_pipeline(n_features=X.shape[1])
    final_pipeline.fit(X, y)

    # Feature importance
    importance_records = log_feature_importance(final_pipeline, feature_names)

    # Save production model
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "model_production_v6.pkl")

    model_data = {
        "model": final_pipeline,
        "version": "v6",
        "classifier": f"GBM(n={N_ESTIMATORS}, depth={MAX_DEPTH}, lr={LEARNING_RATE})",
        "feature_selection": f"SelectKBest(MI, k={min(K_BEST, X.shape[1])})",
        "features": feature_names,
        "photo_features": list(PHOTO_FEATURES),
        "video_features": list(VIDEO_FEATURES),
        "aggregation": "mean/std/min/max/cv/range per subject + interaction features",
        "trained_at": datetime.now().isoformat(),
        "n_subjects": len(merged_df),
        "n_positive": n_pos,
        "n_negative": n_neg,
        "excluded_subjects": EXCLUDED_SUBJECTS,
        "cv_auc": summary["mean_auc"],
        "cv_auc_std": summary["std_auc"],
        "cv_sensitivity": summary["mean_sensitivity"],
        "cv_specificity": summary["mean_specificity"],
        "per_fold_auc": summary["per_fold_auc"],
        "top_features": importance_records,
        "disclaimer": DISCLAIMER,
    }

    with open(model_path, "wb") as f:
        pickle.dump(model_data, f)
    logging.info(f"\nProduction model saved: {model_path}")

    # Timestamped backup
    ts_path = os.path.join(MODELS_DIR, f"model_v6_{ts}.pkl")
    with open(ts_path, "wb") as f:
        pickle.dump(model_data, f)
    logging.info(f"Backup saved: {ts_path}")

    # Save summary JSON (machine-readable)
    summary_json = {
        "version": "v6",
        "timestamp": ts,
        "n_subjects": len(merged_df),
        "n_positive": n_pos,
        "n_negative": n_neg,
        "n_features": len(feature_names),
        "excluded_subjects": EXCLUDED_SUBJECTS,
        "hyperparameters": {
            "n_estimators": N_ESTIMATORS,
            "max_depth": MAX_DEPTH,
            "learning_rate": LEARNING_RATE,
            "k_best": min(K_BEST, X.shape[1]),
            "n_splits": summary["n_folds"],
        },
        "cv_results": summary,
        "fold_results": fold_records,
        "top_features": importance_records,
        "model_path": model_path,
        "disclaimer": DISCLAIMER,
    }
    json_path = os.path.join(RESULTS_DIR, f"v6_summary_{ts}.json")
    with open(json_path, "w") as f:
        json.dump(summary_json, f, indent=2)
    logging.info(f"Summary JSON saved: {json_path}")

    # Final comparison
    logging.info(f"\n{'='*60}")
    logging.info(f"V4 baseline (urine only, mean agg): AUC=0.739")
    logging.info(f"V6 production (rich agg + interactions): AUC={summary['mean_auc']:.4f}")
    delta = summary["mean_auc"] - 0.739
    logging.info(f"Delta from V4: {delta:+.4f}")
    logging.info(f"{'='*60}")
    logging.info(f"Log: {log_file}")
    logging.info(DISCLAIMER)

    return model_path, summary


if __name__ == "__main__":
    train_v6()
