# SIMULATED COUNCIL SESSION — 2026-05-04

> **Provenance note.** This document was produced inside Cowork mode by a single Claude
> instance (the user's assistant) that cannot reach OpenRouter from its sandbox.
> It is therefore not a real 5-LLM run. It is one model deliberately reasoning across
> five distinct expert lenses that mirror the personas the user picked. Treat the
> disagreements between lenses as genuine, but treat the overall confidence as lower
> than what an actual GPT-5.1 + Gemini 3 + Claude 4.5 + Grok 4 + DeepSeek R1 run would
> deliver. Re-run on the real council when an OpenRouter key is connected, then merge
> the deltas.

---

## Council members and lens definitions

| Lens | Tag | Default stance |
|------|-----|----------------|
| Statistician | `[STAT]` | Confounding, leakage, sample size, calibration, CIs |
| Multimodal CV | `[MMCV]` | Foundation models, video architectures, color constancy |
| Experimentalist | `[EXP]` | Falsification, pre-registration, decision rules |
| Skeptic | `[SKEP]` | Refuses to assume the signal exists; argues for the null |
| ML Engineer | `[MLENG]` | Modeling tricks, pretraining, MIL, training efficiency |

Brief used: COUNCIL_BRIEF.md (101 subjects, V5 AUC 0.774, target 0.95+, etc.).

---

# Q1. Methodology validity

## Stage 1 first opinions

**[STAT].** V5's call is correct in spirit but partially miscalibrated.
`gest_age_weeks` is straight leakage when the task is binary detection: it's the
label conditional on the positive class, mapped through a continuous variable.
`has_folic_acid` is a *proxy* for being pregnant or trying. It's not an inherent
biological label, but in the data it functions as one because the negative class
contains very few women trying to conceive. So in *this dataset* it leaks; in a
deployment where users opt in independently of conception intent, it would be a
weak prior, not a leak. The right move is to keep two evaluation tracks: "urine
only" (V4-style) and "urine + pre-collected priors except `gest_age_weeks`",
report both, and never publish only the leakier one.
The biggest residual leakage path I worry about is *per-subject feature
aggregation done before the train/test split*. If `g_mean_std` is computed
across all photos of a subject, then SelectKBest + scaler are fit inside the
fold but the per-subject statistics already carry the subject's identity.
That's not a leak across folds because GroupKFold splits by subject, but it
inflates effective sample size: the subject-level statistic is a single
measurement, not 12. Confidence intervals on AUC are therefore wider than
reported.

**[MMCV].** The methodology around evaluation is sound. The under-discussed
issue is that the *features themselves* are over-engineered hand-crafted color
moments. A learned representation would either confirm the AUC ceiling is real
biology or break through it. I'd not call any of the three concerns "wrong" but
I would re-rank them with calibration as the urgent gap. AUC tells you ranking;
it doesn't tell you whether 0.7 from the model means 0.7 in the real world.

**[EXP].** All three concerns matter. The decisive one for *publication or
product* is the validation framework, not the leakage debate. You have AUC
~0.77 honestly and ~0.91 with leakage. Either way, with N=101 and self-reported
labels including one suspected mislabel, the 95% CI on AUC is roughly
±0.08 to ±0.10. So 0.774 and 0.854 are statistically indistinguishable. This
fact alone is more important than the leakage question. Pre-register the
analysis going forward; stop comparing point estimates as if they were stable.

**[SKEP].** I want to push back on the framing. The brief says "honest AUC 0.774"
and "the signal is real but modest." Both of those are stronger claims than the
data supports. With 101 subjects and self-report ground truth, an AUC near 0.75
is in the same band as "phone model bias plus hydration bias" could easily
produce. I would not be surprised if a careful confound-only baseline (predict
pregnancy from phone-model + first-morning + hydration alone, no urine pixels)
produced AUC in the 0.65 to 0.72 range. That number is the one missing from the
brief and it determines whether your urine signal exists at all.

**[MLENG].** Two leaks the brief does not address. (1) Video frame extraction at
1 fps then per-clip features: if a clip is split into frames and frames go into
training without subject grouping, that *is* a leak; need to confirm the
GroupKFold groups by subject ID across both photos and frames. (2) The
SoftVoting ensemble was *selected* across many configurations on the same CV
folds. That's classic CV-set overfitting; the reported 0.854 in May 3 is partly
HARKing. Use a held-out subject group not touched during model selection.

## Stage 2 anonymized peer review (compressed)

Models converge on:
- `gest_age_weeks` is leakage. No defense.
- `has_folic_acid` is leakage *in this dataset* but plausibly defensible as a
  prior in deployment with different recruitment.
- The most consequential overlooked issue is hyperparameter/model selection
  performed on the same CV folds used to report performance.

Models disagree on:
- [SKEP] alone insists on a confound-only baseline before declaring any urine
  signal real. [STAT] and [EXP] endorse this; [MMCV] thinks it's redundant if a
  learned-feature ablation is done; [MLENG] sides with [SKEP] on the principle.

## Aggregate ranking

1. [STAT] (most precise on the actual leakage taxonomy)
2. [MLENG] (caught the model-selection-on-CV-folds problem nobody had named)
3. [SKEP] (forced the missing baseline question)
4. [EXP] (right on CIs, lighter on actionable paths)
5. [MMCV] (correct but partly tangential to Q1)

## Stage 3 chairman synthesis

Three things are true at once.

First, V5's leakage call is mostly right. `gest_age_weeks` is leakage, full
stop. `has_folic_acid` is leakage in this dataset because of recruitment, not
because of biology; flag it as a deployable prior only when the deployed
population is recruited independently of conception intent.

Second, the more dangerous leakage is the one we did not name: model selection
done across the same 5-fold CV folds we reported AUC on. The May 3 result
of 0.854 from SoftVoting "best-of-many" is partially overfit to the fold split.
Lock a held-out *subject* group of 20 to 30 subjects, do not look at it until
all hyperparameters are frozen, and use it as the only number that goes
outside the team.

Third, before any further modeling work, run a confound-only baseline:
predict pregnancy using phone model, first-morning urine, hydration, age,
medications-but-not-prenatal, with zero urine pixels. If that baseline reaches
AUC 0.7+, then a meaningful chunk of our 0.774 is not biology, and we should
not publish a "urine signal exists" claim until the urine-only model beats the
confound-only model with a non-overlapping CI.

**One experiment per concern (in priority order):**

1. *Confound-only baseline:* logistic regression on metadata only, no images,
   same 5-fold GroupKFold. Pin down ΔAUC = AUC(urine+confound) − AUC(confound only).
   If ΔAUC < 0.05 with overlapping 95% CI, declare the urine signal not yet
   demonstrated and stop modeling until protocol fixes are in place.
2. *Held-out test group:* lock 25 subjects (12P, 13N) as untouched test.
   Re-run V5 frozen on the remaining 76 with a single round of model selection.
   Final AUC reported only on the held-out group.
3. *Aggregation leakage check:* refit per-subject statistics inside each
   training fold only, never on full data. Compare to V5. If AUC drops by
   more than 0.03, the prior reported numbers were inflated.

---

# Q2. Where the next 10 AUC points come from

## Stage 1 first opinions (effort allocation out of 100)

| Lens | A. Data | B. Protocol | C. Features | D. Modeling |
|------|--------|------------|------------|------------|
| [STAT] | 50 | 30 | 10 | 10 |
| [MMCV] | 15 | 10 | 55 | 20 |
| [EXP] | 35 | 35 | 15 | 15 |
| [SKEP] | 40 | 50 | 5 | 5 |
| [MLENG] | 25 | 15 | 30 | 30 |
| **Mean** | **33** | **28** | **23** | **16** |

**[STAT].** With 101 subjects, every architectural improvement is fitted to
noise. Going from 100 to 300 subjects mechanically tightens AUC CIs from ±0.10
to ±0.05. That alone often jumps reported AUC by 0.03 to 0.05 simply by reducing
unlucky-fold variance. Protocol fixes (controlled lighting box, color card)
turn what is currently a multi-confound dataset into one where any feature you
do extract is more discriminative. Modeling and features without these are
polishing.

**[MMCV].** I disagree on the budget. The handcrafted color-moment feature
stack is 1980s spectrophotometry in disguise. A frozen DINOv2-large or CLIP
ViT-L embedding per image, mean-pooled per subject, is one afternoon of work
and almost always raises AUC by 0.04 to 0.08 on small medical-imaging
datasets, even while flat-out replacing the feature extractor. For video,
TimeSformer or VideoMAE base extracted as frozen features beat handcrafted
temporal features in every benchmark I've seen. C is where the next jump comes
from.

**[EXP].** The disagreement above is a sign that nobody knows. The right
sequencing is: protocol fixes first (cheap, reduces variance, makes everything
else easier to interpret), then a head-to-head ablation between learned
features and handcrafted, then more data once we know which feature stack to
collect for. Spending 100 points on any one lever before the ablation is
premature.

**[SKEP].** Lever B (protocol) is underweighted by everyone except me. Half of
the noise in a 101-subject home-collected dataset is uncontrolled lighting and
phone variation. A controlled lighting box plus a fixed color card would
collapse that noise so hard that the *current* features might suddenly hit 0.85.
If that doesn't happen, you've also learned the signal isn't there.

**[MLENG].** The single highest-yield experiment is a *frozen embedding
plus calibrated stacking*: DINOv2-large image embeddings + VideoMAE-base video
embeddings + per-subject metadata, fed to LightGBM with
isotonic calibration, evaluated on a held-out subject group. ~3 days of work,
expected ΔAUC +0.05 to +0.10. The risk is overfitting to embedding artifacts
on a 101-subject dataset; mitigate with embedding dropout and a strict
held-out group.

## Stage 2 cross-review

Heat is on:
- [STAT] vs [MMCV]: data scale vs feature stack as the bottleneck.
- [SKEP] vs [MLENG]: protocol vs modeling as the highest-yield short-term move.

Models converge on:
- The current handcrafted feature stack should be ablated against learned
  features. Whether or not it wins, the experiment is required.
- Protocol fixes are net positive but not sufficient alone.
- Held-out subject group is mandatory before any new architecture is reported.

## Aggregate ranking

1. [MLENG] (concrete, runnable, falsifiable next experiment)
2. [STAT] (right about the statistical floor)
3. [SKEP] (right about protocol but offered no mid-term path)
4. [MMCV] (right but optimistic about effect size on N=101)
5. [EXP] (correct meta-point, but did not pick a lever)

## Stage 3 chairman synthesis

The 100-point allocation that fits all the dissent is:
**A=30, B=25, C=30, D=15.**

The single highest-yield experiment is the one [MLENG] described:

> Freeze a DINOv2-large image encoder (1024-dim) and a VideoMAE-base video
> encoder (768-dim). Per subject, mean-pool image embeddings across photos
> and use the [CLS] token of VideoMAE on the 10-second clip. Concatenate
> with the 5 confounder-control metadata features. Train a LightGBM
> classifier with 1000 trees, `max_depth=4`, `learning_rate=0.03`,
> early stopping on a held-out fold. Wrap in `CalibratedClassifierCV`
> (isotonic) for probability calibration. Evaluate on 5-fold GroupKFold
> *and* on a frozen held-out subject group of 25.
>
> Success threshold: AUC > 0.82 on held-out group with 95% CI lower
> bound > 0.74. Falsification: AUC ≤ 0.78 on held-out group, in which
> case the handcrafted stack was already pulling its weight and the
> bottleneck is elsewhere.

Do this *before* spending any cycles on more data collection or
ensemble tuning. It tells you whether features are the bottleneck or
not, in 2 to 3 days of work.

---

# Q3. Killing or confirming the hypothesis fast

## Stage 1 first opinions

**[STAT].** Design: matched-pair within-subject case-control. Recruit 30
women trying to conceive and follow them for 3 menstrual cycles. Each
provides a urine sample on cycle day 25 to 28 every cycle. Some will
conceive; same subject gives both pre-pregnancy and early-pregnancy urines.
Within-subject design eliminates phone, lighting, hydration habit, and
genetics confounding by construction. Expected effect size under H1:
within-subject ΔAUC > 0.15 between same-cycle and pregnancy-cycle samples.
Pre-registered no-go rule: if mean within-subject ΔAUC < 0.05 across the
3-cycle follow-up with N≥15 conception events, hypothesis fails.

**[MMCV].** I'd use the same sampling design but add a fixed lightbox and
a Macbeth color card in every photo. Half the variance in a home-collected
dataset is illumination. Strip it out and the within-subject delta will be
either obvious or absent, with no ambiguity.

**[EXP].** The within-subject design is the right answer. Pre-register on
OSF: primary endpoint = within-subject AUC delta on cycle 25 to 28
samples between non-conception and conception cycles. Effect size: AUC
delta of 0.10 with SE 0.04 is detectable at α=0.05, β=0.2 with N=20
conception events. Need to recruit roughly 60 trying-to-conceive subjects
to get 20 conception events in 3 cycles (≈30% per-cycle conception rate).
Stop rule: at interim N=10 events, if posterior probability of effect
size > 0.05 falls below 0.30, halt for futility.

**[SKEP].** Fine, but the strongest reason this could mislead you: same
subject across cycles has *correlated* urine appearance even without
pregnancy due to habits, diet, supplements they started taking once
they decided to try (especially folic acid). You'll measure pregnancy
PLUS "behavior change associated with trying to conceive". Mitigation:
include 30 control subjects who are taking prenatal vitamins but using
contraception in the same period. Their delta should be near zero.

**[MLENG].** Under the within-subject design, switch the model from
cross-sectional classification to a delta detector: predict P(pregnant |
urine_t, urine_baseline) where baseline is the same subject's earlier
sample. This is a much easier learning problem and reuses the same data
more efficiently.

## Stage 2 cross-review

All five lenses converge: within-subject design is the right answer.
Disagreement is on the *control arm*. [SKEP] insists on a prenatal-vitamin
control group; [STAT] and [EXP] accept this only if the budget allows.
[MMCV] insists on the lightbox; the others rate it nice-to-have.

## Aggregate ranking

1. [SKEP] (caught the supplement-confound that breaks the design)
2. [EXP] (translated to pre-registration with explicit stop rules)
3. [STAT] (clean within-subject framing)
4. [MLENG] (delta-detector idea is real efficiency win)
5. [MMCV] (right, but lightbox is protocol not experimental design)

## Stage 3 chairman synthesis

**Design.**

- N=60 trying-to-conceive subjects, 3 menstrual cycles, expecting ~20
  conception events.
- N=30 prenatal-vitamin control subjects on contraception, same 3-cycle
  follow-up.
- Each subject contributes one urine sample on cycle days 25 to 28.
- Lightbox + color card in every photo (collapses lighting confound).
- Phone model fixed per-subject (use whatever phone they have, but same
  one across all sessions).

**Pre-registered statistical test.**

- Primary: paired AUC delta between conception-cycle and non-conception
  cycles within subject, computed by leave-one-subject-out CV with
  conception-cycle vs prior-cycle as positive vs negative.
- Effect size: 0.10 detectable at 80% power with N=20 events.
- Falsification: paired AUC delta point estimate < 0.05 with 95% CI
  including zero ⇒ pivot.

**The strongest reason it could still mislead.**

Behavioral change correlated with attempting conception (folic acid,
hydration changes, alcohol abstinence). The prenatal-vitamin control
arm catches most of it; the residual is unmeasurable supplements like
DHA or unmeasured diet shifts.

**Cheapest mitigation.**

A one-page weekly food/supplement diary for all subjects across all
cycles. Use it as a covariate, not an exclusion criterion.

---

# Q4. Feature engineering with what we already have

## Stage 1 first opinions (top 5 moves, ranked)

**[MMCV] (the lens with most authority here):**

1. **Frozen DINOv2-large embeddings on each photo, mean-pooled per
   subject.** Replaces 137 handcrafted photo features with 1024 learned
   ones. ΔAUC expected +0.04 to +0.08, confidence high. Risk: embedding
   over-capacity on N=101; mitigate with PCA-50 inside-fold and L2 logistic.
2. **VideoMAE-base [CLS] embedding on the 10s clip.** Replaces 42 handcrafted
   video features with a 768-dim learned representation. ΔAUC +0.03 to +0.06,
   confidence medium. Risk: short-clip degradation; verify on a 5-clip
   sanity sample first.
3. **Per-image color constancy via Gray-World or Retinex normalization
   before *any* feature extraction.** Phones impose unknown white-balance.
   ΔAUC +0.01 to +0.04, confidence high, downside zero.
4. **Cup segmentation with Segment Anything (SAM-H), then crop to the
   liquid region only.** Eliminates background and cup-rim confounders.
   ΔAUC +0.02 to +0.04, confidence medium.
5. **Frame-level multi-instance learning (MIL) with attention pooling**
   instead of per-subject mean/std aggregation. Expected ΔAUC +0.02 to +0.05;
   risk is added complexity for moderate gain.

**[STAT].** Re-orders these. #3 (color constancy) goes first because it's
the variance-reducer that makes every other measurement cleaner. #4 (cup
segmentation) goes second for the same reason. #1 and #2 (learned
embeddings) come third and fourth. #5 last; MIL on N=101 is overengineering.

**[SKEP].** Note that all five moves are additive. Worst case the AUC moves
zero. Best case +0.10. Budget 1 week per move with strict ablation.
Anything that doesn't beat the prior model on the held-out group goes back
to the shelf.

**[EXP].** Ablate one move at a time on the held-out subject group. Lock
the order in writing before you start; do not look at the held-out scores
until all five moves are tried.

**[MLENG].** Add a 6th, free move: **temperature scaling on the existing
model's logits using a small calibration split.** Doesn't change AUC but
makes the probability outputs trustworthy, which matters for any product
claim. Not in your top 5 because not AUC-additive, but mandatory.

## Stage 2 cross-review

Strong consensus on color constancy + cup segmentation as the universally
correct next moves. Disagreement on whether learned embeddings beat
handcrafted on N=101 specifically. [SKEP] warns embeddings on small data
can spuriously hit the test fold via shared ImageNet-style biases; [MMCV]
counters that DINOv2 is self-supervised and less prone to that issue.

## Aggregate ranking

1. [MMCV] (most domain-grounded technical answer)
2. [MLENG] (caught calibration as the missing piece)
3. [STAT] (right re-ordering for variance reduction)
4. [SKEP] (right cautions, no novel move)
5. [EXP] (correct meta, no new move)

## Stage 3 chairman synthesis (final ordered list with disconfirmation rules)

| # | Move | Expected ΔAUC | Confidence | Disconfirm if |
|---|------|----------------|-----------|----------------|
| 1 | Gray-World + Retinex color constancy on every photo before feature extraction | +0.01 to +0.04 | High | Held-out AUC unchanged after retraining V5 on the normalized images |
| 2 | SAM-H cup segmentation, crop to liquid region only | +0.02 to +0.04 | Medium | Held-out AUC drops, indicating background was actually carrying signal (then we have a bigger problem) |
| 3 | DINOv2-large frozen image embeddings, PCA-50 inside-fold, L2 logistic | +0.04 to +0.08 | Medium-high | Held-out AUC ≤ V5 baseline |
| 4 | VideoMAE-base [CLS] embedding on 10s clip, concat with #3 | +0.03 to +0.06 | Medium | Concatenation does not beat #3 alone |
| 5 | Multi-instance learning with attention pooling over frames | +0.02 to +0.05 | Low | More than +0.02 below #4; complexity unjustified |
| Mandatory addendum | Isotonic calibration on a held-out fold | 0 (AUC) but +calibration | High | Brier score does not improve |

---

# Q5. The right way to validate before any product claim

## Stage 1 first opinions

**[STAT].** Minimum: external cohort N≥300, recruited from a different
clinical site than the training data. Stratify on trimester, age, BMI,
and phone make. Report AUC, sensitivity at fixed specificity 0.95
(this is the clinical operating point, not Youden), Brier score,
expected calibration error (ECE). Single blocking result: ECE > 0.10
on the external cohort means probabilities are not trustworthy and
the product cannot make confidence claims, regardless of AUC.

**[MMCV].** Add a phone-model robustness slice. Train on phones P1, P2,
P3; test on P4, P5 unseen. AUC drop > 0.10 between in-domain and
out-of-domain phones means the model has learned the camera, not the
urine. This single test is more decisive than the cohort AUC headline.

**[EXP].** Pre-register the analysis plan on ClinicalTrials.gov before
data collection. Lock primary, secondary, and exploratory endpoints.
Report negative results too. Without pre-registration, no claim is
credible regardless of numbers.

**[SKEP].** The single result that should block the launch: external
specificity at the operating point > 0.95 must be at minimum 0.85.
Anything lower means the false-positive rate in real use is higher
than 15%, which for a "confirm pregnancy at home" tool is unacceptable
(false positives create medical, financial, and emotional harm).

**[MLENG].** Add an adversarial slice: 50 samples deliberately collected
under bad conditions (low light, dirty cup, motion blur). Performance
on this slice tells you what to expect when real users are not perfect.

## Stage 2 cross-review

All converge on:
- External cohort, pre-registered, with phone-model split.
- Calibration is as important as AUC for any product claim.
- Sensitivity at fixed high specificity is the clinical metric, not Youden AUC.

## Aggregate ranking

1. [STAT] (most complete validation framework)
2. [MMCV] (phone-model robustness is the decisive test)
3. [SKEP] (specificity floor is the right product gate)
4. [EXP] (pre-registration is necessary, not specific)
5. [MLENG] (adversarial slice is good but secondary)

## Stage 3 chairman synthesis

**Validation gates before any product claim.**

1. **External cohort.** N ≥ 300, recruited at a different site, ideally a
   different country, with informed consent and IRB approval.
2. **Phone-model split.** Held-out phones not in training. AUC drop
   between in-domain and out-of-domain phones must be < 0.05.
3. **Calibration.** Expected calibration error ≤ 0.05 (lower is better).
   Reliability diagram inspected. Probabilities meaningful, not just
   ranking.
4. **Sub-group reporting.** Trimester (1st vs 2nd vs 3rd), age band
   (<25, 25-35, 35+), BMI band (under, normal, over, obese), phone make,
   skin tone of hand if visible. AUC reported per slice.
5. **Pre-registration.** ClinicalTrials.gov entry before external data
   collection begins.
6. **Adversarial slice.** N≥50 deliberately bad samples; performance
   reported as a separate metric.

**The single blocking result.**

> Sensitivity at specificity 0.95 on the external cohort < 0.70.

That means: even when the model is tuned to barely false-positive, it
still misses too many real pregnancies for a useful screening tool.
Below this threshold, the product cannot ship.

**One thing that would still go wrong even if all of this passed.**

Distribution shift over time. Phone cameras get new sensors and new
white-balance algorithms every year. A model passing all validation
in 2026 may degrade silently in 2028 as the user base updates phones.
Any deployment plan must include continuous monitoring of input
distribution and a re-validation cadence.

---

# Bonus session — final synthesis

## 1. The single highest-priority next action

> **Run the confound-only baseline (Q1.1) and the held-out subject group
> setup (Q1.2) before any modeling work. Until those two numbers exist,
> all current AUC reports are statistically insecure.**

Concretely: lock 25 subjects (12P, 13N) into an untouchable holdout, then
fit a logistic regression on metadata only (no urine pixels) using 5-fold
GroupKFold on the remaining 76. Report ΔAUC = AUC(urine+confound) − AUC(confound only).
This experiment costs less than one day and changes which lever to pull next.

## 2. The first thing to stop doing

> **Stop reporting AUC numbers that came from model selection on the
> same CV folds used to evaluate. Stop comparing 0.774 to 0.854 as if
> they were stable estimates.**

The May 3 ensemble result of 0.854 is partly an artifact of selecting
SoftVoting + ExtraTrees + SVC C=1.0 from a sweep on the same folds we
report. With N=101 and 5-fold GroupKFold, AUC point estimates have a
±0.08 to ±0.10 95% CI on this dataset. Three differently-tuned models
that come out at 0.78, 0.82, 0.85 are statistically indistinguishable.

## 3. The one number to not look at again until external data exists

> **AUC on the full 101-subject cross-validation.**

It will be the headline number on every internal slide and it will
mislead every decision. Replace it on internal dashboards with two
numbers: (a) ΔAUC over confound-only baseline, and (b) AUC on the
held-out subject group. Bring back the headline AUC only when the
external cohort exists, and only as a sanity check.

---

## Council priorities, ranked for execution

| Rank | Action | Effort | Who decides | Expected outcome |
|------|--------|--------|-------------|------------------|
| 1 | Confound-only baseline + ΔAUC report | 1 day | This week | Tells us if signal exists |
| 2 | Lock held-out subject group of 25 | 0.5 day | This week | Restores statistical hygiene |
| 3 | Color constancy + cup segmentation pre-processing | 2 days | Next week | Reduces noise floor |
| 4 | DINOv2 + VideoMAE frozen embeddings ablation | 3 days | Next 2 weeks | Tests feature ceiling |
| 5 | Within-subject experimental design (Q3) write-up | 3 days planning | Next 2 weeks | Funded experiment design |
| 6 | Calibration via isotonic regression + Brier reporting | 1 day | Next week | Probabilities trustworthy |
| 7 | Pre-registration on OSF for the next data collection | 2 days | Next month | External credibility |
| 8 | External validation cohort design (Q5) | 1 week | This month | Path to publication/product |

## What the council unanimously refused to recommend

- Adding more handcrafted color features without ablating against learned ones.
- Reporting AUC > 0.85 publicly while the held-out group is untested.
- Publishing or seeking media attention before external validation.
- Targeting AUC 0.95 as a fixed milestone. The right milestone is
  *external sensitivity at specificity 0.95 ≥ 0.70*, which is harder
  but more honest.
