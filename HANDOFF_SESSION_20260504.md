# HANDOFF SESSION - May 4, 2026
## Survey Extraction COMPLETE + V6 Model Training + Leakage Discovery

---

## STATUS

### Survey Metadata Extraction - ALL 101 SUBJECTS COMPLETE
- **ALL subjects now have survey data** (old format P1-P34/P41/N1-N28 + new format P42-P52/N31-N60)
- Complete survey: `data/processed/survey_metadata_complete.csv` (101 rows)
- Positive surveys: `data/processed/survey_metadata_positive_new.csv` (11 rows)
- Negative surveys: `data/processed/survey_metadata_negative_new.csv` (30 rows)
- Combined: `data/processed/survey_metadata_all_new.csv` (41 rows, with binary features)

### Model V6 (Pure Urine Signal) - CURRENT PRODUCTION
- **AUC = 0.749** (5-fold GroupKFold, 101 subjects, N57 excluded)
- Sensitivity = 0.602, Specificity = 0.734
- Saved: `models/model_production_v6.pkl`
- Features: 221 photo+video (rich aggregation: mean/std/min/max/cv/range per subject + interaction features)
- **NO survey features** (see leakage discovery below)

### Model V6 Fusion (Late Fusion) - BEST QUALITY VARIANT
- **AUC = 0.770** (5-fold GroupKFold, 68 subjects with video, N57 excluded)
- Sensitivity = 0.694, Specificity = 0.713
- **Lowest variance: std = 0.043** (most stable across folds)
- Per-fold: [0.833, 0.735, 0.750, 0.810, 0.725]
- Architecture: 0.7 * photo_model + 0.3 * video_model (late fusion)
- Saved: `models/model_v6_fusion.pkl`
- Only works for subjects with both photo AND video data

---

## CRITICAL DISCOVERY: V5 Survey Feature Leakage (Session 2)

### What happened
V5 (AUC=0.774) included 5 "confounder control" survey features: age, first_morning, coffee, fluids, health_condition. These were intended to help the model account for non-pregnancy factors.

### Why it was wrong
The old survey format (P1-P34, P41, N1-N28 = 61 subjects) didn't capture age, coffee, first_morning — these fields defaulted to 0. The new survey format (P42-P52, N31-N60 = 40 subjects) did capture them.

Result:
- **21/46 positive** subjects have age=0 (old format)
- **Only 3/55 negative** subjects have age=0
- The model learned `age=0` → likely positive, which is really `old survey format → likely positive`
- Same pattern for coffee (2/46 pos vs 21/55 neg) and first_morning

**V5's AUC=0.774 was inflated by ~0.03 from this format-artifact leakage.**

### The honest numbers
When survey features are excluded entirely:
- V4 (urine only, mean aggregation): AUC = 0.739
- V6 (urine only, rich aggregation + interactions): AUC = 0.749
- V6 fusion (photo + video late fusion, 68 subjects): AUC = 0.770

The actual improvement from rich aggregation and interaction features: **+0.010 AUC** (0.739 → 0.749).

---

## CRITICAL FLAG: N57 POSSIBLY MISLABELED (STILL UNRESOLVED)

Subject NEGATIVE_57 checked "Confirmed pregnant (blood test or ultrasound)" in Section 1, BUT:
- Under confirmation method, only "Home urine test only" is checked (NOT blood test or ultrasound)
- Weeks of pregnancy left BLANK
- Takes folic acid + calcium (consistent with prenatal care)
- Age 20, no health conditions
- Folder is in NEGATIVE/57/

Contradictory form: self-identified as confirmed pregnant, but only confirmation is home urine test. Same ambiguity as N22→P41.

**N57 is currently EXCLUDED from all V6 models.**

Options:
- A: Reclassify to P53 (treat as pregnant)
- B: Exclude permanently
- C: Keep as negative

---

## MODEL PERFORMANCE HISTORY

| Date | Model | Subjects | AUC | Sens | Spec | Notes |
|------|-------|----------|-----|------|------|-------|
| Apr 30 | Video RF (V1) | 61 | 0.825 | 0.865 | 0.480 | Overfit, low specificity |
| May 3 | Ensemble (V3) | 102 | 0.854* | 0.810 | 0.619 | *Non-reproducible fold split |
| May 4 | Urine only (V4) | 101 | 0.739 | 0.630 | 0.764 | Pure urine, mean aggregation |
| May 4 | Urine+survey (V5) | 101 | 0.774 | 0.652 | 0.782 | **Survey format leakage** |
| May 4 | Leaky (V5) | 101 | 0.907 | 0.761 | 0.873 | INVALID (label leakage) |
| **May 4** | **V6 production** | **101** | **0.749** | **0.602** | **0.734** | **Honest, rich aggregation** |
| **May 4** | **V6 fusion** | **68** | **0.770** | **0.694** | **0.713** | **Best: 0.7P+0.3V, std=0.043** |

### V6 Training Experiments (15 configurations tested)
| Model | AUC | ±std | Note |
|-------|-----|------|------|
| GBM_mutinfo_k90 + survey | 0.799 | 0.086 | Survey leakage — INVALID |
| GBM_d2_lr05_k50 (no survey) | 0.741 | 0.085 | Best single-model urine-only |
| Late fusion 0.7P/0.3V | 0.770 | 0.043 | Best overall (68 subjects) |
| XGBoost k30 | 0.714 | 0.098 | No advantage over GBM |
| Photo-only | 0.701 | 0.077 | |
| Video-only | 0.685 | 0.073 | |

### Key finding: Mutual information > f_classif
Mutual information feature selection consistently outperformed ANOVA f_classif:
- MI k=50: AUC=0.736 vs f_classif k=50: AUC=0.693
- MI captures non-linear relationships between features and labels

---

## TOP 20 FEATURES (V6, urine only)

| Rank | Feature | Importance | Type |
|------|---------|------------|------|
| 1 | edge_intensity_max | 0.0947 | Photo texture |
| 2 | t_r_ratio_complexity | 0.0897 | Video temporal |
| 3 | turbidity_mean | 0.0573 | Photo clarity |
| 4 | color_variance_min | 0.0487 | Photo color |
| 5 | t_layla_r_autocorr | 0.0478 | Video spectral |
| 6 | ix_r_mean_std_x_b_mean_std | 0.0476 | Interaction (new) |
| 7 | edge_intensity_std | 0.0435 | Photo texture var |
| 8 | layla_r_ratio_std_min | 0.0313 | Photo spectral |
| 9 | t_hue_mean | 0.0288 | Video color |
| 10 | b_mean_min | 0.0270 | Photo blue |

**Key insight (V6)**: Edge intensity (texture) and video temporal complexity are the strongest genuine urine features. The interaction feature `r_mean_std * b_mean_std` (red-blue variability interaction) ranked #6 — suggesting that the joint variability across color channels within a subject carries signal.

---

## SURVEY DATA SUMMARY

### Negative Subjects (N31-N60) Key Findings

| Statistic | Value |
|-----------|-------|
| Age range | 19-36 |
| Mean age | 23.1 |
| First morning urine | 17% (5/30) |
| Has medications | 37% (11/30) |
| Has folic acid | 7% (2/30) |
| Has health condition | 17% (5/30) |
| Coffee drinkers | 50% (15/30) |

### Health conditions in negatives
- Fever: N40, N58
- UTI: N43, N53
- Diabetes: N33

### Medications in negatives (notable)
- Folic acid: N44, N57 (N57 may be mislabeled pregnant)
- Vitamin B: N37, N55
- Multivitamin: N37, N47, N50, N59

### Positive vs Negative Comparison (survey subjects only)
| Feature | Positive (n=11) | Negative (n=30) |
|---------|-----------------|-----------------|
| Has medications | 55% | 37% |
| Has folic acid | 45% | 7% |
| Has health condition | 0% | 17% |

**Key insight**: Folic acid use (45% vs 7%) is a strong differentiator — it's a prenatal supplement, NOT a urine signal.

---

## FILES CREATED/UPDATED THIS SESSION

| File | Description |
|------|-------------|
| src/train_v6.py | V6 training script with rich aggregation + interactions |
| models/model_production_v6.pkl | V6 production (AUC=0.749, 101 subjects) |
| models/model_v6_fusion.pkl | V6 late fusion (AUC=0.770, 68 subjects) |
| models/model_v6_20260504_*.pkl | Timestamped V6 backup |
| data/processed/survey_metadata_complete.csv | ALL 101 subjects |

---

## NEXT STEPS (PRIORITY ORDER)

### 1. Resolve N57 (user decision needed)
- Currently excluded from all models
- Options: reclassify to P53, exclude permanently, or keep as negative

### 2. Fix survey data for honest confounder control
The survey features CAN'T be used for modeling until the old-format subjects (P1-P34/P41, N1-N28) have their missing fields filled in:
- Need to re-extract age, coffee, first_morning from old survey forms
- Many old surveys may genuinely not have this info → need standardized re-collection
- Until then, survey features must stay excluded from production models

### 3. Collect more data (primary path to better AUC)
The signal ceiling with 101 subjects appears to be AUC ~0.74-0.77. No classifier or feature engineering pushes past this. The bottleneck is data quantity and quality:
- Priority: subjects with video (late fusion needs more video-equipped subjects)
- Priority: first-morning urine (currently underrepresented)
- Priority: controlled hydration (reduces biggest confounder)

### 4. Consider alternative visual features
Current features (color, texture, turbidity, spectral ratios) may be near their information ceiling. Ideas:
- Foam decay rate measurement (manual annotation from video)
- Particle/sediment detection (custom CV pipeline)
- Surface tension proxy from meniscus shape
- Frequency-domain analysis of video frames

### 5. External validation
Test on a held-out batch collected independently to estimate real-world performance.

---

## HONEST ASSESSMENT

With 101 subjects and pure urine visual features:
- **AUC = 0.749** means the model is better than random (0.50) but far from diagnostic quality
- The 95% CI on AUC is roughly [0.65, 0.85] given the fold variance
- **This is a signal worth investigating** but cannot be used for any clinical or consumer decision
- The path forward is more data, not more sophisticated ML

*Research use only. Experimental probability model. Not a diagnostic test.*
