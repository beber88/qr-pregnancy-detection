# Next Session: Extract Negative Survey Forms
## Resume point: N31-N60 (30 folders)

---

## What is already done

- Pipeline V2 complete: all 102 subjects have numerical features extracted
- Best model: AUC=0.854 (Ensemble V3, saved as model_best_v3_20260503.pkl)
- ALL positive surveys extracted: P42-P52 saved in `data/processed/survey_metadata_positive_new.csv`
- Previous positive surveys (P1-P34, P41): see HANDOFF_PROMPT.md tables

## Your task

Extract survey form metadata from 30 NEGATIVE folders: N31 through N60.

### Critical rules to avoid pixel crash

1. **Load ONLY 1 image per folder** - the survey form image
2. **Process in batches of 5 folders MAX** - then write results to CSV immediately
3. **Do NOT load urine images or payment photos** - only the survey form
4. **Survey forms are typically the second-to-last timestamp** in each folder
5. **After every batch of 5, append results to the CSV file** before continuing

### How to find the survey form efficiently

The survey form is usually NOT the first or last image chronologically. Strategy:
- Sort files by timestamp
- Skip the earliest timestamps (usually urine photos)
- Check the second-to-last or third-to-last timestamp image
- If it shows a paper form with checkboxes/text: that is the survey
- If it shows a payment screenshot or urine: try the next image

### Data to extract from each survey form

For NEGATIVE (non-pregnant) subjects:
- `subject_id`: NEGATIVE_31 through NEGATIVE_60
- `label`: 0
- `gest_age_weeks`: 0 (not pregnant)
- `age`: subject age (number)
- `first_morning`: 1 if first morning urine, 0 if not
- `medications`: comma-separated list or 'none'
- `health`: comma-separated health conditions or 'none'
- `phone`: phone model
- `coffee`: 1 if yes, 0 if no
- `fluids_cups`: approximate cups of fluid in past 2 hours (0-4)

### Save format

Append to: `data/processed/survey_metadata_negative_new.csv`

Save after EVERY batch of 5. Use this Python pattern:
```python
import pandas as pd, os
new_rows = [...]  # your extracted data
df = pd.DataFrame(new_rows)
path = 'data/processed/survey_metadata_negative_new.csv'
if os.path.exists(path):
    existing = pd.read_csv(path)
    df = pd.concat([existing, df], ignore_index=True)
df.to_csv(path, index=False)
```

### Batch plan

- Batch 1: N31-N35 (5 folders) -> save -> write handoff
- Batch 2: N36-N40 (5 folders) -> save -> write handoff
- Batch 3: N41-N45 (5 folders) -> save -> write handoff
- Batch 4: N46-N50 (5 folders) -> save -> write handoff
- Batch 5: N51-N55 (5 folders) -> save -> write handoff
- Batch 6: N56-N60 (5 folders) -> save -> write handoff

If you can do 2-3 batches per session, that is great. Always save and write handoff before stopping.

### After ALL negatives are extracted

1. Merge positive and negative survey CSVs:
```python
pos = pd.read_csv('data/processed/survey_metadata_positive_new.csv')
neg = pd.read_csv('data/processed/survey_metadata_negative_new.csv')
full = pd.concat([pos, neg], ignore_index=True)
full.to_csv('data/processed/survey_metadata_all_new.csv', index=False)
```

2. Add binary feature columns:
```python
full['has_medications'] = (full['medications'] != 'none').astype(int)
full['has_folic_acid'] = full['medications'].str.contains('folic', na=False).astype(int)
full['has_antibiotics'] = full['medications'].str.contains('antibiotic', na=False).astype(int)
full['has_health_condition'] = (full['health'] != 'none').astype(int)
```

3. Merge with features_v2.csv and retrain the ensemble model
4. Run threshold optimization (Youden's J + clinical sensitivity >= 0.95)
5. Run per-trimester analysis on positive subjects
