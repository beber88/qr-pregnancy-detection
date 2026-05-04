# Perplexity response — 2026-05-04

> Source: user-supplied Perplexity output. Saved verbatim for later
> cross-model synthesis. Not edited.

# Q1 - Methodology validity
### Direct verdict
You are correct to treat 0.774 as the honest model and 0.907 as invalid for the scientific question "is there a real visual urine signal?" - the 0.907 is dominated by label-coded and behavior-coded priors, not bulk urine appearance. Including `gest_age_weeks` is classic label leakage for a binary detection task, and `has_folic_acid` is also leakage relative to your stated goal of urine-only signal, even though it could be acceptable as a product-side prior in a different framing. The remaining leakage paths (aggregation timing, model selection on the same CV folds, subtle phone/lighting cohort effects) are less egregious but still easily big enough to move AUC by ~0.05 on N=~100 and must be cleaned up before you trust any third-decimal or even second-decimal AUC.

### (a) has_folic_acid
`has_folic_acid` is not automatically "forbidden" in a product sense, but it is incompatible with your current scientific hypothesis and with the way you are currently sampling. In the real world, folic acid use is a behavioral marker of "trying to conceive / early pregnancy care," so in your dataset it is almost certainly enriched in positives and near-positives, making it a strong prior on the label independent of any urine physics.
As a *deployable* feature, it could be defensible only if: (1) you commit to a questionnaire-augmented risk model, not a "urine-only" diagnostic; (2) your recruitment and future deployment population are aligned (same rates of TTC, supplement use, etc.); and (3) you explicitly treat it as a prior (e.g., Bayesian pretest probability) and calibrate accordingly, rather than quietly mixing it into a black-box classifier. If you keep the current vision - "can urine appearance alone separate pregnant from non-pregnant?" - then `has_folic_acid` is label leakage with respect to that question and should be excluded from any performance number you use to argue that a visual urine signal exists.
**Decisive experiment for `has_folic_acid`:** Train three models on the current dataset with strict subject-wise GroupKFold: (1) folic-acid-only logistic regression; (2) urine-only features; (3) urine+folic. If model (1) alone gets high AUC (e.g., >0.75) and model (3) improves substantially over (2), then almost all of that gain is coming from behavior, not physics; you should then treat any combined AUC as non-evidence for a visual signal, and report urine-only AUC as your scientific metric.

### (b) gest_age_weeks
For the binary detection task ("pregnant vs not"), `gest_age_weeks` is straight-up label leakage and cannot be defended. A continuous variable that is by definition zero for all negatives and >0 for all positives is just a soft version of the label; folding it into a classifier and then quoting AUC is equivalent to partially re-using the label as an input feature.
It becomes legitimate only under a *different task definition*: e.g., staging gestational age conditional on already-known pregnancy status, or predicting gestational age as a regression target among confirmed pregnancies. In that framing, you would (a) restrict the dataset to confirmed pregnant subjects; (b) ensure your binary decision ("pregnant?") is *not* what you're evaluating; and (c) treat gestational age as the supervised label, not an input.
**Decisive experiment for `gest_age_weeks`:** Fit a one-feature logistic regression or simple threshold classifier using `gest_age_weeks` alone to predict the binary label, under GroupKFold. If its AUC is already very high (likely >0.9), you have proven it is effectively an encoded label. You should then **ban** this feature completely from any pregnancy-vs-nonpregnancy classifier and scrub any historic AUCs computed with it.

### (c) Remaining leakage paths
You have done several things right - GroupKFold by subject and feature selection inside the fold are the minimum necessary to avoid trivial subject-level leakage - but some remaining paths are real:
- **Per-subject aggregation before CV split.** If any statistics (means, stds, mins, maxes, CV) were computed using *all* images before partitioning subjects, you can get subtle train-test contamination (e.g., global normalization or PCA fitted across all subjects).
- **Frame-level vs subject-level leakage in video.** If any models are trained at frame/clip level with non-grouped CV, you will massively overestimate performance because clips from the same subject leak into both train and test; your feature extraction appears subject-level, which is good, but double-check that no frame-level experiments are sneaking into model comparison.
- **Model selection on the same CV folds used for reporting.** Tuning hyperparameters, feature selection thresholds, and ensembling strategies on the same 5 folds whose AUC you finally report inflates AUC via "CV on CV". With N=~101, that can easily add 0.03 to 0.05.
- **Phone model / lighting confounding.** The smartphone urinalysis literature shows that illumination and device differences substantially affect color readings and diagnostic performance, and lightboxes plus color references are used explicitly to control this. If your recruitment waves differ in both pregnancy prevalence and phone/lighting distributions, you can get spurious "signal" that is really device or environment.
**Decisive experiment for leakage paths:** Implement a fully *nested* GroupKFold pipeline from raw images: in each outer fold, recompute per-subject aggregates and SelectKBest **only on the training subjects**, tune model type/hyperparameters by an inner CV, then evaluate once on the outer fold. At the same time, hold out a small, temporally separated cohort if you have it. If the honest, nested estimate drops meaningfully (e.g., from ~0.77 to ~0.65 to 0.7), you know that feature computation or model selection leakage was inflating the original numbers.

### Ranked concerns and decisive experiments
1. **gest_age_weeks (highest danger):** Because it is a direct encoding of the label, using it destroys the validity of any "can urine appearance separate classes?" claim. Decisive experiment: one-feature `gest_age_weeks` classifier as above; if AUC is high, permanently exclude it from this task.
2. **has_folic_acid:** Dangerous for your *scientific* question but salvageable in a different, questionnaire-augmented product framing. Decisive experiment: compare folic-only vs urine-only vs combined models to quantify how much of the AUC is behavioral prior vs visual; treat any gain from folic as non-evidence for urine signal.
3. **Remaining leakage paths (aggregation, model selection, confounded phones/lighting):** Important but fixable; they mostly affect the *magnitude* of AUC rather than fabricating a signal from nothing. Decisive experiment: fully nested CV from raw images plus, ideally, a small temporal/clinic hold-out; if the gap between old and nested AUC is large, you know your previous pipeline was optimistic and must be recalibrated.

# Q2 - Where the AUC points come from
### Effort allocation (must total 100)
- A. Data scale: 35
- B. Protocol: 30
- C. Features: 25
- D. Modeling: 10
### Justification
- **A. Data scale (35).** With N=101 and 5-fold CV, your AUC CI is wide (~+/-0.08 to 0.10), so you literally do not know if true performance is 0.65 or 0.85. More subjects are the only way to both narrow the CI and reduce overfitting for any richer feature set or model class. Without more data, the variance of any experiment you run will dominate the modest improvements you're chasing.
- **B. Protocol (30).** Smartphone-based urinalysis papers repeatedly show that standardized illumination (lightboxes), fixed geometry, and color calibration targets are critical for robust colorimetric performance across devices and environments. Your current "natural daylight, 30 cm, white background" protocol is good for a pilot but still highly variable. If the pregnancy signal in bulk urine color/texture is weak, improving SNR via protocol is likely where several AUC points can be gained.
- **C. Features (25).** You are already using engineered color and temporal statistics, but not yet exploiting deep visual representations, explicit color constancy, or learned video embeddings. Given that other smartphone urinalysis systems hit good performance by combining standardized imaging with learned colorimetric features, it is plausible that better features could unlock additional signal - *if* it exists. The risk is that, at current N, complex features overfit unless protocol and sample size improve.
- **D. Modeling (10).** You are already using a reasonable ensemble of linear and non-linear models. Upgrading to, say, gradient boosting or more sophisticated stacking will probably yield at most a few AUC points on top of whatever information is present in the features and protocol, especially at N=~100. Sophisticated modeling only makes sense after you have more subjects and a better-controlled signal.

### Highest-yield experiment
**Top lever:** A. Data scale.
**Specific experiment:**
- **Dataset:** Prospectively recruit ~300 to 400 additional subjects (target ~120 to 150 pregnant, 180 to 250 non-pregnant) over several weeks, using an *improved* standardized imaging protocol: fixed lightbox, color calibration card in every frame, fixed distance and angle, and logging of phone model and time-of-day. Keep the current 101 subjects as an *internal* cohort; use the new cohort primarily for external validation and re-training.
- **Model:** Start with the current honest V5 pipeline (urine-only features + non-leaky confounder controls) and one stronger baseline model (e.g., calibrated gradient boosting on the same features), but keep the feature set identical at first to isolate the effect of data scale.
- **Metric:** Primary: AUC on a held-out, subject-wise external test set (e.g., 20 to 25% of the new cohort), with 95% CI via DeLong. Secondary: calibration (Brier score, calibration plots), sensitivity at fixed high specificity.
- **Success threshold:** External AUC >= 0.85 with a 95% CI width <= 0.06 (e.g., 0.82 to 0.88), and similar performance when you retrain on all old+new training data and re-evaluate on the same held-out subjects. This would indicate a real visual signal beyond sampling noise.
- **Time budget:** 6 to 8 weeks end-to-end: 4 to 6 weeks for recruitment and data collection with the new protocol, 1 to 2 weeks for pipeline implementation and analysis.
- **Falsification rule:** If after adding these 300 to 400 subjects and controlling protocol, the honest urine-only model's external AUC remains in the ~0.7 to 0.78 band with tight CI (e.g., 0.72 to 0.76), you should downgrade expectations for reaching 0.95 in any realistic deployment and seriously consider that bulk urine appearance is simply too weak a signal for a standalone product.

# Q3 - Falsification experiment
### Design
Design a single, pre-registered, case-control experiment that asks: "Can a model using *only* standardized urine imagery (plus non-leaky nuisance controls) distinguish pregnant from non-pregnant women above chance, after matching away obvious confounders?" The key is to (1) standardize capture aggressively; (2) match subjects on hydration, time-of-day, and phone model; and (3) pre-register the full pipeline, including feature set, model, and decision thresholds.
You will collect one visit per subject, with 3 still photos and one 10-second video per protocol, in a controlled lightbox with a color card in each frame, fixed cup type, distance, and angle. No questionnaire variables that directly encode pregnancy behaviors (like folic acid use) are used as inputs; they are only used for matching and sensitivity analysis.

### Sample size and recruitment
In four weeks, a realistic target is on the order of **50 to 60 pregnant and 50 to 60 non-pregnant** women from the same clinical environments. For example, recruit:
- Pregnant group: women 5 to 12 weeks pregnant confirmed by quantitative hCG or early ultrasound at OB/GYN or fertility clinics.
- Non-pregnant group: women of similar age presenting to the same clinics for contraception counseling, gynecologic exams, or other issues, with a contemporaneous negative professional pregnancy test.
This gives N=~100 to 120 subjects in total, which, under a hypothesized AUC of 0.75 vs 0.5, gives moderate power (~80%) to reject H0 at alpha=0.05 using standard ROC power approximations, especially if class sizes are roughly balanced.

### Matching strategy
To neutralize confounders without over-complicating the model:
- **Phone model:** For each pregnant subject, recruit at least one non-pregnant subject using the *same phone model* (ideally the same physical device) and identical cup setup and lightbox.
- **Hydration and time-of-day:** During recruitment, record self-reported fluid intake over the past 2 to 3 hours and time-of-day. For each pregnant subject, choose non-pregnant controls with similar time windows (e.g., within 1 hour) and similar self-reported hydration ("fasted / first morning," "normal," "high fluids").
- **Supplements and medications:** Record folic acid, prenatal vitamins, and medications, but use them only to check matching balance; do **not** use them as model inputs. Aim for similar prevalence of folic acid use in both groups so that any remaining pregnancy signal cannot be primarily behavioral.
- **Inclusion of nuisance covariates:** Age and phone model can be included as covariates or stratification variables in the analysis to adjust residual confounding, but they are not the main signal of interest.
The goal is a matched case-control set where pregnancy status is not strongly predictable from obvious non-visual priors.

### Pre-registered test, expected effect, no-go rule
- **Pre-registered pipeline:**
  - Fixed imaging protocol (lightbox + color card + fixed geometry).
  - Fixed feature set: your current 179-D urine image/video features recomputed under the new protocol, plus maybe one pre-defined deep embedding baseline (e.g., ResNet-18 penultimate-layer features averaged per subject) if you want to lock it in.
  - Fixed model family: e.g., logistic regression + ExtraTrees + SVC soft-voting ensemble with hyperparameters defined a priori or tuned only inside nested CV.
  - Evaluation: strict GroupKFold by subject, no model tuning on the final folds; ideally also a small temporal hold-out if recruitment allows.
- **Statistical test:**
  - Primary: ROC AUC significantly >0.5 using DeLong's test on held-out predictions, with a pre-specified target AUC under H1 of 0.75.
  - Secondary: sensitivity at 95% specificity with binomial CIs; calibration curve.
- **Expected effect size under H1:** Assume true AUC =~0.75; under this, with ~50 to 60 per class, you should see point estimates around 0.7 to 0.8 with 95% CI not overlapping 0.5 too closely.
- **No-go rule under H0:** If the pre-registered pipeline, applied exactly as specified, yields:
  - AUC <=0.65 with a 95% CI that includes 0.5 (e.g., 0.52 to 0.68), **and**
  - No clinically interesting trade-off at high specificity (e.g., sensitivity <=0.6 at 95% specificity),
  you should treat this as strong evidence against a practically useful visual urine signal and pause or kill further feature/model tinkering until you change either biology (different biomarkers/modality) or product concept.

### Strongest residual risk and mitigation
The strongest residual risk is **unmeasured or incompletely matched confounding**: for example, pregnant women in early care might still differ systematically in diet, underlying health, or clinic workflow from non-pregnant controls, leaving some residual non-visual or quasi-visual signal (e.g., specific medications that subtly tint urine) even after matching on phone, time-of-day, and hydration.
The cheapest mitigation is to perform **within-clinic and within-visit sensitivity analyses**: e.g., restrict analysis to pairs of subjects recruited on the same day, from the same clinic, using the same phone and lightbox, and re-compute AUC. If performance collapses in this tightly matched subset while remaining elevated overall, you have evidence that broader clinic-level or recruitment-wave confounding is driving the signal; that would argue against scaling the project without a more sophisticated causal design.

# Q4 - Top 5 feature engineering moves
For each move, assume you keep strict GroupKFold by subject and, ideally, nested CV for any new hyperparameters.

1. **Move name:** Deep CNN embeddings for still images
   - **Expected dAUC:** +0.02 to +0.05 over the current hand-crafted photo features, if any subtle texture/shape cues exist, with effect more visible after you have >200 subjects; at N=101, expect only noisy hints.
   - **Confidence:** Medium-low (overfitting risk is real at current N).
   - **Risk:** High-dimensional feature vectors (e.g., 512 to 2048 dims from ResNet/EfficientNet) on 101 subjects are a classic recipe for optimistic CV if not carefully regularized; you risk chasing noise and "discovering" fold-specific texture artifacts.
   - **Disconfirmation signal:** If in nested GroupKFold, adding CNN embeddings (e.g., ResNet-18 penultimate layer, per-image mean pooling per subject) fails to improve median AUC or increases variance across folds (large swings fold-to-fold), you should drop deep features until you have a larger dataset.

2. **Move name:** Explicit color constancy and white balancing using background/card
   - **Expected dAUC:** +0.02 to +0.03 by reducing lighting variance and making color and "yellowness" features more consistent across phones and conditions; this aligns with improvements seen when smartphone urinalysis systems use standardized illumination and calibration cards.
   - **Confidence:** Medium.
   - **Risk:** Moderate; if real-world deployment does not strictly enforce the same background/card, models trained on aggressively normalized images may generalize poorly to uncontrolled environments. Also, bad calibration (e.g., mis-detected white region) can introduce artifacts.
   - **Disconfirmation signal:** If after implementing per-image white balancing (using the white background or a calibration card) and recomputing all color features, AUC does not improve or worsens under nested CV, and performance becomes more phone-specific, treat this as evidence that further "fancy" color constancy is not worth it until protocol is tightened.

3. **Move name:** Multi-instance learning (MIL) over multiple photos/video frames per subject
   - **Expected dAUC:** +0.02 by smarter aggregation of within-subject variability - your current top features already suggest that per-subject variability is more informative than absolute values.
   - **Confidence:** Medium-low.
   - **Risk:** Implementing MIL (e.g., attention-based pooling over image embeddings) at N=101 subjects is very prone to overfitting; the model may memorize idiosyncratic per-subject patterns instead of learning generalizable bag-level signatures. Computationally modest, but statistically fragile.
   - **Disconfirmation signal:** If a MIL model (e.g., simple attention pooling over per-image CNN features) fails to outperform simple mean/standard deviation pooling of features under nested CV, or shows highly unstable AUC across folds, you should abandon it and stick to simpler aggregations.

4. **Move name:** Learned video embeddings (e.g., VideoMAE / 3D CNN) replacing handcrafted temporal descriptors
   - **Expected dAUC:** +0.03 in the optimistic case where subtle temporal patterns (e.g., micro-movements, specular changes) correlate with pregnancy physiology - though this is speculative and probably only testable with far more video samples.
   - **Confidence:** Low.
   - **Risk:** Very high dimensionality, high compute, and extreme overfitting risk given only 68 clips and 101 subjects. You may end up learning camera shake patterns or compression artifacts, not biology.
   - **Disconfirmation signal:** If a pre-trained video embedding (e.g., VideoMAE base, per-clip pooled embedding, then per-subject pooling) plus a simple classifier does not beat or is less stable than your current hand-crafted video temporal features under strict CV, you should stop investing in video models until you have at least an order of magnitude more clips.

5. **Move name:** Phone- and illumination-adjusted residual features
   - **Expected dAUC:** +0.01 to +0.02 by explicitly modeling and removing phone and lighting effects - e.g., z-scoring color features within each phone model or regressing them on phone model and brightness, then using residuals. This aligns with the way smartphone urinalysis systems treat device variance as a nuisance factor.
   - **Confidence:** Medium.
   - **Risk:** You might inadvertently remove part of the true signal if, for example, pregnancy status interacts with phone-specific capture (e.g., different user groups clustering on different phones). Also, with small numbers per phone model, residualization can be noisy.
   - **Disconfirmation signal:** If after residualizing features on phone model and global brightness the AUC drops or becomes more unstable, and no subgroup (e.g., within a single common phone model) shows clear improvement, you should revert to raw features plus explicit phone-model stratified evaluation instead of residualization.

# Q5 - Validation requirements
### External cohort design
Before making any external claim, you need at least **one large, prospective, blinded external cohort** collected under a pre-specified imaging protocol and analysis plan. Concretely:
- N=~500 to 1000 women from multiple sites (e.g., different clinics and geographic regions), with pregnancy status determined by professional standard (lab hCG or ultrasound).
- The model is frozen before external evaluation (features, preprocessing, and parameters fixed).
- All imaging is done with the intended deployment protocol (cup, lightbox, instructions, supported phone models), and lab staff are blinded to model outputs.
- Evaluate AUC with 95% CI, sensitivity/specificity at clinically meaningful thresholds, and compare performance across sites.
If this external cohort fails to reproduce internal CV performance (e.g., external AUC is <0.85 when internal was 0.95), you cannot credibly claim the model "works" in a general sense.

### Phone-model robustness test
You must demonstrate robustness across **multiple phone models and OS versions**:
- Pre-specify a set of supported devices (e.g., top 3 to 5 iOS and Android phones by market share).
- For each device, collect sufficient samples (ideally >=100 subjects per phone class, or at least enough to estimate AUC with CI width <=0.1).
- Evaluate AUC, sensitivity, specificity, and calibration separately for each phone model, and test for significant performance differences.
The smartphone urinalysis literature shows that device and illumination conditions can materially affect colorimetric accuracy; rigorous systems either restrict to calibrated devices or implement device-specific corrections. If your model performs well only on a subset of phones, you must either restrict deployment or build device-specific calibrations.

### Calibration assessment
High AUC is not sufficient; for any probabilistic output, you must assess and, if necessary, correct **calibration**:
- Compute Brier score and draw calibration curves (e.g., reliability diagrams) on the external cohort, ideally with enough samples to populate deciles of predicted probability.
- Apply Platt scaling or isotonic regression using a *calibration set* distinct from the final test set if raw probabilities are miscalibrated.
- Verify that predicted probabilities align with empirical risks across clinically relevant ranges (e.g., 1 to 5%, 5 to 20%, >20% pregnancy risk).
Poor calibration - especially overconfident high-risk predictions in non-pregnant users - can be more harmful than a modestly lower AUC, because it directly misleads users' decisions.

### Required sub-group slices
At minimum, you need to report performance by:
- **Age:** e.g., <25, 25 to 34, >=35.
- **Gestational age:** e.g., <6 weeks, 6 to 8 weeks, >8 weeks among positives, because signal may vary with hCG dynamics and other physiological changes.
- **Hydration/time-of-day:** first-morning vs later, low vs high fluid intake.
- **Phone model:** as above, stratified by device class.
- **Key health factors:** e.g., known kidney disease, diabetes, or other conditions that affect urine appearance.
These slices are in line with how smartphone urinalysis and diagnostic tools report subgroup performance to detect biases and failure modes.

### Single blocking result
The single clearest blocking result should be: **a substantial performance drop plus miscalibration on the primary external cohort**, e.g., overall AUC <0.85 *and* severe miscalibration (e.g., women given >=50% predicted probability who are actually pregnant <20% of the time, or vice versa) in the intended use population. If this happens, it means your internal 0.95 AUC was not representative, and launching would be irresponsible regardless of how good internal CV looked.

### What still goes wrong if all of the above passes
Even if all validation steps pass, real-world, unsupervised home use will introduce protocol violations (wrong cups, lighting, distance), off-label populations, and behavioral feedback loops that were not present in your trials, so true field performance will likely be worse and more skewed than the carefully estimated metrics from controlled cohorts.

# Bonus - three one-liners
1. Highest-priority next action: Run a pre-registered, tightly matched case-control study with a standardized imaging protocol to test whether any robust urine-only signal exists under realistic constraints.
2. First thing to stop doing: Stop training or even glancing at models that include `gest_age_weeks` or pregnancy-behavior features like `has_folic_acid` when arguing about visual urine signal.
3. Number not to look at until external data: The 0.907 AUC from the leaky V5 model (and, more broadly, any leaky AUC using gestational age or folic acid) should be treated as dead to you.

# What I uniquely see that other models might miss
Your own top discriminating features being variability measures (std, CV, temporal complexity) rather than absolute color strongly suggests the model is latching onto capture instability and micro-artifacts more than stable biophysical differences, which is exactly the kind of thing that collapses under a stricter protocol. The smartphone urinalysis literature shows that robust systems effectively "burn" a lot of engineering effort on illumination and device control before doing anything fancy with modeling, and your current protocol is still below that bar. Given that even metabolomics-based pregnancy detection in animal urine maxes out around AUC 0.8 with direct access to molecular concentrations, a 0.95 AUC target from bulk RGB appearance alone is biologically ambitious and should be treated as the hypothesis under attack, not the goal you must reach at all costs.

# Literature anchor (search-augmented only)
1. **"Accuracy of smartphone camera urine photo colorimetry as indicators of dehydration" - Bustam et al., Digit Health, 2023.**
   Finding: Using a smartphone to capture urine images in a customized photo box under controlled lighting, the authors showed that RGB color values can predict dehydration status with good diagnostic accuracy, but performance depends strongly on illumination and device conditions.
   Impact on Q1/Q3: Reinforces that uncontrolled "natural daylight" protocols are a major noise and confounding source; your falsification experiment in Q3 should therefore adopt a lightbox-style standardized capture or risk mistaking lighting variance for biological signal.
   Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC10474791/

2. **"Smartphone-Based Point-of-Care Urinalysis Under Variable Illumination" - Ra et al., IEEE J Transl Eng Health Med, 2017.**
   Finding: The paper demonstrates that smartphone-based analysis of urine test strips can achieve reliable results only when algorithms correct for variable illumination and device-specific color responses, using reference regions and calibration.
   Impact on Q1/Q3: Strengthens the argument that phone/lighting confounding is a real, nontrivial leakage path in your current dataset and that the Q3 experiment must either fix illumination (lightbox + calibration card) or explicitly model illumination as a nuisance factor.
   Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC5764119/

3. **"Urine Test Strip Quantitative Assay with a Smartphone Camera" - Pohanka, Int J Anal Chem, 2024.**
   Finding: The study shows that a smartphone camera can quantitatively read urine test-strip analytes like glucose and albumin with low limits of detection when RGB channels are analyzed under controlled conditions.
   Impact on Q1/Q3: Confirms that smartphones can support quantitative urinalysis, but only when the signal comes from designed colorimetric chemistry (test strips), not bulk urine; this emphasizes that your pregnancy task is inherently harder and should be evaluated with stricter skepticism in Q1 and with a strong null-focused design in Q3.
   Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC10963100/

4. **"Artificial Intelligence in Diagnostics: Enhancing Urine Test Accuracy Using a Mobile Phone-Based Reading System" - Kim, Ann Lab Med, 2024.**
   Finding: The authors report that AI models applied to smartphone-captured urine strip images can improve standardization and accuracy of urinalysis across settings, but highlight the need for extensive validation and device-robust calibration.
   Impact on Q1/Q3: Supports your focus on rigorous external validation in Q5 and suggests that any pregnancy model based on smartphone urine images will need similar multi-device validation before claims are credible, reinforcing the emphasis on robust external and subgroup analyses.
   Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC11788702/

5. **"Exploration of urinary metabolite dynamicity for early detection of pregnancy in Murrah buffaloes" - Prabhakar et al., Sci Rep, 2022.**
   Finding: Using 1H-NMR metabolomics, the authors identified urinary metabolite signatures that distinguish pregnant from non-pregnant buffaloes, with combined biomarker AUC around 0.8 for early pregnancy detection.
   Impact on Q1/Q3: This result, even in a different species, underscores that early-pregnancy signal in urine is detectable but not trivially strong even with direct access to metabolites; it makes your aspiration of AUC 0.95 from bulk RGB appearance alone look optimistic and supports using the Q3 experiment explicitly as a potential project kill-switch if honest AUC remains modest.
   Source: https://www.nature.com/articles/s41598-022-20298-1
