# Training Report - May 3, 2026
## Advanced Model Training Results on 102 Subjects

---

## Executive Summary

Pipeline V2 re-run on expanded dataset: 102 subjects (46 positive, 56 negative), 1,227 images, 68 video clips. Three rounds of model training performed: baseline, feature engineering, and advanced ensemble optimization.

**Best model achieved: AUC = 0.854, Sensitivity = 0.810, Specificity = 0.619**

---

## Dataset

| Metric | Value |
|--------|-------|
| Total subjects | 102 (46P + 56N) |
| Photos | 447 |
| Video frames | 780 |
| Video clips | 68 (36P + 32N) |
| Photo features | 32 per image, aggregated to 137 per subject (mean/std/min/max + engineered) |
| Video features | 42 temporal features per clip |
| Combined features | 179 per subject (photo + video) |

---

## Round 1: Baseline (same architecture as April 30)

| Model | AUC | Sensitivity | Specificity | Algorithm |
|-------|-----|-------------|-------------|-----------|
| Photo_V2 | 0.749 | 0.651 | 0.707 | LogisticRegression |
| Video | 0.743 | 0.690 | 0.633 | LogisticRegression |
| Combined | 0.690 | 0.781 | 0.553 | RandomForest |

Compared to April 30 (61 subjects): AUC dropped across all tiers (Photo 0.786->0.749, Video 0.825->0.743), but specificity improved dramatically (Photo 0.42->0.71). The April 30 model was over-fitted on a smaller sample.

---

## Round 2: Feature Engineering

Changes from baseline:
- Photo features aggregated per subject: mean, std, min, max (4x expansion: 32->128)
- Added coefficient of variation (CV) for key features: yellowness, saturation, brightness, concentration darkness, lab_b, lab_chroma
- Added ratio features: yellow/brightness, saturation/turbidity, lab_a/lab_b
- Total photo features per subject: 137
- Combined with 42 video features: 179 total

| Model | AUC | Sensitivity | Specificity |
|-------|-----|-------------|-------------|
| Photo LR top50 (f_classif) | 0.763 | 0.617 | 0.767 |
| Combined LR top50 | 0.810 | 0.838 | 0.706 |
| Combined LR C=0.01 top50 | 0.819 | 0.810 | 0.651 |

---

## Round 3: Ensemble Optimization (BEST RESULTS)

Tested: SoftVoting, Stacking, varied hyperparameters, feature selection methods.

| Model | AUC | Sensitivity | Specificity |
|-------|-----|-------------|-------------|
| SoftVoting (LR+ET+SVM) top50 | 0.838 | 0.838 | 0.681 |
| **SoftVoting (LR+ET5+SVM1) top50** | **0.854** | **0.810** | **0.619** |
| SoftVoting (LR+ET4+SVM1) top50 | 0.854 | 0.810 | 0.644 |
| Vote4 (LR+ET+SVM+KNN) top50 | 0.833 | 0.892 | 0.586 |
| Stacking (LR+ET+SVM)->LR top50 | 0.833 | 0.950 | 0.147 |

**Best model**: SoftVoting ensemble of:
- LogisticRegression (C=0.01)
- ExtraTreesClassifier (500 trees, max_depth=5)
- SVC (RBF kernel, C=1.0)

With SelectKBest (f_classif, k=50) feature selection on combined photo+video features.

### 5-Fold Cross-Validation Detail (Best Model)

| Fold | N | AUC | Sensitivity | Specificity |
|------|---|-----|-------------|-------------|
| 1 | 14 | 0.854 | 0.625 | 0.833 |
| 2 | 14 | 0.837 | 0.714 | 0.571 |
| 3 | 14 | 0.854 | 0.833 | 0.625 |
| 4 | 13 | 1.000 | 1.000 | 0.667 |
| 5 | 13 | 0.725 | 0.875 | 0.400 |
| **Mean** | - | **0.854 +/-0.087** | **0.810** | **0.619** |

---

## Top 20 Discriminating Features

| Rank | Feature | F-score | Category |
|------|---------|---------|----------|
| 1 | t_r_ratio_complexity | 13.45 | Video temporal |
| 2 | t_layla_r_autocorr | 10.29 | Video spectral |
| 3 | t_hue_mean | 8.89 | Video color |
| 4 | t_value_trend | 8.50 | Video brightness |
| 5 | t_activity_trend | 8.15 | Video motion |
| 6 | hue_spread_mean | 7.11 | Photo color |
| 7 | gy_ratio_mean | 6.58 | Photo color ratio |
| 8 | t_rg_ratio_std | 5.99 | Video color |
| 9 | t_r_ratio_std | 5.61 | Video spectral |
| 10 | t_layla_r_stability | 5.34 | Video spectral |
| 11 | t_flow_coherence_mean | 4.81 | Video optical flow |
| 12 | t_value_std | 4.76 | Video brightness |
| 13 | layla_r_ratio_mean | 4.66 | Photo spectral |
| 14 | t_texture_std | 4.54 | Video texture |
| 15 | t_hue_trend | 4.43 | Video color |
| 16 | layla_rg_ratio_min | 4.20 | Photo spectral |
| 17 | lab_a_mean | 3.99 | Photo CIELAB |
| 18 | layla_r_ratio_min | 3.60 | Photo spectral |
| 19 | gy_ratio_max | 3.22 | Photo color ratio |
| 20 | r_mean_max | 3.20 | Photo red channel |

**Key insight**: 12 of the top 20 features are VIDEO temporal features. The temporal behavior of urine (how color, brightness, and texture change over the video) is a much stronger pregnancy signal than static photo features alone. This confirms the April 30 finding and is stronger with more data.

---

## Model Files

| File | Description | Size |
|------|-------------|------|
| model_best_v3_20260503.pkl | Best ensemble model (AUC=0.854) | 1.0MB |
| model_production_v3.pkl | Copy of best, for production use | 1.0MB |
| model_photo_v2_20260503_154502.pkl | Photo-only baseline | 4KB |
| model_video_20260503_154502.pkl | Video-only baseline | 5KB |
| model_combined_20260503_154502.pkl | Combined baseline | 402KB |

---

## Performance History

| Date | Subjects | Best Model | AUC | Sens | Spec |
|------|----------|-----------|-----|------|------|
| Apr 30 | 61 | Video RF | 0.825 | 0.865 | 0.480 |
| May 3 (baseline) | 102 | Photo LR | 0.749 | 0.651 | 0.707 |
| **May 3 (advanced)** | **102** | **Ensemble V3** | **0.854** | **0.810** | **0.619** |

---

## Next Steps to Improve Further

1. **More data**: Each additional subject improves model stability. Priority: more negative controls with confounders (fever, UTI, medications)
2. **Survey metadata integration**: 37 folders still need survey form extraction (gestational age, medications, etc.). Adding these as features will likely improve the model
3. **Video-first strategy**: Since 12/20 top features are temporal, investing in better video capture quality and longer clips could yield significant gains
4. **Threshold optimization**: Current threshold is 0.5. Optimizing the decision threshold for clinical use (maximize sensitivity at acceptable specificity) is needed
5. **Per-trimester models**: Separate models for first vs second trimester may capture different signal profiles
6. **Confounder-aware training**: Adding medication/hydration/time-of-day as explicit features from survey data

---

*Research use only. Experimental probability model. Not a diagnostic test.*
