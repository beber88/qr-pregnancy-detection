"""
Simulation V2 — 500 Agents with Comprehensive Urine Atlas

Uses clinical-grade urine visual parameters from medical literature.
Generates diverse profiles and tests through the prediction engine.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import os
import sys
import json
import csv
import random
import time
from datetime import datetime

import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urine_atlas import (
    MEDICATION_EFFECTS, FOOD_EFFECTS, MEDICAL_CONDITIONS,
    generate_comprehensive_image, weighted_choice
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "simulated_v2")
RESULTS_CSV = os.path.join(OUTPUT_DIR, "simulation_v2_results.csv")


def create_comprehensive_profiles(n=500):
    """Create 500 profiles covering ALL known urine visual states."""
    profiles = []

    # 250 pregnant across all trimesters
    for i in range(250):
        weeks = random.choices(
            range(4, 41),
            weights=[3]*9 + [2]*14 + [1]*14,  # More early pregnancy
            k=1
        )[0]
        trimester = 1 if weeks <= 13 else (2 if weeks <= 27 else 3)
        age = random.randint(16, 45)
        hydration = random.betavariate(2, 3)  # Skewed toward hydrated

        # Pick medication by weighted probability
        med_name, _ = weighted_choice(MEDICATION_EFFECTS)
        food_name, _ = weighted_choice(FOOD_EFFECTS)
        cond_name, _ = weighted_choice(MEDICAL_CONDITIONS)

        # Pregnancy-specific conditions
        if random.random() < 0.08:
            cond_name = "proteinuria_mild"  # Preeclampsia risk
        if random.random() < 0.12 and weeks > 20:
            cond_name = "glycosuria"  # Gestational diabetes

        profiles.append({
            "id": i + 1,
            "pregnant": True,
            "weeks": weeks,
            "trimester": trimester,
            "age": age,
            "hydration": round(hydration, 3),
            "first_morning": random.random() < 0.4,
            "medication": med_name,
            "food_effect": food_name,
            "condition": cond_name,
            "foam_extra": 0.1 + weeks * 0.005,
            "fluids_2h": random.choice(["none", "1_cup", "2_3_cups", "4_plus"]),
            "coffee_4h": random.random() < 0.25,
            "exercise_today": random.random() < 0.15,
            "bmi": random.choice(["underweight", "normal", "overweight", "obese"]),
        })

    # 250 not pregnant
    for i in range(250):
        age = random.randint(16, 55)
        hydration = random.betavariate(2, 3)
        cycle_day = random.randint(1, 28)

        med_name, _ = weighted_choice(MEDICATION_EFFECTS)
        food_name, _ = weighted_choice(FOOD_EFFECTS)
        cond_name, _ = weighted_choice(MEDICAL_CONDITIONS)

        profiles.append({
            "id": 250 + i + 1,
            "pregnant": False,
            "weeks": 0,
            "trimester": 0,
            "age": age,
            "hydration": round(hydration, 3),
            "cycle_day": cycle_day,
            "first_morning": random.random() < 0.4,
            "medication": med_name,
            "food_effect": food_name,
            "condition": cond_name,
            "foam_extra": 0.02,
            "fluids_2h": random.choice(["none", "1_cup", "2_3_cups", "4_plus"]),
            "coffee_4h": random.random() < 0.4,
            "exercise_today": random.random() < 0.25,
            "bmi": random.choice(["underweight", "normal", "overweight", "obese"]),
        })

    random.shuffle(profiles)
    return profiles


def run_simulation(n=500, use_api=False):
    """Run comprehensive simulation."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print(f"SIMULATION V2: {n} Agents (Comprehensive Urine Atlas)")
    print("=" * 60)

    profiles = create_comprehensive_profiles(n)

    # Load prediction model
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "api"))
    from predict import extract_photo_features, predict_logistic

    with open(os.path.join(PROJECT_ROOT, "models", "model_photo_v2.json")) as f:
        model = json.load(f)

    results = []
    tp = fp = tn = fn = errors = 0
    all_probs_pos = []
    all_probs_neg = []

    for idx, profile in enumerate(profiles):
        agent_id = profile["id"]
        label = "pregnant" if profile["pregnant"] else "not_pregnant"
        img_path = os.path.join(OUTPUT_DIR, f"agent_{agent_id:04d}_{label}.jpg")

        # Generate comprehensive image
        img_meta = generate_comprehensive_image(profile, img_path)

        # Predict
        with open(img_path, "rb") as f:
            features = extract_photo_features(f.read())

        if features:
            prob = predict_logistic(model, features)
        else:
            prob = None
            errors += 1

        if prob is not None:
            predicted_positive = prob >= 0.5
            actual_positive = profile["pregnant"]

            if actual_positive and predicted_positive: tp += 1
            elif actual_positive and not predicted_positive: fn += 1
            elif not actual_positive and predicted_positive: fp += 1
            else: tn += 1

            if actual_positive:
                all_probs_pos.append(prob)
            else:
                all_probs_neg.append(prob)

        results.append({
            "agent_id": agent_id,
            "pregnant": profile["pregnant"],
            "weeks": profile["weeks"],
            "trimester": profile["trimester"],
            "age": profile["age"],
            "hydration": profile["hydration"],
            "first_morning": profile["first_morning"],
            "medication": profile["medication"],
            "food_effect": profile["food_effect"],
            "condition": profile["condition"],
            "armstrong_level": img_meta["armstrong_level"],
            "specific_gravity": img_meta["specific_gravity"],
            "lighting": img_meta["lighting"],
            "phone": img_meta["phone"],
            "angle": img_meta["angle"],
            "urine_r": img_meta["urine_rgb"][0],
            "urine_g": img_meta["urine_rgb"][1],
            "urine_b": img_meta["urine_rgb"][2],
            "probability": round(prob, 4) if prob is not None else None,
            "predicted_positive": prob >= 0.5 if prob is not None else None,
            "correct": (prob >= 0.5) == profile["pregnant"] if prob is not None else None,
            "error": None if prob is not None else "extraction_failed",
        })

        if (idx + 1) % 50 == 0 or (idx + 1) == n:
            total_done = tp + fp + tn + fn
            acc = (tp + tn) / total_done if total_done > 0 else 0
            print(f"  [{idx+1}/{n}] TP={tp} FP={fp} TN={tn} FN={fn} Acc={acc:.3f}")

    # Save
    fieldnames = list(results[0].keys())
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Stats
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    # AUC calculation
    from sklearn.metrics import roc_auc_score
    y_true = [1] * len(all_probs_pos) + [0] * len(all_probs_neg)
    y_score = all_probs_pos + all_probs_neg
    try:
        auc = roc_auc_score(y_true, y_score)
    except:
        auc = 0

    print("\n" + "=" * 60)
    print("SIMULATION V2 RESULTS")
    print("=" * 60)
    print(f"Total agents:    {n}")
    print(f"Errors:          {errors}")
    print(f"")
    print(f"Confusion Matrix (threshold=0.5):")
    print(f"                 Predicted POS  Predicted NEG")
    print(f"  Actual POS     TP={tp:<12} FN={fn}")
    print(f"  Actual NEG     FP={fp:<12} TN={tn}")
    print(f"")
    print(f"Accuracy:        {accuracy:.4f}")
    print(f"Sensitivity:     {sensitivity:.4f}")
    print(f"Specificity:     {specificity:.4f}")
    print(f"AUC:             {auc:.4f}")
    print(f"")
    print(f"Probability Distribution:")
    print(f"  Pregnant:     mean={np.mean(all_probs_pos):.4f} std={np.std(all_probs_pos):.4f}")
    print(f"  Not pregnant: mean={np.mean(all_probs_neg):.4f} std={np.std(all_probs_neg):.4f}")
    print(f"  Separation:   {np.mean(all_probs_pos) - np.mean(all_probs_neg):.4f}")
    print(f"")
    print(f"Results: {RESULTS_CSV}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    run_simulation(n=500)
