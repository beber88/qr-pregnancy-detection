"""
Phase 1 V2 — Enhanced Feature Extraction with Calibration + Layla-Range Features

Builds on phase1_extract.py, adding:
  - Calibration card color normalization (critical for cross-device consistency)
  - Layla-range spectral proxy features targeting 590-670nm absorbance
  - R-channel ratio features (R/(R+G+B), R/G) for pregnancy signal detection
  - CIELAB color space features for perceptual uniformity
  - Temporal-ready output (features structured for longitudinal analysis)

Feature groups:
  A. Original 15 features (from phase1_extract.py)
  B. Calibration quality metrics (4 features)
  C. Layla-range spectral proxy features (6 features)  ← KEY ADDITION
  D. CIELAB perceptual features (4 features)
  E. Concentration proxy features (3 features)

Total: 32 features per image

Reference: Layla et al. 2019 — pregnancy urine shows absorbance peak at
590-670nm, overlapping RGB R-channel (580-700nm). R/(R+G+B) ratio is our
best RGB approximation of this spectral measurement.

Research use only. Not a diagnostic test.
"""

import cv2
import numpy as np
import logging
from skimage.feature import local_binary_pattern

from calibration import calibrate_image, compute_illuminant_estimate


# ── Group A: Original features (same as phase1_extract.py) ──────────────

def extract_original_features(image, roi_mask):
    """Extract the original 15 features. Input should be calibrated image."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    n_px = max(cv2.countNonZero(roi_mask), 1)
    roi_bgr = cv2.bitwise_and(image, image, mask=roi_mask)
    roi_hsv = cv2.bitwise_and(hsv, hsv, mask=roi_mask)
    roi_gray = cv2.bitwise_and(gray, gray, mask=roi_mask)

    b_mean = np.sum(roi_bgr[:, :, 0]) / n_px
    g_mean = np.sum(roi_bgr[:, :, 1]) / n_px
    r_mean = np.sum(roi_bgr[:, :, 2]) / n_px
    brightness = np.sum(roi_hsv[:, :, 2]) / n_px

    lap = cv2.Laplacian(roi_gray, cv2.CV_64F)
    lap_vals = lap[roi_mask > 0]
    turbidity = float(np.var(lap_vals)) if len(lap_vals) > 0 else 0.0

    hue_vals = roi_hsv[:, :, 0][roi_mask > 0]
    if len(hue_vals) > 0:
        hist, _ = np.histogram(hue_vals, bins=18, range=(0, 180))
        dominant_hue = float(np.argmax(hist) * 10)
        hue_spread = float(np.std(hue_vals))
    else:
        dominant_hue, hue_spread = 0.0, 0.0

    lbp = local_binary_pattern(gray, P=8, R=1, method="uniform")
    lbp_vals = lbp[roi_mask > 0]
    texture_score = float(np.var(lbp_vals)) if len(lbp_vals) > 0 else 0.0

    edges = cv2.Canny(roi_gray, 50, 150)
    edge_vals = edges[roi_mask > 0]
    edge_intensity = float(np.sum(edge_vals > 0) / n_px)

    blurred_g = cv2.GaussianBlur(roi_gray, (9, 9), 2)
    circles = cv2.HoughCircles(
        blurred_g, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
        param1=50, param2=30, minRadius=3, maxRadius=30,
    )
    bubble_count = 0 if circles is None else len(circles[0])

    gray_vals = gray[roi_mask > 0]
    contrast = float(np.std(gray_vals)) if len(gray_vals) > 0 else 0.0

    sat_vals = roi_hsv[:, :, 1][roi_mask > 0]
    saturation = float(np.mean(sat_vals)) if len(sat_vals) > 0 else 0.0

    rgb_vals = roi_bgr[roi_mask > 0]
    color_variance = float(np.var(rgb_vals)) if len(rgb_vals) > 0 else 0.0

    yellowness = (r_mean + g_mean) / (2 * max(b_mean, 1))
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
        "edge_intensity": round(edge_intensity, 6),
        "bubble_count": int(bubble_count),
        "contrast": round(contrast, 4),
        "saturation": round(saturation, 4),
        "color_variance": round(color_variance, 4),
        "yellowness": round(yellowness, 4),
        "gy_ratio": round(gy_ratio, 4),
    }


# ── Group C: Layla-range spectral proxy features ────────────────────────
#
# Layla et al. (2019) found pregnancy urine absorbance peaks at 590-670nm.
# The RGB R-channel (Bayer filter ~580-700nm) overlaps this range.
# These features extract maximum information from R-channel relative
# to other channels, after calibration normalization.

def extract_layla_features(image, roi_mask):
    """
    Extract spectral proxy features targeting 590-670nm pregnancy signal.

    After calibration, the R-channel best approximates absorbance in the
    Layla range. We compute ratios and distributions that would change
    if the 590-670nm absorbance shifts.
    """
    n_px = max(cv2.countNonZero(roi_mask), 1)

    # Get float channels from ROI
    roi_pixels = image[roi_mask > 0].astype(float)
    if len(roi_pixels) == 0:
        return _layla_defaults()

    b_vals = roi_pixels[:, 0]
    g_vals = roi_pixels[:, 1]
    r_vals = roi_pixels[:, 2]

    total = r_vals + g_vals + b_vals
    total = np.where(total < 1, 1, total)  # Avoid div/0

    # Feature C1: R-channel ratio — primary Layla proxy
    # Higher = more 590-670nm absorbance/reflection
    r_ratio = r_vals / total
    r_ratio_mean = float(np.mean(r_ratio))

    # Feature C2: R/G ratio — pregnancy-related RI change indicator
    # Layla showed RI increase shifts absorbance; R/G captures relative shift
    rg_ratio = r_vals / np.where(g_vals < 1, 1, g_vals)
    rg_ratio_mean = float(np.mean(rg_ratio))

    # Feature C3: R/B ratio — complementary spectral indicator
    rb_ratio = r_vals / np.where(b_vals < 1, 1, b_vals)
    rb_ratio_mean = float(np.mean(rb_ratio))

    # Feature C4: R-channel variance within ROI
    # Pregnancy may cause heterogeneous absorbance patterns
    r_ratio_std = float(np.std(r_ratio))

    # Feature C5: R-channel skewness
    # Asymmetric distribution may indicate subtle concentration gradients
    r_mean_val = np.mean(r_vals)
    r_std_val = max(np.std(r_vals), 0.001)
    r_skew = float(np.mean(((r_vals - r_mean_val) / r_std_val) ** 3))

    # Feature C6: Red dominance score
    # Fraction of ROI pixels where R is the strongest channel
    r_dominant = float(np.mean((r_vals > g_vals) & (r_vals > b_vals)))

    return {
        "layla_r_ratio": round(r_ratio_mean, 6),
        "layla_rg_ratio": round(rg_ratio_mean, 6),
        "layla_rb_ratio": round(rb_ratio_mean, 6),
        "layla_r_ratio_std": round(r_ratio_std, 6),
        "layla_r_skew": round(r_skew, 6),
        "layla_r_dominant": round(r_dominant, 6),
    }


def _layla_defaults():
    return {
        "layla_r_ratio": 0.0,
        "layla_rg_ratio": 0.0,
        "layla_rb_ratio": 0.0,
        "layla_r_ratio_std": 0.0,
        "layla_r_skew": 0.0,
        "layla_r_dominant": 0.0,
    }


# ── Group D: CIELAB perceptual color features ───────────────────────────

def extract_lab_features(image, roi_mask):
    """
    CIELAB features are perceptually uniform — small deltaE = small
    perceived difference. Better for detecting subtle color shifts
    than RGB or HSV.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab_pixels = lab[roi_mask > 0].astype(float)

    if len(lab_pixels) == 0:
        return {"lab_L": 0.0, "lab_a": 0.0, "lab_b": 0.0, "lab_chroma": 0.0}

    L_mean = float(np.mean(lab_pixels[:, 0]))
    a_mean = float(np.mean(lab_pixels[:, 1])) - 128  # OpenCV LAB: a,b offset by 128
    b_mean = float(np.mean(lab_pixels[:, 2])) - 128
    chroma = float(np.sqrt(a_mean**2 + b_mean**2))

    return {
        "lab_L": round(L_mean, 4),
        "lab_a": round(a_mean, 4),
        "lab_b": round(b_mean, 4),
        "lab_chroma": round(chroma, 4),
    }


# ── Group E: Concentration proxy features ────────��──────────────────────

def extract_concentration_features(image, roi_mask):
    """
    Urine concentration is the #1 confounder (hydration-driven).
    Explicit concentration estimation helps the model SEPARATE
    hydration effects from pregnancy effects.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_pixels = hsv[roi_mask > 0].astype(float)

    if len(hsv_pixels) == 0:
        return {"conc_proxy_sv": 0.0, "conc_proxy_yellow_sat": 0.0, "conc_darkness": 0.0}

    s_vals = hsv_pixels[:, 1]
    v_vals = hsv_pixels[:, 2]

    # SV product — higher S and lower V = darker, more concentrated
    sv_product = float(np.mean(s_vals * (255 - v_vals)))

    # Yellow saturation — specifically the saturation in the yellow hue range
    h_vals = hsv_pixels[:, 0]
    yellow_mask = (h_vals >= 15) & (h_vals <= 35)  # Yellow range in OpenCV HSV
    if np.any(yellow_mask):
        yellow_sat = float(np.mean(s_vals[yellow_mask]))
    else:
        yellow_sat = 0.0

    # Darkness (inverse brightness) — simple concentration correlate
    darkness = 255.0 - float(np.mean(v_vals))

    return {
        "conc_proxy_sv": round(sv_product, 4),
        "conc_proxy_yellow_sat": round(yellow_sat, 4),
        "conc_darkness": round(darkness, 4),
    }


# ── Main extraction function ─────────��──────────────────────────────────

def extract_features_v2(image_path):
    """
    Extract all 32 features from a single image with calibration.

    Pipeline:
      1. Read image
      2. Detect + apply calibration (if card found)
      3. Detect cup ROI
      4. Extract all feature groups on calibrated image
      5. Return features + calibration metadata

    Returns:
        dict with all features + calibration info, or None if image unreadable.
    """
    img = cv2.imread(image_path)
    if img is None:
        logging.warning(f"Cannot read: {image_path}")
        return None

    # Step 1: Resize for consistent processing
    target_size = (512, 512)
    img_resized = cv2.resize(img, target_size)

    # Step 2: Detect ROI first (needed for calibration to exclude cup)
    roi_mask = _detect_cup_roi(img_resized)

    # Step 3: Calibrate using white paper background (excludes cup region)
    calibrated, cal_info = calibrate_image(img_resized, cup_mask=roi_mask)
    calibrated_resized = calibrated
    original_resized = img_resized

    # Step 4: Extract all feature groups
    features = {}

    # Group A: Original 15 features (on calibrated image)
    features.update(extract_original_features(calibrated_resized, roi_mask))

    # Group B: Calibration quality
    features["cal_card_found"] = int(cal_info.get("card_found", False))
    features["cal_delta_e"] = cal_info.get("delta_e_gray", -1.0)
    features["cal_quality_ok"] = int(cal_info.get("calibration_quality_ok", False))
    features["cal_cct_estimate"] = compute_illuminant_estimate(original_resized, cal_info)

    # Group C: Layla-range spectral proxy (on CALIBRATED image — critical)
    features.update(extract_layla_features(calibrated_resized, roi_mask))

    # Group D: CIELAB perceptual
    features.update(extract_lab_features(calibrated_resized, roi_mask))

    # Group E: Concentration proxy
    features.update(extract_concentration_features(calibrated_resized, roi_mask))

    return features


def _detect_cup_roi(image):
    """Detect cup region. Same logic as phase1_extract.py."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)

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
