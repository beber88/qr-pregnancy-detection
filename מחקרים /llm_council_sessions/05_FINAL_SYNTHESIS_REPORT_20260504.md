# FINAL SYNTHESIS REPORT - 2026-05-04
## Pregnancy Detection AI - Master integration of 4-source LLM Council

> **Provenance.** This document integrates four independent expert critiques on
> the project state as of 2026-05-04. All four sources read the same factual
> brief and answered the same questions, with the noted exception of Gemini
> which produced a comprehensive Hebrew literature review instead of a
> structured Q1-Q5 response.
>
> **Sources:**
> 1. **Simulated Council** - my 4-agent simulation (Stat / MMCV / EXP / SKEP / MLENG lenses)
> 2. **Perplexity** - structured response with literature anchor
> 3. **Gemini** - comprehensive Hebrew biomedical literature review
> 4. **ChatGPT (GPT-5)** - rigorous structured response with literature anchor
>
> **Purpose.** This is the single document that drives integration into the
> codebase. It supersedes the v1 ACTION_PLAN_FROM_COUNCIL.md.

---

## EXECUTIVE SUMMARY

Three findings dominate the entire 4-source council:

**1. The methodology call is correct, but the deeper risk is one we hadn't named.**
All four sources confirm that V5 (AUC 0.774) is the honest model and V5-leaky
(AUC 0.907) is invalid because of `gest_age_weeks` and `has_folic_acid`. The
*more dangerous* leakage path that ChatGPT and the simulated council both
flagged independently: model selection performed on the same CV folds we
report AUC on. The May 3 ensemble result of 0.854 is partly an artifact of
selection-on-folds. This is the single most consequential methodology issue.

**2. The literature changes our target.** Gemini and Perplexity surfaced
prior art (Bustam, Flaucher, Shen Stanford, buffalo NMR, Zhang preeclampsia)
that all point to the same conclusion: **the urine pregnancy signal is real
at molecular level (LC-MS, NMR), not at smartphone-RGB level**. There is no
published precedent for detecting pregnancy from raw urine appearance alone
via smartphone. Successful smartphone urine CV in prenatal care all uses
reagent strips. This re-anchors the AUC 0.95 target as biologically
aspirational rather than the fixed milestone.

**3. The next step is unanimous: scale + protocol, not features.** Three of
four sources (Perplexity, ChatGPT, simulated council with revisions)
allocate 60-80% of effort to data scale and protocol fixes (lightbox + color
card + locked rig), and only 15-30% to features. Of the four, only my
original simulated council was bullish on DINOv2/VideoMAE; ChatGPT and
Perplexity both rate frozen embeddings at medium-low confidence at N=101.
The corrected effort allocation across the council is roughly **A=40, B=30,
C=20, D=10** (data, protocol, features, modeling).

---

## SECTION 1 - WHERE THE COUNCIL CONVERGES (4 of 4)

These are the decisions that are now ready for execution. No further
debate needed.

### 1.1 Leakage taxonomy

| Concern | Verdict |
|---------|---------|
| `gest_age_weeks` as feature for binary detection | **LEAKAGE. Permanently exclude.** All 4 agree. ChatGPT calls it "target encoding". Valid only for staging-among-confirmed-pregnancies, not screening. |
| `has_folic_acid` as feature for binary detection | **Leakage in current dataset. Defensible only in different recruitment / different task framing.** All 4 agree. |
| GroupKFold by subject | **Necessary but not sufficient.** All 4 agree. |
| SelectKBest fit inside fold | **Correct as far as it goes.** All 4 agree. |
| Per-subject aggregation before split | **Concerning. Requires explicit audit.** 3 of 4 explicitly flag (ChatGPT, Perplexity, simulated council). |
| **Model selection on the same folds reported** | **THE most underestimated leakage path.** ChatGPT and simulated council surfaced this independently. |

### 1.2 Mandatory next experiments

All four sources independently call for these, in roughly this order of priority:

1. **Confound-only baseline.** Train a metadata-only model (no urine pixels)
   on age, hydration, first-morning, phone-model, time-of-day, with `gest_age_weeks`,
   `has_folic_acid`, `has_medications` EXCLUDED. Same 5-fold GroupKFold.
   Quantify ΔAUC = AUC(urine + confounds) - AUC(confounds only). This is the
   single experiment that decides whether the urine signal is real.

2. **Held-out subject group.** Lock 25 subjects, never look at them until
   model is frozen. ChatGPT goes further and proposes a chronological holdout
   of the last 120 collected, but at our N=101 a subject-level lock is the
   pragmatic implementation.

3. **Aggregation-leakage audit.** Verify per-subject statistics are fit
   inside each fold only.

4. **Locked-pipeline rerun.** Pick one model, lock all hyperparameters,
   evaluate once on the holdout. Stop the practice of "best CV over many tries".

### 1.3 Validation requirements before any product claim

All four converge on:

- External cohort, prospective, 400-600 subjects minimum.
- Phone-model robustness with leave-one-phone-family-out development.
- Calibration metrics mandatory (Brier, ECE, calibration slope), not just AUC.
- Sub-group reporting: gestational age band, first-morning, hydration bin,
  folic acid use, phone family, age band, health-condition strata.
- Pre-registration on OSF/ClinicalTrials.gov before recruitment.
- Single blocking result: failure on the intended-use subgroup
  (early gestation, primary phone family) at the locked threshold.

### 1.4 The biological ceiling argument

All four sources reach the same conclusion through different paths:

- **Perplexity:** buffalo NMR metabolomics maxes at AUC ~0.8 with direct
  molecular access.
- **Gemini:** Stanford LC-MS/MS metabolomics for gestational dating reached
  R=0.95, but with molecular-level resolution, not photo.
- **ChatGPT:** "I cannot find a peer-reviewed paper showing pregnancy detection
  from raw urine appearance via smartphone."
- **Simulated council:** acknowledged via Skeptic lens that the visible
  signal may not exist independent of confounds.

**Implication:** AUC 0.95 from raw smartphone RGB is biologically aspirational.
The right operating-point milestone is **external sensitivity at specificity
0.95 >= 0.70 within the intended-use subgroup**.

---

## SECTION 2 - WHERE THE COUNCIL DIVERGES (and how to resolve)

### 2.1 Effort allocation: 100 points across data / protocol / features / modeling

| Source | A. Data | B. Protocol | C. Features | D. Modeling |
|--------|---------|-------------|-------------|-------------|
| Simulated Council | 30 | 25 | 30 | 15 |
| Perplexity | 35 | 30 | 25 | 10 |
| ChatGPT | 45 | 35 | 15 | 5 |
| Gemini (inferred) | ~30 | ~40 | ~20 | ~10 |
| **Council mean** | **~35** | **~32** | **~22** | **~10** |

**Resolution.** ChatGPT is the most aggressive on data+protocol; my
simulation was the most bullish on features. The mean is **~35/32/22/10**.
Adopt this. The actionable read: **two-thirds of effort on data quantity
and quality, one-third on features and modeling combined.** This is a
significant correction of the v1 action plan, which was 30/25/30/15.

### 2.2 The single highest-yield experiment

| Source | Top experiment |
|--------|---------------|
| Simulated Council | DINOv2 + VideoMAE frozen embeddings + LightGBM, evaluated on holdout |
| Perplexity | Recruit 300-400 new subjects with improved protocol, retrain V5-style |
| ChatGPT | 300 new subjects with rock-solid rig (lightbox, color card, fixed cup), urine-only baseline LOCKED, success threshold AUC >= 0.82 with lower CI 0.75 |
| Gemini (inferred) | Improve protocol + adopt CIE Lab* / HSV features + add multi-biomarker chemistry context |

**Resolution.** The data-scale-with-protocol experiment wins 2-1 over the
features experiment. The integrated design from ChatGPT and Perplexity:

- 300 new subjects, 150 confirmed pregnant 4-8 weeks (serum beta-hCG),
  150 confirmed non-pregnant.
- Lightbox + color card + fixed cup + fixed phone-mount.
- Single locked baseline: handcrafted features on ROI-segmented liquid
  region, with white-balance via background, LogisticRegression.
- Single challenger: frozen DINOv2 linear probe.
- Held-out chronological group of 120.
- Success: external AUROC >= 0.82, lower 95% CI >= 0.75, metadata-only
  baseline does not exceed 0.60.
- Falsification: external AUROC < 0.75 OR improvement < 0.03 over current
  baseline. Either kills the project as a stick-replacement.

### 2.3 Falsification experiment design

| Source | Design |
|--------|--------|
| Simulated Council | Within-subject longitudinal: 60 TTC + 30 prenatal-vitamin contraception controls, 3 cycles |
| Perplexity | Cross-sectional matched case-control N=100-120 |
| ChatGPT | Cross-sectional matched case-control N=240 (120P + 120N), 1:1 matched on first-morning, hydration, phone, supplement use, time |
| Gemini (inferred) | Did not propose specific design |

**Resolution.** Cross-sectional matched wins 2-1 over within-subject
longitudinal. ChatGPT's design at N=240 is the most disciplined. The
within-subject ideas from my simulation should be integrated as a
*sensitivity analysis* on the matched cohort: pair each pregnant subject
with a non-pregnant one matched on phone+hydration+time, and report the
within-pair difference as a robustness check.

### 2.4 Confidence in deep features

| Source | Verdict on DINOv2 / VideoMAE at N=101 |
|--------|---------------------------------------|
| Simulated Council | medium-high; expected ΔAUC +0.04 to +0.08 |
| Perplexity | medium-low; ΔAUC +0.02 to +0.05 |
| ChatGPT | medium-low; "won't rescue you from weak measurement and small data" |
| Gemini | did not weigh in directly |

**Resolution.** My simulation overestimated. The corrected expected ΔAUC
from frozen embeddings at N=101 is **+0.02 to +0.05 with medium-low
confidence**. Move from priority #1 to priority #3 in the feature
engineering plan. ROI segmentation + color constancy moves up to #1
(this is now the unanimous top feature engineering recommendation).

### 2.5 Top feature engineering moves: integrated ranking

Combining ChatGPT (most explicit) with Perplexity and the simulated council:

| Rank | Move | ΔAUC | Confidence | Source agreement |
|------|------|------|-----------|------------------|
| 1 | Liquid ROI segmentation + white-background color constancy | +0.03 to +0.06 | medium | All 3 explicit sources rate this top-2 |
| 2 | Cross-view dispersion features (pairwise ΔE2000, JS divergence, brightness rank) | +0.02 to +0.04 | medium | ChatGPT unique; aligns with our top-feature observation |
| 3 | CIE Lab* turbidity features (L* especially), HSV color features alongside RGB | +0.01 to +0.03 | medium | Gemini biomedical literature; novel addition |
| 4 | Frozen DINOv2 ViT-B/14 liquid-ROI embeddings, PCA-50 inside fold | +0.02 to +0.05 | medium-low | All 3 mention; downgraded from #1 |
| 5 | Nuisance-residualized features (regress out phone, lighting, time-of-day) | 0 to +0.03 | medium | ChatGPT unique; very useful diagnostic |
| 6 | Frozen VideoMAE temporal embeddings | +0.01 to +0.03 | low | All 3; rated lowest at N=68 clips |

**Mandatory addendum.** Isotonic calibration + Brier/ECE reporting on every
trained model. All four sources demand this.

---

## SECTION 3 - NEW EVIDENCE NOT IN THE V1 PLAN

These findings were surfaced by the council and were not in the previous
action plan. They change project decisions.

### 3.1 The smartphone-CV literature uses reagent strips, not raw urine

**Source.** ChatGPT explicit; Gemini implicit (Healthy.io, uChek, Flaucher
papers all use strips).

**Implication.** Our project's premise of "no hardware, just photo of urine
in cup" has no published precedent in the smartphone-CV literature. Every
successful smartphone urinalysis paper from 2018 onward leverages either
(a) reagent strips, or (b) a calibration card / lightbox / fixed rig.

**Decision required.** This raises a strategic question we must address
explicitly (see Section 6).

### 3.2 Dehydration is a strong visible-light signal in raw urine

**Source.** Perplexity Bustam 2023 + ChatGPT same citation.

**Implication.** Our top features (g_mean_std, lab_L_std, brightness_std,
gy_ratio_mean) are highly correlated with hydration. We may be partly
detecting hydration differences between pregnant and non-pregnant women,
not pregnancy itself. Pregnant women in early gestation with morning sickness
are often dehydrated; non-pregnant women in our recruitment are not. This is
a confound mechanism more biologically specific than we previously articulated.

**Action.** Add specific gravity or urine osmolality (or self-reported
hydration as proxy) as an explicit covariate. Stratify all reporting by
hydration band. Match on hydration in the falsification experiment.

### 3.3 The Stanford XGBoost gestational-dating result

**Source.** Gemini Hebrew review, citing a Stanford LC-MS/MS metabolomics
study with R=0.95 in CA cohort.

**Implication.** When people see "R=0.95 for predicting pregnancy
information from urine," they think this validates our approach. It does
not. That R=0.95 is from molecular-level metabolomics with 6 specific
metabolites measured by mass spectrometry, not from smartphone photos.
Whenever the project communicates externally, this distinction must be
preserved.

### 3.4 CIE Lab* L* threshold for turbidity

**Source.** Gemini Hebrew review, citing L*<89.165 -> AUC 0.984 for
clear vs turbid urine.

**Implication.** A specific, validated turbidity threshold exists. We
should compute L* explicitly on each photo and use it as a feature.
Pregnant urine in early gestation is more often dilute (low turbidity,
high L*) than non-pregnant urine, but this is largely a hydration-axis
confound (see 3.2).

### 3.5 HSV more robust than RGB

**Source.** Gemini.

**Implication.** All our color features are computed in RGB. Convert
all to HSV (or include both spaces) and let the ablation tell us which
is stronger. Specifically Hue is more robust to lighting than R/G/B.

### 3.6 Healthy.io 510(k) regulatory precedent

**Source.** Gemini.

**Implication.** Healthy.io secured 510(k) by demonstrating substantial
equivalence to a cleared lab reader (ACON Mission U500) and using a
physical color calibration card. This is the regulatory pathway any
smartphone urinalysis product takes. We should fold this into the
existing `regulatory_roadmap_pregnancy_ai.md` document.

### 3.7 PE biomarkers (KIM-1, MCP-1, hexadecanal)

**Source.** Gemini.

**Implication.** Not directly actionable for our pregnancy-detection task,
but useful background context. If the project pivots to a broader
prenatal-monitoring app (PE risk + gestational dating + pregnancy
confirmation), these are the molecular targets.

---

## SECTION 4 - INTEGRATED ACTION PLAN (supersedes v1)

The execution sequence below merges all four sources. Items in **bold** are
unanimous. Items in *italic* are 3-of-4 consensus. Items in regular text
are 2-of-4 with no objection.

### Phase A - STATISTICAL HYGIENE (this week)

**A1.** Lock holdout subject group of 25 (12P + 13N stratified). File:
`data/processed/holdout_subjects.csv`. Random seed `HOLDOUT_SEED = 20260504`.
Once committed, do not modify.

**A2.** Run confound-only baseline (`src/confound_baseline.py`). Report
ΔAUC = AUC(urine + confound) - AUC(confound only) as the primary internal metric.

**A3.** Audit per-subject aggregation. Verify all per-subject statistics
are computed inside-fold only. Document in code comments.

**A4.** Re-run V5 with the new evaluation regime: nested GroupKFold,
held-out group, ΔAUC vs confound, calibration metrics. Report the seven
metrics: auc_cv, auc_holdout, delta_auc_vs_confound, sens_at_spec95,
brier, ece, phone_robustness.

### Phase B - NOISE-FLOOR REDUCTION (next week)

**B1.** Implement liquid ROI segmentation (`src/segment_cup.py`). Use SAM-H
or simpler classical segmentation if SAM is heavy. Crop to liquid region.

**B2.** Implement white-background color constancy (`src/color_constancy.py`).
Compute white-point from background pixels in each photo and normalize.
Re-run all features.

*B3.* Add CIE Lab* features to feature stack: L*, a*, b* per image plus
their per-subject summaries. Add HSV variants of every existing RGB
feature (or replace RGB with HSV; let ablation decide).

*B4.* Add cross-view dispersion features: pairwise ΔE2000 between the 3
photos per subject, JS divergence between color histograms, brightness
rank instability.

### Phase C - FEATURE CEILING TEST (weeks 2-3, only after Phase A passes)

C1. Frozen DINOv2-large or ViT-B/14 image embeddings. PCA-50 inside
fold. L2 logistic with concat to 5 confounder controls. Evaluate on
holdout. Falsification: holdout AUC <= V5 baseline.

C2. Frozen VideoMAE-base [CLS] on 10s clips. Concat with #1 only if #1
beats baseline. Falsification: video features add < 0.02 over #1 alone.

*C3.* Nuisance-residualized features as a diagnostic. Regress phone-model,
background luminance, exposure, white-balance, first-morning, time-bucket
out of every feature inside-fold. Compare honest CV with and without
residualization. If residualization drops AUC by more than 0.05, we have
been training on shortcuts.

### Phase D - CALIBRATION (concurrent with C)

**D1.** Wrap final model in `CalibratedClassifierCV(method="isotonic", cv=5)`.
Add Brier and ECE to every training report. Plot reliability diagram.

**D2.** Threshold lock: select the operating threshold once, on training
data, and never re-tune on the holdout.

### Phase E - EXPERIMENTAL PROTOCOL (this month - planning, not data collection)

**E1.** Write the matched falsification protocol document
`docs/falsification_protocol_v1.md` based on the integrated design in §2.3:
- N=240 (120P + 120N), 4-8 weeks gestation, serum beta-hCG ground truth
- 1:1 matched on first-morning, hydration bin, phone model, supplement
  use, time of day, age band
- Lightbox + color card + fixed cup + fixed phone mount
- Locked pipeline before data collection begins
- Pre-registered on OSF
- Pre-registered no-go: AUROC < 0.70 OR lower CI < 0.60 OR doesn't beat
  metadata-only baseline by 0.05
- Mini consecutive cohort of 50-75 unscreened users immediately after,
  same threshold, as deployability check

**E2.** Source 250 lightbox + color card kits (~1500 USD). Standardize
the kit and the protocol document before any new subject is recruited.

**E3.** Update `discovery_protocol_longitudinal_urine_imaging.md` with the
new matched-cohort design.

### Phase F - METRICS DASHBOARD

**F1.** Replace headline AUC with the seven-metric tuple in every internal
report. File: `src/dashboard_metrics.py`.

**F2.** Decision log file `docs/decisions.md` records every model release
with date, motivating council recommendation, files changed, before/after
metrics, and decision (ship / revert / iterate).

### Phase G - WHAT TO STOP (unanimous)

- **Stop reporting AUC numbers from model selection runs as if they were
  stable evaluations.**
- **Stop comparing 0.774 vs 0.854 as if the difference were meaningful.**
- **Stop using `gest_age_weeks` and `has_folic_acid` as features for the
  binary detection task.** Period.
- **Stop quoting AUC 0.95 as a fixed milestone.** Replace with "external
  sensitivity at specificity 0.95 >= 0.70 within intended-use subgroup".
- **Stop publishing or sharing externally any number while the held-out
  group is untested.**

---

## SECTION 5 - CODE-LEVEL CHANGES

Concrete files to create or modify in `src/`. Estimated effort in parentheses.

### New files

```
src/confound_baseline.py            (~80 lines, 1 day)
src/segment_cup.py                  (~150 lines, 2 days)
src/color_constancy.py              (~100 lines, 1 day)
src/cielab_features.py              (~80 lines, 0.5 day)
src/hsv_features.py                 (~80 lines, 0.5 day)
src/dispersion_features.py          (~120 lines, 1 day)
src/embed_dinov2.py                 (~100 lines, 1 day)
src/embed_videomae.py               (~100 lines, 1 day)
src/nuisance_residualize.py         (~100 lines, 1 day)
src/dashboard_metrics.py            (~150 lines, 1 day)
src/calibrate_model.py              (~80 lines, 0.5 day)
docs/falsification_protocol_v1.md   (planning, 3 days)
docs/decisions.md                   (template, 0.5 day)
data/processed/holdout_subjects.csv (one-shot creation)
```

### Modifications to existing files

```
src/features_v2.py     - audit aggregation timing, add fold-only computation guarantee
src/train_v2.py        - exclude holdout, integrate calibration, switch to nested CV
src/inference_v2.py    - load calibrated model, apply nuisance residualization
src/api_v2.py          - update model loader to V6 once trained
README.md              - update headline metrics tuple, remove 0.95 target
```

### Total estimated effort

Approximately **3 weeks of focused engineering work** to implement Phases A
through D. Plus **2 weeks of planning** for Phase E. Plus **6-8 weeks of
data collection** if Phase E goes ahead. Total: 11-13 weeks to a defensible
external evaluation.

---

## SECTION 6 - THE EXISTENTIAL PIVOT QUESTION

The council surfaced something the user explicitly asked us to be ready
to confront: "If yes - we have a breakthrough. If no - we pivot."

The aggregated literature evidence is:

1. There is no published precedent for pregnancy detection from raw urine
   appearance via smartphone. (ChatGPT explicit; Gemini implicit through
   the Healthy.io / Flaucher / uChek lineage of strip-based products.)
2. The molecular pregnancy signal in urine is real but sits at LC-MS / NMR
   resolution, not smartphone-RGB resolution. (Stanford 6-metabolite,
   buffalo NMR, Zhang PE.)
3. Dehydration is a strong confounding signal in raw urine appearance.
   (Bustam 2023.)
4. Even with optimal protocol (lightbox + color card + locked rig), the
   council's most-pessimistic-case expected external AUC is 0.75-0.82,
   not 0.95.

**This means: the project as currently scoped (zero hardware, just photo)
may not be biologically achievable to AUC 0.95.** The council does not
say it's impossible. It says the literature gives no precedent, and the
biological ceiling from molecular methods is not 0.95.

The strategic options the council collectively raises are:

### Option A: Continue as planned, accept lower target
- Target: external sensitivity at specificity 0.95 >= 0.70 within intended-use
  subgroup.
- Position the product as a "screening / probability indicator" not a
  "diagnostic test".
- Regulatory path: less stringent than diagnostic claim.

### Option B: Hybrid product (smartphone + minimal calibration card)
- Adds a printed color/lightbox card the user includes in the photo.
- Still no chemistry, still much cheaper than a stick.
- Regulatory path: Healthy.io precedent, well-trodden 510(k) route.

### Option C: Hybrid product (smartphone + reagent strip)
- Adds a cheap reagent strip (still costs less than current sticks).
- Has published smartphone-CV precedent (Flaucher 2022, Healthy.io products).
- Likely route to AUC 0.95+ but loses the "no hardware" claim.

### Option D: Pivot to adjacent visible-light task with proven feasibility
- Dehydration tracking (Bustam 2023): proven smartphone CV signal.
- UTI screening: proven smartphone CV signal in literature.
- Gestational dating among confirmed pregnancies: would need molecular
  collection, not pure photo.

**This decision is yours, not the council's.** The council is unanimous
that the existing data does not yet rule out Option A, but the literature
makes Option A's success genuinely uncertain. Phase E (the falsification
experiment) is designed precisely to make this decision evidence-based.

---

## SECTION 7 - DECISION LOG SEED

This is the first entry in `docs/decisions.md`. Every future model release
or methodology change appends a similar entry.

```markdown
## 2026-05-04 - Council synthesis adopted, V5 frozen, V6 plan locked

**Triggering event.** 4-source LLM Council session
(simulated_council + Perplexity + Gemini + ChatGPT).

**Decisions.**
1. V5 (AUC 0.774) is the last model in the unaudited regime. No new
   models trained until Phase A (statistical hygiene) is complete.
2. The headline AUC reporting practice is replaced with the seven-metric
   tuple defined in F1.
3. The 0.95 internal AUC target is replaced with "external sensitivity
   at specificity 0.95 >= 0.70 in the intended-use subgroup".
4. `gest_age_weeks`, `has_folic_acid`, `has_medications` are PERMANENTLY
   excluded from the binary-detection feature set. They may be used only
   in a separate staging task on confirmed pregnancies.
5. Phase A through D engineering work is sized at ~3 weeks. Phase E
   experimental protocol planning is sized at 2 weeks. Phase E data
   collection (if approved) is sized at 6-8 weeks.

**Files affected.** All of `src/*.py` will be touched. New
`docs/falsification_protocol_v1.md` to be written. Existing
`regulatory_roadmap_pregnancy_ai.md` to be updated with Healthy.io 510(k)
precedent.

**Council documents that drove this.** All five files in
`מחקרים/llm_council_sessions/`. Master synthesis in
`05_FINAL_SYNTHESIS_REPORT_20260504.md` (this file).
```

---

## SECTION 8 - WHAT TO DO TODAY, THIS WEEK, THIS MONTH

### Today (90 minutes)
1. Read this synthesis report end to end.
2. Decide: do you accept the corrected effort allocation (35/32/22/10)?
3. Decide: do you accept the corrected target (sens@spec95 >= 0.70 instead
   of AUC 0.95)?
4. Decide: are you willing to lock the holdout group and never look at it?

### This week (5 days)
1. Implement A1 + A2 + A3 (holdout lock, confound baseline, aggregation
   audit). Approximately 2-3 days of code.
2. Re-run V5 under the new evaluation regime. Half a day.
3. Read the seven-metric output. Make the strategic call: do we proceed to
   Phase B (improve current pipeline) or jump straight to Phase E
   (falsification experiment)?

### This month (4 weeks)
1. Phase B (ROI segmentation, color constancy, Lab*/HSV features, cross-view
   dispersion). Approximately 2 weeks of code.
2. Phase C (DINOv2 ablation). 1 week of code.
3. Phase D (calibration). Concurrent.
4. Phase E planning document. 3 days.
5. Source the lightbox + color card kits. Procurement, not engineering.

### Next 8-12 weeks
1. If Phase A through D produce holdout AUC > 0.78 with calibration
   metrics in range: launch Phase E (240-subject prospective falsification
   study).
2. If they produce holdout AUC <= 0.74: this is the point to seriously
   consider Options B, C, or D from §6.

---

## End of synthesis. The full deliverable is now ready for system integration.

> **Filing.** This document lives at:
> `מחקרים/llm_council_sessions/05_FINAL_SYNTHESIS_REPORT_20260504.md`
>
> The corresponding executable plan lives at:
> `ACTION_PLAN_V2_FROM_COUNCIL.md` (project root).
>
> The original v1 plan at `ACTION_PLAN_FROM_COUNCIL.md` is preserved for
> historical comparison but is now superseded.
