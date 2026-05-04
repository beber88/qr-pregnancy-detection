# ACTION PLAN V2 - Pregnancy Detection AI
## Derived from 4-source LLM Council, 2026-05-04

> **Supersedes** ACTION_PLAN_FROM_COUNCIL.md (v1).
> v1 was based on the simulated council alone. v2 incorporates Perplexity,
> Gemini, and ChatGPT critiques. The full reasoning is in
> `מחקרים/llm_council_sessions/05_FINAL_SYNTHESIS_REPORT_20260504.md`.

---

## The seven-metric report (replaces "AUC headline")

Every model release from now on reports:

| Metric | Definition | Threshold |
|--------|-----------|-----------|
| `auc_cv` | 5-fold GroupKFold AUC, mean ± 95% CI | report only |
| `auc_holdout` | AUC on locked 25-subject holdout | primary internal metric |
| `delta_auc_vs_confound` | AUC(urine + confound) - AUC(confound only) | must be >= 0.05 |
| `sens_at_spec95` | Sensitivity at specificity 0.95 | primary external metric |
| `brier` | Brier score on holdout | <= 0.20 |
| `ece` | Expected calibration error on holdout | <= 0.07 |
| `phone_robustness` | AUC drop, in-domain phones vs out-of-domain | >= -0.05 (i.e., drop < 0.05) |

`auc_cv` and `auc_holdout` shown together. `delta_auc_vs_confound` is the
number that decides whether the urine signal is real. The old headline
`auc_cv = 0.774` is now meaningless without these companions.

---

## Effort allocation (revised from v1)

v1: 30 / 25 / 30 / 15 (data / protocol / features / modeling)
**v2: 35 / 32 / 22 / 10**

Roughly two-thirds of effort goes to data scale and protocol fixes.
Features and modeling combined are one-third. This is a meaningful
correction; v1 was over-bullish on features.

---

## Phase A - STATISTICAL HYGIENE (this week)

### A1. Lock holdout subject group

**File:** `data/processed/holdout_subjects.csv`

```python
# Pseudocode for one-shot creation
import pandas as pd
import numpy as np
HOLDOUT_SEED = 20260504
np.random.seed(HOLDOUT_SEED)
all_subjects = pd.read_csv("data/processed/survey_metadata_complete.csv")
positives = all_subjects[all_subjects.label == 1].sample(12, random_state=HOLDOUT_SEED)
negatives = all_subjects[all_subjects.label == 0].sample(13, random_state=HOLDOUT_SEED)
holdout = pd.concat([positives, negatives])
holdout.to_csv("data/processed/holdout_subjects.csv", index=False)
# COMMIT THIS FILE. Do not modify.
```

### A2. Confound-only baseline

**File:** `src/confound_baseline.py`

```python
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss

CONFOUND_FEATURES = ["age", "first_morning", "coffee", "fluids",
                     "has_health_condition", "phone_model_onehot"]
EXCLUDED_FEATURES = ["gest_age_weeks", "has_folic_acid",
                     "has_medications", "has_progesterone", "has_antibiotics"]

def run_confound_baseline(df, holdout_ids):
    train = df[~df.subject_id.isin(holdout_ids)]
    X = train[CONFOUND_FEATURES]
    y = train["label"]
    groups = train["subject_id"]
    cv = GroupKFold(n_splits=5)
    aucs = []
    for tr, te in cv.split(X, y, groups):
        m = LogisticRegression(C=1.0, max_iter=1000)
        m.fit(X.iloc[tr], y.iloc[tr])
        p = m.predict_proba(X.iloc[te])[:, 1]
        aucs.append(roc_auc_score(y.iloc[te], p))
    return np.mean(aucs), np.std(aucs)
```

**Decision rule on output:**
- < 0.55: no confound signal. V5's 0.774 is largely urine. Continue.
- 0.55-0.65: mild confound. Report ΔAUC, not raw AUC.
- 0.65-0.75: strong confound. Pivot to controlled protocol urgently.
- \> 0.75: V5 is mostly noise. Project hypothesis fails first test.

### A3. Aggregation audit

Read `src/features_v2.py` line by line. Verify every per-subject
aggregation (mean, std, min, max, CV) is computed inside-fold or is
deterministic per-subject and not influenced by other subjects' data.
Document each aggregation point with a one-line comment stating where it
runs.

### A4. Re-run V5 with new regime

Switch from current evaluation to nested-GroupKFold with held-out group.
Report all seven metrics. Save as `models/model_production_v5b.pkl`.

---

## Phase B - NOISE-FLOOR REDUCTION (next week)

### B1. Liquid ROI segmentation

**File:** `src/segment_cup.py`

Use SAM-H if compute allows, else classical Otsu + connected components on
the inner cup region. Crop every photo to the liquid region. Output to
`data/raw/cropped/`.

### B2. White-background color constancy

**File:** `src/color_constancy.py`

Detect white pixels in background, compute white-point, divide each channel
by white-point ratio, re-scale to [0, 255]. Save normalized photos to
`data/raw/normalized/`.

### B3. CIE Lab* + HSV features

**File:** `src/cielab_features.py`, `src/hsv_features.py`

Add 12 new features per image: L*, a*, b* mean/std/min/max, plus H/S/V
mean/std/min/max. Re-run feature extraction.

### B4. Cross-view dispersion features

**File:** `src/dispersion_features.py`

For each subject with 3+ photos, compute:
- pairwise ΔE2000 between photos (mean, max)
- Jensen-Shannon divergence between RGB histograms
- variance of highlight area (top 5% brightness pixels)
- brightness rank instability (correlation of brightness ranks across photos)

Add 8 new features per subject.

---

## Phase C - FEATURE CEILING TEST (weeks 2-3)

### C1. Frozen DINOv2 embeddings

**File:** `src/embed_dinov2.py`

```python
import torch
from transformers import AutoModel, AutoImageProcessor

model = AutoModel.from_pretrained("facebook/dinov2-large")
processor = AutoImageProcessor.from_pretrained("facebook/dinov2-large")
model.eval()

def embed_image(pil_image):
    inputs = processor(images=pil_image, return_tensors="pt")
    with torch.no_grad():
        out = model(**inputs)
    # Take CLS token: [1, 1024]
    return out.last_hidden_state[:, 0, :].squeeze().numpy()
```

Mean-pool per subject. Save to `data/processed/dinov2_embeddings.npy`.

### C2. Frozen VideoMAE embeddings

**File:** `src/embed_videomae.py`

Sample 16 frames uniformly from each 10s clip, run VideoMAE-base, take
[CLS]. Save to `data/processed/videomae_embeddings.npy`.

### C3. Nuisance-residualized features

**File:** `src/nuisance_residualize.py`

Inside each training fold:
```python
nuisance_X = train[NUISANCE_FEATURES]  # phone, lighting, time, hydration
for feat in URINE_FEATURES:
    reg = LinearRegression().fit(nuisance_X, train[feat])
    train[feat + "_resid"] = train[feat] - reg.predict(nuisance_X)
    test[feat + "_resid"] = test[feat] - reg.predict(test[NUISANCE_FEATURES])
```

Then train classifier on residuals + nuisance variables as separate covariates.

---

## Phase D - CALIBRATION (concurrent with C)

**File:** `src/calibrate_model.py`

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss

def calibrate(base_model, X_train, y_train, X_holdout, y_holdout):
    calib = CalibratedClassifierCV(base_model, method="isotonic", cv=5)
    calib.fit(X_train, y_train)
    p = calib.predict_proba(X_holdout)[:, 1]
    brier = brier_score_loss(y_holdout, p)
    ece = expected_calibration_error(y_holdout, p, n_bins=10)
    return calib, brier, ece
```

---

## Phase E - FALSIFICATION EXPERIMENT (planning this month)

**Goal.** Settle whether the urine appearance signal exists, in 4-8 weeks
of recruitment.

### Design (per ChatGPT, integrated with simulated council)

- N = 240. 120 confirmed pregnant 4-8 weeks (serum beta-hCG positive),
  120 confirmed non-pregnant (serum beta-hCG negative, ultrasound where
  feasible).
- 1:1 matched pairs on: first-morning yes/no, hydration bin (specific
  gravity bands), phone model, supplement use (folic acid, prenatal
  vitamins), caffeine in past 6 hours, age band, time-of-day window.
- Exclusion: gross hematuria, active UTI symptoms, urine-coloring
  medications.
- Same physical kit per subject: cup, mount, lightbox, color card, framing.
- Pipeline LOCKED before recruitment based on Phase A-D output. Single
  primary model. One challenger. No retuning during data collection.

### Pre-registration

- Platform: OSF
- Primary endpoint: subject-level AUROC of locked urine-only model on
  N=240 matched cohort.
- Secondary: calibration slope, calibration-in-the-large, Brier, ECE,
  sens at spec95, sens at spec70.
- No-go rule: AUROC < 0.70 OR lower 95% CI < 0.60 OR doesn't beat
  metadata-only baseline by >= 0.05. Either kills the project as a
  stick replacement.

### Mini consecutive cohort (immediately after main study)

- N = 50-75 unscreened, consecutive-arrival users.
- Same threshold, same pipeline, no matching.
- If discrimination or calibration collapse here while passing on the
  matched cohort, we know matched study confirms existence but not
  deployability.

---

## Phase F - METRICS DASHBOARD

**File:** `src/dashboard_metrics.py`

```python
def report_model(model, name, X_train, y_train, groups, X_holdout, y_holdout):
    # Run all 7 metrics
    return {
        "name": name,
        "auc_cv": cv_auc_with_ci(model, X_train, y_train, groups),
        "auc_holdout": holdout_auc_with_ci(model, X_holdout, y_holdout),
        "delta_auc_vs_confound": auc_holdout - confound_baseline_auc,
        "sens_at_spec95": sens_at_specificity(model, X_holdout, y_holdout, 0.95),
        "brier": brier_score_loss(y_holdout, p_holdout),
        "ece": expected_calibration_error(y_holdout, p_holdout),
        "phone_robustness": phone_family_drop(model, X_holdout, y_holdout),
    }
```

Output goes to `reports/metrics_<model_name>_<date>.json`.

---

## Phase G - WHAT TO STOP (unanimous council ruling)

1. Stop quoting AUC 0.95 as a fixed milestone. Replace with
   "external sens@spec95 >= 0.70 in intended-use subgroup".
2. Stop reporting AUC numbers from model selection runs as if they were
   stable evaluations.
3. Stop comparing 0.774 vs 0.854 as if the difference were meaningful.
4. Stop using `gest_age_weeks` and `has_folic_acid` as features for the
   binary detection task. Permanent ban.
5. Stop publishing or sharing externally any number while the held-out
   group is untested.

---

## Sanity check after Phase A

Expected output if signal is real:

```
[V5b]
auc_cv         = 0.77 ± 0.08
auc_holdout    = 0.74 ± 0.10
delta_auc_vs_confound = 0.12   <- URINE SIGNAL EXISTS
sens_at_spec95 = 0.41
brier          = 0.18
ece            = 0.06
phone_robustness = -0.04 AUC (acceptable)
```

If `delta_auc_vs_confound < 0.05` with overlapping CI, halt all modeling
and execute Phase E first. The signal is not in the urine pixels.

If `delta_auc_vs_confound > 0.10`, proceed to Phase B-D aggressively.

---

## End of action plan v2.

The full reasoning behind every item is in
`מחקרים/llm_council_sessions/05_FINAL_SYNTHESIS_REPORT_20260504.md`.

The strategic pivot question (Options A/B/C/D) is in §6 of the synthesis
report. That decision is yours.
