"""
Inference V2 — Unified Photo + Video Prediction Engine

Handles:
  - Single photo → 32 features → prediction
  - Single video → 42 temporal features → prediction
  - Subject folder (photos + videos) → combined features → best prediction

Automatically selects the best available model tier:
  Combined > Video > Photo (by training AUC)

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

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."
IMAGE_EXT = {".jpg", ".jpeg", ".png"}
VIDEO_EXT = {".mp4", ".mov", ".avi"}


class InferenceEngineV2:
    """
    Unified inference engine for photo and video analysis.

    Loads available model tiers and selects the best one for each input type.
    """

    def __init__(self):
        self.models = {}  # tier_name → {model, features, metadata}
        self._is_loaded = False

    def load_models(self, models_dir=None):
        """Load all available model tiers."""
        if models_dir is None:
            models_dir = MODELS_DIR

        if not os.path.isdir(models_dir):
            raise NotImplementedError("No models directory found")

        pkl_files = [f for f in os.listdir(models_dir) if f.endswith(".pkl")]
        if not pkl_files:
            raise NotImplementedError("No trained models found")

        for fname in pkl_files:
            path = os.path.join(models_dir, fname)
            try:
                with open(path, "rb") as f:
                    data = pickle.load(f)
                tier = data.get("tier", "unknown")
                self.models[tier] = {
                    "model": data["model"],
                    "features": data["features"],
                    "classifier": data.get("classifier"),
                    "version": data.get("version"),
                    "auc": data.get("best_auc", 0),
                    "path": path,
                }
                logging.info(f"Loaded model: {tier} ({data.get('classifier')}, AUC={data.get('best_auc', '?')})")
            except Exception as e:
                logging.warning(f"Failed to load {fname}: {e}")

        self._is_loaded = len(self.models) > 0
        if self._is_loaded:
            logging.info(f"Models loaded: {list(self.models.keys())}")

    def predict_photo(self, image_path):
        """Predict from a single photo."""
        timestamp = datetime.now().isoformat()

        # Validate
        validation = validate_image(image_path)
        if not validation["is_valid"]:
            return self._error_response("Image failed validation", validation, timestamp)

        # Extract features
        features = extract_features_v2(image_path)
        if features is None:
            return self._error_response("Feature extraction failed", validation, timestamp)

        # Find best photo-capable model
        model_info = self._get_model_for("photo")
        if model_info is None:
            return {
                "probability": None,
                "input_type": "photo",
                "features": features,
                "validation": validation,
                "model_version": None,
                "timestamp": timestamp,
                "disclaimer": DISCLAIMER,
                "error": "No trained model available",
            }

        # Predict
        proba = self._predict(model_info, features)

        return {
            "probability": round(float(proba), 4),
            "input_type": "photo",
            "model_tier": model_info["tier"],
            "features": features,
            "validation": validation,
            "model_version": model_info.get("version"),
            "timestamp": timestamp,
            "disclaimer": DISCLAIMER,
        }

    def predict_video(self, video_path):
        """Predict from a single video — analyzes temporal behavior."""
        timestamp = datetime.now().isoformat()

        # Extract temporal features
        features = extract_video_features(video_path)
        if features is None:
            return {
                "probability": None,
                "input_type": "video",
                "features": None,
                "timestamp": timestamp,
                "disclaimer": DISCLAIMER,
                "error": "Video feature extraction failed",
            }

        # Find best video-capable model
        model_info = self._get_model_for("video")
        if model_info is None:
            return {
                "probability": None,
                "input_type": "video",
                "features": features,
                "model_version": None,
                "timestamp": timestamp,
                "disclaimer": DISCLAIMER,
                "error": "No video-trained model available",
            }

        proba = self._predict(model_info, features)

        return {
            "probability": round(float(proba), 4),
            "input_type": "video",
            "model_tier": model_info["tier"],
            "features": features,
            "model_version": model_info.get("version"),
            "timestamp": timestamp,
            "disclaimer": DISCLAIMER,
        }

    def predict_subject(self, folder_path):
        """
        Predict from a subject folder containing photos and/or videos.
        Uses the best available evidence.
        """
        timestamp = datetime.now().isoformat()

        if not os.path.isdir(folder_path):
            return self._error_response(f"Not a directory: {folder_path}", {}, timestamp)

        files = sorted(os.listdir(folder_path))
        photo_results = []
        video_results = []

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            fpath = os.path.join(folder_path, fname)

            if ext in IMAGE_EXT:
                result = self.predict_photo(fpath)
                photo_results.append({"filename": fname, **result})

            elif ext in VIDEO_EXT:
                result = self.predict_video(fpath)
                video_results.append({"filename": fname, **result})

        # Aggregate predictions
        all_probas = []
        for r in photo_results + video_results:
            if r.get("probability") is not None:
                all_probas.append(r["probability"])

        # Video predictions get higher weight (more information)
        video_probas = [r["probability"] for r in video_results if r.get("probability") is not None]
        photo_probas = [r["probability"] for r in photo_results if r.get("probability") is not None]

        if video_probas and photo_probas:
            # Weighted average: video gets 60%, photos 40%
            video_mean = np.mean(video_probas)
            photo_mean = np.mean(photo_probas)
            final_proba = 0.6 * video_mean + 0.4 * photo_mean
        elif video_probas:
            final_proba = np.mean(video_probas)
        elif photo_probas:
            final_proba = np.mean(photo_probas)
        else:
            final_proba = None

        return {
            "probability": round(float(final_proba), 4) if final_proba is not None else None,
            "input_type": "subject_folder",
            "n_photos": len(photo_results),
            "n_videos": len(video_results),
            "photo_results": photo_results,
            "video_results": video_results,
            "timestamp": timestamp,
            "disclaimer": DISCLAIMER,
        }

    def _get_model_for(self, input_type):
        """Find the best model for the given input type."""
        if not self._is_loaded:
            return None

        if input_type == "photo":
            # Prefer Combined > Photo_V2 > any with photo features
            for tier in ["Combined", "Photo_V2"]:
                if tier in self.models:
                    return {"tier": tier, **self.models[tier]}

        elif input_type == "video":
            for tier in ["Combined", "Video"]:
                if tier in self.models:
                    return {"tier": tier, **self.models[tier]}

        # Fallback: any model
        if self.models:
            best_tier = max(self.models, key=lambda k: self.models[k].get("auc", 0))
            return {"tier": best_tier, **self.models[best_tier]}

        return None

    def _predict(self, model_info, features):
        """Run prediction with a specific model."""
        feature_order = model_info["features"]
        available = {k: features.get(k, 0) for k in feature_order}
        X = pd.DataFrame([available])[feature_order]
        proba = model_info["model"].predict_proba(X)[0]
        return proba[1]  # P(pregnant)

    def _error_response(self, error, validation, timestamp):
        return {
            "probability": None,
            "features": None,
            "validation": validation,
            "timestamp": timestamp,
            "disclaimer": DISCLAIMER,
            "error": error,
        }

    @property
    def is_loaded(self):
        return self._is_loaded

    @property
    def available_tiers(self):
        return list(self.models.keys())
