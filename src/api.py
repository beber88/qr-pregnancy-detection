"""
FastAPI Web Server — Pregnancy Detection AI
Endpoints:
  POST /predict         — Upload single image, validate, return result
  POST /predict_subject — Upload multiple files for one subject (3 photos + optional video)
  GET  /health          — System status and model info
  GET  /stats           — Dataset statistics

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import json
import uuid
import shutil
import tempfile
import logging
from datetime import datetime
from typing import List

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd

from inference import PregnancyInferenceEngine, DISCLAIMER
from validate_image import validate_image
from phase1_extract import extract_features

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
REGISTRY_PATH = os.path.join(MODELS_DIR, "registry.json")
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")


def get_production_model_path():
    """Read registry.json and return the path to the production hand_coded model."""
    if not os.path.exists(REGISTRY_PATH):
        return None
    try:
        with open(REGISTRY_PATH, "r") as f:
            registry = json.load(f)
        prod_filename = registry.get("production", {}).get("hand_coded")
        if prod_filename:
            path = os.path.join(MODELS_DIR, prod_filename)
            if os.path.exists(path):
                return path
    except (json.JSONDecodeError, KeyError):
        pass
    return None


# Initialize engine — load the production model from registry.json
engine = PregnancyInferenceEngine()

try:
    prod_path = get_production_model_path()
    if prod_path:
        engine.load_model(prod_path)
    else:
        engine.load_model()  # Falls back to latest .pkl
except (NotImplementedError, Exception):
    pass  # Expected — model not yet trained

app = FastAPI(
    title="Pregnancy Detection AI",
    description=DISCLAIMER,
    version="0.1.0",
)

# Serve static UI files
if os.path.isdir(UI_DIR):
    app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")


@app.get("/")
async def root():
    """Redirect to UI."""
    return FileResponse(os.path.join(UI_DIR, "index.html"))


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Upload an image for analysis.
    Returns validation results and probability (if model is available).
    """
    request_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    # Read uploaded file
    contents = await file.read()
    if len(contents) == 0:
        return JSONResponse(status_code=400, content={
            "request_id": request_id,
            "timestamp": timestamp,
            "error": "Empty file uploaded",
            "disclaimer": DISCLAIMER,
        })

    # Save to temp file for processing
    suffix = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Validate
        validation = validate_image(tmp_path)

        if not validation["is_valid"]:
            return JSONResponse(status_code=422, content={
                "request_id": request_id,
                "timestamp": timestamp,
                "status": "validation_failed",
                "validation": validation,
                "probability": None,
                "disclaimer": DISCLAIMER,
            })

        # Predict
        if engine.is_loaded:
            result = engine.predict_from_image(tmp_path)
            return {
                "request_id": request_id,
                "timestamp": timestamp,
                "status": "success",
                "probability": result["probability"],
                "features": result["features"],
                "validation": result["validation"],
                "model_version": result["model_version"],
                "disclaimer": DISCLAIMER,
            }
        else:
            # Model not available — extract features but no prediction
            features = extract_features(tmp_path)

            return {
                "request_id": request_id,
                "timestamp": timestamp,
                "status": "model_not_available",
                "probability": None,
                "message": "Model not yet trained — awaiting NEGATIVE data. "
                           "Image passed validation and features were extracted successfully.",
                "features": features,
                "validation": validation,
                "model_version": None,
                "disclaimer": DISCLAIMER,
            }
    finally:
        os.unlink(tmp_path)


@app.post("/predict_subject")
async def predict_subject(files: List[UploadFile] = File(...)):
    """
    Upload multiple files for one subject (3 photos + optional video).
    Returns aggregated probability plus per-image details.
    """
    request_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    if not files:
        return JSONResponse(status_code=400, content={
            "request_id": request_id,
            "timestamp": timestamp,
            "error": "No files uploaded",
            "disclaimer": DISCLAIMER,
        })

    # Save all files to a temp directory
    tmp_dir = tempfile.mkdtemp(prefix="subject_")

    try:
        image_paths = []
        skipped = []

        for f in files:
            contents = await f.read()
            if len(contents) == 0:
                skipped.append({"filename": f.filename, "reason": "Empty file"})
                continue

            ext = os.path.splitext(f.filename or "file")[1].lower()

            # Skip video files — in production these would be frame-extracted,
            # but for the API we accept only image uploads
            if ext in {".mp4", ".mov", ".avi"}:
                skipped.append({"filename": f.filename, "reason": "Video files not supported via API upload. Submit extracted frames as images."})
                continue

            if ext not in {".jpg", ".jpeg", ".png"}:
                skipped.append({"filename": f.filename, "reason": f"Unsupported format: {ext}"})
                continue

            # Write to temp dir
            safe_name = f.filename or f"image_{len(image_paths)}{ext}"
            tmp_path = os.path.join(tmp_dir, safe_name)
            with open(tmp_path, "wb") as out:
                out.write(contents)
            image_paths.append(tmp_path)

        if not image_paths:
            return JSONResponse(status_code=422, content={
                "request_id": request_id,
                "timestamp": timestamp,
                "status": "no_valid_images",
                "error": "No valid image files found in upload",
                "skipped": skipped,
                "disclaimer": DISCLAIMER,
            })

        # Process each image: validate + extract features + predict
        per_image = []
        probabilities = []
        all_features = []
        n_valid = 0

        for img_path in image_paths:
            fname = os.path.basename(img_path)
            validation = validate_image(img_path)

            if not validation["is_valid"]:
                per_image.append({
                    "filename": fname,
                    "status": "validation_failed",
                    "validation": validation,
                    "probability": None,
                    "features": None,
                })
                continue

            features = extract_features(img_path)
            if features is None:
                per_image.append({
                    "filename": fname,
                    "status": "extraction_failed",
                    "validation": validation,
                    "probability": None,
                    "features": None,
                })
                continue

            n_valid += 1
            all_features.append(features)

            if engine.is_loaded:
                result = engine.predict_from_image(img_path)
                prob = result.get("probability")
                per_image.append({
                    "filename": fname,
                    "status": "success",
                    "validation": validation,
                    "probability": prob,
                    "features": features,
                })
                if prob is not None:
                    probabilities.append(prob)
            else:
                per_image.append({
                    "filename": fname,
                    "status": "model_not_available",
                    "validation": validation,
                    "probability": None,
                    "features": features,
                })

        # Aggregate probability across valid images
        agg_probability = None
        if probabilities:
            agg_probability = round(float(sum(probabilities) / len(probabilities)), 4)

        status = "success" if engine.is_loaded and probabilities else "model_not_available"
        message = None
        if not engine.is_loaded:
            message = (
                "Model not yet trained — awaiting NEGATIVE data. "
                f"{n_valid} image(s) passed validation and features were extracted."
            )

        return {
            "request_id": request_id,
            "timestamp": timestamp,
            "status": status,
            "probability": agg_probability,
            "message": message,
            "n_files_received": len(files),
            "n_valid_images": n_valid,
            "n_skipped": len(skipped),
            "skipped": skipped if skipped else None,
            "per_image": per_image,
            "model_version": engine.model_metadata.get("version") if engine.model_metadata else None,
            "disclaimer": DISCLAIMER,
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.get("/health")
async def health():
    """System health check."""
    model_info = None
    if engine.is_loaded and engine.model_metadata:
        model_info = {
            "classifier": engine.model_metadata.get("classifier"),
            "version": engine.model_metadata.get("version"),
            "trained_at": engine.model_metadata.get("trained_at"),
            "n_subjects": engine.model_metadata.get("n_subjects"),
        }

    # Count subjects in training data
    n_subjects = 0
    if os.path.exists(FEATURES_CSV):
        try:
            df = pd.read_csv(FEATURES_CSV)
            n_subjects = df["subject_id"].nunique()
        except Exception:
            pass

    # Production model from registry
    production_model = None
    try:
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, "r") as f:
                registry = json.load(f)
            production_model = registry.get("production", {}).get("hand_coded")
    except Exception:
        pass

    return {
        "status": "healthy",
        "model_loaded": engine.is_loaded,
        "model_info": model_info,
        "production_model": production_model,
        "n_subjects_in_data": n_subjects,
        "timestamp": datetime.now().isoformat(),
        "disclaimer": DISCLAIMER,
    }


@app.get("/stats")
async def stats():
    """Dataset statistics."""
    result = {
        "n_positive": 0,
        "n_negative": 0,
        "n_features": 0,
        "n_total_images": 0,
        "last_trained": None,
        "disclaimer": DISCLAIMER,
    }

    if os.path.exists(FEATURES_CSV):
        try:
            df = pd.read_csv(FEATURES_CSV)
            result["n_positive"] = int(df[df["label"] == 1]["subject_id"].nunique())
            result["n_negative"] = int(df[df["label"] == 0]["subject_id"].nunique())
            result["n_total_images"] = len(df)

            feature_cols = [c for c in df.columns if c not in
                          ("filepath", "subject_id", "label", "media_type", "frame_number")]
            result["n_features"] = len(feature_cols)
        except Exception:
            pass

    # Model registry info
    try:
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, "r") as f:
                registry = json.load(f)
            result["n_models_trained"] = len(registry.get("models", []))
            result["production_model"] = registry.get("production", {}).get("hand_coded")
            if registry.get("models"):
                latest = max(registry["models"], key=lambda e: e.get("trained_at", ""))
                result["last_trained"] = latest.get("trained_at")
                result["latest_auc"] = latest.get("mean_auc")
    except Exception:
        pass

    # Fallback: check model files directly
    if result["last_trained"] is None and os.path.isdir(MODELS_DIR):
        pkl_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".pkl")]
        if pkl_files:
            latest = max(pkl_files, key=lambda f: os.path.getmtime(
                os.path.join(MODELS_DIR, f)))
            mtime = os.path.getmtime(os.path.join(MODELS_DIR, latest))
            result["last_trained"] = datetime.fromtimestamp(mtime).isoformat()

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
