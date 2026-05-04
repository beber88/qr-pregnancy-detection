# VS Code / Claude Code Sync Instructions
## Updated: May 3, 2026

---

## What Changed (done by Cowork session)

The following files were created or updated in the QR PROJECT folder. Claude Code in VS Code shares the same folder, so all changes are immediately visible.

### Data Files Updated
- `data/processed/index.csv` - Rebuilt: 1,227 rows, 102 subjects (was 856 rows, 61 subjects)
- `data/processed/features_v2.csv` - Rebuilt: 1,227 rows, 37 columns, 102 subjects
- `data/processed/video_features.csv` - Rebuilt: 68 subjects, 44 columns
- `data/processed/features_v2_backup_20260503.csv` - Backup of previous version

### New Model Files
- `models/model_best_v3_20260503.pkl` - Best ensemble model (AUC=0.854)
- `models/model_production_v3.pkl` - Production copy of best model
- `models/model_photo_v2_20260503_154502.pkl` - Photo-only baseline (AUC=0.749)
- `models/model_video_20260503_154502.pkl` - Video-only baseline (AUC=0.743)
- `models/model_combined_20260503_154502.pkl` - Combined baseline (AUC=0.690)

### Documentation Updated
- `HANDOFF_PROMPT.md` - Updated pipeline status, model performance history, new subjects list
- `HANDOFF_SESSION_20260503.md` - Session handoff with pipeline completion status
- `NEW_DATA_ANALYSIS_PROMPT.md` - Updated analysis instructions with two-track approach
- `TRAINING_REPORT_20260503.md` - Full training report with all results
- `SURVEY_MAPPING.md` - Survey-to-folder mapping (unchanged)

---

## What Claude Code Should Do Next

Paste this into Claude Code:

```
Read TRAINING_REPORT_20260503.md and HANDOFF_SESSION_20260503.md.

The Cowork session has completed:
1. Pipeline V2 re-run on all 102 subjects (features_v2.csv rebuilt with 1,227 rows)
2. Video features re-extracted (68 subjects)
3. Baseline models retrained (Photo AUC=0.749, Video AUC=0.743)
4. Advanced ensemble model trained: AUC=0.854, saved as model_best_v3_20260503.pkl

YOUR REMAINING TASKS:

A) SURVEY METADATA EXTRACTION (37 folders remaining)
   Read ONLY the survey form image from each folder below.
   Extract: gestational age, age, medications, health, first morning urine, phone model.
   Save to data/processed/survey_metadata_new.csv
   
   Folders to process:
   - POSITIVE: 46, 47, 48, 49, 50, 51, 52 (7 folders)
   - NEGATIVE: 31-60 (30 folders)
   
   Process in batches of 8-10 survey forms.
   Write HANDOFF_SESSION file after each batch.
   Do NOT load urine images - only survey form images.

B) INTEGRATE SURVEY METADATA INTO MODEL
   After extracting survey data, add these as features:
   - gestational_age_weeks (numeric, positive only)
   - subject_age (numeric)
   - first_morning_urine (binary)
   - has_medications (binary)
   - has_iron_supplement (binary)
   - has_folic_acid (binary)
   - has_antibiotics (binary)
   - has_progesterone (binary)
   - has_health_condition (binary)
   
   Merge with existing features and retrain the ensemble.

C) THRESHOLD OPTIMIZATION
   The current decision threshold is 0.5.
   Find the optimal threshold that maximizes:
   - Youden's J (sensitivity + specificity - 1)
   - Clinical threshold (sensitivity >= 0.95 at best possible specificity)
   Report both thresholds and their performance.

D) PER-TRIMESTER ANALYSIS
   For positive subjects with known gestational age:
   - First trimester (< 13 weeks): does the model perform differently?
   - Second trimester (13-27 weeks): different signal profile?
   Report per-trimester AUC if enough subjects exist.

IMPORTANT: model_best_v3_20260503.pkl contains the full pipeline:
  - feature_selector (SelectKBest, k=50)
  - scaler (StandardScaler)
  - classifier (VotingClassifier: LR + ExtraTrees + SVM)
  Load it with pickle.load() to get a dict with all components.
```

---

## Model Architecture (for Claude Code reference)

The best model (V3) uses this pipeline:

```
Raw images -> features_v2.py (32 features per image)
     |
     v
Photo aggregation per subject: mean, std, min, max -> 128 features
     + 9 engineered features (CV ratios, cross-feature ratios) -> 137 features
     |
     v
Merge with video_features.csv (42 temporal features) -> 179 features
     |
     v
SelectKBest (f_classif, k=50) -> 50 features
     |
     v
StandardScaler
     |
     v
SoftVoting Ensemble:
  - LogisticRegression (C=0.01)
  - ExtraTreesClassifier (500 trees, max_depth=5)
  - SVC (RBF, C=1.0)
     |
     v
Probability output (0.0 to 1.0)
```

Top discriminating features are predominantly video temporal features (12/20 top features), confirming that urine behavior over time is a stronger pregnancy signal than static color.
