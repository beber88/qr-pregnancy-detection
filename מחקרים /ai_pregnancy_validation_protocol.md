# Clinical Validation Protocol for a Smartphone-Based AI Pregnancy Detection System

## Protocol synopsis

This protocol describes a prospective, multi-site, regulator-oriented clinical validation study for a smartphone-based artificial intelligence system that analyzes photographs of urine or urine-based test artifacts to determine pregnancy status. The protocol is intentionally written to withstand review under ICH-GCP principles, FDA expectations for diagnostic software and AI/ML-enabled medical devices, and peer-reviewed publication standards. FDA treats pregnancy tests as Class II in vitro diagnostic devices under 21 CFR 862.1155, and OTC human chorionic gonadotropin (hCG) tests are typically cleared through the 510(k) pathway with analytical and clinical performance evidence anchored to urine and serum hCG concentrations.[cite:332][cite:135] FDA also states that AI/ML-enabled Software as a Medical Device remains subject to existing device pathways and lifecycle evidence expectations, with additional attention to data quality, model change control, and postmarket monitoring.[cite:305][cite:324]

The protocol is written in a conservative way because a vision-only pregnancy detector from photographs of native urine has no obvious FDA predicate and would almost certainly face a higher evidentiary burden than a smartphone reader for an hCG-based strip or cassette.[cite:305][cite:329][cite:332] Accordingly, the protocol is designed around the strictest defensible reference framework: quantitative serum beta-hCG as the gold standard, ultrasound confirmation for clinically positive participants when feasible, prespecified handling of uncertain and peri-implantation cases, a locked algorithm, and extensive subgroup analyses across demographics, device classes, and capture environments.[cite:135][cite:305]

## Administrative information

### Protocol title

Prospective Multi-Site Clinical Validation of a Smartphone-Based AI Pregnancy Detection System Using Urine Images Against Quantitative Serum beta-hCG Reference Standard.

### Protocol version

Version 1.0

### Sponsor

To be completed by sponsor.

### Coordinating center / CRO

To be completed by sponsor.

### Investigational product

A smartphone application that captures and analyzes urine photographs and outputs a binary pregnancy result, a confidence score, and an image quality flag.

### Intended use under evaluation

The investigational system is intended to aid in detection of pregnancy in people of reproductive potential by analysis of smartphone photographs of urine-related images under specified conditions. Because the intended use claim materially determines regulatory classification, this protocol assumes the highest-risk interpretation for validation planning and should not be construed as the final cleared claim language.[cite:305][cite:314]

## 1. Study objectives and hypotheses

### 1.1 Primary objective

To estimate the diagnostic sensitivity and specificity of the locked AI system for detection of pregnancy relative to quantitative serum beta-hCG reference status in the intended-use population.

### 1.2 Primary hypothesis

The primary hypothesis is that the lower bound of the two-sided 95% confidence interval for sensitivity will be at least 97.0%, and the lower bound of the two-sided 95% confidence interval for specificity will be at least 97.0%, when compared with pregnancy status defined by quantitative serum beta-hCG and follow-up adjudication. This target is intentionally close to the historical performance expectations for high-quality OTC hCG pregnancy tests and reflects the fact that a clinically deployed pregnancy detection system must have very low false reassurance and low false alarm rates.[cite:332][cite:135][cite:341]

Formally, letting Se denote sensitivity and Sp denote specificity:

\[
H_{0,Se}: Se \le 0.97 \quad \text{vs} \quad H_{A,Se}: Se > 0.97
\]

\[
H_{0,Sp}: Sp \le 0.97 \quad \text{vs} \quad H_{A,Sp}: Sp > 0.97
\]

For operational purposes, the study will be considered successful only if both co-primary performance targets are met.

### 1.3 Secondary objectives

- To estimate AUC, positive predictive value, and negative predictive value in the enrolled population.
- To assess calibration of the model confidence score using Brier score and reliability analysis.
- To quantify performance by gestational subgroup, age, race/ethnicity, BMI category, phone model class, and lighting condition.
- To assess image acquisition failure rates and the proportion of images classified as non-evaluable by the quality-control module.
- To compare AI performance with commercially available lateral flow pregnancy tests when both are collected in the same participants as contextual benchmarking.[cite:332][cite:135]
- To examine test-retest repeatability for repeated captures from the same urine sample.

### 1.4 Secondary hypotheses

- The AUC will exceed 0.98 in the intended-use population.
- The absolute difference in sensitivity and specificity across prespecified demographic strata will not exceed 5 percentage points unless explained by wide confidence intervals due to sparse data.
- The rate of nonevaluable images after one repeat capture will be below 3%.

### 1.5 Framing: non-inferiority, superiority, or standalone validation

For a novel vision-based pregnancy detection system with no clean predicate for native-urine image interpretation, standalone validation is the most regulator-ready framing. A non-inferiority claim against a commercial lateral flow test is not sufficient because the reference standard for pregnancy status should be an independent clinical truth standard rather than another marketed test, and FDA’s historical framework for pregnancy testing is anchored to hCG-based truth, not merely comparator agreement.[cite:135][cite:332] Superiority to an OTC lateral flow product may be explored secondarily, but should not replace the primary standalone validation framework because comparator misclassification would bias estimates and complicate regulatory interpretation.[cite:332][cite:135]

## 2. Reference standard and outcome adjudication

### 2.1 Gold standard

The primary reference standard will be quantitative serum beta-hCG measured in a CLIA-certified central or site laboratory using an FDA-cleared assay. Quantitative serum beta-hCG is the accepted biochemical gold standard for early pregnancy ascertainment and avoids the circularity of validating a urine-image system against another urine-based screening device.[cite:135][cite:332]

### 2.2 Pregnancy status definition

A participant will be adjudicated as pregnant if either of the following applies:

- Serum beta-hCG is greater than or equal to the assay-specific pregnancy threshold at the index visit and follow-up confirms rising or appropriately persistent pregnancy-associated hCG; or
- Ultrasound follow-up confirms intrauterine or extrauterine pregnancy after an initially borderline biochemical result.

A participant will be adjudicated as not pregnant if:

- Serum beta-hCG is below the assay-specific non-pregnant threshold at index and remains non-pregnant on follow-up when follow-up is required; or
- Initial indeterminate/borderline hCG resolves downward to non-pregnant status without ultrasound evidence of pregnancy.

### 2.3 Ultrasound confirmation

Transvaginal or transabdominal ultrasound is not required for all participants, but it will be used as confirmatory evidence for serum-positive participants when clinically appropriate and feasible, especially in participants with discordant or borderline serum results. Ultrasound is particularly important for adjudication of biochemical pregnancies, ectopic pregnancies, and very early cases around the discriminatory zone.[cite:135]

### 2.4 Follow-up schedule for adjudication

Because very early pregnancy and peri-implantation dynamics can produce borderline hCG values, all participants with any of the following will undergo follow-up:

- Serum beta-hCG in the indeterminate/borderline zone specified in the laboratory manual.
- Discordance between AI result and serum result.
- Reported ongoing fertility treatment or very recent missed period with high clinical suspicion.
- Inadequate or questionable specimen chain-of-custody or image quality.

Follow-up will occur at 48 to 72 hours for repeat serum beta-hCG and, when indicated clinically, at 7 to 14 days for ultrasound confirmation. A rise or fall pattern consistent with viable intrauterine pregnancy, failing pregnancy, or non-pregnant status will be used in adjudication.

### 2.5 Indeterminate cases

Indeterminate cases will be assigned into one of three prespecified categories:

- Reference-standard indeterminate.
- Index-test indeterminate due to image quality / system non-evaluable output.
- Clinical-adjudication indeterminate after incomplete follow-up.

The primary analysis will exclude reference-standard indeterminate cases from the denominator but will report their frequency separately. A sensitivity analysis will treat all unresolved indeterminate cases first as false negatives/false positives and then as true negatives/true positives to create worst-case and best-case bounds. This is important because regulators generally expect transparency around exclusions and non-evaluable outcomes in diagnostic studies.[cite:305][cite:135]

## 3. Population and sampling

### 3.1 Target population

People of reproductive potential presenting for pregnancy evaluation, fertility monitoring, menstrual delay assessment, emergency or outpatient gynecologic evaluation, or self-referred testing in ambulatory settings.

### 3.2 Inclusion criteria

- Age 18 years or older, or local age of majority if different.
- Able and willing to provide informed consent.
- Able to provide a urine sample and undergo blood draw for serum beta-hCG.
- Presenting for pregnancy testing, possible early pregnancy assessment, fertility monitoring, or related evaluation.
- Willing to allow capture of smartphone images under protocol-defined procedures and to participate in follow-up if needed.

### 3.3 Exclusion criteria

- Inability to provide informed consent.
- Known current pregnancy beyond 12 completed gestational weeks if the protocol is intended to validate early-detection use only.
- Prior enrollment in the study during the same pregnancy episode.
- Recent exogenous hCG administration within a prespecified washout window, such as fertility treatment triggers, because this directly confounds the biological target.
- Specimen contamination or insufficient sample volume.
- Immediate medical instability requiring emergency management before study procedures can be completed.
- Conditions deemed by the investigator to make follow-up unlikely or outcome adjudication unreliable.

### 3.4 Recruitment strategy

Enrollment should preferentially sample across the pretest probability spectrum rather than relying on convenience sampling from a single obstetric clinic. To produce unbiased estimates of specificity, the cohort must include a large number of truly non-pregnant participants as well as participants at varying pregnancy stages, including very early gestations close to the detection boundary. Multi-setting recruitment from family planning clinics, emergency departments, reproductive endocrinology clinics, urgent care sites, and community ambulatory centers is therefore recommended.

### 3.5 Stratification plan

The study will prospectively stratify enrollment targets across the following axes:

- **Gestational age / pregnancy timing:** suspected peri-implantation or preclinical phase; estimated gestational weeks 1-4, 5-6, 7-8, 9-10, and 11-12, based on last menstrual period and adjudicated clinically.
- **Age groups:** 18-24, 25-34, 35-44, and 45+ years.
- **Race/ethnicity:** locally relevant categories with minimum prespecified representation.
- **BMI category:** <25, 25-29.9, 30-34.9, and ≥35 kg/m².
- **Phone model class:** current iPhone flagship/recent generation, older iPhone generation, premium Android, mid-tier Android, budget Android.
- **Lighting condition:** daylight dominant, warm indoor LED/tungsten, cool fluorescent/LED, low light with app-guided flash/no-flash capture.

These strata are operationally relevant because phone sensor pipelines, user behavior, and body habitus may correlate with image characteristics and healthcare-seeking pathways, and regulators increasingly expect bias and robustness documentation for AI-enabled devices.[cite:305][cite:324]

### 3.6 Handling very early pregnancy and pre-implantation period

A true pre-implantation pregnancy is biochemically undetectable even with serum beta-hCG, so participants recruited before implantation cannot be meaningfully classified as pregnant at the index timepoint. Accordingly, the protocol will classify pre-implantation participants according to index-visit truth, not future pregnancy status. Participants who conceive after the index visit are not false negatives; they are non-pregnant at baseline. This distinction is essential for both biostatistical validity and regulatory interpretability.

If desired, an exploratory sub-study may enroll participants trying to conceive before expected implantation and follow them longitudinally. However, those data must be analyzed separately because they answer a different question: prediction of imminent pregnancy rather than detection of existing pregnancy.

### 3.7 Expected prevalence

Expected prevalence depends on recruitment setting. Emergency/urgent care or self-testing settings may produce pregnancy prevalence around 10% to 30%, while fertility and early pregnancy assessment clinics may exceed 40%. To support stable estimates of both sensitivity and specificity, the study should not depend on natural prevalence alone; targeted enrichment of positive cases is acceptable for sensitivity estimation, provided that PPV and NPV are recalculated using the observed overall study prevalence and, if desired, prevalence-standardized scenarios.

For sample size planning below, an overall analyzable prevalence of 25% pregnant and 75% non-pregnant will be assumed.

### 3.8 Sample size and power analysis

The study uses co-primary endpoints of sensitivity and specificity. The sample size must therefore satisfy precision and power requirements for both positive and negative groups.

#### Precision-based sample size for a proportion

For a target proportion \(p\) and half-width \(d\) of a normal-approximation confidence interval, the classic sample size formula is:

\[
n \approx \frac{Z_{1-\alpha/2}^2 p(1-p)}{d^2}
\] (1)

For sensitivity planning, let \(p = 0.99\) and desired half-width \(d = 0.015\) with \(Z_{0.975}=1.96\):

\[
n_{pos} \approx \frac{1.96^2 \times 0.99 \times 0.01}{0.015^2} \approx 169
\] (2)

For specificity planning with the same assumptions:

\[
n_{neg} \approx 169
\] (3)

Because normal approximations can be optimistic at extreme proportions and FDA submissions usually rely on exact intervals such as Clopper-Pearson, the study should inflate these values. A pragmatic inflation to at least 250 positive and 400 negative evaluable participants is recommended for the primary analysis.

#### Hypothesis-testing perspective

To test whether true sensitivity exceeds 0.97 when the anticipated sensitivity is 0.99 using a one-sided alpha of 0.025, an exact binomial design with around 250 positive cases provides comfortable power above 80% and robust confidence interval behavior. Similarly, 400 or more negative cases gives adequate precision around a 0.99 specificity target.

#### Operational inflation

Allowing for 10% total attrition due to non-evaluable images, incomplete follow-up, and reference-standard indeterminacy, the enrollment target should be approximately:

- **Positive evaluable target:** 250
- **Negative evaluable target:** 400
- **Total evaluable target:** 650
- **Total enrolled target with attrition:** 720 to 760

If prevalence is 25%, then 760 participants would yield about 190 positives naturally, which is below the 250-positive target. Therefore, the protocol should permit controlled enrichment of likely positive participants, for example through early pregnancy assessment clinics, while preserving a broad negative cohort for specificity estimation.

### 3.9 Alternative precision-enhanced design

If the sponsor intends to pursue a high-confidence claim such as sensitivity ≥99% with lower 95% CI bound above 98%, the study should target 350 to 500 positives and 500 to 700 negatives. This more conservative design would be more likely to withstand intense scrutiny for a novel AI-based detector.

## 4. Study sites and operations

### 4.1 Study design

Prospective, blinded, multi-site diagnostic accuracy study.

### 4.2 Justification for multi-site execution

Multi-site design is required because smartphone image quality and participant characteristics vary by geography, clinic workflow, lighting architecture, and device ownership patterns. Single-site performance often overestimates real-world accuracy and does not adequately test generalization across hardware and user populations. FDA’s AI/ML framing and GMLP principles emphasize representative data and clinically relevant conditions of use, which strongly supports multi-site validation.[cite:305][cite:324]

### 4.3 Number and type of sites

A minimum of 5 to 8 sites is recommended, with at least:

- One emergency or urgent care site.
- One reproductive endocrinology / fertility site.
- Two or more general OB/GYN or family planning ambulatory sites.
- One geographically distinct community site serving a diverse demographic population.

### 4.4 Site qualification

Each site must demonstrate:

- Ability to recruit the intended-use population.
- Access to serum beta-hCG testing with chain-of-custody controls.
- Capability to conduct follow-up serum and ultrasound when required.
- Staff trained in GCP, specimen handling, and standardized image acquisition.

### 4.5 Training and standardization

All site personnel involved in study procedures will undergo standardized training on:

- Eligibility screening and consent.
- Urine sample collection and labeling.
- Blood draw timing and processing.
- Image capture SOP.
- Use of study smartphones if a provisioned-device design is chosen, or participant-device onboarding if bring-your-own-device is allowed.
- Documentation of ambient conditions and procedural deviations.
- Reporting of adverse events and unexpected positive results.

Training will be documented by certificates, competency checks, and retraining logs.

### 4.6 Image capture protocol

To reduce pre-analytic variability, the following capture procedures will be mandated:

- Images must be acquired before reference results are known.
- At least two images per sample under the app-guided workflow.
- Automated logging of device model, operating system version, timestamp, flash setting, and exposure metadata when available.
- Prespecified framing instructions and live on-screen alignment cues.
- Storage of original files plus processed derivatives.
- Independent quality-control labeling of a sample of images to audit adherence.

### 4.7 Data quality protocols

- Real-time image quality scoring by the app with repeat capture requested if quality is below threshold.
- Central data monitoring to flag anomalous distributions by site or device class.
- Regular review of missingness, protocol deviations, and enrollment balance.
- A blinded imaging core lab or central review panel for a random subset of captures.

## 5. Statistical analysis plan

### 5.1 Analysis populations

- **Intent-to-diagnose (ITD):** all enrolled participants with an index image capture attempt, regardless of image quality or follow-up completion.
- **Evaluable primary analysis set:** participants with an evaluable AI output and adjudicated pregnancy status.
- **Per-protocol set:** participants without major protocol deviations.

The primary analysis should be performed on the evaluable set, with supportive analyses on the ITD population treating non-evaluable AI outputs as failures from a usability and real-world performance perspective.

### 5.2 Primary endpoint

The primary endpoint is binary diagnostic accuracy relative to adjudicated pregnancy status, summarized as:

- Sensitivity = TP / (TP + FN)
- Specificity = TN / (TN + FP)

Exact two-sided 95% Clopper-Pearson confidence intervals will be reported for sensitivity and specificity.

### 5.3 Secondary endpoints

- AUC from the continuous confidence score.
- PPV and NPV using the observed study prevalence and selected external prevalence scenarios.
- Brier score for probabilistic calibration.
- Calibration slope/intercept and reliability plot summaries.
- Non-evaluable rate and repeat-capture rescue rate.
- Test-retest repeatability for repeated captures.

### 5.4 Hypothesis testing framework

Because sensitivity and specificity are co-primary, no multiplicity adjustment is needed between them if success requires both endpoints to meet their thresholds. Secondary endpoints and subgroup analyses will be interpreted descriptively unless a formal hierarchical testing scheme is prespecified.

### 5.5 Confidence interval methods

- **Sensitivity and specificity:** Clopper-Pearson exact intervals.
- **AUC:** DeLong confidence intervals.
- **Predictive values:** exact or bootstrap intervals depending on scenario analysis.
- **Calibration metrics:** bootstrap confidence intervals where appropriate.

### 5.6 Subgroup analyses

Performance will be disaggregated by:

- Gestational timing bins.
- Age group.
- Race/ethnicity.
- BMI category.
- Phone model class.
- Lighting condition.
- Geographic site.

For each subgroup, sensitivity, specificity, and non-evaluable rate will be reported with exact confidence intervals. Interaction tests using logistic regression with product terms may be performed exploratorily, but descriptive subgroup performance is the primary regulatory objective.

### 5.7 Missing data handling

Missingness can arise in reference standard, image capture, metadata, or follow-up. The following prespecified rules will apply:

- Missing primary reference standard with no adjudication: excluded from the primary evaluable analysis, counted in ITD sensitivity analyses.
- Missing AI output due to app failure or inadequate image: counted separately as non-evaluable; treated as failure in supportive real-world analyses.
- Missing covariates for subgroup analyses: subgroup denominator reduced; no single imputation for the primary report.
- Missing follow-up in borderline cases: case remains indeterminate unless adjudicated by the clinical events committee.

Multiple imputation is not recommended for the primary endpoint because pregnancy truth status should be directly observed or adjudicated rather than modeled.

### 5.8 Interim analysis rules

One blinded sample-size re-estimation may be performed after approximately 50% of planned enrollment to verify prevalence assumptions, non-evaluable rate, and subgroup balance. No formal interim efficacy stopping is recommended because this is a diagnostic validation study, not a therapeutic trial. Unblinded performance looks before model lock should be prohibited to avoid operational bias.

### 5.9 Decision threshold justification

The AI system must have a prospectively fixed binary decision threshold before clinical validation begins. The threshold should be selected using an independent development/validation dataset and justified based on the clinical cost of false negatives versus false positives. In pregnancy detection, false negatives generally have greater potential safety impact than false positives, suggesting a sensitivity-prioritized threshold, provided specificity remains acceptable.

### 5.10 Example operating-point justification

A candidate threshold may be chosen to maximize a weighted Youden index:

\[
J_w = w \times Sensitivity + Specificity - 1
\] (4)

where \(w > 1\) to reflect the higher cost of false negatives. The chosen weight must be prespecified and justified in the statistical analysis plan.

### 5.11 Illustrative shell tables

| Endpoint | Numerator | Denominator | Estimate | 95% CI | Success criterion |
|---|---:|---:|---:|---|---|
| Sensitivity | TP | TP+FN | % | Exact CP | Lower bound > 97.0% |
| Specificity | TN | TN+FP | % | Exact CP | Lower bound > 97.0% |
| Non-evaluable rate | Non-evaluable | All attempted | % | Exact CP | < 3% after repeat |
| AUC | NA | NA | Value | DeLong | Descriptive |

## 6. AI-specific controls

### 6.1 Model lock

The full algorithm, including preprocessing, quality-control logic, threshold, and postprocessing, must be frozen before the first participant in the pivotal study is enrolled. A model lock memorandum will include:

- Training dataset freeze date.
- Version identifiers for code, weights, preprocessing assets, and decision thresholds.
- Evidence that no pivotal-study images contributed to training, threshold selection, or calibration fitting.

FDA’s AI/ML SaMD materials emphasize lifecycle control and transparency around modifications; a locked model is the safest approach for a pivotal validation study.[cite:305][cite:324]

### 6.2 Prevention of test-set leakage

The protocol must document how the sponsor prevented leakage between development and clinical validation datasets. Required controls include:

- Unique subject identifiers across all sponsor datasets.
- Deduplication by image fingerprint and metadata.
- Blocking by participant, not by image, when partitioning development datasets.
- Exclusion of all study-site participants from training if any pre-pivotal site data were used in development.
- Audit trail of dataset provenance.

### 6.3 Handling model updates during the study

No algorithmic updates are permitted during the pivotal study. Bug fixes that do not change model output logic may be allowed only with data coordinating center approval, documented impact assessment, and ideally dual-run verification showing identical outputs. Any update affecting model predictions, preprocessing, image quality gating, or threshold requires protocol amendment and likely restart or separate cohort analysis.

### 6.4 Calibration analysis

Since the product may output confidence scores, calibration must be assessed using:

- Brier score.
- Calibration-in-the-large.
- Calibration slope.
- Reliability diagram with prespecified bins.
- Optional isotonic or Platt recalibration only on a separate non-pivotal dataset, not on the pivotal dataset.

### 6.5 Robustness and stress testing

Although not primary clinical endpoints, the sponsor should maintain a companion analytical robustness report addressing:

- Blur, defocus, glare, glare masking, JPEG compression, HDR-induced tone shifts.
- Device model shifts.
- Lighting shifts.
- User handling errors.

These concerns are well aligned with FDA’s attention to AI/ML lifecycle robustness and with the known challenges of smartphone colorimetric analysis under uncontrolled conditions.[cite:305][cite:324]

## 7. Bias and fairness analysis

### 7.1 Equity objectives

The study must prospectively evaluate whether diagnostic performance is consistent across demographic and device subgroups. This is a scientific and regulatory necessity for consumer-camera medical AI because performance can drift with phenotype, access patterns, and hardware.

### 7.2 Prespecified subgroup minimums

The sponsor should set operational minimum sample targets per subgroup whenever feasible, for example:

- At least 50 positive and 100 negative cases in major race/ethnicity strata.
- At least 50 positive cases captured on iPhone-class devices and 50 on Android-class devices.
- At least 30 positive cases in low-light or non-daylight conditions.

### 7.3 Minimum acceptable subgroup performance

A practical fairness criterion is that no major subgroup should show sensitivity or specificity more than 5 percentage points below the overall study estimate without formal root-cause analysis. Confidence intervals must be reported, and sparse-data caveats should be explicit.

### 7.4 Statistical approach

- Descriptive estimates with exact confidence intervals for each subgroup.
- Absolute and relative performance gaps versus the overall cohort.
- Exploratory logistic regression for interaction effects.
- Assessment of image quality failure disparity across subgroups.

## 8. Comparison to clinical benchmarks

### 8.1 Current market context

FDA-cleared OTC pregnancy tests historically claim around 25 mIU/mL sensitivity, with some products claiming lower cutoffs under specified conditions, and market expectations for clinical performance are correspondingly high.[cite:332][cite:135][cite:341] That does not mean every commercial test performs identically in every study, but it does mean that any new AI pregnancy detector will be judged against an established standard of high analytical sensitivity around the missed-period timeframe.[cite:135][cite:332]

### 8.2 Benchmarking strategy in this protocol

The protocol recommends optional parallel testing with one or more marketed lateral flow urine hCG tests in a subset or all participants. These results are contextual and not primary truth. The analysis may report:

- Percent agreement between AI and comparator lateral flow test.
- Difference in sensitivity/specificity versus serum-adjudicated truth.
- Discordance patterns near the hCG decision boundary.

### 8.3 Meta-analytic context

If the final study report includes literature benchmarking, it should cite systematic evidence on home pregnancy test performance rather than relying on marketing materials alone. However, the present protocol intentionally avoids depending on literature-derived sensitivity/specificity as a formal benchmark because the pivotal comparison should remain anchored to prospectively collected truth data.

## 9. Ethical framework

### 9.1 Ethical principles

The study will follow ICH-GCP, the Declaration of Helsinki, and applicable local regulations. Because pregnancy results can have immediate psychological, reproductive, and medical consequences, result disclosure and counseling processes must be carefully designed.

### 9.2 IRB / ethics submission package

The sponsor or CRO will submit the following:

- Full protocol.
- Investigator brochure or device dossier.
- Informed consent form.
- Recruitment materials.
- Privacy notice and data handling plan.
- CRFs and participant diary forms, if any.
- DSMB/medical monitor charter if used.
- Risk analysis focused on incorrect result disclosure.

### 9.3 Informed consent structure

Consent must explain:

- The investigational nature of the AI system.
- That clinical truth will be determined by serum testing and follow-up, not by the app.
- That images and metadata will be stored and analyzed.
- Potential risks of emotional distress from unexpected pregnancy or non-pregnancy results.
- How results will or will not be returned during the study.

### 9.4 Return of results protocol

Because incorrect immediate return of an investigational AI result could cause harm, the primary protocol should avoid using the AI result for clinical decision-making during pivotal validation. Recommended approach:

- The investigational AI output remains blinded to participant and care team.
- Standard-of-care pregnancy testing and serum hCG results guide clinical care.
- If local IRB requires return of certain information, only validated clinical results should be returned, not investigational classifications.

### 9.5 Positive-result handling and support

Unexpected pregnancy results can create acute emotional stress or safety concerns. Sites must have a prespecified response process, including:

- Immediate communication of standard clinical test results by qualified staff.
- Access to counseling resources consistent with local law and practice.
- Referral pathways for prenatal care, miscarriage care, or ectopic pregnancy evaluation where clinically indicated.
- Documentation of participant distress events as adverse events when appropriate.

### 9.6 Data retention and destruction

Images, metadata, and reference results will be stored in de-identified or coded form for the regulatory retention period specified by sponsor SOP and applicable law. Access controls, encryption at rest and in transit, and role-based permissions are mandatory. Destruction schedules should distinguish between regulated study records that must be retained and exploratory data that may be deleted earlier under consent terms.

## 10. Real-world validation phase and postmarket surveillance

### 10.1 Purpose

If the product achieves clearance or authorization, a postmarket real-world performance study should evaluate generalization under true consumer use. FDA’s AI/ML framework emphasizes lifecycle oversight and postmarket monitoring for drift, bias, and failure modes.[cite:305][cite:324]

### 10.2 Design

A prospective observational registry will collect:

- Real-world captures and quality metrics.
- Device model/OS information.
- User-reported context such as timing since missed period.
- Confirmatory pregnancy outcomes where feasible, including subsequent serum tests, clinician diagnosis, or ultrasound.

### 10.3 Monitoring metrics

- Ongoing sensitivity/specificity in linked-outcome subsets.
- Non-evaluable rate and repeat-capture rate.
- Drift in image feature distributions by phone class or geography.
- Complaint rate and serious incident rate.
- Fairness metrics across demographic groups.

### 10.4 Trigger thresholds

The postmarket plan should define triggers for CAPA or field action, such as:

- Sensitivity drop of more than 2 percentage points versus pivotal baseline in a monitored cohort.
- Sudden increase in non-evaluable rate for a new phone OS version.
- Evidence of subgroup-specific degradation beyond prespecified fairness margins.

## Case report form (CRF) outline

### CRF Module 1: Screening and eligibility

- Site ID
- Participant ID
- Date/time of screening
- Age
- Eligibility checklist
- Consent obtained (Y/N)
- Exclusion reason if screen failure

### CRF Module 2: Baseline clinical data

- Last menstrual period date
- Estimated gestational age if known
- Pregnancy symptoms
- Fertility treatment within past 30 days
- Current medications, especially exogenous hCG
- Relevant gynecologic/obstetric history
- BMI, race/ethnicity, smoking status

### CRF Module 3: Specimen and imaging

- Urine collection time
- Blood draw time
- Sample ID linkage
- Device model / OS
- Lighting condition code
- Flash/HDR status if available
- Number of capture attempts
- Image quality flags
- App output (stored blinded)

### CRF Module 4: Reference standard

- Serum beta-hCG value
- Assay name and laboratory ID
- Urine comparator test result if used
- Ultrasound performed (Y/N)
- Ultrasound findings

### CRF Module 5: Follow-up

- Repeat serum beta-hCG values and times
- Follow-up ultrasound
- Final adjudicated pregnancy status
- Reason for indeterminate status if applicable

### CRF Module 6: Safety and distress

- Adverse events
- Distress event related to unexpected pregnancy result
- Counseling/referral provided

## Operational statistical shells

### Primary 2x2 table

|  | Reference pregnant | Reference not pregnant |
|---|---:|---:|
| AI positive | TP | FP |
| AI negative | FN | TN |

### Derived metrics

\[
Sensitivity = \frac{TP}{TP + FN}
\] (5)

\[
Specificity = \frac{TN}{TN + FP}
\] (6)

\[
PPV = \frac{TP}{TP + FP}
\] (7)

\[
NPV = \frac{TN}{TN + FN}
\] (8)

### Example Clopper-Pearson reporting language

For each primary proportion, the two-sided 95% exact Clopper-Pearson confidence interval will be reported as the primary inferential interval because exact methods are standard and conservative for binomial endpoints in diagnostic submissions.

## Monitoring, governance, and documentation

### Committees

- Medical Monitor
- Clinical Events Committee for adjudication of difficult cases
- Data Management Committee
- Optional DSMB if sponsor/IRB deems necessary

### Core documents

- Protocol and amendments
- SAP finalized before database lock
- Data management plan
- Monitoring plan
- Image handling SOP
- Adjudication charter
- Model lock memorandum
- Deviation handling SOP

## Recommended execution sequence for a CRO

1. Finalize intended use, claims, and analysis populations.
2. Finalize model lock and software version control package.
3. Confirm laboratory assay and adjudication algorithm.
4. Stand up eCRF, image repository, and metadata pipeline.
5. Train and qualify sites.
6. Run 20- to 40-subject operational pilot without looking at efficacy endpoints to confirm workflow.
7. Launch pivotal enrollment.
8. Perform blinded prevalence and quality review at 50% enrollment.
9. Lock database and execute SAP.
10. Prepare clinical study report with exact interval estimates, subgroup tables, non-evaluable analysis, and fairness appendix.

## Interpretation and regulatory positioning

A study built on this protocol would be scientifically rigorous enough for peer review and directionally aligned with FDA expectations for AI-enabled medical devices, but the regulatory success of the product would still depend heavily on the intended use and whether the underlying biological measurement has a plausible predicate or clinical rationale. FDA’s published materials on AI/ML SaMD make clear that the pathway is not defined by the AI label alone but by the device function, risk, and evidence package.[cite:305][cite:324] For a smartphone-based pregnancy detector, this means the clinical study can be robust, yet the overall clearance strategy may still favor a chemistry-plus-reader architecture over vision-only analysis of native urine because the latter lacks a clear predicate and may face a higher burden under De Novo review.[cite:329][cite:332][cite:135]
