# COUNCIL QUESTIONS — Pregnancy Detection AI

> Run order: Q1 to Q5. Each session: paste COUNCIL_BRIEF.md, then the question.
> Goal: extract concrete, prioritized improvement actions from a multi-model debate.

---

## Q1. Methodology validity (start here)

> Given the brief, is our V5 reading of "AUC 0.774 is the honest model and the
> 0.907 leaky version is invalid" correct, or are we being too strict and discarding
> usable signal? Specifically:
>
> - Is `has_folic_acid` automatically label leakage, or could there be a defensible
>   way to use it as a prior in a deployed product?
> - Is including `gest_age_weeks` always invalid, or only invalid when the model is
>   evaluated on populations where pregnancy detection (not staging) is the task?
> - Are GroupKFold by subject and SelectKBest fit inside the fold sufficient
>   guards, or do you see remaining leakage paths (per-subject aggregation
>   computed before split, video frames sharing a subject, etc.)?
>
> Rank the three concerns above by how much they should worry us, and tell us
> what one experiment each would pin down.

---

## Q2. Where the next 10 AUC points come from

> Our honest AUC is 0.774. Target is 0.95+. Allocate 100 effort points across
> these four levers and justify the split:
>
> A. More subjects (data scale, currently 101).
> B. Better photography protocol (controlled lighting box, fixed phone, color card).
> C. Better features (deep CNN embeddings, learned color constancy, video models like
>    R(2+1)D or VideoMAE, hand-crafted spectroscopy proxies).
> D. Better modeling (gradient boosting, calibrated stacking, multi-instance learning,
>    contrastive pretraining, transformer fusion of photo+video+metadata).
>
> Then pick the single highest-yield specific experiment under your top lever
> and describe it in implementation terms: dataset slice, model, metric, success
> threshold, runtime budget, falsification criterion.

---

## Q3. Killing or confirming the hypothesis fast

> Assume we have 4 weeks and a budget for one focused experiment that should
> either confirm "urine appearance carries a real pregnancy signal independent
> of confounders" or kill the project. Design that experiment.
>
> The design must include:
>
> - Sample size and recruitment criteria.
> - The matching strategy that neutralizes hydration, time of day, phone model,
>   and supplement intake.
> - The pre-registered statistical test, the effect size you expect under H1,
>   and the no-go decision rule under H0.
> - What you would do differently from our current data collection.
>
> Then state the strongest reason this experiment could still mislead us, and
> the cheapest way to mitigate it.

---

## Q4. Feature engineering with what we already have

> Without collecting one new sample, what are the top five feature engineering
> moves you would make on our 101-subject dataset to push AUC, in priority order?
>
> Be specific. Not "use deep learning" but "fine-tune a CLIP-ViT-B/32 on
> per-image binary labels with subject-level GroupKFold, extract the 512-dim
> embedding, average per subject, concatenate with the 42 video features,
> train logistic regression with L2".
>
> For each move tell us:
> - Expected AUC delta and your confidence in it.
> - The risk it adds (overfitting, leakage, computational, brittleness).
> - The disconfirmation signal that should make us drop it.

---

## Q5. The right way to validate before any product claim

> Suppose we reach AUC 0.95 on internal cross-validation. What is the minimum
> validation evidence we need before we can credibly tell anyone outside the
> team that this works?
>
> Cover:
>
> - External cohort design (size, geography, recruitment independence).
> - Phone-model robustness test.
> - Calibration assessment (is the probability output meaningful, not just
>   the AUC).
> - Sub-group slices that must be reported (trimester, age band, BMI band,
>   skin tone if relevant, phone make).
> - The single result that, if it failed, should block the product launch.
>
> End with one sentence on what would still go wrong even if all of the above
> passed.

---

## Bonus session, after Q1 to Q5

> Synthesize the council outputs from Q1 to Q5 into:
>
> 1. The single highest-priority next action.
> 2. The first thing we should stop doing.
> 3. The one number we should not look at again until we have external data.
