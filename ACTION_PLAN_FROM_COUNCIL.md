# ACTION PLAN — Pregnancy Detection AI, derived from Council session 2026-05-04

> Source: `tools/llm-council/sessions/SIMULATED_COUNCIL_20260504.md`.
> All AUC targets here assume the new evaluation regime described in §1.

This file is the bridge between the council's recommendations and the
codebase under `src/`. Each item is sized for one or two work-sessions and
includes the file to touch, the specific change, and the success / failure
test.

---

## Phase A — STATISTICAL HYGIENE (this week, before any new modeling)

### A1. Lock a held-out subject group

**Goal.** Restore the statistical meaning of every AUC we report.

**Files to touch.**
- `data/processed/subject_groups.csv` (new)
- `src/train_v2.py` (modify)

**Plan.**
1. Pick 25 subjects: 12 positive, 13 negative, stratified to roughly match
   the overall age and trimester distribution. Use a fixed random seed
   `HOLDOUT_SEED = 20260504`.
2. Write `subject_groups.csv` with columns `subject_id, group` where
   group is one of `train`, `holdout`. Commit this file. Once committed,
   do not modify.
3. In `train_v2.py`, before any fitting, drop holdout subjects from the
   training matrix. The holdout is loaded only by a separate
   `evaluate_holdout.py` script that runs once the model is frozen.

**Success.** All future model files have a paired holdout AUC reported
alongside the CV AUC.

**Failure mode.** If anybody re-tunes a model after seeing holdout
performance, the holdout is burned. Treat it as one-shot. If burned,
collect a new holdout from the next data batch.

---

### A2. Confound-only baseline

**Goal.** Quantify how much of our 0.774 AUC is non-urine signal.

**File to create.** `src/confound_baseline.py`

**Plan.**
```python
# Load data/processed/survey_metadata_complete.csv (101 subjects)
# Drop label-leak features: gest_age_weeks, has_folic_acid,
#   has_medications, has_progesterone, has_antibiotics
# Keep: age, first_morning, coffee, fluids, has_health_condition,
#   phone_model_onehot
# Train: LogisticRegression(C=1.0) and ExtraTreesClassifier(200, max_depth=4)
# Evaluate: 5-fold GroupKFold on subject_id
# Report: AUC, sensitivity, specificity, calibration (Brier)
# Save: models/baseline_confound_only.pkl
```

**Success criterion to interpret.**

| Confound-only AUC | Interpretation |
|-------------------|----------------|
| < 0.55 | No confound signal. V5's 0.774 is largely urine. Continue confidently. |
| 0.55 to 0.65 | Mild confound. ΔAUC vs V5 is the real urine signal. Report ΔAUC, not AUC. |
| 0.65 to 0.75 | Strong confound. Most of V5 is metadata. Pivot to controlled protocol. |
| > 0.75 | V5 is noise. Project hypothesis fails the first test. Pivot now. |

---

### A3. Aggregation leakage check

**Goal.** Confirm per-subject statistics (`g_mean_std`, `lab_L_std`, etc.)
are computed inside-fold, not on the full dataset.

**File to inspect.** `src/features_v2.py` and `src/train_v2.py`.

**Plan.** Audit the code path. If any aggregation runs on the full
dataset before splitting, refactor so per-subject statistics are computed
only on the training fold. Re-run V5. If AUC drops by more than 0.03,
the historical numbers were inflated.

**Success.** A documented one-paragraph note in `train_v2.py` describing
where each aggregation happens, with the train-only invariant explicit.

---

## Phase B — NOISE-FLOOR REDUCTION (next week)

### B1. Color constancy preprocessing

**Goal.** Strip phone-specific white-balance noise from every image.

**File to create.** `src/color_constancy.py`

**Plan.**
```python
# For each image in PICTURES/:
#   apply Gray-World normalization (every channel divided by its mean,
#   then re-scaled to mean 0.5)
#   AND optionally Retinex-MSR (multi-scale Retinex)
# Save normalized copies under data/raw/normalized/{POSITIVE,NEGATIVE}/<id>/
# Update build_index.py to point to the normalized folder behind a CLI flag
```

**Success.** Re-run V5 features extraction on normalized images.
Held-out AUC moves up by 0.01 to 0.04 (per council Q4).

**Failure.** Held-out AUC unchanged → drop normalization, keep original.

---

### B2. Cup segmentation with SAM

**Goal.** Crop every photo to the urine-liquid region; eliminate background
and cup-rim contamination as features.

**Dependencies.** `pip install segment-anything torch torchvision`.

**File to create.** `src/segment_cup.py`

**Plan.**
1. Use SAM-H with a single point prompt at image center (urine cup is
   centered by protocol). Output the largest mask containing the prompt.
2. Crop to bounding box of the mask plus 5% padding.
3. Save crops to `data/raw/cropped/`.
4. Re-run features extraction.

**Success.** Held-out AUC moves up by 0.02 to 0.04.

**Failure.** AUC drops → background was carrying signal, which is a
finding worth investigating (probably a phone-specific artifact).

---

## Phase C — FEATURE CEILING TEST (weeks 2-3)

### C1. Frozen DINOv2 image embeddings

**Goal.** Determine whether learned embeddings beat handcrafted features
on this specific dataset.

**Dependencies.** `pip install torch torchvision`. DINOv2-large checkpoint
from facebookresearch/dinov2.

**File to create.** `src/embed_dinov2.py`

**Plan.**
```python
# Load DINOv2-large (frozen, eval mode)
# For each image:
#   resize to 518x518, normalize per ImageNet stats
#   forward pass, take last-layer [CLS] token = 1024-dim embedding
# Aggregate per subject: mean of embeddings across that subject's photos
# Save to data/processed/dinov2_subject_embeddings.npy
```

Then in a new training script `src/train_dinov2.py`:

```python
# Inside each GroupKFold split:
#   PCA(50) fit on training subjects
#   LogisticRegression(C=0.1) on PCA components
#   plus optional concat with the 5 confounder-control features
# Evaluate: 5-fold GroupKFold + held-out group
```

**Success.** Held-out AUC ≥ 0.82 with 95% CI lower bound > 0.74.

**Failure.** Held-out AUC ≤ V5 baseline. Interpretation: the urine
signal that exists is not better captured by ImageNet-style learned
features. Keep handcrafted, focus on protocol.

---

### C2. VideoMAE-base video embeddings

**Goal.** Test whether video temporal signal is better captured learned
than handcrafted.

**File to create.** `src/embed_videomae.py`

**Plan.** Load VideoMAE-base from HuggingFace, sample 16 frames uniformly
from each 10s clip, forward pass, take [CLS] = 768-dim. Concatenate
per-subject with DINOv2 embeddings.

**Success.** Adds +0.03 to +0.06 AUC on top of DINOv2 alone.

**Failure.** No additive gain. Possibly the clip is too short for
VideoMAE to extract temporal signal; revert to handcrafted video features.

---

## Phase D — CALIBRATION (concurrent with C)

### D1. Isotonic calibration on V5 and successors

**Goal.** Make the model's probability outputs trustworthy, not just the
ranking.

**File to modify.** `src/inference_v2.py`, `src/train_v2.py`.

**Plan.**
```python
from sklearn.calibration import CalibratedClassifierCV
calibrated = CalibratedClassifierCV(base_model, method="isotonic", cv=5)
calibrated.fit(X_train, y_train)
```

Add Brier score and Expected Calibration Error (ECE) to all reports.
Add reliability diagram to the EDA pipeline.

**Success.** Brier ≤ 0.20, ECE ≤ 0.07 on the held-out group.

**Failure.** ECE > 0.10 → probability outputs are misleading; gate any
"this is a probability" UI claim until calibration is fixed.

---

## Phase E — EXPERIMENTAL PROTOCOL (this month)

### E1. Within-subject longitudinal recruitment plan

**Goal.** Set up the experiment that can falsify the hypothesis cleanly.

**Output.** A protocol document `docs/experimental_protocol_v1.md` with:
- Recruitment criteria (60 trying-to-conceive + 30 prenatal-vitamin
  contraception controls).
- 3-cycle longitudinal sampling, days 25 to 28 each cycle.
- Lightbox + color card supplied per subject.
- Phone fixed per subject, model logged.
- Weekly food/supplement diary.
- IRB submission outline (if relevant in the user's jurisdiction).
- Pre-registration on OSF before recruitment begins.

This is design work, not code. Block 3 days for it.

---

### E2. Lightbox + color card kit

**Goal.** Strip half of the lighting noise from collected data.

**Action.** Source 100 lightbox+color-card kits (~5 USD each on AliExpress,
total ~500 USD). Ship to the next batch of subjects with their cup.

This is procurement, not engineering, but it changes the data-quality
floor for every model trained from this point forward.

---

## Phase F — MASTER METRICS DASHBOARD

### F1. Replace headline AUC with a metrics tuple

**File to create.** `src/dashboard_metrics.py`

**Per-model report fields:**
- `auc_cv`: 5-fold GroupKFold AUC ± 95% CI.
- `auc_holdout`: held-out subject group AUC ± 95% CI.
- `delta_auc_vs_confound`: AUC over the confound-only baseline.
- `sens_at_spec95`: sensitivity at specificity 0.95.
- `brier`: Brier score on held-out.
- `ece`: expected calibration error on held-out.
- `phone_robustness`: AUC drop between in-domain and out-of-domain phones.

Internally, `delta_auc_vs_confound` and `auc_holdout` are the only two
numbers used to compare model versions.

---

## Phase G — WHAT TO STOP

The council was unanimous on these:

- **Stop reporting AUC numbers from model selection runs as if they were
  stable evaluations.** Every AUC must say which split it came from.
- **Stop comparing 0.774 vs 0.854 as if the difference were meaningful.**
  CIs overlap by a wide margin.
- **Stop using `gest_age_weeks` as a feature for the binary detection
  task, even ablated.** It is the label.
- **Stop publishing or sharing externally any number while the held-out
  group is untested.**

---

## Sanity check before declaring this plan done

After Phase A, the next training run produces:

```
[Holdout]
auc_cv         = 0.77 ± 0.08
auc_holdout    = 0.74 ± 0.10
delta_auc_vs_confound = 0.12  (urine signal exists)
sens_at_spec95 = 0.41
brier          = 0.18
ece            = 0.06
phone_robustness = -0.04 AUC (acceptable)
```

If `delta_auc_vs_confound < 0.05` with overlapping CI, halt all modeling
work and execute Phase E first. The signal is not in the urine pixels.

If `delta_auc_vs_confound > 0.10`, proceed to Phase B and C aggressively.

Either branch is real progress. The current state, where we don't know
which branch we're on, is the actual emergency.

---

## Decision log to maintain going forward

A new file `docs/decisions.md` records every model release with:
- Date.
- Council recommendation that motivated the change.
- Files changed.
- The seven metrics from F1 before and after.
- Decision: ship / revert / iterate.

This is the single artifact that keeps the project honest.
