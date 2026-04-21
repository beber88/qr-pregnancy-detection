"""
Inference Engine — PregnancyInferenceEngine
Full plumbing for single-image and subject-folder prediction.
Model slot is empty until training completes.

CRITICAL: Feature extraction uses the SAME code path as training
(phase1_extract.extract_features + phase1_extract.detect_cup_roi).

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import pickle
import logging
from datetime import datetime

import numpy as np
import pandas as pd

# Shared feature extraction — identical code path for training and inference
from phase1_extract import extract_features, FEATURE_NAMES
from validate_image import validate_image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
DISCLAIMER = "Research use only. Experimental probability model. Not a diagnostic test."

IMAGE_EXT = {".jpg", ".jpeg", ".png"}


class PregnancyInferenceEngine:
    """
    Inference engine for pregnancy detection from urine sample images.

    Usage:
        engine = PregnancyInferenceEngine()
        engine.load_model("models/model_B_v1.pkl")
        result = engine.predict_from_image("path/to/image.jpg")
    """

    def __init__(self):
        self.model = None
        self.model_metadata = None
        self.model_path = None
        self._is_loaded = False

    def load_model(self, model_path=None):
        """
        Load a trained model from disk.
        Raises NotImplementedError if no model has been trained yet.

        Args:
            model_path: Path to .pkl model file. If None, looks for the
                        latest model in models/ directory.
        """
        if model_path is None:
            model_path = self._find_latest_model()

        if model_path is None or not os.path.exists(model_path):
            raise NotImplementedError(
                "Model not yet trained — awaiting NEGATIVE data. "
                "Run sanity_check.py first, then train.py once NEGATIVE "
                "samples are available in PICTURES/NEGATIVE/."
            )

        with open(model_path, "rb") as f:
            data = pickle.load(f)

        self.model = data["model"]
        self.model_metadata = {
            "classifier": data.get("classifier"),
            "features": data.get("features", FEATURE_NAMES),
            "version": data.get("version"),
            "trained_at": data.get("trained_at"),
            "n_subjects": data.get("n_subjects"),
            "cv_scores": data.get("cv_scores"),
        }
        self.model_path = model_path
        self._is_loaded = True
        logging.info(f"Model loaded: {model_path}")

    def predict_from_image(self, image_path):
        """
        Run prediction on a single image.

        Args:
            image_path: Path to a urine sample image.

        Returns:
            dict with keys:
                probability (float): 0.0-1.0 pregnancy probability
                features (dict): Extracted feature values
                validation (dict): Image validation results
                model_version (str): Which model was used
                timestamp (str): When prediction was made
                disclaimer (str): Legal disclaimer
        """
        timestamp = datetime.now().isoformat()

        # Step 1: Validate image
        validation = validate_image(image_path)
        if not validation["is_valid"]:
            return {
                "probability": None,
                "features": None,
                "validation": validation,
                "model_version": self._get_model_version(),
                "timestamp": timestamp,
                "disclaimer": DISCLAIMER,
                "error": "Image failed validation",
            }

        # Step 2: Extract features (same code path as training)
        features = extract_features(image_path)
        if features is None:
            return {
                "probability": None,
                "features": None,
                "validation": validation,
                "model_version": self._get_model_version(),
                "timestamp": timestamp,
                "disclaimer": DISCLAIMER,
                "error": "Feature extraction failed",
            }

        # Step 3: Check model is loaded
        if not self._is_loaded:
            return {
                "probability": None,
                "features": features,
                "validation": validation,
                "model_version": None,
                "timestamp": timestamp,
                "disclaimer": DISCLAIMER,
                "error": "Model not yet trained — awaiting NEGATIVE data",
            }

        # Step 4: Predict
        feature_order = self.model_metadata.get("features", FEATURE_NAMES)
        X = pd.DataFrame([features])[feature_order]
        proba = self.model.predict_proba(X)[0]

        # proba[1] = probability of class 1 (pregnant)
        pregnancy_probability = float(proba[1])

        return {
            "probability": round(pregnancy_probability, 4),
            "features": features,
            "validation": validation,
            "model_version": self._get_model_version(),
            "timestamp": timestamp,
            "disclaimer": DISCLAIMER,
        }

    def predict_from_subject_folder(self, folder_path):
        """
        Run prediction on all images in a subject folder.
        Aggregates predictions across multiple angles/frames.

        Args:
            folder_path: Path to a folder containing images from one subject.

        Returns:
            dict with keys:
                probability (float): Aggregated probability (mean of valid images)
                per_image (list[dict]): Individual prediction results
                n_valid (int): Number of images that passed validation
                n_total (int): Total images found
                timestamp (str): When prediction was made
                disclaimer (str): Legal disclaimer
        """
        timestamp = datetime.now().isoformat()

        if not os.path.isdir(folder_path):
            return {
                "probability": None,
                "per_image": [],
                "n_valid": 0,
                "n_total": 0,
                "timestamp": timestamp,
                "disclaimer": DISCLAIMER,
                "error": f"Not a directory: {folder_path}",
            }

        # Collect all images in folder
        image_files = sorted([
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.splitext(f)[1].lower() in IMAGE_EXT
        ])

        per_image = []
        probabilities = []

        for img_path in image_files:
            result = self.predict_from_image(img_path)
            per_image.append({
                "filename": os.path.basename(img_path),
                **result,
            })
            if result.get("probability") is not None:
                probabilities.append(result["probability"])

        # Aggregate: mean probability across valid images
        agg_probability = None
        if probabilities:
            agg_probability = round(float(np.mean(probabilities)), 4)

        return {
            "probability": agg_probability,
            "per_image": per_image,
            "n_valid": len(probabilities),
            "n_total": len(image_files),
            "timestamp": timestamp,
            "disclaimer": DISCLAIMER,
        }

    def _find_latest_model(self):
        """Find the most recently modified .pkl file in models/."""
        if not os.path.isdir(MODELS_DIR):
            return None
        pkl_files = [
            os.path.join(MODELS_DIR, f)
            for f in os.listdir(MODELS_DIR)
            if f.endswith(".pkl")
        ]
        if not pkl_files:
            return None
        return max(pkl_files, key=os.path.getmtime)

    def _get_model_version(self):
        if self.model_metadata:
            return self.model_metadata.get("version")
        return None

    @property
    def is_loaded(self):
        return self._is_loaded
