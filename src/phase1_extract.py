"""
Phase 1 — Feature Extraction
Reads index.csv, extracts 15 visual features from every image/frame,
and saves features.csv with subject_id on each row.

Features extracted:
  1. r_mean        — Mean red channel (ROI)
  2. g_mean        — Mean green channel (ROI)
  3. b_mean        — Mean blue channel (ROI)
  4. brightness    — HSV V-channel mean (ROI)
  5. turbidity     — Laplacian variance (lower = cloudier)
  6. dominant_hue  — Center of most common hue bin
  7. hue_spread    — Std of hue values
  8. texture_score — Local Binary Pattern variance
  9. edge_intensity— Canny edge pixel ratio in ROI
 10. bubble_count  — HoughCircles bubble detection
 11. contrast      — Std of grayscale values
 12. saturation    — HSV S-channel mean (ROI)
 13. color_variance— Overall RGB variance
 14. yellowness    — (R+G) / (2*B) ratio
 15. gy_ratio      — G/R ratio

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import logging
from datetime import datetime

import cv2
import numpy as np
import pandas as pd
from skimage.feature import local_binary_pattern

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
INDEX_CSV = os.path.join(PROCESSED_DIR, "index.csv")
FEATURES_CSV = os.path.join(PROCESSED_DIR, "features.csv")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

TARGET_SIZE = (512, 512)

FEATURE_NAMES = [
    "r_mean", "g_mean", "b_mean", "brightness", "turbidity",
    "dominant_hue", "hue_spread", "texture_score", "edge_intensity",
    "bubble_count", "contrast", "saturation", "color_variance",
    "yellowness", "gy_ratio",
]


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"phase1_extract_{ts}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_file


def detect_cup_roi(image):
    """
    Detect the cup/liquid region. Returns a binary mask.
    Strategy: convert to HSV, look for the non-white region in the
    lower-center of the image where the liquid sits.
    Falls back to center 60% crop.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)

    # Adaptive threshold to find the cup against white background
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 25, 5
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest = max(contours, key=cv2.contourArea)
        area_ratio = cv2.contourArea(largest) / (image.shape[0] * image.shape[1])
        if 0.05 < area_ratio < 0.85:
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [largest], -1, 255, -1)
            return mask

    # Fallback: center 60%
    h, w = gray.shape
    mask = np.zeros((h, w), dtype=np.uint8)
    y1, y2 = int(h * 0.2), int(h * 0.8)
    x1, x2 = int(w * 0.2), int(w * 0.8)
    mask[y1:y2, x1:x2] = 255
    return mask


def extract_features(image_path):
    """Extract all 15 features from a single image. Returns dict or None."""
    img = cv2.imread(image_path)
    if img is None:
        logging.warning(f"Cannot read: {image_path}")
        return None

    img = cv2.resize(img, TARGET_SIZE)
    roi_mask = detect_cup_roi(img)

    # Color spaces
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Masked regions
    n_px = max(cv2.countNonZero(roi_mask), 1)
    roi_bgr = cv2.bitwise_and(img, img, mask=roi_mask)
    roi_hsv = cv2.bitwise_and(hsv, hsv, mask=roi_mask)
    roi_gray = cv2.bitwise_and(gray, gray, mask=roi_mask)

    # 1-3: RGB means
    b_mean = np.sum(roi_bgr[:, :, 0]) / n_px
    g_mean = np.sum(roi_bgr[:, :, 1]) / n_px
    r_mean = np.sum(roi_bgr[:, :, 2]) / n_px

    # 4: Brightness (V channel)
    brightness = np.sum(roi_hsv[:, :, 2]) / n_px

    # 5: Turbidity (Laplacian variance)
    lap = cv2.Laplacian(roi_gray, cv2.CV_64F)
    lap_vals = lap[roi_mask > 0]
    turbidity = float(np.var(lap_vals)) if len(lap_vals) > 0 else 0.0

    # 6-7: Hue histogram
    hue_vals = roi_hsv[:, :, 0][roi_mask > 0]
    if len(hue_vals) > 0:
        hist, _ = np.histogram(hue_vals, bins=18, range=(0, 180))
        dominant_hue = float(np.argmax(hist) * 10)
        hue_spread = float(np.std(hue_vals))
    else:
        dominant_hue, hue_spread = 0.0, 0.0

    # 8: Texture (LBP variance)
    lbp = local_binary_pattern(gray, P=8, R=1, method="uniform")
    lbp_vals = lbp[roi_mask > 0]
    texture_score = float(np.var(lbp_vals)) if len(lbp_vals) > 0 else 0.0

    # 9: Edge intensity (Canny ratio)
    edges = cv2.Canny(roi_gray, 50, 150)
    edge_vals = edges[roi_mask > 0]
    edge_intensity = float(np.sum(edge_vals > 0) / n_px)

    # 10: Bubble count (HoughCircles)
    blurred_g = cv2.GaussianBlur(roi_gray, (9, 9), 2)
    circles = cv2.HoughCircles(
        blurred_g, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
        param1=50, param2=30, minRadius=3, maxRadius=30,
    )
    bubble_count = 0 if circles is None else len(circles[0])

    # 11: Contrast (grayscale std)
    gray_vals = gray[roi_mask > 0]
    contrast = float(np.std(gray_vals)) if len(gray_vals) > 0 else 0.0

    # 12: Saturation (S channel mean)
    sat_vals = roi_hsv[:, :, 1][roi_mask > 0]
    saturation = float(np.mean(sat_vals)) if len(sat_vals) > 0 else 0.0

    # 13: Color variance (overall RGB)
    rgb_vals = roi_bgr[roi_mask > 0]
    color_variance = float(np.var(rgb_vals)) if len(rgb_vals) > 0 else 0.0

    # 14: Yellowness — (R+G)/(2B)
    yellowness = (r_mean + g_mean) / (2 * max(b_mean, 1))

    # 15: Green/Red ratio
    gy_ratio = g_mean / max(r_mean, 1)

    return {
        "r_mean": round(r_mean, 4),
        "g_mean": round(g_mean, 4),
        "b_mean": round(b_mean, 4),
        "brightness": round(brightness, 4),
        "turbidity": round(turbidity, 4),
        "dominant_hue": round(dominant_hue, 4),
        "hue_spread": round(hue_spread, 4),
        "texture_score": round(texture_score, 4),
        "edge_intensity": round(edge_intensity, 4),
        "bubble_count": int(bubble_count),
        "contrast": round(contrast, 4),
        "saturation": round(saturation, 4),
        "color_variance": round(color_variance, 4),
        "yellowness": round(yellowness, 4),
        "gy_ratio": round(gy_ratio, 4),
    }


def run_extraction():
    log_file = setup_logging()
    logging.info("=" * 60)
    logging.info("PHASE 1 — Feature Extraction")
    logging.info("=" * 60)

    if not os.path.exists(INDEX_CSV):
        logging.error(f"index.csv not found at {INDEX_CSV}. Run build_index.py first.")
        sys.exit(1)

    index_df = pd.read_csv(INDEX_CSV)
    logging.info(f"Loaded index: {len(index_df)} rows")

    rows = []
    for i, idx_row in index_df.iterrows():
        features = extract_features(idx_row["filepath"])
        if features is None:
            continue

        row = {
            "filepath": idx_row["filepath"],
            "subject_id": idx_row["subject_id"],
            "label": idx_row["label"],
            "media_type": idx_row["media_type"],
            "frame_number": idx_row["frame_number"],
            **features,
        }
        rows.append(row)

        if (i + 1) % 20 == 0 or (i + 1) == len(index_df):
            logging.info(f"  Extracted {i + 1}/{len(index_df)}")

    df = pd.DataFrame(rows)
    df.to_csv(FEATURES_CSV, index=False)
    logging.info(f"\nSaved: {FEATURES_CSV}")
    logging.info(f"Shape: {df.shape}")
    logging.info(f"Subjects: {df['subject_id'].nunique()}")
    logging.info(f"Log: {log_file}")

    return df


if __name__ == "__main__":
    run_extraction()
