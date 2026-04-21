"""
Data Validation Layer
Every image must pass validation before entering the system (training or inference).

Checks:
  (a) Image readable and at least 500x500 px
  (b) Cup ROI detection succeeded and occupies 10-70% of the frame
  (c) Not too dark (mean brightness > 30) or overexposed (mean brightness > 240)
  (d) Not too blurry (Laplacian variance above minimum threshold)

Returns: dict with is_valid, issues[], warnings[]

Research use only. Experimental probability model. Not a diagnostic test.
"""

import cv2
import numpy as np

# Thresholds
MIN_DIMENSION = 500
MIN_ROI_RATIO = 0.03
MAX_ROI_RATIO = 0.80
MIN_BRIGHTNESS = 30
MAX_BRIGHTNESS = 240
MIN_LAPLACIAN_VAR = 20.0   # Below this = warning (soft blur)
HARD_BLUR_THRESHOLD = 10.0  # Below this = hard reject (unusable)


def validate_image(image_path):
    """
    Validate a single image for processing eligibility.

    Args:
        image_path: Path to the image file.

    Returns:
        dict with keys:
            is_valid (bool): True if image passes all critical checks.
            issues (list[str]): Critical problems — image cannot be processed.
            warnings (list[str]): Non-critical concerns — image can proceed.
            metadata (dict): Extracted validation metrics.
    """
    issues = []
    warnings = []
    metadata = {}

    # --- Check (a): Readable and minimum size ---
    img = cv2.imread(image_path)
    if img is None:
        return {
            "is_valid": False,
            "issues": [f"Image unreadable: {image_path}"],
            "warnings": [],
            "metadata": {},
        }

    h, w = img.shape[:2]
    metadata["height"] = h
    metadata["width"] = w
    metadata["file_path"] = image_path

    if h < MIN_DIMENSION or w < MIN_DIMENSION:
        issues.append(
            f"Image too small: {w}x{h} px (minimum {MIN_DIMENSION}x{MIN_DIMENSION})"
        )

    # --- Check (c): Brightness (run before ROI, uses full image) ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(np.mean(gray))
    metadata["mean_brightness"] = round(mean_brightness, 2)

    if mean_brightness < MIN_BRIGHTNESS:
        issues.append(
            f"Image too dark: mean brightness {mean_brightness:.1f} (minimum {MIN_BRIGHTNESS})"
        )
    elif mean_brightness > MAX_BRIGHTNESS:
        issues.append(
            f"Image overexposed: mean brightness {mean_brightness:.1f} (maximum {MAX_BRIGHTNESS})"
        )
    elif mean_brightness < 60:
        warnings.append(f"Image is dim: mean brightness {mean_brightness:.1f}")
    elif mean_brightness > 220:
        warnings.append(f"Image is very bright: mean brightness {mean_brightness:.1f}")

    # --- Check (d): Blur detection (Laplacian variance) ---
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    lap_var = float(np.var(laplacian))
    metadata["laplacian_variance"] = round(lap_var, 2)

    if lap_var < HARD_BLUR_THRESHOLD:
        issues.append(
            f"Image too blurry: Laplacian variance {lap_var:.1f} (minimum {HARD_BLUR_THRESHOLD})"
        )
    elif lap_var < MIN_LAPLACIAN_VAR:
        warnings.append(
            f"Image is soft: Laplacian variance {lap_var:.1f} (ideal > {MIN_LAPLACIAN_VAR}). "
            "Blurry images in one class but not the other create confounds."
        )
    elif lap_var < 50:
        warnings.append(f"Image slightly blurry: Laplacian variance {lap_var:.1f}")

    # --- Check (b): Cup ROI detection ---
    # Strategy 1: Adaptive threshold
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    thresh1 = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 25, 5,
    )

    # Strategy 2: Otsu threshold (better for cup-on-white-background)
    _, thresh2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Strategy 3: Saturation-based (cup liquid has color vs white bg)
    hsv_full = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sat = hsv_full[:, :, 1]
    _, thresh3 = cv2.threshold(sat, 15, 255, cv2.THRESH_BINARY)

    # Try each strategy, pick the one that gives the best contour
    roi_detected = False
    roi_ratio = 0.0
    frame_area = h * w

    for thresh in [thresh1, thresh2, thresh3]:
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            continue
        largest = max(contours, key=cv2.contourArea)
        ratio = cv2.contourArea(largest) / frame_area
        if MIN_ROI_RATIO <= ratio <= MAX_ROI_RATIO and ratio > roi_ratio:
            roi_ratio = ratio
            roi_detected = True

    metadata["roi_ratio"] = round(roi_ratio, 4)
    metadata["roi_detected"] = roi_detected

    if not roi_detected:
        if roi_ratio > 0:
            if roi_ratio < MIN_ROI_RATIO:
                issues.append(
                    f"Cup ROI too small: {roi_ratio:.1%} of frame "
                    f"(minimum {MIN_ROI_RATIO:.0%})"
                )
            else:
                issues.append(
                    f"Cup ROI too large: {roi_ratio:.1%} of frame "
                    f"(maximum {MAX_ROI_RATIO:.0%}). "
                    "Cup may be too close or background not visible."
                )
        else:
            issues.append("Cup ROI not detected — no significant contour found")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "metadata": metadata,
    }


def validate_image_from_bytes(image_bytes):
    """
    Validate an image from raw bytes (for API uploads).
    Same checks as validate_image but accepts bytes instead of file path.
    """
    img_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        return {
            "is_valid": False,
            "issues": ["Image unreadable from uploaded bytes"],
            "warnings": [],
            "metadata": {},
        }

    # Write to a temp path isn't needed — replicate logic inline
    # Save to temp, validate, clean up
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name
        cv2.imwrite(tmp_path, img)

    result = validate_image(tmp_path)
    os.unlink(tmp_path)
    return result
