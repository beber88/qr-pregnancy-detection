# Pregnancy Detection AI

> **Research use only. Experimental probability model. Not a diagnostic test.**

Computer vision + machine learning pipeline that analyzes photos of urine samples
to detect visual patterns associated with pregnancy.

## Current State

| Phase | Status |
|-------|--------|
| Phase 1 — Feature Extraction | **COMPLETE** (15 positive subjects, 219 images) |
| Sanity Check | Waiting for NEGATIVE data |
| Phase 2 — Model Training | Waiting for NEGATIVE data |
| Phase 3 — Visualization | EDA on positive-only complete |
| Web API + UI | Built, serving "model not available" until trained |

## Project Structure

```
QR PROJECT/
├── PICTURES/                    # Original images (NEVER modified)
│   ├── POSITIVE/                # Pregnant subjects (1/, 2/, ... 15/)
│   └── NEGATIVE/                # Not pregnant subjects (empty — awaiting data)
├── data/
│   ├── raw/video_frames/        # Extracted frames from videos (1fps)
│   └── processed/
│       ├── index.csv            # Master index of all images + frames
│       └── features.csv         # 15 visual features per image
├── src/
│   ├── build_index.py           # Scan PICTURES/, extract video frames, build index
│   ├── phase1_extract.py        # Extract 15 visual features from each image
│   ├── eda_report.py            # EDA report with variance decomposition
│   ├── validate_image.py        # Image quality validation gate
│   ├── inference.py             # PregnancyInferenceEngine class
│   ├── sanity_check.py          # Confound detection (run BEFORE training)
│   ├── train.py                 # Model training with GroupKFold
│   ├── api.py                   # FastAPI web server
│   └── ui/
│       ├── index.html           # Web interface
│       └── app.js               # Frontend logic
├── models/                      # Saved .pkl model files (empty until trained)
├── reports/
│   └── eda_positive_only.pdf    # Phase 1 EDA report
├── logs/                        # Timestamped log files
├── requirements.txt
├── run_pipeline.py              # Runs build_index → extract → EDA
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart
```

### 2. Run the data pipeline

```bash
python run_pipeline.py
```

This executes:
- `build_index.py` — Scans `PICTURES/`, extracts 1 frame/sec from videos, writes `index.csv`
- `phase1_extract.py` — Extracts 15 features from every image, writes `features.csv`
- `eda_report.py` — Generates `reports/eda_positive_only.pdf`

### 3. Launch the web server

```bash
cd src && python api.py
```

Then open http://localhost:8000 in your browser. Upload a urine sample photo to test
the validation and feature extraction pipeline. The model will return "not yet available"
until training is complete.

### 4. When NEGATIVE data arrives

Add subject folders to `PICTURES/NEGATIVE/` following the same structure:
```
NEGATIVE/
  001/
    photo1.jpg
    photo2.jpg
    photo3.jpg
    video.mp4
  002/
    ...
```

Then run these steps **in order**:

```bash
# Step 1: Re-run pipeline to index + extract features from all data
python run_pipeline.py

# Step 2: Sanity check — detect data collection confounds
cd src && python sanity_check.py

# Step 3: Train (only if sanity check passes)
python train.py

# Step 4: Restart the API server to load the new model
python api.py
```

## Component Details

### Features Extracted (15)

| # | Feature | Method | What it measures |
|---|---------|--------|------------------|
| 1 | r_mean | RGB mean (ROI) | Red channel intensity |
| 2 | g_mean | RGB mean (ROI) | Green channel intensity |
| 3 | b_mean | RGB mean (ROI) | Blue channel intensity |
| 4 | brightness | HSV V-channel | Overall lightness |
| 5 | turbidity | Laplacian variance | Cloudiness/transparency |
| 6 | dominant_hue | Hue histogram | Primary color |
| 7 | hue_spread | Hue std | Color distribution width |
| 8 | texture_score | LBP variance | Surface pattern complexity |
| 9 | edge_intensity | Canny edge ratio | Light reflections at edges |
| 10 | bubble_count | HoughCircles | Number of bubbles |
| 11 | contrast | Grayscale std | Light/dark variation |
| 12 | saturation | HSV S-channel | Color richness |
| 13 | color_variance | RGB variance | Pixel-to-pixel variation |
| 14 | yellowness | (R+G)/(2B) | Urine color depth |
| 15 | gy_ratio | G/R ratio | Green-red balance |

### Image Validation Checks

Every image must pass these checks before processing:
- **Readable** and at least 500x500 px
- **Cup ROI** detected, occupying 10-70% of frame
- **Not too dark** (brightness > 30) or **overexposed** (brightness > 240)
- **Not too blurry** (Laplacian variance > 20)

### Sanity Check (sanity_check.py)

Trains a model using only technical metadata (file size, timestamp, dimensions,
brightness) that should NOT predict pregnancy. If AUC > 0.65, there is a systematic
difference in how POSITIVE and NEGATIVE photos were collected, and Model B results
cannot be trusted.

### Training (train.py)

- **GroupKFold** cross-validation: no subject appears in both train and test
- Three candidates: LogisticRegression, RandomForest, GradientBoosting
- Best model selected by mean AUC across folds
- Saved to `models/model_B_v1.pkl`

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/predict` | POST | Upload image → validation + prediction |
| `/health` | GET | System status, model version |
| `/stats` | GET | Dataset statistics |

All responses include the mandatory disclaimer.

## Output Files

| File | Description |
|------|-------------|
| `data/processed/index.csv` | Every image/frame with subject_id, label, media_type |
| `data/processed/features.csv` | 15 features per image with subject_id |
| `reports/eda_positive_only.pdf` | Variance decomposition, distributions, correlations |
| `models/model_B_v1.pkl` | Trained model + metadata (after training) |
| `logs/*.log` | Timestamped logs for every pipeline step |

## Troubleshooting

**"index.csv not found"**
→ Run `python run_pipeline.py` first, or `cd src && python build_index.py`

**"Both classes required"**
→ NEGATIVE samples haven't been added yet. Add folders to `PICTURES/NEGATIVE/`

**"Model not yet trained"**
→ Expected until NEGATIVE data arrives and training completes

**"CONFOUND DETECTED" from sanity_check.py**
→ Photos from POSITIVE and NEGATIVE groups were taken under different conditions.
  Check timing, phones, lighting. Re-collect with matched conditions.

**API won't start**
→ Run `pip install fastapi uvicorn python-multipart` and try again

**Video frames not extracted**
→ Ensure OpenCV is installed with video support: `pip install opencv-python`

## Photography Protocol

For new samples, follow this protocol exactly:
- Clear plastic cup with lid
- White background
- Natural light
- 30cm distance
- 3 angle photos + 10 second video
- Within 60 seconds of urination

---

*Research use only. Experimental probability model. Not a diagnostic test.*
