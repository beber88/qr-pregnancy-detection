# Next Session Instructions
## Updated: May 4, 2026

---

## What is done

- ALL survey metadata extracted: P42-P52 (11 positive) + N31-N60 (30 negative)
- Survey CSVs saved: survey_metadata_positive_new.csv, survey_metadata_negative_new.csv, survey_metadata_all_new.csv
- Model V4 trained with survey features: AUC=0.756 (robust 5-fold GroupKFold)
- Production model saved: models/model_production_v4.pkl

## CRITICAL: Verify N57

Subject NEGATIVE_57 marked "Confirmed pregnant" on their survey form but is filed under NEGATIVE/57/.
Same pattern as N22 which was reclassified to POSITIVE_41.

If N57 is indeed pregnant:
1. Move NEGATIVE/57 contents to POSITIVE/53 (or next available positive number)
2. Update label in features_v2.csv for that subject
3. Retrain model

## Remaining tasks (priority order)

### 1. Extract survey metadata for original 61 subjects
The original subjects (P1-P34, P41, N1-N28) also have survey forms in their folders.
Extracting these would give us survey data for ALL 102 subjects instead of just 41.
This is valuable because:
- Medication/supplement info for confounding analysis
- First morning urine flag for hydration control
- Age for demographic analysis

### 2. Push model accuracy higher
Current best: AUC=0.756 (V4, 5-fold GroupKFold)
Ideas to try:
- Feature selection with mutual information instead of f_classif
- Stacking ensemble instead of voting
- Add interaction features (e.g., brightness_std * t_hue_mean)
- Try XGBoost or LightGBM
- Calibration (Platt scaling or isotonic regression)
- Remove N57 if mislabeled (cleaner labels = better model)

### 3. Collect more data
Priority subjects to add:
- More first-morning urine samples (currently underrepresented)
- Subjects with known confounders (fever, UTI, medications)
- Third trimester positives (currently underrepresented)
- Controlled hydration samples

---

## File locations

| File | Rows | Description |
|------|------|-------------|
| data/processed/features_v2.csv | 1,227 | 37 features per image, 102 subjects |
| data/processed/video_features.csv | 68 | 44 temporal features per video clip |
| data/processed/survey_metadata_all_new.csv | 41 | Survey data for new subjects only |
| models/model_production_v4.pkl | - | Best model (AUC=0.756) |
| HANDOFF_SESSION_20260504.md | - | Full session report |
