# MASTER PROMPT v2: Dual-Track Research and Commercial Platform

## For Claude Code - Complete Build Plan

This document supersedes MASTER_PROMPT.md v1. Changes from v1:
- Acknowledges all SEVEN project-knowledge documents, not four.
- Adds a research arm for rigorous investigation of native-urine spectral signatures, following Urinary Physiological Changes section 8.1 framing.
- Expands the analyte panel from hCG alone to hCG + E1-3G + PdG, per Urinary Changes section 3.1-3.2 and Table 2.
- Aligns the validation architecture to ai_pregnancy_validation_protocol.md v1.0.
- Incorporates engineering knowledge from Engineering Anatomy of Modern Home Pregnancy Tests for informed design of the strip-reading and signal-extraction modules.

---

## FRAMING: WHY THIS IS DUAL-TRACK

Track A: Commercial track (goes to FDA 510(k)/De Novo for clearance and revenue)
- Multi-analyte smartphone reader for hCG + E1-3G + PdG + 10-parameter urinalysis
- Prenatal risk fusion layer
- Locked model, regulatory-grade documentation

Track B: Research track (generates IP, scientific publications, potential moat)
- First-in-world controlled imaging corpus of standardized urine photographs with known pregnancy status and full biochemical metadata
- Hyperspectral-from-RGB inference to probe for sub-visual pregnancy signatures
- Rigorous null-result-tolerant study design using serum beta-hCG as ground truth
- Any positive finding is published and protected; any null finding is itself valuable scientific output

Both tracks share 85 percent of the codebase (capture, calibration, edge inference, data infrastructure). Only the analyte heads and claim language differ.

No claim from Track B enters Track A labeling until Track B validation meets prespecified thresholds and passes independent review. This is the firewall that protects both the science and the regulatory integrity.

---

## CONTEXT BLOCK FOR CLAUDE CODE (paste at the start of every stage)

```
You are building a dual-track smartphone-based urinalysis, pregnancy detection, and early pregnancy monitoring system. Two tracks share a codebase; one goes to clinical clearance now, one runs as a prospective research program to investigate whether native urine contains sub-visual spectral signatures of pregnancy.

PROJECT KNOWLEDGE, read all before starting any stage:
1. smartphone_urinalysis_market_intel.md - competitive landscape, patents to design around
2. urine_appearance_atlas_cv.md - visual phenomenology, what CV can measure
3. regulatory_roadmap_pregnancy_ai.md - FDA pathway, documentation needs
4. forensic_failures_medical_ai.md - 20 documented failure modes to avoid
5. Urinary_Physiological_and_Biochemical_Changes_in_Early_Human_Pregnancy.md - biomarker biology and research gaps
6. Engineering_Anatomy_and_Performance_of_Modern_Home_Pregnancy_Tests.md - LFA mechanics for informed signal extraction
7. ai_pregnancy_validation_protocol.md - the clinical study this product is being built to pass

CORE RULES:
- Firewall: Track B (research) claims never reach Track A (commercial) labeling until the validation protocol primary endpoints are met and externally reviewed.
- Every training/evaluation split is by participant ID, by acquisition episode, by site, and by phone model. Never by image. Leakage checks run in CI.
- Every model is locked before any pivotal validation. PCCP governs updates.
- Every module has a docstring citing: intended use, regulatory class, confounders, limitations, and specific sections of the 7 project-knowledge documents.
- No em-dashes, no Hebrew maqafs in any text artifact. Use hyphens, colons, commas.
- No adaptive learning in production without regulatory review.

TRACK A COMMERCIAL ANALYTES (locked, chemistry-backed):
- hCG lateral flow (intact + free beta, optionally beta-core-aware)
- E1-3G enzymatic/immunochromatographic (early luteal signal)
- PdG enzymatic/immunochromatographic (luteal phase signal)
- 10-parameter urinalysis (glucose, protein, blood, pH, SG, ketone, nitrite, leukocytes, bilirubin, urobilinogen)
- ACR (for CKD/preeclampsia monitoring)

TRACK B RESEARCH ANALYTES (exploratory, no clinical claim):
- Hyperspectral-from-RGB reconstruction of native urine spectra
- Multi-frame temporal features (foam decay, sediment settling)
- Differential within-subject features (same user across cycle)
```

---

## STAGE 1: Scaffold and regulatory-grade repository

Identical to v1 Stage 1, with these additions:

```
Add two more top-level directories:
/research
  /corpus-collection     Protocols, consent forms, and data-collection runners for the prospective imaging corpus
  /hyperspectral         Spectral inference experiments (RGB -> multi-band reconstruction)
  /null-hypothesis-tests Pre-registered negative-control tests for Track B
/clinical
  /protocols             Copies and working versions of ai_pregnancy_validation_protocol.md and derivative documents
  /site-sop              Per-site standard operating procedures for specimen collection and imaging

Add a root-level TRACK_FIREWALL.md document describing:
- What information flows from Track B to Track A (only infrastructure improvements and confounder models)
- What NEVER flows (pregnancy-classification outputs from Track B until formally cleared)
- Sign-off process for any proposed firewall change (requires clinical, regulatory, and ethics review)
```

---

## STAGE 2: Capture pipeline with reference-free colorimetry AND hyperspectral pre-processing

Extended from v1. Same reference-free colorimetry goals, plus new Track B affordances.

```
Build the capture pipeline in /apps/mobile and /packages/cv-core with these additions over v1:

Part A (unchanged): mobile capture UX with quality gate.

Part B (extended): reference-free color calibration WITH optional spectral reconstruction branch.
- Standard branch feeds rectified calibrated sRGB to downstream readers.
- Optional research branch, gated by a feature flag READ_RESEARCH_SPECTRA, additionally passes the same frames to a learned RGB-to-spectral model that outputs a 31-band (400-700 nm, 10 nm steps) estimated reflectance spectrum per pixel.
- The spectral model is trained on public hyperspectral datasets (e.g., ICVL, CAVE) with fine-tuning planned on captured-phone vs ground-truth-spectrophotometer pairs collected during Track B corpus collection.
- Spectral output is stored but NOT consumed by any Track A inference.

Part C (new): Dual-capture protocol for research samples
- For enrolled research participants, capture protocol includes:
  - Urine in standardized clear cup against white background (native-urine photo).
  - Same urine imaged again immediately after a drop of standard reagent is added (reagent-stimulated photo).
  - Three reagent drops are tested per sample in separate aliquots: A) Benedict's-style glucose reagent, B) nitroprusside-style ketone reagent, C) an E1-3G or PdG enzymatic reagent, chosen to generate color changes that scale with analyte concentration.
  - All captures timestamped and paired to the same urine sample.
- This dual-capture approach is a direct response to Urinary Changes section 8.1 research-gap framing and section 7.2 ranking, which notes medium-high signal potential from steroid-metabolite colorimetry.

Part D (new): Phone-ISP characterization pipeline
- A one-time per-phone-model calibration routine (run during corpus collection) captures a Macbeth ColorChecker under controlled light and derives a phone-ISP fingerprint.
- Fingerprints are aggregated into a cross-model calibration library, stored in /packages/cv-core/phone-fingerprints/.
- This is how we design around Healthy.io's US9972077B2 color-board patent: no per-capture reference is needed because the phone itself has been pre-characterized.

Quality gates remain the same as v1, with an added check for spectral-reconstruction confidence when the research branch is active.

Deliverables: working mobile capture flow, cv-core library, research-branch toggle, phone-fingerprint library seeded with 10 phone models, plus a model card for the spectral reconstruction model including explicit research-only disclaimer.
```

---

## STAGE 3: Multi-analyte strip reader (hCG, E1-3G, PdG, 10-parameter)

This stage replaces v1 Stage 3 and Stage 4. The unified reader handles four strip families.

```
Build a unified lateral-flow and reagent-strip reader in /packages/ml-models/strip-reader.

Architecture
- Shared backbone (EfficientNet-B0 or MobileViT-S) with four task-specific heads:
  - head_hcg: semi-quantitative intact-hCG estimation in mIU/mL plus category (not-pregnant, faint, positive, strong, equivocal-5-to-25-window)
  - head_e1_3g: semi-quantitative E1-3G in ng/mg creatinine range, plus categorical (low, normal, elevated)
  - head_pdg: semi-quantitative PdG, with same categorical structure
  - head_10p: 10-parameter dipstick classifier across all pads
- A cross-task regularizer encourages shared representations for common features (strip geometry, line detection) while allowing head specialization.
- A timing-aware module reconciles readings taken at manufacturer-specified windows (hCG typically 3-5 minutes, 10-parameter 60-120 seconds depending on analyte).

Chemistry-informed design
- Per Engineering Anatomy doc section 2.3, colloidal-gold LFA test lines have LSPR peak at 520-530 nm. The reader is explicitly trained to attend to line intensity at this spectral region, which is why the optional hyperspectral branch from Stage 2 is valuable for Track B extension.
- Hook-effect detection (Engineering Anatomy section 7 and Urinary Changes section 2.6.2): the model includes a hook-effect anomaly head that flags cases where the test-line pattern deviates from expected sandwich-assay morphology.
- Beta-core-fragment variant hook effect (Urinary Changes section 2.2): the model's hook-head is trained on simulated and real beta-core-predominant samples, allowing it to flag late-first-trimester samples with unusual band patterns.

Confounder disentanglement
- An auxiliary multi-label head predicts confounders per capture:
  - B-vitamin tinting (bright-neon-yellow background)
  - Bilirubin staining
  - Hematuria tinting
  - Extreme concentration or dilution
  - Phenazopyridine or rifampin use (if detectable by spectrum)
  - Menstrual-blood contamination
- Confounder predictions are displayed to users AND fed back as auxiliary features into the main heads, improving robustness per Urinary Changes section 6.

Training data strategy (Track A)
- Primary: lab-generated strips across full concentration range, ground truth from Siemens Clinitek (10-p) and quantitative serum beta-hCG (hCG) and lab immunoassay (E1-3G, PdG).
- Cross-manufacturer: at least 3 hCG strip makers validated, at least 2 E1-3G and PdG strip makers where commercially available.
- Field set: multi-site, multi-phone, multi-lighting captures from at least 500 participants across trying-to-conceive, early pregnant, established pregnant, and non-pregnant cohorts.
- Splits: by participant and by episode, verified in CI with a perceptual-hash leakage check.

Calibration
- Label smoothing + explicit calibration regularizer (ECE target under 0.03).
- Reliability diagrams, Brier score, and bootstrap confidence intervals reported per head.

Evaluation (Track A)
- hCG head: sensitivity/specificity at 25 mIU/mL per ai_pregnancy_validation_protocol.md primary hypothesis (target lower 95 percent CI bound above 97 percent).
- hCG head: sensitivity at 10 mIU/mL with uncertainty reporting, per the 2.4 detection thresholds context in Urinary Changes.
- E1-3G and PdG heads: performance against lab immunoassay, per-window (days 7, 9, 11, 13 post LH peak) reporting.
- 10-parameter head: weighted kappa vs Clinitek, target >= 0.85.
- Cross-phone worst-subgroup kappa is the primary phone-robustness metric.
- Per-gestational-week performance for hCG head, 3-12 weeks.

Regulatory artifacts
- MODEL_CARD.md per head, with locked weights SHA, training data description, subgroup performance, known failure modes.
- Validation reports in /packages/regulatory/validation/strip-reader-Vx.md aligned to both FDA OTC hCG guidance and the protocol's section 5 statistical analysis plan.
- PCCP covering allowed updates per head independently.

Ship as a callable library plus cloud inference endpoint. Mobile integration comes in Stage 5.
```

---

## STAGE 4: Research corpus collection and Track B exploratory modeling

NEW stage, no v1 equivalent. This is the scientifically ambitious work.

```
Build the Track B research infrastructure in /research/.

Goal
Answer, for the first time in the peer-reviewed literature, whether smartphone-captured urine images (with and without reagent stimulation) contain sub-visual spectral, textural, or temporal signatures of early pregnancy that are statistically and clinically distinguishable from non-pregnant urine, beyond confounders.

This is framed as research from day one. Any positive outputs from this stage are subject to independent statistical review and DO NOT enter the Track A commercial product without separate clearance.

Corpus design
- Prospective enrollment mirroring ai_pregnancy_validation_protocol.md with the following additions:
  - Cycling, trying-to-conceive cohort: daily captures from day of LH surge through 21 days post-ovulation, paired with daily urinary E1-3G, PdG, and intact-hCG lab measurements.
  - Confirmed-pregnant cohort: weekly captures through first trimester, paired with serum beta-hCG and ultrasound.
  - Non-pregnant controls: matched on age, race, BMI, medications, captured on matching days to enable within-subject and between-subject comparisons.
  - Target: 500 participants across three cohorts, approximately 10000-15000 captures total.
- All captures include:
  - Native-urine photo (clear cup, white background, dual-capture protocol from Stage 2)
  - Three reagent-stimulated photos (glucose, ketone, steroid-metabolite reagents)
  - Metadata: time since LH surge, last meal, last medication, last supplement, hydration behavior, medications
  - Paired lab panel: serum beta-hCG, urine E1-3G, urine PdG, urine intact-hCG, urine creatinine, urine osmolality, urine specific gravity
  - Phone model, ISP version, timestamp
- IRB approval at each site before any capture. Consent explicitly covers research use of images and biochemical data.

Pre-registered analyses (freeze before first enrollment)
Analysis 1: Null hypothesis test on native-urine color alone
- Hypothesis: native urine color (CIE L*a*b*, HSV statistics, and spectral-band energies from the hyperspectral branch) does NOT differentiate pregnant from non-pregnant on matched captures.
- Pre-registered statistical test: permutation test with within-subject and between-subject pairings.
- Expected outcome per Urinary Changes section 5.1 and 7.1: null (no signal). Publishing this as a rigorous negative result is itself a scientific contribution.

Analysis 2: Subthreshold signal exploration on native urine
- Exploratory gradient-boosted model on all extractable features from native-urine captures.
- Outputs: held-out AUROC for pregnancy classification.
- Pre-registered: any AUROC above 0.55 at p < 0.001 (Bonferroni-corrected across feature families) is considered evidence of a subthreshold signal warranting deeper investigation.
- Pre-registered: AUROC at or near 0.50 is considered confirmation of the null, publishable as such.

Analysis 3: Reagent-stimulated captures for E1-3G and PdG
- Hypothesis: reagent-stimulated captures at known timing windows (day 7-14 post LH) carry signal distinguishing conception from non-conception cycles.
- This is the likely high-yield analysis per Urinary Changes Table 2 (Medium-High signal for steroid-metabolite strip pads).
- Pre-registered statistical test: classification AUROC with held-out cohort, calibrated confidence intervals.

Analysis 4: Within-subject differential analysis
- For users with baseline captures outside the conception window, does a delta-feature representation (current - baseline) improve classification vs absolute features?
- Pre-registered: improvement of at least 5 AUROC points required to declare differential signal.

Analysis 5: Temporal features (foam decay, sediment settling)
- Per Urine Appearance Atlas sections 3 and 5, these are weak signals alone. Analysis asks whether they add marginal AUROC over the main feature set.

Publication commitments
- Any null result is published within 12 months of study closure.
- Any positive result is externally replicated at a second independent site before commercial incorporation.
- Pre-registration is filed with OSF or similar registry before first enrollment.

Track B modeling framework (/research/hyperspectral/)
- RGB-to-spectral reconstruction model with uncertainty quantification.
- Multi-modal fusion model combining native-urine spectra + reagent-stimulated captures + user metadata.
- Interpretability layer (SHAP, Integrated Gradients) to identify which spectral bands or feature combinations drive any observed signal. This is critical for later regulatory defensibility if any finding is translated to Track A.

Deliverables
- Pre-registered study protocol with OSF link
- IRB-approved consent forms and capture SOP
- Corpus collection dashboard with enrollment, completion, and quality metrics
- Five locked pre-registered analysis notebooks
- A NULL_RESULT_READY.md document acknowledging that null is the expected outcome and that the scientific value holds either way
```

---

## STAGE 5: Prenatal risk fusion and early-pregnancy-monitoring layer

Extended from v1 Stage 5 with the expanded analyte panel.

```
Build the prenatal risk fusion and monitoring module in /packages/ml-models/prenatal-fusion.

Inputs (Track A, locked)
- hCG readings (semi-quantitative, from Stage 3)
- E1-3G and PdG readings (daily or every-other-day during try-to-conceive period)
- 10-parameter urinalysis readings
- User-reported symptoms, cycle timing, gestational age when known

Outputs
- Pregnancy likelihood index: probabilistic output combining hCG + E1-3G + PdG + timing. This is the commercial differentiator: competing products use hCG alone and therefore have a detection floor at approximately day 10 post-ovulation. By combining E1-3G and PdG, this system aims to generate a meaningful probabilistic signal from day 7 post-LH (see Urinary Changes section 3.1-3.2).
- hCG doubling trajectory analysis with flags for suspected ectopic or failing-pregnancy patterns.
- Preeclampsia risk flag (persistent proteinuria trend plus symptoms), UTI flag, GDM flag, HG/dehydration flag.
- Each flag includes its evidence trail.

Design principles (same as v1)
- Decision support, not diagnosis.
- Interpretable model (Bayesian network or boosted trees with SHAP).
- Hard rules for escalation in critical patterns (suspected ectopic, heavy bleeding symptom + positive hCG, severe headache + proteinuria, etc).

Evaluation
- Retrospective validation against confirmed clinical outcomes.
- Prospective validation as part of the ai_pregnancy_validation_protocol.md extended endpoints.
- Explicit comparison against hCG-only baseline to quantify the value of adding E1-3G and PdG.

Deliverables
- Fusion module
- Clinician dashboard (/apps/clinician-web)
- Validation report documenting the incremental value over hCG-only approaches
```

---

## STAGE 6: Locked release, PCCP, and submission-ready artifacts

Identical to v1 Stage 6, with these additions:

```
Additional artifacts specific to the expanded system:

1. Claims matrix now spans three analyte families (hCG, E1-3G, PdG) plus 10-parameter plus prenatal fusion. Each claim is tied to its supporting evidence and its specific labeling.

2. The E1-3G and PdG claims are the most novel to FDA. Submission strategy:
   - Primary 510(k) for hCG reader (predicate: existing OTC smartphone pregnancy readers and/or Scanwell-style clearance)
   - Secondary 510(k) or De Novo for E1-3G and PdG as fertility/ovulation monitoring. Rule-out strategy: First Response Daily Ovulation Test and similar E1-3G-based products have existing clearances; the submission rides on these predicates.
   - Prenatal fusion labeled as clinical decision support tool (CDS), following FDA CDS criteria to potentially qualify as non-device software depending on final feature design, with explicit fallback to SaMD classification if needed.

3. Track B explicitly excluded from the initial 510(k) submission. A separate research registry maintains the Track B results independently.

4. Labeling is layered:
   - Clinician-facing labeling with full statistical performance claims.
   - Consumer-facing labeling with plain-language guidance and strong confirmatory-testing messaging.
   - Both versions explicitly state what the product is NOT (not a diagnosis, not a substitute for clinical care, not validated for IVF monitoring or for gestational-trophoblastic-disease follow-up).
```

---

## STAGE 7: Red-team evaluation before submission

Same as v1 Stage 7, plus these Track B specific red-teams:

```
Additional red-team exercises:

Red-team 9: Track B firewall integrity
- Audit the codebase for any unintended information flow from research corpus to commercial model weights or thresholds.
- Verify that all Track A training runs explicitly exclude research-corpus-derived features unless those features have been independently validated and re-collected in a Track-A-eligible study.

Red-team 10: Pre-registration adherence
- Verify that Track B analyses matched the pre-registered plan, that no undisclosed analyses were run, and that all outcomes (including null results) are reported.

Red-team 11: Multi-analyte false positive risk
- Specifically probe: does adding E1-3G and PdG as probabilistic inputs inflate the false-positive rate by combining noise? Run sensitivity analyses with E1-3G and PdG heads disabled to confirm that the combined pregnancy-likelihood index does not underperform hCG-only on specificity.

Red-team 12: Beta-core fragment variant hook effect
- Deliberately test on late-first-trimester samples where beta-core predominates. Verify that the system correctly flags these rather than missing them or producing false confidence.

Red-team 13: Menstrual contamination and implantation bleeding
- Per Urinary Changes section 6.5, this is a critical confounder in the peri-implantation window. Verify that captures with visible blood flags appropriately route to equivocal/repeat-testing paths.

No release to FDA submission until all 13 red-teams return signed GO.
```

---

## SEQUENTIAL EXECUTION GUIDE

Do NOT feed Claude Code all seven stages at once. Execute in this order, with human review between each:

1. Stage 1 (scaffold): 2-3 weeks
2. Stage 2 (capture + calibration + spectral branch): 6-8 weeks
3. Stage 3 (unified strip reader): 10-14 weeks, overlapping with Stage 4 corpus collection
4. Stage 4 (research corpus collection): runs in parallel with Stage 3-5 across 6-12 months
5. Stage 5 (prenatal fusion): 6-8 weeks after Stage 3 reaches v0.5
6. Stage 6 (release and submission artifacts): 4-6 weeks after Stage 5 reaches v1.0
7. Stage 7 (red-teaming): 4-8 weeks, blocks all release

Total timeline to FDA submission: 18-24 months if well-staffed, consistent with regulatory_roadmap section 7.

---

## HOW TO DRIVE CLAUDE CODE EFFECTIVELY

For each stage:

1. Paste the CONTEXT BLOCK at the top.
2. Paste the stage prompt verbatim.
3. At the end, add this instruction:

```
Before writing any code, do the following and report back:
a. Confirm you have read all 7 project-knowledge documents.
b. List the three highest-risk design decisions in this stage.
c. For each risk, cite the specific section of project-knowledge that informs your mitigation.
d. Only proceed to code once I reply "PROCEED."
```

Require Claude Code to pause and check in. Do not let it write code without this verification step. This is a regulated medical device; the review discipline matters more than speed.

After each stage:
- Independent review by technical lead, regulatory consultant, clinical advisor.
- Update TRACK_FIREWALL.md with any new information flow decisions.
- Archive the stage's artifacts with a dated git tag.
- Proceed only after sign-off from all three reviewers.

---

## WHAT THIS BUILDS

1. The only smartphone urinalysis system reading hCG + E1-3G + PdG simultaneously, extending the detection window earlier than any OTC product on the market.
2. Reference-free colorimetry via phone-ISP fingerprinting, designing around Healthy.io's foundational color-board patent.
3. A prenatal risk fusion layer with longitudinal tracking across four clinical flag categories.
4. The first controlled, pre-registered, publishable study on whether native urine images contain sub-visual pregnancy signatures.
5. Regulatory-grade documentation ready for a tiered FDA submission strategy (510(k) for hCG, 510(k)-or-De-Novo for fertility monitoring, CDS or SaMD for prenatal fusion).
6. Thirteen red-teamed defensibility reports before any submission.

## WHAT THIS DOES NOT BUILD

- Any Track A claim that pregnancy can be detected from native urine images alone. This remains a Track B research question, not a commercial product.
- An adaptive, self-learning deployed system. Model lock and PCCP govern all updates.
- Wellness framing to dodge regulation. Intended use drives pathway; labeling matches evidence.

## IF TRACK B FINDS A SIGNAL

If the pre-registered Track B analyses identify a statistically robust signal in native urine captures:
1. Independent replication at a second site before any discussion of commercial incorporation.
2. Publication in a peer-reviewed journal.
3. Separate regulatory strategy, likely De Novo, with the full weight of the replicated evidence behind it.
4. No modification of the initial Track A submission; the Track A product ships on its own merits.

## IF TRACK B FINDS NOTHING

That is the expected base case per existing literature. The result is still scientifically valuable:
1. Published as a rigorous negative finding.
2. Protects future patients and investors from pursuing a false lead.
3. Positions the company as the entity that actually did the hard experiment.
4. Track A ships on its own merits, with a defensible commercial moat.

Both outcomes are wins. That is the point of the asymmetric research design.
