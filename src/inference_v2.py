"""
Inference V2 — V6 Model Prediction Engine

Handles:
  - Subject folder (multiple photos + optional video) → aggregated features → prediction
  - Single photo → single-image aggregation → prediction (less reliable)
  - Single video → video features → prediction (requires fusion model)

V6 models expect subject-level aggregated features (mean/std/min/max/cv/range +
interaction features, ~221 total). Single-image predictions set all variability
features to 0, which reduces accuracy — multiple photos per subject are strongly
recommended.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import pickle
import logging
from datetime import datetime

import numpy as np
import pandas as pd

from features_v2 import extract_features_v2
from video_features import extract_video_features
from validate_image import validate_image
from train_v6 import (
    PHOTO_FEATURES, VIDEO_FEATURES,
    rich_aggregate, add_interaction_features,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."
IMAGE_EXT = {".jpg", ".jpeg", ".png"}
VIDEO_EXT = {".mp4", ".mov", ".avi"}


class InferenceEngineV2:
    """
    Prediction engine for V6 models.

    Loads model_production_v6.pkl (photo+video combined) and optionally
    model_v6_fusion.pkl (late fusion for subjects with video).
    """

    def __init__(self):
        self.production_model = None  # V6 production (all subjects)
        self.fusion_model = None      # V6 fusion (subjects with video only)
        self._is_loaded = False

    def load_models(self, models_dir=None):
        """Load V6 production model and optional fusion model."""
        if models_dir is None:
            models_dir = MODELS_DIR

        if not os.path.isdir(models_dir):
            raise FileNotFoundError(f"Models directory not found: {models_dir}")

        # Load production model
        prod_path = os.path.join(models_dir, "model_production_v6.pkl")
        if os.path.exists(prod_path):
            with open(prod_path, "rb") as f:
                data = pickle.load(f)
            self.production_model = data
            logging.info(
                f"Loaded V6 production: AUC={data.get('cv_auc', '?')}, "
                f"{len(data.get('features', []))} features"
            )

        # Load fusion model (optional)
        fusion_path = os.path.join(models_dir, "model_v6_fusion.pkl")
        if os.path.exists(fusion_path):
            with open(fusion_path, "rb") as f:
                data = pickle.load(f)
            self.fusion_model = data
            logging.info(
                f"Loaded V6 fusion: AUC={data.get('cv_auc', '?')}"
            )

        self._is_loaded = self.production_model is not None
        if not self._is_loaded:
            logging.warning("No V6 production model found.")

    def predict_subject(self, folder_path):
        """
        Predict from a subject folder containing photos and/or videos.
        This is the primary inference path — V6 models are trained on
        subject-level aggregated features.
        """
        timestamp = datetime.now().isoformat()

        if not self._is_loaded:
            return self._error("Models not loaded", timestamp)

        if not os.path.isdir(folder_path):
            return self._error(f"Not a directory: {folder_path}", timestamp)

        files = sorted(os.listdir(folder_path))
        photo_paths = []
        video_paths = []
        validation_issues = []

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            fpath = os.path.join(folder_path, fname)
            if ext in IMAGE_EXT:
                val = validate_image(fpath)
                if val["is_valid"]:
                    photo_paths.append(fpath)
                else:
                    validation_issues.append({"file": fname, "issues": val.get("issues", [])})
            elif ext in VIDEO_EXT:
                video_paths.append(fpath)

        if not photo_paths and not video_paths:
            return self._error("No valid photos or videos found", timestamp)

        # Extract per-image photo features
        photo_feature_rows = []
        for path in photo_paths:
            feats = extract_features_v2(path)
            if feats is not None:
                photo_feature_rows.append(feats)

        # Aggregate to subject level (replicating training pipeline)
        proba = None
        n_photos_used = len(photo_feature_rows)

        if photo_feature_rows:
            subject_features = self._aggregate_photo_features(photo_feature_rows)

            # Add video features if available
            video_feats = None
            if video_paths:
                video_feats = extract_video_features(video_paths[0])

            if video_feats is not None:
                for col in VIDEO_FEATURES:
                    subject_features[col] = video_feats.get(col, 0)

            proba = self._predict_from_features(subject_features)

        result = {
            "probability": round(float(proba), 4) if proba is not None else None,
            "input_type": "subject_folder",
            "n_photos": len(photo_paths),
            "n_photos_used": n_photos_used,
            "n_videos": len(video_paths),
            "model_version": "v6",
            "model_auc": self.production_model.get("cv_auc"),
            "timestamp": timestamp,
            "disclaimer": DISCLAIMER,
        }
        if validation_issues:
            result["validation_issues"] = validation_issues
        if n_photos_used == 1:
            result["warning"] = (
                "Single photo — variability features are zero. "
                "Multiple photos per subject strongly recommended."
            )
        return result

    def predict_photo(self, image_path):
        """
        Predict from a single photo. Less reliable than subject-level prediction
        because all variability features (std/cv/range) will be zero.
        """
        timestamp = datetime.now().isoformat()

        if not self._is_loaded:
            return self._error("Models not loaded", timestamp)

        validation = validate_image(image_path)
        if not validation["is_valid"]:
            return self._error(
                f"Image failed validation: {validation.get('issues', [])}",
                timestamp,
            )

        feats = extract_features_v2(image_path)
        if feats is None:
            return self._error("Feature extraction failed", timestamp)

        subject_features = self._aggregate_photo_features([feats])
        proba = self._predict_from_features(subject_features)

        return {
            "probability": round(float(proba), 4) if proba is not None else None,
            "input_type": "single_photo",
            "model_version": "v6",
            "model_auc": self.production_model.get("cv_auc"),
            "timestamp": timestamp,
            "warning": (
                "Single photo — variability features are zero. "
                "Multiple photos per subject strongly recommended."
            ),
            "disclaimer": DISCLAIMER,
        }

    def predict_video(self, video_path):
        """
        Predict from a single video. Requires the fusion model.
        Falls back to production model with video features only.
        """
        timestamp = datetime.now().isoformat()

        if not self._is_loaded:
            return self._error("Models not loaded", timestamp)

        feats = extract_video_features(video_path)
        if feats is None:
            return self._error("Video feature extraction failed", timestamp)

        return {
            "probability": None,
            "input_type": "video_only",
            "model_version": "v6",
            "timestamp": timestamp,
            "error": (
                "Video-only prediction not supported in V6. "
                "V6 models require photo features as the base. "
                "Use predict_subject() with a folder containing both photos and video."
            ),
            "disclaimer": DISCLAIMER,
        }

    def _aggregate_photo_features(self, feature_rows):
        """
        Replicate the training-time aggregation pipeline:
        raw per-image features → rich_aggregate → interaction features → flat dict.
        """
        rows = []
        for feats in feature_rows:
            row = {"subject_id": "INFERENCE", "label": 0}
            for col in PHOTO_FEATURES:
                row[col] = feats.get(col, 0)
            rows.append(row)

        df = pd.DataFrame(rows)
        available = [c for c in PHOTO_FEATURES if c in df.columns]
        agg_df, agg_cols = rich_aggregate(df, available)
        agg_df, agg_cols = add_interaction_features(agg_df, agg_cols)

        return agg_df.iloc[0].to_dict()

    def _predict_from_features(self, subject_features):
        """Run the V6 pipeline on aggregated subject features."""
        model_info = self.production_model
        feature_order = model_info["features"]
        feature_vec = {k: subject_features.get(k, 0) for k in feature_order}
        X = pd.DataFrame([feature_vec])[feature_order]

        proba = model_info["model"].predict_proba(X)[0]
        return proba[1]  # P(pregnant)

    def _error(self, message, timestamp):
        return {
            "probability": None,
            "timestamp": timestamp,
            "disclaimer": DISCLAIMER,
            "error": message,
        }

    @property
    def is_loaded(self):
        return self._is_loaded

    @property
    def model_info(self):
        if not self._is_loaded:
            return None
        m = self.production_model
        return {
            "version": m.get("version"),
            "cv_auc": m.get("cv_auc"),
            "n_subjects": m.get("n_subjects"),
            "n_features": len(m.get("features", [])),
            "classifier": m.get("classifier"),
        }
