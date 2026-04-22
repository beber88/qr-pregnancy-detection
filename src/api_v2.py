"""
API V2 — Photo + Video Upload + Unified Prediction

Endpoints:
  POST /predict         — Upload photo OR video → auto-detect → prediction
  POST /predict_subject — Upload multiple files (photos + videos) → combined
  GET  /health          — System status, available model tiers
  GET  /stats           — Dataset statistics (photos, videos, subjects)

The API automatically detects whether the upload is a photo or video
and routes to the appropriate analysis pipeline.

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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd

from inference_v2 import InferenceEngineV2, DISCLAIMER

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_V2_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "features_v2.csv")
VIDEO_FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "video_features.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")

IMAGE_EXT = {".jpg", ".jpeg", ".png"}
VIDEO_EXT = {".mp4", ".mov", ".avi"}

# Initialize engine
engine = InferenceEngineV2()
try:
    engine.load_models()
except Exception:
    pass  # Expected — models not yet trained

app = FastAPI(
    title="Pregnancy Detection AI V2",
    description=f"Photo + Video analysis. {DISCLAIMER}",
    version="2.0.0",
)

if os.path.isdir(UI_DIR):
    app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")


@app.get("/")
async def root():
    if os.path.exists(os.path.join(UI_DIR, "index.html")):
        return FileResponse(os.path.join(UI_DIR, "index.html"))
    return {"message": "Pregnancy Detection AI V2", "disclaimer": DISCLAIMER}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Upload a photo OR video for analysis.
    Auto-detects file type and routes to the appropriate pipeline.
    """
    request_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    contents = await file.read()
    if len(contents) == 0:
        return JSONResponse(status_code=400, content={
            "request_id": request_id,
            "error": "Empty file",
            "disclaimer": DISCLAIMER,
        })

    ext = os.path.splitext(file.filename or "file")[1].lower()
    suffix = ext or ".jpg"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        if ext in VIDEO_EXT:
            # Video analysis
            if not engine.is_loaded:
                from video_features import extract_video_features
                features = extract_video_features(tmp_path)
                return {
                    "request_id": request_id,
                    "timestamp": timestamp,
                    "status": "model_not_available",
                    "input_type": "video",
                    "probability": None,
                    "features": features,
                    "message": "Video features extracted. Model not yet trained — awaiting NEGATIVE data.",
                    "disclaimer": DISCLAIMER,
                }

            result = engine.predict_video(tmp_path)
            return {
                "request_id": request_id,
                "timestamp": timestamp,
                "status": "success" if result.get("probability") is not None else "error",
                **result,
            }

        else:
            # Photo analysis
            if not engine.is_loaded:
                from features_v2 import extract_features_v2
                from validate_image import validate_image
                validation = validate_image(tmp_path)
                features = extract_features_v2(tmp_path) if validation["is_valid"] else None
                return {
                    "request_id": request_id,
                    "timestamp": timestamp,
                    "status": "model_not_available" if validation["is_valid"] else "validation_failed",
                    "input_type": "photo",
                    "probability": None,
                    "features": features,
                    "validation": validation,
                    "message": "Features extracted. Model not yet trained — awaiting NEGATIVE data." if validation["is_valid"] else None,
                    "disclaimer": DISCLAIMER,
                }

            result = engine.predict_photo(tmp_path)
            status = "success" if result.get("probability") is not None else "validation_failed"
            return {
                "request_id": request_id,
                "timestamp": timestamp,
                "status": status,
                **result,
            }

    finally:
        os.unlink(tmp_path)


@app.post("/predict_subject")
async def predict_subject(files: List[UploadFile] = File(...)):
    """
    Upload multiple files (photos + videos) for one subject.
    Returns combined prediction using all available evidence.
    Videos are weighted higher (60%) than photos (40%) when both exist.
    """
    request_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    if not files:
        return JSONResponse(status_code=400, content={
            "request_id": request_id,
            "error": "No files uploaded",
            "disclaimer": DISCLAIMER,
        })

    tmp_dir = tempfile.mkdtemp(prefix="subject_v2_")

    try:
        for f in files:
            contents = await f.read()
            if len(contents) == 0:
                continue
            safe_name = f.filename or f"file_{uuid.uuid4().hex[:6]}"
            with open(os.path.join(tmp_dir, safe_name), "wb") as out:
                out.write(contents)

        if engine.is_loaded:
            result = engine.predict_subject(tmp_dir)
        else:
            # Extract features only
            from features_v2 import extract_features_v2
            from video_features import extract_video_features
            from validate_image import validate_image

            photo_features = []
            video_features_list = []

            for fname in sorted(os.listdir(tmp_dir)):
                ext = os.path.splitext(fname)[1].lower()
                fpath = os.path.join(tmp_dir, fname)

                if ext in IMAGE_EXT:
                    v = validate_image(fpath)
                    if v["is_valid"]:
                        feat = extract_features_v2(fpath)
                        if feat:
                            photo_features.append({"filename": fname, "features": feat})

                elif ext in VIDEO_EXT:
                    feat = extract_video_features(fpath)
                    if feat:
                        video_features_list.append({"filename": fname, "features": feat})

            result = {
                "probability": None,
                "input_type": "subject_folder",
                "n_photos": len(photo_features),
                "n_videos": len(video_features_list),
                "photo_features": photo_features,
                "video_features": video_features_list,
                "message": "Features extracted. Model not yet trained — awaiting NEGATIVE data.",
                "disclaimer": DISCLAIMER,
            }

        return {
            "request_id": request_id,
            "timestamp": timestamp,
            "status": "success" if result.get("probability") is not None else "model_not_available",
            **result,
        }

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.get("/health")
async def health():
    tiers = {}
    if engine.is_loaded:
        for tier_name, info in engine.models.items():
            tiers[tier_name] = {
                "classifier": info.get("classifier"),
                "version": info.get("version"),
                "auc": info.get("auc"),
            }

    return {
        "status": "healthy",
        "model_loaded": engine.is_loaded,
        "available_tiers": list(tiers.keys()),
        "tier_details": tiers,
        "capabilities": {
            "photo_analysis": True,
            "video_analysis": True,
            "combined_analysis": True,
        },
        "features": {
            "photo": 32,
            "video": 42,
            "combined": 74,
        },
        "timestamp": datetime.now().isoformat(),
        "disclaimer": DISCLAIMER,
    }


@app.get("/stats")
async def stats():
    result = {
        "n_positive_subjects": 0,
        "n_negative_subjects": 0,
        "n_photo_features": 0,
        "n_video_features": 0,
        "disclaimer": DISCLAIMER,
    }

    if os.path.exists(FEATURES_V2_CSV):
        try:
            df = pd.read_csv(FEATURES_V2_CSV)
            result["n_positive_subjects"] = int(df[df["label"] == 1]["subject_id"].nunique())
            result["n_negative_subjects"] = int(df[df["label"] == 0]["subject_id"].nunique())
            result["n_total_photo_images"] = len(df)
            result["n_photo_features"] = 32
        except Exception:
            pass

    if os.path.exists(VIDEO_FEATURES_CSV):
        try:
            df = pd.read_csv(VIDEO_FEATURES_CSV)
            result["n_subjects_with_video"] = len(df)
            result["n_video_features"] = 42
        except Exception:
            pass

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
