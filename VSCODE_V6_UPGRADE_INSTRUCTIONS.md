# VS Code / Claude Code - V6 Upgrade Instructions
## Updated: May 4, 2026

---

## CONTEXT

This project is Urinalysis AI - a smartphone-based pregnancy detection system using urine images/videos. The system has gone through multiple model versions (V1-V6) with critical leakage discoveries along the way.

**Current production model:** V6 (AUC=0.749, 101 subjects, pure urine features)
**Best model:** V6 Fusion (AUC=0.770, 68 subjects with video, late fusion 0.7P+0.3V)

Read `HANDOFF_SESSION_20260504.md` for full session history before starting any work.

---

## WHAT CHANGED (V5 -> V6)

### 1. Leakage discovered and fixed
- `gest_age_weeks` was label leakage (F=52.33). BANNED permanently.
- `has_folic_acid` was behavioral leakage (45% positive vs 7% negative). BANNED.
- All survey features excluded from production models until old-format subjects re-surveyed.
- V5 AUC=0.774 was inflated by ~0.03 from survey format artifact.
- V5 AUC=0.907 was INVALID (label leakage). Never reference this number.

### 2. Model architecture changed
- V4/V5: SoftVoting ensemble (LR + ExtraTrees + SVC), f_classif feature selection
- V6: GradientBoostingClassifier (depth=2, lr=0.05), mutual_info_classif selection (k=50-90)
- V6 adds rich aggregation: mean/std/min/max/cv/range per subject + interaction features
- V6 Fusion: 0.7 * photo_model + 0.3 * video_model (late fusion)

### 3. N57 excluded
- Subject NEGATIVE_57 had contradictory survey (marked "confirmed pregnant" but filed as negative)
- Removed from features_v2.csv (now 1,222 rows, 101 subjects)
- If reinstated, would be POSITIVE_53

### 4. Survey metadata complete
- `survey_metadata_complete.csv` has ALL 101 subjects
- Old format subjects (P1-P34/P41, N1-N28) have partial data (many fields = 0 = missing)
- New format subjects (P42-P52, N31-N60) have complete data

---

## TASKS TO IMPLEMENT (Priority Order)

### Task 1: Update train_v6.py to production standard
The current `train_v6.py` was built during experimentation. Clean it up:

```python
# KEY PARAMETERS (do not change without nested CV justification):
# - GradientBoostingClassifier(n_estimators=200, max_depth=2, learning_rate=0.05)
# - SelectKBest(mutual_info_classif, k=90)
# - GroupKFold(n_splits=5) by subject_id
# - NO survey features in feature matrix
# - Exclude N57 (NEGATIVE_57)

# AGGREGATION (per subject):
# For each base feature: compute mean, std, min, max, cv, range
# Interaction features: pairwise products of top variability features
# Total: ~221 features per subject
```

Files to update:
- `src/train_v6.py` - clean up, add logging, save fold-level results
- `src/inference_v2.py` - update to load V6 model and V6 feature pipeline

### Task 2: Implement nested cross-validation
Current V6 uses simple 5-fold GroupKFold. All reviewers require nested CV:

```python
# Outer loop: 5-fold GroupKFold (evaluation)
# Inner loop: 3-fold GroupKFold (hyperparameter tuning + feature selection k)
# Feature selection (SelectKBest) MUST be inside inner loop
# Scaler fitting MUST be inside inner loop
# Report outer-fold AUC as the honest metric
```

This is the single most important code change. If nested AUC drops by >0.03 from current 0.749, it means our current number is slightly optimistic.

### Task 3: Add metadata-only baseline
Build a "shortcut detector" model that uses ONLY non-urine features:

```python
metadata_features = ['phone_model_encoded', 'capture_hour_bucket',
                     'background_luminance', 'first_morning',
                     'num_images', 'has_video']
# If this model achieves AUC > 0.60, we have acquisition confounding
# This is a CRITICAL diagnostic - not a production model
```

### Task 4: Implement ROI segmentation + white-balance normalization
Top priority feature engineering move (expected +0.03 to +0.06 AUC):

```python
# 1. Detect cup boundaries in image
# 2. Segment liquid region (ROI)
# 3. Extract white background region
# 4. Compute white-balance correction factors from background
# 5. Apply correction to liquid ROI
# 6. Recompute ALL color features on corrected ROI
# Save as features_v3.csv
```

Update `src/features_v2.py` or create `src/features_v3.py`.

### Task 5: Add cross-view dispersion features
Second priority feature engineering move (expected +0.02 to +0.04 AUC):

```python
# For each subject with 3+ photos:
# - Pairwise DeltaE2000 between photos (color difference metric)
# - Jensen-Shannon divergence of color histograms
# - Variance of highlight area across photos
# - Brightness rank instability
# - Angle-consistency summaries
```

### Task 6: Implement DINOv2 frozen embeddings (experimental)
Third priority, medium-low confidence:

```python
# Use DINOv2 ViT-B/14 or ViT-S/14 as frozen feature extractor
# Extract CLS token + mean patch embedding per liquid ROI
# Aggregate per subject: mean, std, pairwise cosine distance
# Add as supplementary features (do NOT replace handcrafted)
# WARNING: p >> n risk at N=101. Only useful after N > 300.
```

### Task 7: Update API and inference pipeline
Once features are updated:
- `src/api_v2.py` -> update to use V6 model
- `src/inference_v2.py` -> update feature pipeline to match training
- Add calibration (Platt scaling) to probability output
- Add confidence interval to predictions

### Task 8: Build data collection protocol validator
For Phase 2 data collection:

```python
# Validate new images meet protocol:
# - White background detected (luminance check)
# - Cup boundaries visible
# - Minimum resolution (e.g., 1280x960)
# - No extreme blur (Laplacian variance threshold)
# - Color card detected (if protocol requires)
# - Metadata logged (phone model, timestamp, etc.)
```

---

## CRITICAL RULES

1. **NEVER include survey features in production models** until old-format subjects are re-surveyed
2. **NEVER include gest_age_weeks** in any binary pregnancy classifier
3. **NEVER include has_folic_acid** without a riboflavin-balanced cohort
4. **ALWAYS use GroupKFold by subject_id** - never random splits
5. **Feature selection MUST be inside CV folds** - never global SelectKBest
6. **Report nested CV AUC** as the primary metric going forward
7. **N57 stays excluded** until user makes final decision
8. **Mutual information > f_classif** for feature selection (proven in V6 experiments)

---

## FILE LOCATIONS

| File | Description |
|------|-------------|
| `src/train_v6.py` | Current training script |
| `src/features_v2.py` | Photo feature extraction |
| `src/video_features.py` | Video feature extraction |
| `src/inference_v2.py` | Inference pipeline |
| `src/api_v2.py` | REST API |
| `data/processed/features_v2.csv` | 1,222 rows, 37 cols, 101 subjects |
| `data/processed/video_features.csv` | 68 video clips, 44 features |
| `data/processed/survey_metadata_complete.csv` | All 101 subjects survey data |
| `models/model_production_v6.pkl` | Production model (AUC=0.749) |
| `models/model_v6_fusion.pkl` | Fusion model (AUC=0.770) |
| `HANDOFF_SESSION_20260504.md` | Full session history |
| `research/` | Clinical reviews from Perplexity, Gemini, ChatGPT |

---

## HONEST NUMBERS TO REMEMBER

- V6 Production: AUC = 0.749, Sensitivity = 0.602, Specificity = 0.734
- V6 Fusion: AUC = 0.770, Sensitivity = 0.694, Specificity = 0.713
- Signal ceiling with 101 subjects: ~0.74-0.77 AUC
- 95% CI: roughly [0.65, 0.85]
- Target for Phase 2 external: >= 0.82 (lower CI >= 0.75)
- No-go threshold: < 0.70 external AUC

The path forward is more data and better protocol, not more sophisticated ML.
