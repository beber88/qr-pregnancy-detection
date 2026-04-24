"""
Urine Visual Atlas — Comprehensive Synthetic Generator

Based on clinical literature:
- Armstrong 8-level hydration color scale (validated RGB)
- Layla et al. 2019: pregnancy refractive index shift at 590-670nm
- Simerville 2005: urine color clinical classification
- Spectrophotometric L*a*b* correlations with specific gravity

Generates photorealistic synthetic urine images covering ALL known
visual states, medications, conditions, hydration levels, and
pregnancy-specific changes.

Research use only. Experimental probability model. Not a diagnostic test.
"""

import random
import math
import numpy as np
import cv2


# ═══════════════════════════════════════════════════════════
# ARMSTRONG 8-LEVEL HYDRATION SCALE (validated RGB)
# ═══════════════════════════════════════════════════════════
ARMSTRONG_SCALE = {
    1: {"rgb": (255, 255, 199), "sg": 1.005, "desc": "optimal hydration, pale straw"},
    2: {"rgb": (255, 251, 186), "sg": 1.008, "desc": "normal hydration"},
    3: {"rgb": (255, 249, 164), "sg": 1.012, "desc": "normal, straw yellow"},
    4: {"rgb": (255, 232, 77),  "sg": 1.016, "desc": "mild dehydration, yellow"},
    5: {"rgb": (245, 227, 157), "sg": 1.020, "desc": "moderate dehydration"},
    6: {"rgb": (229, 201, 135), "sg": 1.024, "desc": "dehydrated, dark yellow"},
    7: {"rgb": (207, 159, 72),  "sg": 1.028, "desc": "severely dehydrated, amber"},
    8: {"rgb": (147, 140, 74),  "sg": 1.032, "desc": "extreme dehydration, brown-green"},
}

# ═══════════════════════════════════════════════════════════
# MEDICATION COLOR EFFECTS
# ═══════════════════════════════════════════════════════════
MEDICATION_EFFECTS = {
    "none":            {"r_shift": 0,   "g_shift": 0,   "b_shift": 0,   "prob": 0.50},
    "b_vitamins":      {"r_shift": 10,  "g_shift": 30,  "b_shift": -20, "prob": 0.15,
                        "desc": "riboflavin fluorescent yellow-green"},
    "iron":            {"r_shift": -5,  "g_shift": -15, "b_shift": -10, "prob": 0.10,
                        "desc": "darker yellow from iron oxidation"},
    "folic_acid":      {"r_shift": 5,   "g_shift": 5,   "b_shift": -5,  "prob": 0.12,
                        "desc": "slight yellow intensification"},
    "prenatal_multi":  {"r_shift": 8,   "g_shift": 20,  "b_shift": -15, "prob": 0.08,
                        "desc": "combined B2+iron effect"},
    "phenazopyridine": {"r_shift": 60,  "g_shift": -20, "b_shift": -80, "prob": 0.02,
                        "desc": "bright orange UTI medication"},
    "rifampin":        {"r_shift": 50,  "g_shift": -30, "b_shift": -60, "prob": 0.01,
                        "desc": "reddish-orange TB medication"},
    "metronidazole":   {"r_shift": -30, "g_shift": -40, "b_shift": -20, "prob": 0.01,
                        "desc": "dark brown antibiotic"},
    "calcium":         {"r_shift": 0,   "g_shift": 0,   "b_shift": 0,   "prob": 0.05,
                        "desc": "no visible effect"},
    "progesterone":    {"r_shift": 2,   "g_shift": -3,  "b_shift": -2,  "prob": 0.03,
                        "desc": "minimal effect, slight concentration"},
}

# ═══════════════════════════════════════════════════════════
# FOOD EFFECTS
# ═══════════════════════════════════════════════════════════
FOOD_EFFECTS = {
    "none":      {"r_shift": 0,  "g_shift": 0,   "b_shift": 0,   "prob": 0.70},
    "beets":     {"r_shift": 40, "g_shift": -30, "b_shift": -10, "prob": 0.05,
                  "desc": "pink-red betanin, affects 10-14% of people"},
    "asparagus": {"r_shift": -5, "g_shift": 10,  "b_shift": 5,   "prob": 0.05,
                  "desc": "slight greenish tinge"},
    "carrots":   {"r_shift": 20, "g_shift": 5,   "b_shift": -15, "prob": 0.05,
                  "desc": "orange from beta-carotene"},
    "coffee":    {"r_shift": -5, "g_shift": -8,  "b_shift": -5,  "prob": 0.10,
                  "desc": "slightly darker, diuretic effect"},
    "turmeric":  {"r_shift": 15, "g_shift": 10,  "b_shift": -20, "prob": 0.03,
                  "desc": "deep yellow from curcumin"},
    "berries":   {"r_shift": 10, "g_shift": -5,  "b_shift": 5,   "prob": 0.02,
                  "desc": "slight reddish tinge from anthocyanins"},
}

# ═══════════════════════════════════════════════════════════
# MEDICAL CONDITIONS
# ═══════════════════════════════════════════════════════════
MEDICAL_CONDITIONS = {
    "healthy":          {"r_shift": 0,   "g_shift": 0,   "b_shift": 0,
                         "turbidity": 0, "foam": 0, "prob": 0.80},
    "uti_mild":         {"r_shift": 0,   "g_shift": -5,  "b_shift": -3,
                         "turbidity": 0.3, "foam": 0.1, "prob": 0.06},
    "uti_moderate":     {"r_shift": 5,   "g_shift": -10, "b_shift": -5,
                         "turbidity": 0.6, "foam": 0.2, "prob": 0.03},
    "proteinuria_mild": {"r_shift": 0,   "g_shift": -2,  "b_shift": -2,
                         "turbidity": 0.1, "foam": 0.4, "prob": 0.04},
    "proteinuria_mod":  {"r_shift": 0,   "g_shift": -5,  "b_shift": -5,
                         "turbidity": 0.2, "foam": 0.7, "prob": 0.02},
    "glycosuria":       {"r_shift": 5,   "g_shift": 5,   "b_shift": -5,
                         "turbidity": 0, "foam": 0.05, "prob": 0.02},
    "hematuria_micro":  {"r_shift": 15,  "g_shift": -10, "b_shift": -5,
                         "turbidity": 0.1, "foam": 0.05, "prob": 0.02},
    "hematuria_gross":  {"r_shift": 60,  "g_shift": -50, "b_shift": -30,
                         "turbidity": 0.4, "foam": 0.1, "prob": 0.005},
    "liver_bilirubinuria": {"r_shift": -10, "g_shift": -20, "b_shift": -30,
                         "turbidity": 0.2, "foam": 0.3, "prob": 0.005},
}

# ═══════════════════════════════════════════════════════════
# PREGNANCY-SPECIFIC SPECTRAL CHANGES (Layla 2019)
# ═══════════════════════════════════════════════════════════
# Refractive index change: +0.0004 above normal
# Absorbance shift at 590-670nm (overlaps RGB R-channel)
# Effect scales with gestational age and hormone levels

def pregnancy_spectral_shift(weeks, trimester):
    """
    Model the Layla 2019 spectral signature.
    590-670nm absorbance change -> R-channel shift.
    Refractive index: normal ~1.333, pregnant 1.3386-1.3426.
    """
    if weeks == 0:
        return {"r_shift": 0, "g_shift": 0, "b_shift": 0, "ri_delta": 0}

    # hCG peaks at week 10-12, then plateaus
    hcg_factor = min(1.0, weeks / 12) if weeks <= 12 else 0.8

    # Estrogen/progesterone rise continuously
    hormone_factor = min(1.0, weeks / 30)

    # Combined spectral effect
    # R-channel: slight increase from 590-670nm absorbance
    r_shift = 3 + 5 * hcg_factor + 3 * hormone_factor
    # G-channel: slight decrease (complementary)
    g_shift = -2 - 3 * hormone_factor
    # B-channel: decrease from concentration + spectral
    b_shift = -3 - 4 * hormone_factor

    # Add concentration effect (kidneys filter 50% more in pregnancy)
    # This leads to either MORE dilute (if drinking enough) or MORE concentrated
    concentration_shift = random.gauss(0, 5)

    # Refractive index delta
    ri_delta = 0.0004 * hormone_factor + random.gauss(0, 0.0001)

    return {
        "r_shift": r_shift + concentration_shift * 0.3,
        "g_shift": g_shift + concentration_shift * -0.5,
        "b_shift": b_shift + concentration_shift * -0.3,
        "ri_delta": ri_delta,
    }


# ═══════════════════════════════════════════════════════════
# LIGHTING CONDITIONS (affect white balance)
# ═══════════════════════════════════════════════════════════
LIGHTING_PROFILES = {
    "natural_daylight":  {"bg": (252, 252, 248), "cct": 5500, "prob": 0.25,
                          "wb_r": 1.0, "wb_g": 1.0, "wb_b": 1.0},
    "natural_window":    {"bg": (248, 250, 255), "cct": 6500, "prob": 0.15,
                          "wb_r": 0.95, "wb_g": 0.98, "wb_b": 1.05},
    "cool_led":          {"bg": (245, 248, 255), "cct": 6000, "prob": 0.20,
                          "wb_r": 0.96, "wb_g": 0.99, "wb_b": 1.04},
    "warm_indoor":       {"bg": (255, 248, 235), "cct": 3500, "prob": 0.15,
                          "wb_r": 1.06, "wb_g": 1.0,  "wb_b": 0.90},
    "warm_tungsten":     {"bg": (255, 240, 220), "cct": 2700, "prob": 0.08,
                          "wb_r": 1.10, "wb_g": 0.98, "wb_b": 0.85},
    "fluorescent":       {"bg": (248, 255, 248), "cct": 4100, "prob": 0.07,
                          "wb_r": 0.98, "wb_g": 1.02, "wb_b": 0.95},
    "mixed":             {"bg": (245, 245, 240), "cct": 4500, "prob": 0.05,
                          "wb_r": 1.02, "wb_g": 1.0,  "wb_b": 0.96},
    "dim_bathroom":      {"bg": (220, 215, 210), "cct": 3000, "prob": 0.03,
                          "wb_r": 1.05, "wb_g": 0.98, "wb_b": 0.88},
    "harsh_overhead":    {"bg": (255, 255, 255), "cct": 5000, "prob": 0.02,
                          "wb_r": 1.0, "wb_g": 1.0,  "wb_b": 1.0},
}

# ═══════════════════════════════════════════════════════════
# CAMERA / PHONE CHARACTERISTICS
# ═══════════════════════════════════════════════════════════
PHONE_PROFILES = {
    "iPhone_13":     {"noise": 2,  "sharpness": 0.9, "color_accuracy": 0.95, "prob": 0.12},
    "iPhone_14":     {"noise": 1.5,"sharpness": 0.95,"color_accuracy": 0.96, "prob": 0.10},
    "iPhone_15":     {"noise": 1.5,"sharpness": 0.95,"color_accuracy": 0.97, "prob": 0.08},
    "Samsung_S23":   {"noise": 2,  "sharpness": 0.92,"color_accuracy": 0.93, "prob": 0.08},
    "Samsung_A54":   {"noise": 3,  "sharpness": 0.85,"color_accuracy": 0.88, "prob": 0.06},
    "Xiaomi_13":     {"noise": 2.5,"sharpness": 0.88,"color_accuracy": 0.90, "prob": 0.06},
    "Xiaomi_Redmi":  {"noise": 4,  "sharpness": 0.80,"color_accuracy": 0.85, "prob": 0.08},
    "Vivo_Y36":      {"noise": 3.5,"sharpness": 0.82,"color_accuracy": 0.86, "prob": 0.06},
    "Infinix_Hot30":{"noise": 4.5,"sharpness": 0.78,"color_accuracy": 0.83, "prob": 0.06},
    "Tecno_Spark10": {"noise": 4,  "sharpness": 0.80,"color_accuracy": 0.84, "prob": 0.06},
    "Oppo_A78":      {"noise": 3,  "sharpness": 0.85,"color_accuracy": 0.88, "prob": 0.05},
    "Huawei_Nova":   {"noise": 2.5,"sharpness": 0.87,"color_accuracy": 0.89, "prob": 0.04},
    "Google_Pixel7": {"noise": 1.5,"sharpness": 0.93,"color_accuracy": 0.95, "prob": 0.04},
    "Motorola_G":    {"noise": 4,  "sharpness": 0.79,"color_accuracy": 0.84, "prob": 0.05},
    "old_android":   {"noise": 6,  "sharpness": 0.70,"color_accuracy": 0.78, "prob": 0.06},
}

# ═══════════════════════════════════════════════════════════
# CUP TYPES
# ═══════════════════════════════════════════════════════════
CUP_TYPES = {
    "standard_clear_small": {"w": 100, "h": 80,  "tint_r": 0, "tint_g": 0, "tint_b": 0},
    "standard_clear_med":   {"w": 130, "h": 100, "tint_r": 0, "tint_g": 0, "tint_b": 0},
    "standard_clear_large": {"w": 150, "h": 120, "tint_r": 0, "tint_g": 0, "tint_b": 0},
    "specimen_cup":         {"w": 80,  "h": 90,  "tint_r": 0, "tint_g": 0, "tint_b": 0},
    "slightly_blue_tint":   {"w": 130, "h": 100, "tint_r": -5,"tint_g": -3,"tint_b": 5},
    "slightly_green_tint":  {"w": 130, "h": 100, "tint_r": -5,"tint_g": 5, "tint_b": -3},
}

# ═══════════════════════════════════════════════════════════
# ANGLE / PERSPECTIVE VARIATIONS
# ═══════════════════════════════════════════════════════════
CAMERA_ANGLES = {
    "top_down":     {"cy_offset": -40, "scale_y": 0.7, "prob": 0.30},
    "eye_level":    {"cy_offset": 0,   "scale_y": 1.0, "prob": 0.25},
    "slight_above": {"cy_offset": -20, "scale_y": 0.85,"prob": 0.30},
    "slight_below": {"cy_offset": 15,  "scale_y": 1.1, "prob": 0.10},
    "angled_side":  {"cy_offset": 5,   "scale_y": 0.95,"prob": 0.05},
}


def weighted_choice(options_dict):
    """Choose from dict with 'prob' weights."""
    items = list(options_dict.items())
    weights = [v.get("prob", 1.0 / len(items)) for _, v in items]
    total = sum(weights)
    weights = [w / total for w in weights]
    idx = np.random.choice(len(items), p=weights)
    return items[idx]


def compute_urine_rgb(armstrong_level, pregnancy_shift, medication, food, condition, lighting):
    """Compute final urine RGB from all factors."""
    base = ARMSTRONG_SCALE[armstrong_level]["rgb"]
    r, g, b = float(base[0]), float(base[1]), float(base[2])

    # Pregnancy spectral shift
    r += pregnancy_shift["r_shift"]
    g += pregnancy_shift["g_shift"]
    b += pregnancy_shift["b_shift"]

    # Medication
    r += medication.get("r_shift", 0)
    g += medication.get("g_shift", 0)
    b += medication.get("b_shift", 0)

    # Food
    r += food.get("r_shift", 0)
    g += food.get("g_shift", 0)
    b += food.get("b_shift", 0)

    # Medical condition
    r += condition.get("r_shift", 0)
    g += condition.get("g_shift", 0)
    b += condition.get("b_shift", 0)

    # White balance from lighting
    r *= lighting.get("wb_r", 1.0)
    g *= lighting.get("wb_g", 1.0)
    b *= lighting.get("wb_b", 1.0)

    # Natural variation
    r += random.gauss(0, 3)
    g += random.gauss(0, 3)
    b += random.gauss(0, 3)

    return (
        max(40, min(255, int(r))),
        max(20, min(255, int(g))),
        max(5,  min(255, int(b))),
    )


def generate_comprehensive_image(profile, output_path):
    """Generate a photorealistic synthetic urine image with all factors."""
    # Resolve all factors
    lighting_name, lighting = weighted_choice(LIGHTING_PROFILES)
    phone_name, phone = weighted_choice(PHONE_PROFILES)
    angle_name, angle = weighted_choice(CAMERA_ANGLES)
    cup_name = random.choice(list(CUP_TYPES.keys()))
    cup = CUP_TYPES[cup_name]

    # Armstrong level from hydration
    hydration = profile["hydration"]
    if profile.get("first_morning", False):
        hydration = min(1.0, hydration + 0.2)
    armstrong_level = max(1, min(8, int(1 + hydration * 7)))

    # Pregnancy shift
    preg_shift = pregnancy_spectral_shift(
        profile.get("weeks", 0),
        profile.get("trimester", 0)
    )

    # Medication
    med_name = profile.get("medication", "none")
    medication = MEDICATION_EFFECTS.get(med_name, MEDICATION_EFFECTS["none"])

    # Food
    food_name = profile.get("food_effect", "none")
    food = FOOD_EFFECTS.get(food_name, FOOD_EFFECTS["none"])

    # Condition
    cond_name = profile.get("condition", "healthy")
    condition = MEDICAL_CONDITIONS.get(cond_name, MEDICAL_CONDITIONS["healthy"])

    # Final color
    urine_r, urine_g, urine_b = compute_urine_rgb(
        armstrong_level, preg_shift, medication, food, condition, lighting
    )

    # ─── Build image ───
    size = 512
    img = np.ones((size, size, 3), dtype=np.uint8)
    bg = lighting["bg"]
    img[:] = bg

    # Background texture (paper/surface variation)
    noise_level = phone["noise"]
    noise = np.random.normal(0, noise_level, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Cup geometry
    cx = 256 + random.randint(-20, 20)
    cy = 280 + angle["cy_offset"] + random.randint(-10, 10)
    cup_w = cup["w"] + random.randint(-10, 10)
    cup_h = int(cup["h"] * angle["scale_y"]) + random.randint(-5, 5)
    fill_level = random.uniform(0.25, 0.85)

    top_w = cup_w + 15
    bot_w = cup_w - 10
    top_y = cy - cup_h
    bot_y = cy + cup_h

    pts = np.array([
        [cx - top_w, top_y], [cx + top_w, top_y],
        [cx + bot_w, bot_y], [cx - bot_w, bot_y],
    ], dtype=np.int32)

    # Cup body (transparent plastic with tint)
    overlay = img.copy()
    cup_color = (230 + cup["tint_b"], 235 + cup["tint_g"], 240 + cup["tint_r"])
    cv2.fillPoly(overlay, [pts], cup_color)
    img = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)

    # Urine fill
    fill_top = int(bot_y - (bot_y - top_y) * fill_level)
    fill_ratio = (bot_y - fill_top) / max(bot_y - top_y, 1)
    fill_w = int(bot_w + (top_w - bot_w) * (1 - fill_ratio))

    urine_pts = np.array([
        [cx - fill_w, fill_top], [cx + fill_w, fill_top],
        [cx + bot_w, bot_y], [cx - bot_w, bot_y],
    ], dtype=np.int32)

    # Main urine fill with depth gradient
    urine_overlay = img.copy()
    cv2.fillPoly(urine_overlay, [urine_pts], (urine_b, urine_g, urine_r))
    img = cv2.addWeighted(img, 0.3, urine_overlay, 0.7, 0)

    # Depth gradient (darker at bottom)
    for y_off in range(max(0, fill_top), min(size, bot_y)):
        depth = (y_off - fill_top) / max(bot_y - fill_top, 1)
        darken = int(25 * depth)
        y_w = int(bot_w + (fill_w - bot_w) * (bot_y - y_off) / max(bot_y - fill_top, 1))
        x_start = max(0, cx - y_w)
        x_end = min(size, cx + y_w)
        img[y_off, x_start:x_end] = np.clip(
            img[y_off, x_start:x_end].astype(np.int16) - darken, 0, 255
        ).astype(np.uint8)

    # Turbidity (cloudy appearance)
    turbidity = condition.get("turbidity", 0)
    if turbidity > 0:
        turb_noise = np.random.normal(0, turbidity * 15, (size, size, 3)).astype(np.int16)
        mask = np.zeros((size, size), dtype=np.uint8)
        cv2.fillPoly(mask, [urine_pts], 255)
        for c in range(3):
            channel = img[:, :, c].astype(np.int16) + turb_noise[:, :, c]
            img[:, :, c] = np.clip(channel, 0, 255).astype(np.uint8) * (mask > 0).astype(np.uint8) + \
                           img[:, :, c] * (mask == 0).astype(np.uint8)

    # Foam/bubbles
    foam_prob = condition.get("foam", 0) + profile.get("foam_extra", 0)
    if foam_prob > 0 and random.random() < foam_prob:
        n_bubbles = random.randint(2, int(5 + foam_prob * 20))
        for _ in range(n_bubbles):
            bx = cx + random.randint(-fill_w + 15, fill_w - 15)
            by = fill_top + random.randint(2, 20)
            br = random.randint(2, max(3, int(4 + foam_prob * 3)))
            if 0 <= bx < size and 0 <= by < size:
                cv2.circle(img, (bx, by), br, (240, 240, 245), -1)
                cv2.circle(img, (bx, by), br, (210, 215, 220), 1)

    # Cup outline and rim
    cv2.polylines(img, [pts], True, (195, 200, 210), 2)
    cv2.ellipse(img, (cx, top_y), (top_w, 15), 0, 0, 360, (185, 190, 200), 2)

    # Light reflection
    ref_x = cx - random.randint(30, 60)
    ref_y = cy - random.randint(10, 40)
    cv2.ellipse(img, (ref_x, ref_y), (12, 35), random.randint(-30, 30), 0, 360, (248, 250, 252), -1)

    # Shadow
    shadow_pts = pts.copy()
    shadow_pts[:, 0] += random.randint(5, 15)
    shadow_pts[:, 1] += random.randint(3, 8)
    shadow_mask = np.zeros((size, size), dtype=np.uint8)
    cv2.fillPoly(shadow_mask, [shadow_pts], 255)
    cup_mask = np.zeros((size, size), dtype=np.uint8)
    cv2.fillPoly(cup_mask, [pts], 255)
    shadow_only = cv2.bitwise_and(shadow_mask, cv2.bitwise_not(cup_mask))
    img[shadow_only > 0] = np.clip(
        img[shadow_only > 0].astype(np.int16) - 20, 0, 255
    ).astype(np.uint8)

    # Camera blur (phone quality)
    blur = max(1, int(3 + (1 - phone["sharpness"]) * 6))
    if blur > 1 and blur % 2 == 0:
        blur += 1
    img = cv2.GaussianBlur(img, (blur, blur), 0)

    # JPEG compression artifacts (simulates low-quality phones)
    quality = max(60, int(95 - noise_level * 5))
    _, encoded = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    img = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

    cv2.imwrite(output_path, img)

    return {
        "armstrong_level": armstrong_level,
        "urine_rgb": (urine_r, urine_g, urine_b),
        "specific_gravity": ARMSTRONG_SCALE[armstrong_level]["sg"],
        "lighting": lighting_name,
        "phone": phone_name,
        "angle": angle_name,
        "cup": cup_name,
        "medication": med_name,
        "food": food_name,
        "condition": cond_name,
        "turbidity": turbidity,
        "pregnancy_ri_delta": preg_shift.get("ri_delta", 0),
    }
