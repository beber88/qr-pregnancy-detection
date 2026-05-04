# NEW DATA ANALYSIS PROMPT - May 3, 2026
## For Claude Code in VS Code - Folder-by-Folder Urine Sample Analysis

---

## BEFORE YOU START - CHECK FOR HANDOFF FILES

```bash
ls -t /Users/admin/QR\ PROJECT/HANDOFF_SESSION_*.md 2>/dev/null | head -1
```

If a handoff file exists, READ IT FIRST. It contains:
- Which folders are already done (do not re-process them)
- Where to resume from
- Survey data already extracted (do not re-read those images)
- Pipeline status and any issues found

The most recent handoff file as of May 3, 2026 is: `HANDOFF_SESSION_20260503.md`
It shows P42-P45 are DONE. Resume from P46.

---

## CONTEXT

You are continuing work on a dual-track pregnancy detection system. The full project architecture, regulatory framework, and scientific rationale are documented in:

1. `MASTER_PROMPT_v2.md` - Complete build plan (Track A commercial + Track B research)
2. `HANDOFF_PROMPT.md` - Previous scanning results (P1-P34, P41, N1-N28) with extracted features and model performance
3. `README.md` - Project structure and pipeline overview
4. `SURVEY_MAPPING.md` - Mapping of WhatsApp survey sets to folder numbers

Read ALL of these before starting any analysis work.

---

## WHAT IS NEW (added May 3, 2026)

41 new research subjects were added to the dataset today, collected via WhatsApp surveys from the "Urin test" research group between April 29 and May 1, 2026.

### New POSITIVE folders (pregnant women): P42 through P52

Location: `PICTURES - VIDEO/POSITIVE/42/` through `PICTURES - VIDEO/POSITIVE/52/`

| Folder | Files | Date Collected |
|--------|-------|----------------|
| P42 | 6 | April 29 |
| P43 | 6 | April 29 |
| P44 | 6 | April 29 |
| P45 | 6 | April 29 |
| P46 | 5 | April 29 |
| P47 | 6 | April 29 |
| P48 | 5 | April 30 |
| P49 | 5 | April 30 |
| P50 | 5 | April 30 |
| P51 | 5 | April 30 |
| P52 | 5 | May 1 |

**Total: 11 new pregnant subjects, 60 files**

### New NEGATIVE folders (non-pregnant women): N31 through N60

Location: `PICTURES - VIDEO/NEGATIVE/31/` through `PICTURES - VIDEO/NEGATIVE/60/`

| Folder | Files | Date Collected |
|--------|-------|----------------|
| N31 | 7 | April 29 |
| N32 | 7 | April 29 |
| N33 | 6 | April 29 |
| N34 | 6 | April 29 |
| N35 | 6 | April 29 |
| N36 | 6 | April 29 |
| N37 | 6 | April 29 |
| N38 | 6 | April 29 |
| N39 | 5 | April 29 |
| N40 | 5 | April 29 |
| N41 | 5 | April 29 |
| N42 | 5 | April 29 |
| N43 | 5 | April 29 |
| N44 | 4 | April 29 |
| N45 | 5 | April 29 |
| N46 | 5 | April 30 |
| N47 | 5 | April 30 |
| N48 | 5 | April 30 |
| N49 | 5 | April 30 |
| N50 | 5 | April 30 |
| N51 | 5 | April 30 |
| N52 | 5 | April 30 |
| N53 | 5 | May 1 |
| N54 | 6 | May 1 |
| N55 | 6 | May 1 |
| N56 | 5 | May 1 |
| N57 | 5 | May 1 |
| N58 | 5 | May 1 |
| N59 | 5 | May 1 |
| N60 | 5 | May 1 |

**Total: 30 new non-pregnant subjects, 161 files**

---

## WHAT EACH FOLDER CONTAINS

Each folder number represents ONE woman in the research study. Each folder typically contains:

1. **Urine images (JPEG)** - Top view and/or side view photographs of the urine sample in a clear cup
2. **Urine video (MP4)** - Short video of the urine sample showing liquid behavior, foam, movement, settling
3. **Survey form document (JPEG)** - A filled-out questionnaire with the woman's details: pregnancy status, gestational age (weeks/months), age, medications, supplements, health conditions, first morning urine or not, phone model used
4. **Payment confirmation photo (JPEG)** - GCash payment screenshot (not relevant for analysis, skip this)

File naming convention: `WhatsApp Image YYYY-MM-DD at HH.MM.SS.jpeg` or `WhatsApp Video YYYY-MM-DD at HH.MM.SS.mp4`. Files with `(1)`, `(2)` suffixes are additional images from the same timestamp batch.

---

## CUMULATIVE DATASET STATUS

After this addition, the full dataset is:

| Category | Previously scanned | New (unscanned) | Total with data | Empty (pending) |
|----------|-------------------|-----------------|-----------------|-----------------|
| POSITIVE | P1-P34, P41 (35 subjects) | P42-P52 (11 subjects) | 46 subjects | P35-P40, P53-P100 |
| NEGATIVE | N1-N14, N16-N28 (26 subjects) | N31-N60 (30 subjects) | 56 subjects | N15, N22, N29-N30, N61-N100 |
| **TOTAL** | **61 subjects** | **41 subjects** | **102 subjects** | - |

Previous model performance (61 subjects, April 30 2026):
- Photo model AUC: 0.786
- Video model AUC: 0.825 (best performer)
- Combined model AUC: 0.743

---

## YOUR MISSION

Analyze all 41 new folders to extract visual features, survey metadata, and video temporal features. Then retrain the models with the expanded dataset (102 subjects total). The goal: improve the system's ability to distinguish pregnant from non-pregnant urine samples.

---

## CRITICAL RULES FOR EXECUTION

### Rule 0: TWO-TRACK APPROACH (read this first)

The work is split into two separate tracks to avoid burning through your context window:

**Track 1 - Automated Python pipeline (handles urine images + video):**
Run the existing Python scripts (`run_pipeline.py` or `run_pipeline_v2.py`) to automatically extract all 37 numerical features (color, turbidity, texture, etc.) from every image and video frame. This processes ALL folders at once without loading images into your context. Do this FIRST.

**Track 2 - Survey form extraction (requires your visual reading):**
For each folder, visually read ONLY the survey form image (the one with handwritten/printed text on paper). Extract metadata: pregnancy confirmation method, gestational age, first morning urine, meals, fluids, medications, health conditions, age, phone model. Do NOT load urine images or payment photos into your context - the pipeline already handled those numerically.

WHY: Loading urine images visually into your context burns ~4-5 folders before hitting the pixel/token limit. The Python pipeline extracts better numerical features anyway. Your visual analysis should be reserved for survey forms only, which are text-based and require OCR-like reading that the pipeline cannot do.

### Rule 1: Run the pipeline first

Before any visual inspection:
```bash
cd /Users/admin/QR\ PROJECT
python run_pipeline.py
```
This runs `build_index.py` (scans all new folders) then `phase1_extract.py` (extracts 37 features per image). Check the output: features_v2.csv should grow from 856 rows to include the new subjects.

If the pipeline fails on new folders, debug it. If it needs modification to handle the new folder range, fix the code. The pipeline is the primary analysis tool.

### Rule 2: Survey forms in batches of 8-10

Process survey forms in small batches:
- Batch 1: P46-P52 (7 folders, ~7 survey form images)
- Batch 2: N31-N40 (10 folders, ~10 survey form images)
- Batch 3: N41-N50 (10 folders, ~10 survey form images)
- Batch 4: N51-N60 (10 folders, ~10 survey form images)

For each folder, load ONLY the survey form image (typically the image showing a paper form or questionnaire). Extract:
- Pregnancy confirmed: yes/no, method (ultrasound, blood test, home test)
- Gestational age: weeks or months
- First morning urine: yes/no
- Last meal timing
- Fluid intake
- Coffee/tea: yes/no
- Medications/supplements (flag confounders: antibiotics, progesterone, iron, vitamins)
- Health conditions (flag: fever, UTI, kidney disease)
- Age
- Phone model
- Lighting conditions
- Cup type

Save extracted survey data to `data/processed/survey_metadata_new.csv` after each batch.

### Rule 3: Identify survey forms by content, not filename

WhatsApp filenames are timestamps. To find the survey form without loading all images:
- Survey forms are usually the SECOND-TO-LAST or LAST image chronologically (higher timestamp seconds)
- They show paper/form with text, checkboxes, handwriting
- If unsure, load ONE image at a time to check - if it is urine or payment, close it and try the next

### Rule 4: Rolling handoff (CRITICAL - MUST EXECUTE BEFORE STOPPING)

This is the MOST IMPORTANT rule. You MUST write a handoff file BEFORE your session ends, even if you think you have more capacity. Specifically:

**After completing each batch (Rule 2), immediately write/update the handoff file.** Do not wait until the end. Write it after EVERY batch.

The handoff file is called `HANDOFF_SESSION_[DATE].md` (or `_S2`, `_S3` for multiple sessions on the same date). It must contain:
1. Exactly which folders are DONE (survey extracted + pipeline processed)
2. Exactly which folder to RESUME from
3. All extracted survey data so far (so the next session does not re-read those images)
4. Any anomalies or confounders found
5. Pipeline status (did it run successfully? new row count in features_v2.csv?)
6. The exact next step to execute

**Write the handoff file BEFORE doing anything else after each batch.** If you write it after batch 1 and then crash during batch 2, at least batch 1 results are saved.

**Check for existing handoff files before starting:**
```bash
ls -t /Users/admin/QR\ PROJECT/HANDOFF_SESSION_*.md 2>/dev/null | head -1
```
Read the most recent one and continue from where it left off.

### Rule 5: Context budget awareness

You have roughly 200K tokens of context. Each high-res image costs ~1,500-2,500 tokens. Budget:
- Pipeline output + file reads: ~20K tokens
- Survey form images (8-10 per batch): ~20K tokens per batch
- Your analysis text: ~10K tokens per batch
- Safety margin: always keep 20K tokens free for the handoff file

If you have processed 2 batches (~20 survey forms) and written their data, that is a good session. Write the handoff and stop. Do not push to a third batch unless you are confident you have capacity.

### Rule 6: Append to existing data, never overwrite

The existing `features_v2.csv` (856 rows, 37 columns) contains data from the previous 61 subjects. The pipeline should APPEND new rows. Create a backup before any modification:
```bash
cp data/processed/features_v2.csv data/processed/features_v2_backup_$(date +%Y%m%d).csv
```

### Rule 7: Flag anomalies immediately

If you encounter:
- A folder where the survey says pregnant but the folder is in NEGATIVE (or vice versa)
- Missing content (no urine images, only payment photo)
- Corrupted or unreadable files
- Medications that are strong confounders (antibiotics, iron supplements, progesterone)

Flag it in your output AND in the handoff file. Do not silently skip it.

### Rule 4: Append to existing data, never overwrite

The existing `data/processed/features.csv` (856 rows, 37 columns) and `data/processed/features_v2.csv` contain data from the previous 61 subjects. New data must be APPENDED, not replace the existing file. Create a backup before any modification.

### Rule 5: Match the existing feature schema

The previous scanning chain extracted these feature categories (see HANDOFF_PROMPT.md for the complete table):
- Color (CIE L*a*b*, HSV dominant hue, saturation, value)
- Concentration estimate (LOW, LOW-MOD, MODERATE, MOD-HIGH, HIGH, VERY HIGH)
- Volume estimate (percentage of cup or ml estimate)
- Bubble/foam presence and characteristics
- Transparency/turbidity
- Gestational age (weeks or months, from survey)
- Subject age (from survey)
- Medications/supplements (from survey)
- Health conditions (from survey)
- First morning urine (yes/no, from survey)
- Phone model (from survey)
- Any special notes

New folders must produce data in the SAME schema. Check the existing features_v2.csv columns and match them exactly.

### Rule 6: Flag anomalies immediately

If you encounter:
- A folder that appears mislabeled (e.g., survey says pregnant but folder is in NEGATIVE)
- Missing content (no urine images, only payment photo)
- Unusual urine appearance that does not match any previous pattern
- Corrupted or unreadable files

Flag it in your output and in the handoff file. Do not silently skip it.

---

## ANALYSIS PRIORITIES

After extracting features from all new folders:

1. **Update the feature tables** in HANDOFF_PROMPT.md with the 41 new subjects
2. **Re-run the existing pipeline**: `python run_pipeline.py` (or run_pipeline_v2.py) to rebuild the index and re-extract features
3. **Retrain all models** with the expanded 102-subject dataset
4. **Compare performance** before (61 subjects) vs after (102 subjects) - report AUC, sensitivity, specificity for Photo, Video, and Combined models
5. **Update the synthesis section** - do the new subjects confirm or change the positive vs negative patterns identified previously?
6. **Specifically investigate**:
   - Does the greenish tint pattern (previously seen only in P13-P16) appear in any new positive samples?
   - Does the foam/bubble prominence pattern hold with more data?
   - Do the new negative samples with potential confounders (fever, UTI, medications) change the confounder model?
   - Does the video model maintain its advantage over the photo model with more data?

---

## ONGOING RESEARCH NOTE

This is an active research project. More urine samples (both positive and negative) will be added in future sessions. The system must be designed to grow incrementally:
- New folders will be added to POSITIVE/ and NEGATIVE/ with incrementing numbers
- Each new batch will come with an updated SURVEY_MAPPING.md
- The analysis prompt (this document) will be updated with the new folder ranges
- The rolling handoff system ensures continuity across sessions

---

## QUICK START CHECKLIST

Before starting analysis:

- [ ] Read MASTER_PROMPT_v2.md (understand Track A vs Track B framework)
- [ ] Read HANDOFF_PROMPT.md (understand previous 61 subjects' data and patterns)
- [ ] Read README.md (understand pipeline architecture)
- [ ] Check for any HANDOFF_SESSION_*.md files (pick up from last session if exists)
- [ ] Verify existing features_v2.csv is intact (856 rows, 37 columns)
- [ ] Back up existing data files before any modification
- [ ] Begin folder-by-folder analysis starting from P42

---

## FILE PATHS REFERENCE

```
QR PROJECT/
  PICTURES - VIDEO/
    POSITIVE/
      1/ through 41/     <- Previously scanned (35 with data, 6 empty)
      42/ through 52/    <- NEW: 11 pregnant subjects (scan these)
      53/ through 100/   <- Empty, reserved for future data
    NEGATIVE/
      1/ through 28/     <- Previously scanned (26 with data, 2 empty)
      29/ through 30/    <- Empty
      31/ through 60/    <- NEW: 30 non-pregnant subjects (scan these)
      61/ through 100/   <- Empty, reserved for future data
  data/
    processed/
      features.csv       <- Original feature file
      features_v2.csv    <- Updated feature file (856 rows)
      index.csv          <- Master image index
    raw/
      video_frames/      <- Extracted video frames
  models/
    model_production_v2.pkl  <- Current best model (Video, AUC=0.825)
  src/
    build_index.py       <- Scan and index all images
    phase1_extract.py    <- Extract visual features
    train.py             <- Model training with GroupKFold
    inference.py         <- Inference engine
  MASTER_PROMPT_v2.md
  HANDOFF_PROMPT.md
  SURVEY_MAPPING.md
  NEW_DATA_ANALYSIS_PROMPT.md  <- THIS FILE
  run_pipeline.py
  run_pipeline_v2.py
```

---

*This prompt is part of the rolling research documentation. Update the "WHAT IS NEW" section and folder counts each time new data is added.*
