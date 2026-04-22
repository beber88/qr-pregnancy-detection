"""
Calibration Module — Color Normalization Using White Paper Background

No physical calibration card needed. The white paper sheet that the cup
sits on IS the calibration reference. Every home has white paper.

How it works:
  1. Detect the cup ROI (liquid region)
  2. Sample the white paper AROUND the cup (the background)
  3. Use white paper RGB as the illuminant estimate
  4. Normalize: corrected = raw_pixel / white_paper_mean * 255
  5. After normalization, R-channel values are comparable across
     any phone, any lighting, any room

This is the single most impactful step for signal quality.
Without it, device/lighting noise drowns the subtle 590-670nm
signal identified by Layla et al. (2019).

Research use only. Not a diagnostic test.
"""

import cv2
import numpy as np
import logging


# Thresholds for white paper detection
WHITE_PAPER_MIN_BRIGHTNESS = 180  # Paper region must be bright
WHITE_PAPER_MAX_SATURATION = 40   # Paper region must be near-neutral
WHITE_PAPER_MIN_AREA_RATIO = 0.10 # Paper must cover at least 10% of image


def find_white_paper_region(image, cup_mask=None):
    """
    Detect the white paper background around the cup.

    Strategy:
      1. Find bright, low-saturation pixels (= white paper)
      2. Exclude the cup ROI region
      3. Sample from the remaining white area

    Args:
        image: BGR image
        cup_mask: binary mask of cup region (to exclude). If None, auto-detected.

    Returns:
        dict with paper_found, paper_mask, mean_bgr, sample_regions
    """
    h, w = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # White paper = high V (bright), low S (not colored)
    v_channel = hsv[:, :, 2]
    s_channel = hsv[:, :, 1]

    paper_mask = (
        (v_channel > WHITE_PAPER_MIN_BRIGHTNESS) &
        (s_channel < WHITE_PAPER_MAX_SATURATION)
    ).astype(np.uint8) * 255

    # Exclude the cup region if provided
    if cup_mask is not None:
        # Dilate cup mask slightly to avoid edge effects
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
        cup_expanded = cv2.dilate(cup_mask, kernel, iterations=1)
        paper_mask = cv2.bitwise_and(paper_mask, cv2.bitwise_not(cup_expanded))

    # Clean up small noise
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    paper_mask = cv2.morphologyEx(paper_mask, cv2.MORPH_OPEN, kernel_small)

    paper_area = cv2.countNonZero(paper_mask)
    paper_ratio = paper_area / (h * w)

    if paper_ratio < WHITE_PAPER_MIN_AREA_RATIO:
        return {
            "paper_found": False,
            "paper_ratio": round(paper_ratio, 4),
            "mean_bgr": None,
        }

    # Sample mean BGR from paper region
    paper_pixels = image[paper_mask > 0]
    mean_bgr = np.mean(paper_pixels.reshape(-1, 3), axis=0).astype(float)

    # Also sample from 4 corners of paper for uniformity check
    regions = _sample_quadrants(image, paper_mask)

    return {
        "paper_found": True,
        "paper_ratio": round(paper_ratio, 4),
        "mean_bgr": mean_bgr,
        "paper_mask": paper_mask,
        "quadrant_means": regions,
    }


def _sample_quadrants(image, paper_mask):
    """Sample paper color from 4 quadrants to check lighting uniformity."""
    h, w = image.shape[:2]
    quadrants = {
        "top_left": (0, h//2, 0, w//2),
        "top_right": (0, h//2, w//2, w),
        "bot_left": (h//2, h, 0, w//2),
        "bot_right": (h//2, h, w//2, w),
    }
    results = {}
    for name, (y1, y2, x1, x2) in quadrants.items():
        q_mask = paper_mask[y1:y2, x1:x2]
        q_pixels = image[y1:y2, x1:x2][q_mask > 0]
        if len(q_pixels) > 10:
            results[name] = np.mean(q_pixels.reshape(-1, 3), axis=0).tolist()
        else:
            results[name] = None
    return results


def calibrate_image(image, cup_mask=None):
    """
    Normalize image colors using the white paper background.

    The white paper should appear as pure white (255,255,255) after
    correction. Any color cast from lighting or device is removed.

    Correction: corrected_pixel = raw_pixel / paper_mean * 255

    This is a single-point (white) calibration. It corrects:
    - Color temperature (warm/cool lighting)
    - Device white balance differences
    - Brightness level differences

    Args:
        image: BGR image (uncalibrated)
        cup_mask: optional binary mask of cup region

    Returns:
        tuple: (calibrated_image, calibration_info)
    """
    paper = find_white_paper_region(image, cup_mask)

    if not paper["paper_found"]:
        logging.warning("White paper not detected — returning uncalibrated image")
        return image.copy(), {
            "calibrated": False,
            "paper_found": False,
            "paper_ratio": paper["paper_ratio"],
        }

    white_bgr = paper["mean_bgr"]

    # Per-channel scaling: corrected = raw / white * 255
    # This makes the paper appear as (255, 255, 255) = pure white
    scale = np.array([255.0 / max(ch, 1.0) for ch in white_bgr])

    calibrated = image.astype(float)
    for ch in range(3):
        calibrated[:, :, ch] = calibrated[:, :, ch] * scale[ch]

    calibrated = np.clip(calibrated, 0, 255).astype(np.uint8)

    # Lighting uniformity check
    uniformity = _compute_uniformity(paper["quadrant_means"])

    info = {
        "calibrated": True,
        "paper_found": True,
        "paper_ratio": paper["paper_ratio"],
        "raw_paper_bgr": white_bgr.tolist(),
        "scale_factors": scale.tolist(),
        "lighting_uniformity": uniformity,
        "illuminant_cct": _estimate_cct_from_white(white_bgr),
    }

    return calibrated, info


def _compute_uniformity(quadrant_means):
    """
    Compute lighting uniformity score from quadrant paper samples.
    Returns coefficient of variation of brightness across quadrants.
    Lower = more uniform. Good < 0.05, OK < 0.10, Poor > 0.15.
    """
    if quadrant_means is None:
        return None
    values = [np.mean(v) for v in quadrant_means.values() if v is not None]
    if len(values) < 2:
        return None
    mean_val = np.mean(values)
    if mean_val < 1:
        return None
    cv = float(np.std(values) / mean_val)
    return round(cv, 4)


def _estimate_cct_from_white(white_bgr):
    """
    Estimate illuminant color temperature from white paper color.
    The tint of the "white" paper reveals the lighting CCT.
    """
    b, g, r = white_bgr
    r_b_ratio = r / max(b, 1)

    if r_b_ratio > 1.3:
        return 2700   # Warm incandescent
    elif r_b_ratio > 1.15:
        return 3500   # Warm LED
    elif r_b_ratio > 1.0:
        return 4500   # Neutral LED
    elif r_b_ratio > 0.9:
        return 5500   # Daylight
    elif r_b_ratio > 0.8:
        return 6500   # Overcast
    else:
        return 7500   # Cool fluorescent


def compute_illuminant_estimate(image, cal_info=None):
    """Public API for illuminant estimation."""
    if cal_info and cal_info.get("calibrated"):
        return cal_info.get("illuminant_cct", 5500)

    # Fallback: gray-world assumption
    means = np.mean(image.reshape(-1, 3), axis=0)
    return _estimate_cct_from_white(means)
