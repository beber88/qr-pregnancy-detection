# PREGNANCY DETECTION AI
## Product Specification — Claude Code Brief
**Version 1.0 | Confidential | April 2026**

---

## // SYSTEM GOAL

You are building an AI-powered pregnancy detection system.

The goal is to analyze photos of urine samples and determine pregnancy probability — **replacing the physical home pregnancy test stick.**

Build a computer vision + machine learning pipeline that:
- Accepts urine sample photos as input
- Extracts visual features from the images
- Compares features between pregnant and non-pregnant samples
- Returns a pregnancy probability score (0-100%)

---

## // INPUT — FOLDER STRUCTURE

Organize all data exactly as follows before starting:

```
/data
  /pregnant
    image_001.jpg
    image_002.jpg
    ...
  /not_pregnant
    image_001.jpg
    image_002.jpg
    ...
  metadata.csv
```

**metadata.csv format:**
```
filename, label, weeks_pregnant, time_of_day, hydration, phone_model, vitamins
image_001.jpg, 1, 6, 07:30, 2, iPhone 14, yes
image_002.jpg, 0, 0, 09:00, 3, Samsung S22, no
```

`label: 1 = pregnant | 0 = not pregnant`

---

## // PHASE 1 — FEATURE EXTRACTION

Build a Python script that extracts these features from every image:

| Feature | Description | Method |
|---|---|---|
| RGB averages | Mean R, G, B pixel values | cv2.mean() |
| Brightness score | Overall lightness of image | HSV V-channel mean |
| Turbidity estimate | Transparency / cloudiness level | Laplacian variance |
| Color histogram | Distribution of hues across image | cv2.calcHist() |
| Texture score | Surface pattern complexity | GLCM or LBP |
| Edge reflection | Light reflections at cup edges | Canny edge intensity |
| Bubble detection | Count & size of bubbles | HoughCircles or contours |
| Contrast ratio | Light vs dark variation | std of pixel values |
| Saturation level | Color richness | HSV S-channel mean |
| Color variance | Pixel-to-pixel color variation | np.var() on RGB |

### Output:
- `features.csv` — one row per image, all features + label
- `summary_stats.csv` — mean/std comparison: pregnant vs not_pregnant
- Log file with extraction timestamp and image count

---

## // PHASE 2 — THREE MODELS

Build and compare exactly three models:

| Model | Input | Purpose |
|---|---|---|
| Model A | Metadata only (questionnaire) | Baseline — what can we predict without image? |
| Model B | Image features only | Core test — is there visual signal? |
| Model C | Image + Metadata combined | Does image add value beyond questionnaire? |

### Output for each model:
- Accuracy
- Sensitivity / Recall
- Specificity
- AUC score
- Confusion matrix

> **KEY QUESTION: Does Model B beat Model A?**
> If yes — there is real visual signal. If no — the image adds nothing.

---

## // PHASE 3 — VISUALIZATION & REPORT

- Plot feature distributions: pregnant vs not_pregnant side by side
- Highlight top 3 features with strongest group separation
- ROC curve for each model
- Feature importance chart
- Generate final report: `signal_report.pdf`

### Report must answer:
- Which features show the clearest separation between groups?
- Does the image contribute meaningful signal beyond metadata?
- What is the recommended next step?

---

## // TECH STACK

| Library | Purpose | Install |
|---|---|---|
| Python 3.9+ | Core language | — |
| OpenCV (cv2) | Image processing | pip install opencv-python |
| Pandas + NumPy | Data handling | pip install pandas numpy |
| Scikit-learn | ML models | pip install scikit-learn |
| Matplotlib + Seaborn | Visualization | pip install matplotlib seaborn |
| Pillow | Image loading | pip install Pillow |

---

## // CRITICAL RULES

- **NEVER output "pregnant" or "not pregnant" as a diagnosis**
- **ALWAYS output a probability score between 0-100%**
- Log every model version and dataset version
- Keep `/data/raw` separate from `/data/processed`
- Document every feature extraction step with comments
- Save all model files with version number: `model_B_v1.pkl`
- Never modify original images

> **Legal disclaimer to include in all outputs:**
> `"Research use only. Experimental probability model. Not a diagnostic test."`

---

## // FIRST TASK

Build the feature extraction script for Phase 1.
Ask the user for the image folder structure before starting.
