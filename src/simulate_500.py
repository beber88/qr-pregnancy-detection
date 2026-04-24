"""
Simulate 500 Agents — Synthetic Urine Image Generator + API Tester

Creates 500 synthetic urine images representing women in diverse states:
- 250 pregnant (weeks 4-40, various ages, hydration levels)
- 250 not pregnant (various ages, cycle phases, hydration levels)

Each agent has a profile affecting urine color/appearance:
- Hydration level -> concentration -> color darkness
- Pregnancy weeks -> hormone levels -> subtle color shifts
- Supplements (B vitamins -> bright yellow, iron -> darker)
- Time of day (morning = concentrated, afternoon = diluted)

Sends each image to the Vercel API and records predictions.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import json
import random
import math
import time
import csv
from datetime import datetime

import cv2
import numpy as np

# Try to use requests, fall back to urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "simulated_agents")
RESULTS_CSV = os.path.join(OUTPUT_DIR, "simulation_results.csv")
API_URL = "https://qr-pregnancy-detection.vercel.app/api/predict"


def generate_urine_color(profile):
    """
    Generate realistic urine RGB color based on agent profile.

    Real urine color range:
    - Very dilute (overhydrated): nearly clear, pale straw (R:240 G:235 B:200)
    - Normal hydrated: straw yellow (R:220 G:200 B:120)
    - Mildly dehydrated: dark yellow (R:200 G:170 B:60)
    - Dehydrated: amber (R:180 G:140 B:30)
    - Very dehydrated: dark amber/honey (R:160 G:110 B:20)

    Pregnancy effects (based on Layla 2019):
    - Slightly more red-shifted due to changed refractive index
    - Tends darker due to increased concentration from kidney changes
    """
    # Base hydration (0=very hydrated, 1=very dehydrated)
    hydration = profile["hydration"]

    # Morning urine is always more concentrated
    if profile["first_morning"]:
        hydration = min(1.0, hydration + 0.2)

    # Supplements affect color
    if profile["b_vitamins"]:
        # B vitamins make urine bright neon yellow
        hydration = max(0.0, hydration - 0.15)  # looks more dilute

    if profile["iron_supplement"]:
        # Iron can darken urine
        hydration = min(1.0, hydration + 0.1)

    # Base color interpolation
    r = int(240 - 80 * hydration + random.gauss(0, 5))
    g = int(235 - 125 * hydration + random.gauss(0, 5))
    b = int(200 - 180 * hydration + random.gauss(0, 5))

    # Pregnancy color shift
    if profile["pregnant"]:
        weeks = profile["weeks"]
        # More concentrated due to increased kidney filtration
        r = int(r - 5 - weeks * 0.3)
        g = int(g - 10 - weeks * 0.5)
        # Slight red shift (Layla spectral signature at 590-670nm)
        r = int(r + 3 + weeks * 0.15)
        # More amber tone
        b = int(b - 5 - weeks * 0.2)

    # B vitamin bright yellow boost
    if profile["b_vitamins"]:
        g = int(g + 20)
        r = int(r + 10)
        b = int(b - 10)

    # Clamp
    r = max(100, min(255, r))
    g = max(60, min(255, g))
    b = max(10, min(255, b))

    return (r, g, b)


def generate_synthetic_urine_image(profile, output_path):
    """
    Generate a synthetic urine-in-cup image.

    Creates a 512x512 image with:
    - White/light background (paper)
    - Clear plastic cup outline
    - Urine liquid with realistic color gradient
    - Optional foam/bubbles
    - Lighting variation
    """
    img = np.ones((512, 512, 3), dtype=np.uint8) * 255

    # Background with slight color temperature variation
    lighting = profile["lighting"]
    if lighting == "warm":
        bg = (245, 240, 230)  # warm indoor
    elif lighting == "cool_led":
        bg = (248, 250, 255)  # cool LED
    elif lighting == "natural":
        bg = (252, 252, 248)  # natural daylight
    else:
        bg = (240, 240, 240)  # mixed

    img[:] = bg

    # Add slight background texture (paper grain)
    noise = np.random.normal(0, 3, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Cup parameters
    cx, cy = 256, 280
    cup_w, cup_h = 130, 100
    fill_level = random.uniform(0.3, 0.8)  # How full the cup is

    # Draw cup outline (elliptical)
    # Cup body (trapezoid approximation with ellipses)
    top_w = cup_w + 15
    bot_w = cup_w - 10
    top_y = cy - cup_h
    bot_y = cy + cup_h

    # Cup body polygon
    pts = np.array([
        [cx - top_w, top_y],
        [cx + top_w, top_y],
        [cx + bot_w, bot_y],
        [cx - bot_w, bot_y],
    ], dtype=np.int32)

    # Fill cup body with transparent-ish clear plastic
    overlay = img.copy()
    cv2.fillPoly(overlay, [pts], (230, 235, 240))
    img = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)

    # Urine fill area
    urine_r, urine_g, urine_b = generate_urine_color(profile)
    fill_top = int(bot_y - (bot_y - top_y) * fill_level)

    # Width at fill level (linear interpolation)
    fill_ratio = (bot_y - fill_top) / (bot_y - top_y)
    fill_w = int(bot_w + (top_w - bot_w) * (1 - fill_ratio))

    urine_pts = np.array([
        [cx - fill_w, fill_top],
        [cx + fill_w, fill_top],
        [cx + bot_w, bot_y],
        [cx - bot_w, bot_y],
    ], dtype=np.int32)

    # Urine with slight gradient (darker at bottom)
    urine_overlay = img.copy()
    cv2.fillPoly(urine_overlay, [urine_pts], (urine_b, urine_g, urine_r))
    img = cv2.addWeighted(img, 0.35, urine_overlay, 0.65, 0)

    # Add depth gradient to urine
    for y_off in range(fill_top, bot_y):
        depth = (y_off - fill_top) / max(bot_y - fill_top, 1)
        darken = int(20 * depth)
        y_w = int(bot_w + (fill_w - bot_w) * (bot_y - y_off) / max(bot_y - fill_top, 1))
        for x_off in range(cx - y_w, cx + y_w):
            if 0 <= x_off < 512 and 0 <= y_off < 512:
                img[y_off, x_off, 0] = max(0, img[y_off, x_off, 0] - darken)
                img[y_off, x_off, 1] = max(0, img[y_off, x_off, 1] - darken)
                img[y_off, x_off, 2] = max(0, img[y_off, x_off, 2] - darken)

    # Cup outline
    cv2.polylines(img, [pts], True, (200, 200, 210), 2)

    # Top rim ellipse
    cv2.ellipse(img, (cx, top_y), (top_w, 15), 0, 0, 360, (190, 195, 200), 2)

    # Optional foam/bubbles (more common in pregnancy due to proteinuria)
    if profile.get("has_foam", False):
        n_bubbles = random.randint(3, 12)
        for _ in range(n_bubbles):
            bx = cx + random.randint(-fill_w + 10, fill_w - 10)
            by = fill_top + random.randint(2, 15)
            br = random.randint(2, 5)
            cv2.circle(img, (bx, by), br, (240, 240, 245), -1)
            cv2.circle(img, (bx, by), br, (210, 215, 220), 1)

    # Light reflection on cup
    cv2.ellipse(img, (cx - 50, cy - 30), (15, 40), -20, 0, 360, (250, 252, 255), -1)

    # Add slight blur (camera focus)
    blur_amount = random.choice([1, 3, 3, 5])
    if blur_amount > 1:
        img = cv2.GaussianBlur(img, (blur_amount, blur_amount), 0)

    # Shadow
    shadow = img.copy()
    shadow_pts = pts.copy()
    shadow_pts[:, 0] += 10
    shadow_pts[:, 1] += 5
    cv2.fillPoly(shadow, [shadow_pts], (180, 180, 185))
    mask = np.zeros((512, 512), dtype=np.uint8)
    cv2.fillPoly(mask, [shadow_pts], 255)
    cup_mask = np.zeros((512, 512), dtype=np.uint8)
    cv2.fillPoly(cup_mask, [pts], 255)
    shadow_only = cv2.bitwise_and(mask, cv2.bitwise_not(cup_mask))
    img[shadow_only > 0] = cv2.addWeighted(
        img[shadow_only > 0].reshape(-1, 1, 3), 0.85,
        shadow[shadow_only > 0].reshape(-1, 1, 3), 0.15, 0
    ).reshape(-1, 3)

    cv2.imwrite(output_path, img)
    return output_path


def create_agent_profiles(n=500):
    """Create 500 diverse agent profiles."""
    profiles = []

    # 250 pregnant
    for i in range(250):
        weeks = random.randint(4, 40)
        age = random.randint(18, 42)
        hydration = random.uniform(0.1, 0.9)

        profiles.append({
            "id": i + 1,
            "pregnant": True,
            "weeks": weeks,
            "trimester": 1 if weeks <= 13 else (2 if weeks <= 27 else 3),
            "age": age,
            "hydration": hydration,
            "first_morning": random.random() < 0.4,
            "b_vitamins": random.random() < 0.3,
            "iron_supplement": random.random() < 0.25,
            "folic_acid": random.random() < 0.7,
            "has_uti": random.random() < 0.08,
            "has_nausea": random.random() < (0.6 if weeks < 14 else 0.1),
            "has_foam": random.random() < (0.15 + weeks * 0.005),
            "lighting": random.choice(["natural", "cool_led", "warm", "mixed"]),
            "phone": random.choice(["iPhone 13", "iPhone 14", "Samsung S23", "Vivo", "Infinix", "Tecno", "Xiaomi"]),
            "cup_type": random.choice(["standard_clear", "other_clear"]),
            "fluids_2h": random.choice(["none", "1_cup", "2_3_cups", "4_plus"]),
            "coffee_4h": random.random() < 0.3,
        })

    # 250 not pregnant
    for i in range(250):
        age = random.randint(18, 50)
        hydration = random.uniform(0.05, 0.85)
        cycle_day = random.randint(1, 28)

        profiles.append({
            "id": 250 + i + 1,
            "pregnant": False,
            "weeks": 0,
            "trimester": 0,
            "age": age,
            "hydration": hydration,
            "cycle_day": cycle_day,
            "first_morning": random.random() < 0.4,
            "b_vitamins": random.random() < 0.2,
            "iron_supplement": random.random() < 0.1,
            "folic_acid": random.random() < 0.05,
            "has_uti": random.random() < 0.05,
            "has_nausea": False,
            "has_foam": random.random() < 0.05,
            "lighting": random.choice(["natural", "cool_led", "warm", "mixed"]),
            "phone": random.choice(["iPhone 13", "iPhone 14", "Samsung S23", "Vivo", "Infinix", "Tecno", "Xiaomi"]),
            "cup_type": random.choice(["standard_clear", "other_clear"]),
            "fluids_2h": random.choice(["none", "1_cup", "2_3_cups", "4_plus"]),
            "coffee_4h": random.random() < 0.4,
        })

    random.shuffle(profiles)
    return profiles


def send_to_api(image_path, api_url=API_URL):
    """Send image to API and return prediction."""
    try:
        if HAS_REQUESTS:
            with open(image_path, "rb") as f:
                resp = requests.post(api_url, files={"file": ("test.jpg", f, "image/jpeg")}, timeout=30)
            return resp.json()
        else:
            # urllib fallback
            import io
            boundary = "----SimBoundary" + str(random.randint(100000, 999999))
            with open(image_path, "rb") as f:
                file_data = f.read()

            body = (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="test.jpg"\r\n'
                f"Content-Type: image/jpeg\r\n\r\n"
            ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

            req = urllib.request.Request(
                api_url,
                data=body,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e), "probability": None}


def run_simulation(n=500, use_api=True, batch_size=10):
    """Run the full 500-agent simulation."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print(f"SIMULATION: {n} Agents")
    print("=" * 60)

    profiles = create_agent_profiles(n)
    results = []

    # Stats
    tp = fp = tn = fn = 0
    errors = 0

    for idx, profile in enumerate(profiles):
        agent_id = profile["id"]
        label = "pregnant" if profile["pregnant"] else "not_pregnant"
        img_path = os.path.join(OUTPUT_DIR, f"agent_{agent_id:04d}_{label}.jpg")

        # Generate image
        generate_synthetic_urine_image(profile, img_path)

        # Send to API or predict locally
        if use_api:
            result = send_to_api(img_path)
            prob = result.get("probability")
            model_tier = result.get("model_tier", "unknown")
            error = result.get("error")
        else:
            # Local prediction
            sys.path.insert(0, os.path.join(PROJECT_ROOT, "api"))
            from predict import extract_photo_features, predict_logistic

            with open(img_path, "rb") as f:
                features = extract_photo_features(f.read())

            with open(os.path.join(PROJECT_ROOT, "models", "model_photo_v2.json")) as f:
                model = json.load(f)

            prob = predict_logistic(model, features) if features else None
            model_tier = "Photo_V2_local"
            error = None if features else "extraction_failed"

        # Classify
        if prob is not None:
            predicted_positive = prob >= 0.5
            actual_positive = profile["pregnant"]

            if actual_positive and predicted_positive:
                tp += 1
            elif actual_positive and not predicted_positive:
                fn += 1
            elif not actual_positive and predicted_positive:
                fp += 1
            else:
                tn += 1
        else:
            errors += 1

        results.append({
            "agent_id": agent_id,
            "pregnant": profile["pregnant"],
            "weeks": profile["weeks"],
            "trimester": profile["trimester"],
            "age": profile["age"],
            "hydration": round(profile["hydration"], 2),
            "first_morning": profile["first_morning"],
            "b_vitamins": profile["b_vitamins"],
            "iron_supplement": profile["iron_supplement"],
            "lighting": profile["lighting"],
            "phone": profile["phone"],
            "has_foam": profile["has_foam"],
            "probability": round(prob, 4) if prob is not None else None,
            "predicted_positive": prob >= 0.5 if prob is not None else None,
            "correct": (prob >= 0.5) == profile["pregnant"] if prob is not None else None,
            "model_tier": model_tier,
            "error": error,
        })

        if (idx + 1) % 50 == 0 or (idx + 1) == n:
            total_done = tp + fp + tn + fn
            acc = (tp + tn) / total_done if total_done > 0 else 0
            print(f"  [{idx+1}/{n}] TP={tp} FP={fp} TN={tn} FN={fn} Acc={acc:.3f} Errors={errors}")

        # Rate limiting for API
        if use_api and (idx + 1) % batch_size == 0:
            time.sleep(1)

    # Save results
    fieldnames = list(results[0].keys())
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Final report
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0

    print("\n" + "=" * 60)
    print("SIMULATION RESULTS")
    print("=" * 60)
    print(f"Total agents:    {n}")
    print(f"API errors:      {errors}")
    print(f"")
    print(f"Confusion Matrix:")
    print(f"                 Predicted POS  Predicted NEG")
    print(f"  Actual POS     TP={tp:<12} FN={fn}")
    print(f"  Actual NEG     FP={fp:<12} TN={tn}")
    print(f"")
    print(f"Accuracy:        {accuracy:.4f} ({tp+tn}/{total})")
    print(f"Sensitivity:     {sensitivity:.4f} (TP/{tp+fn})")
    print(f"Specificity:     {specificity:.4f} (TN/{tn+fp})")
    print(f"PPV:             {ppv:.4f}")
    print(f"NPV:             {npv:.4f}")
    print(f"")
    print(f"Results saved:   {RESULTS_CSV}")
    print(f"Images saved:    {OUTPUT_DIR}/")
    print("=" * 60)
    print("Research use only. Experimental probability model. Not a diagnostic test.")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="Run locally instead of API")
    parser.add_argument("--n", type=int, default=500)
    args = parser.parse_args()

    run_simulation(n=args.n, use_api=not args.local)
