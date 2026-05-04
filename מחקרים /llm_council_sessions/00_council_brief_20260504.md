# COUNCIL BRIEF — Pregnancy Detection AI from Urine Photos

> Standing context to paste into the LLM Council before any question.
> Date of brief: 2026-05-04. Owner: Beber.

---

## 1. Vision and scientific question

We are building a smartphone-based pregnancy test that replaces the physical home stick.
The user urinates into a clear plastic cup, photographs and films it, and an ML model
returns a pregnancy probability.

The scientific question we are trying to falsify or confirm is:

> Does the visual signal in a urine photo and short video, captured under a strict
> protocol, contain enough information to separate pregnant from non-pregnant samples
> independently of questionnaire data, and can we reach AUC 0.95 or above?

If yes, this is the first zero-hardware pregnancy test. If no, we pivot.

Our current honest answer is: there is a real but modest signal,
AUC around 0.74 on photo+video features alone. Survey data inflates the score
but most of the gain is label leakage, not biology.

---

## 2. Data

- 101 subjects total. Original split: 46 positive, 55 negative.
- Open question: NEGATIVE_57 may be mislabeled positive (filled out
  "confirmed pregnant" on their survey but is filed in NEGATIVE/57).
  Same pattern as N22 which we already moved to POSITIVE_41.
  If reclassified: 47P + 54N.
- 1,227 photos and 68 video clips (typically 3 photos and 1 short video per subject).
- 40 of the 101 subjects so far have full survey metadata (age, hydration,
  first morning urine, coffee, medications, vitamins, health conditions,
  weeks pregnant for positives).
- The 61 older subjects (P1-P34, P41, N1-N28) still need their survey forms extracted.

Photography protocol:
- Clear plastic cup, white background, natural daylight.
- Phone held 30 cm from cup.
- 3 still photos at different angles plus a 10 second video.
- Photo taken within 60 seconds of urination.
- Phone model logged.

Known sources of noise in our data:
- Phone model variation (different white balance, different sensors).
- Lighting variation (collected at home, daylight only is the rule but
  not strictly verifiable).
- Hydration variation.
- Medications and supplements (notably folic acid, prenatal vitamins).
- Time of day (first morning urine differs from afternoon urine).

---

## 3. Pipeline as it stands

`src/build_index.py` indexes PICTURES/POSITIVE and PICTURES/NEGATIVE,
extracts 1 frame per second from each video, writes `data/processed/index.csv`.

`src/features_v2.py` computes 32 photo features per image
(RGB means and stds, HSV, CIELAB, color ratios such as g/y, r/b,
yellowness, saturation, turbidity proxies, Layla spectral ratios,
concentration darkness, hue spread). Then aggregates per subject into
mean, std, min, max plus engineered CV and ratio features.
137 photo features per subject after aggregation.

`src/video_features.py` computes 42 temporal features per clip:
hue/value/saturation trends and stds, optical flow coherence,
texture std over time, R-channel autocorrelation, color complexity.

Combined feature vector per subject: 179 dimensions.

`src/train_v2.py` trains photo-only, video-only, and combined models.
5-fold GroupKFold on subject ID (no subject leaks across folds).
SelectKBest with f_classif for k=50.
Best ensemble: SoftVoting of LogisticRegression(C=0.01) +
ExtraTreesClassifier(500, max_depth=5) + SVC(RBF, C=1.0).

`src/inference_v2.py` is the production inference path.
`src/api_v2.py` is the FastAPI server.

---

## 4. Current results

| Date | Subjects | Model | AUC | Sens | Spec | Notes |
|------|----------|-------|-----|------|------|-------|
| Apr 30 | 61 | Video RF | 0.825 | 0.865 | 0.480 | Overfit, low specificity |
| May 3 | 102 | Ensemble V3 | 0.854 | 0.810 | 0.619 | Non-reproducible fold split |
| May 4 | 101 | V4 urine only | 0.739 | 0.630 | 0.764 | Pure urine signal |
| **May 4** | **101** | **V5 urine + confounders** | **0.774** | **0.652** | **0.782** | **Honest production** |
| May 4 | 101 | V5-leaky urine + ALL survey | 0.907 | 0.761 | 0.873 | INVALID, label leakage |

The leaky version got AUC 0.907 because it included `gest_age_weeks`,
`has_folic_acid`, and `has_medications` as features. `gest_age_weeks` IS the label
in different form. `has_folic_acid` is taken because someone is pregnant or planning
pregnancy, not because of urine biology. `has_medications` correlates with pregnancy.

V5 is the honest model. It uses urine features plus only confounder controls
(age, first morning, coffee, fluids, health conditions) which help adjust for
non-pregnancy factors that affect urine appearance.

Top discriminating features (V4, urine only):
1. g_mean_std (photo green channel variability across a subject's photos)
2. lab_L_std (photo lightness variability)
3. gy_ratio_mean (photo green/yellow ratio)
4. conc_darkness_std (photo concentration variability)
5. brightness_std
6. t_r_ratio_complexity (video temporal R ratio complexity)
7. t_hue_mean (video temporal hue mean)
8. r_mean_std, b_mean_std, brightness_cv

In our May 3 run on 102 subjects, 12 of the top 20 features were video temporal.
In V4 with stricter aggregation, photo variability features dominate.
Both findings agree on one thing: variability across multiple frames or photos
of the same subject matters more than any single absolute color value.

---

## 5. Constraints, risks, and known weaknesses

- N is small. 101 subjects, 5-fold GroupKFold gives ~20 subjects per held-out fold.
  Confidence intervals on AUC are wide.
- Class balance is roughly 1:1, which is fine for AUC but the field deployment
  prior is more like 1:5 to 1:20.
- Lighting and phone model are confounders we have not formally controlled.
- We do not yet have an external validation cohort. All numbers are
  cross-validation on a single dataset.
- We have no clinical-grade ground truth besides self-report (home test,
  blood test, ultrasound). 1 to 2 mislabels are plausible.
- Regulatory: this is research only. We cannot claim diagnostic performance.
- The 0.95 AUC target may be unreachable from urine appearance alone.
  The biological literature on visible urine differences in early pregnancy is thin.

---

## 6. What we want from the council

A council session is most useful when each model can disagree productively
on one of these axes:

- Is the underlying visual signal real and stable, or are we surfing confounders?
- Where is the next ten-AUC-points coming from: data, features, or model?
- What experiments would falsify the hypothesis fastest?
- What is the right validation setup for an eventual regulatory pivot?

Treat the brief above as fixed shared context. The actual question follows.
