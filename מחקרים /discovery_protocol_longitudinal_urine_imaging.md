# Discovery Protocol: Longitudinal Visual Pregnancy Signal Detection from Smartphone Urine Imaging

## Protocol Version 0.2 — Discovery Phase (Pre-Pivotal) — Updated Post-Research
## Date: 2026-04-22
## Revision: Incorporates findings from 14-question research investigation

---

## Executive Summary

This protocol defines a Discovery-phase research study designed to answer one fundamental question:

**Does a sequence of daily smartphone photographs of the same woman's urine, captured under controlled conditions, contain a detectable signal that distinguishes pregnancy from non-pregnancy — and if so, how strong is that signal?**

This is NOT a clinical validation study. It is a hypothesis-generating study designed to:

1. Build the world's first longitudinal urine image dataset with ground truth pregnancy status (serum beta-hCG)
2. Quantify whether any visual signal exists beyond known confounders
3. Determine if temporal (multi-day) analysis outperforms single-image analysis
4. Identify which visual features carry pregnancy-related information
5. Set realistic AUC targets for subsequent pivotal validation

The study is designed to survive scientific peer review and to produce data that directly feeds the pivotal validation protocol documented in `ai_pregnancy_validation_protocol.md`.

---

## 1. Scientific Rationale

### 1.1 What the literature tells us

Based on our research knowledge base:

- **No pregnancy-specific visual signature** has been identified in native urine from a single timepoint [Urine Appearance Atlas, Section 8; Urinary Biochemical Changes, Section 7.1]
- Single-image AUC ceiling is estimated at **0.65-0.72** based on confounders analysis (revised downward after research)
- hCG, estrogens, progesterone metabolites are **colorless** at physiological concentrations [Urinary Biochemical Changes, Section 7.1]
- However, pregnancy induces **measurable physiological changes** that alter urine composition over days and weeks:
  - Proteinuria rises to 200-250 mg/day (from <150 mg/day baseline) — **NOTE: Research finding #4 confirmed this is BELOW visible threshold; not a viable visual signal** [Urinary Biochemical Changes, Section 4.1]
  - Glucosuria: trace in 34%, positive in 16% of pregnant women [Section 4.2]
  - pH shifts toward alkaline due to respiratory alkalosis compensation [Section 4.5]
  - Gestational hypercalciuria promotes crystal supersaturation [Section 4.6]
  - UTI prevalence rises to 2-13% (asymptomatic bacteriuria) [Section 4.7]
  - Dehydration from morning sickness concentrates urine [Section 5.1]
  - Prenatal vitamin use creates fluorescent yellow from riboflavin [Section 6.1]

### 1.2 The untested hypothesis

No study has ever examined whether the **temporal pattern** of these changes — tracked in the same individual over 14-28 consecutive days — produces a signal that AI can detect.

Individual changes are weak and non-specific. But pregnancy is unique in causing **multiple simultaneous, progressive, correlated changes** in the same person:

- ~~Rising proteinuria~~ — **ELIMINATED post-research: 200-250 mg/day is below visual threshold**
- Increasing morning sickness dehydration (peaks weeks 6-9)
- Onset of prenatal vitamin use (bright yellow, often abrupt)
- Rising UTI risk (progressive)
- pH drift (progressive)
- All happening in a characteristic temporal sequence

**Hypothesis:** A temporal model analyzing daily urine images from the same individual can detect pregnancy with AUC significantly higher than single-image analysis, potentially reaching 0.80-0.88 with metadata integration.

### 1.3 NEW: Physical basis for optical signal (Layla et al. 2019)

Post-research finding: Layla et al. (IJMRHS 2019) demonstrated using a Mach-Zehnder interferometer with Photonic Crystal Fiber that:

- Pregnancy urine has a **measurably higher refractive index** than non-pregnant urine
- **Peak absorbance at 590-670nm** — which overlaps with the RGB Red channel (580-700nm)
- Sensitivity range: 2.9-61 ABS/RIU depending on fiber length

This is critical because it means **a physical-optical pregnancy signal exists in urine**. The signal is real and measurable — with laboratory instruments. The open question is whether a smartphone RGB camera with calibration can capture enough of this signal to be useful.

**Implication for our protocol:** We add explicit R-channel ratio analysis (R/(R+G+B)) as a primary feature, specifically targeting the 590-670nm absorbance window.

### 1.4 Why nobody has tested this

Per our market intelligence [smartphone_urinalysis_market_intel.md]:

- Healthy.io, Scanwell, Vivoo — all went directly to strip-based chemistry
- Academic studies used single timepoints
- No longitudinal urine imaging dataset with pregnancy ground truth exists anywhere
- The assumption "no single-image signal = no signal at all" was never challenged with temporal data

---

## 2. Study Design

### 2.1 Design type

Prospective, observational, longitudinal cohort study with two arms:

- **Arm A (Trying to Conceive — TTC):** Women actively trying to get pregnant, enrolled before expected conception
- **Arm B (Control):** Women of reproductive age not trying to get pregnant and using contraception

### 2.2 Why two arms

Arm A provides the critical data: daily images BEFORE, DURING, and AFTER the implantation window, with serum ground truth. The transition from "not pregnant" to "pregnant" within the same person creates the intra-individual delta signal that is the core of our hypothesis.

Arm B provides matched controls with similar daily imaging cadence, to distinguish pregnancy-related temporal changes from normal cycle variation, seasonal effects, and protocol compliance drift.

### 2.3 Study duration per participant

- **Arm A:** Up to 3 menstrual cycles (approximately 84 days / 12 weeks)
  - If pregnancy confirmed: continue daily imaging through week 12 of gestation
  - If no pregnancy after 3 cycles: study completion
- **Arm B:** One menstrual cycle (approximately 28-35 days)

### 2.4 Total study duration

- Enrollment: 6 months
- Follow-up: up to 6 months after last enrollment
- Total: approximately 12 months

---

## 3. Participants

### 3.1 Arm A — Inclusion criteria

1. Female, age 18-42
2. Actively trying to conceive (self-reported, confirmed by investigator)
3. Regular menstrual cycles (21-35 days) for at least 3 recent cycles
4. Not currently using hormonal contraception (discontinued ≥1 cycle ago)
5. Owns a smartphone with camera (iPhone 12+ or equivalent Android with ≥12MP camera)
6. Willing to photograph urine daily for up to 12 weeks
7. Willing to provide blood samples at specified timepoints
8. Able to read and understand study app instructions
9. Provides informed consent

### 3.2 Arm A — Exclusion criteria

1. Known fertility disorders requiring IVF or IUI with exogenous hCG
2. Current use of exogenous hCG (e.g., trigger shots) — this directly confounds ground truth
3. Known kidney disease, chronic proteinuria, or recurrent UTI (>3/year)
4. Conditions affecting urine appearance: melanuria, porphyria, chronic hematuria
5. Inability to comply with daily imaging protocol
6. Planned travel that would prevent blood draw visits

### 3.3 Arm B — Inclusion criteria

1. Female, age 18-42
2. Using reliable contraception (IUD, OCP, implant, or sterilized partner)
3. Not pregnant and not planning pregnancy during study period
4. Owns qualifying smartphone
5. Willing to photograph urine daily for one menstrual cycle
6. Provides informed consent

### 3.4 Arm B — Exclusion criteria

Same as Arm A exclusions 3-6.

### 3.5 Sample size

**Target enrollment:**

| Arm | Enrolled | Expected pregnancies | Rationale |
|-----|----------|---------------------|-----------|
| A (TTC) | 300 | 90-120 (30-40% per cycle × up to 3 cycles) | Need ≥80 pregnancies with complete longitudinal data for powered temporal analysis |
| B (Control) | 150 | 0 | Matched temporal controls for cycle variation |
| **Total** | **450** | **90-120** | |

**Power justification:**

For the primary analysis (AUC comparison: longitudinal vs. single-image), with 100 positive cases and 250 negative time-series:
- Detectable AUC difference of 0.08 (e.g., 0.72 → 0.80) at alpha=0.05 with power >80%
- Sufficient for 5-fold cross-validation with stable estimates
- Adequate for exploratory subgroup analysis (phone type, lighting, BMI)

---

## 4. Data Collection Protocol — "The Perfect Shot"

### 4.1 Capture protocol (daily, every participant)

This is the most critical section. Signal maximization depends entirely on standardization.

#### Step 1: Timing
- **First Morning Urine (FMU)** — mandatory
- Capture within **30 minutes** of voiding
- Record exact time in app (auto-logged)

#### Step 2: Collection vessel
- Study provides **standardized clear polypropylene cups** (120mL, straight-wall, no markings below 30mL line)
- Fill to standardized mark (approximately 60mL)
- All participants receive identical cups (batch-controlled)

#### Step 3: Environment setup
- Place cup on **provided white calibration card** (laminated, 10×10cm, includes:)
  - Pure white reference patch
  - 18% gray reference patch
  - Color checker strip (6 colors: red, green, blue, cyan, magenta, yellow)
  - QR code linking to participant ID and card batch number
  - Ruler markings (mm) for spatial calibration
- Place on flat surface near window (natural daylight preferred)
- **No direct sunlight** hitting the cup
- **No artificial overhead light** directly above (creates specular reflection)

#### Step 4: Image capture — Still photograph
- Open study app
- App guides framing: phone held **horizontal, perpendicular** above cup at **15-20cm**
- App uses phone accelerometer to verify perpendicular angle (±5°)
- App disables flash, locks white balance to daylight (5500K), locks exposure
- App captures **3 images** in rapid succession (bracket: -0.5EV, 0EV, +0.5EV)
- App performs immediate quality check:
  - Calibration card detected? (4 corners)
  - Cup detected?
  - Blur score acceptable?
  - Lighting uniformity acceptable?
- If quality check fails → prompt retry with specific guidance

#### Step 5: Foam capture — DEPRIORITIZED (exploratory only)
**Post-research update:** Research findings #4 and #5 confirmed that proteinuria at pregnancy-physiological levels (200-250 mg/day) does NOT produce visible foam changes, and foam specificity is only 21.4%. Foam capture is retained as exploratory but removed from primary analysis.

- Optional: Gently swirl cup 3 rotations, capture at 5s and 60s
- Data collected but NOT included in primary model training

#### Step 6: Metadata auto-capture (from EXIF + app sensors)
- Timestamp (ms precision)
- Device model, OS version, camera specs
- Accelerometer data (angle verification)
- Ambient light sensor reading
- GPS (for timezone + approximate latitude for daylight estimation) — with consent
- App version

#### Step 7: Daily questionnaire (in-app, <60 seconds)
- How much water did you drink yesterday? (4 options: <1L, 1-2L, 2-3L, >3L)
- Did you take prenatal/multivitamins today? (Y/N/unsure)
- Any nausea or vomiting in last 24h? (none / mild / moderate / severe)
- Any new medications in last 24h? (free text, optional)
- Any unusual foods (beets, berries, asparagus)? (Y/N)
- Did you have a UTI symptom (burning, urgency)? (Y/N)
- Menstrual bleeding today? (none / spotting / light / moderate / heavy)

### 4.2 Why this protocol works

| Protocol element | What it controls | Why it matters per research base |
|---|---|---|
| FMU only | Hydration variation | Urine Atlas: color dominated by hydration; FMU maximizes concentration and minimizes this confounder |
| Standardized cup | Vessel geometry, transmittance | Eliminates colored/frosted cup artifacts; enables consistent turbidity measurement |
| White calibration card | Lighting + white balance + spatial scale | Urine Atlas Section 7: "smartphone colorimetry with calibration card improved agreement"; per Muhaimin et al. |
| Perpendicular angle | Perspective distortion, specular reflection | Consistent optical path through liquid column |
| Exposure bracketing | Dynamic range | Captures subtle transmittance differences that single exposure may clip |
| Foam protocol | Proteinuria signal | Urine Atlas Section 3: persistent fine foam correlates with proteinuria; pregnancy raises proteinuria to 200-250 mg/day |
| Daily questionnaire | Known confounders | Biochemical Changes Section 6: vitamins, hydration, diet, medications are dominant confounders |

### 4.3 Image storage specifications

- **Format:** RAW (DNG) if device supports it; otherwise highest-quality JPEG + HEIF
- **Resolution:** Native sensor resolution (no downscaling at capture)
- **Color space:** sRGB for JPEG; linear for DNG
- **Storage:** Encrypted upload to study server within 24h; local copy retained until confirmed upload
- **Naming:** `{participant_id}_{date}_{time}_{capture_type}_{bracket}.{ext}`
- **Retention:** Minimum 7 years per regulatory expectation

---

## 5. Ground Truth Collection

### 5.1 Blood draw schedule — Arm A (TTC)

Ground truth is the foundation. Per our validation protocol: **quantitative serum beta-hCG is the gold standard**.

**Baseline (Cycle Day 1-3 of first study cycle):**
- Serum beta-hCG (quantitative) — to confirm non-pregnant baseline
- CBC, CMP (for general health baseline)
- Urinalysis with microscopy (lab-grade, for correlation with images)

**Luteal phase monitoring (each cycle, starting Cycle Day 21 or 7 days post-ovulation):**
- Serum beta-hCG every 48 hours × 4 draws (Days 21, 23, 25, 27 approximately)
- This captures the peri-implantation window with high temporal resolution
- If hCG rises: continue every 48h until >1000 mIU/mL, then weekly
- If hCG negative at Day 27: stop for this cycle, resume next cycle

**If pregnancy confirmed:**
- Weekly serum beta-hCG through week 12
- Ultrasound at 6-7 weeks for viability confirmation
- Urinalysis with microscopy at weeks 4, 6, 8, 10, 12

**At each blood draw visit:**
- Collect concurrent urine sample for lab urinalysis (protein, glucose, pH, SG, microscopy, culture)
- Participant also captures study images of the same urine sample in clinic under controlled lighting (provides clinic-captured reference images)

### 5.2 Blood draw schedule — Arm B (Control)

- **Baseline (Cycle Day 1-3):** Serum beta-hCG + urinalysis with microscopy
- **Mid-cycle (Day 14±2):** Serum beta-hCG (confirms non-pregnant)
- **Late luteal (Day 25±2):** Serum beta-hCG + urinalysis with microscopy

### 5.3 Ground truth classification

Each participant-day will be classified as:

| Classification | Definition | Based on |
|---|---|---|
| **Definitively pregnant** | hCG rising with doubling time <72h AND subsequent ultrasound confirmation | Serum + US |
| **Biochemically pregnant** | hCG positive and rising, but ultrasound not yet done or equivocal | Serum only |
| **Chemical pregnancy / early loss** | hCG rose above threshold then declined without viable pregnancy | Serial serum |
| **Peri-implantation** | Within 6-12 days post-ovulation; hCG may be undetectable even if implantation occurred | Temporal window |
| **Definitively not pregnant** | hCG below threshold at all measured timepoints in this cycle | Serum |
| **Indeterminate** | Insufficient blood draws or borderline results | Flagged for exclusion |

### 5.4 Ovulation confirmation

To accurately time the implantation window:
- Participants use **urinary LH test strips** (provided) daily from Cycle Day 10
- LH surge date recorded in app
- Ovulation estimated as LH surge + 1 day
- Implantation window estimated as ovulation + 6-12 days

---

## 6. Feature Extraction Plan

### 6.1 Raw image features (extracted automatically)

**Color features (per calibration-normalized image):**
- Mean, median, std of H, S, V channels in liquid region
- Mean, median, std of L*, a*, b* (CIELAB) in liquid region
- Dominant color cluster (k-means, k=3)
- Color histogram (32 bins per channel)
- Calibration-normalized absolute color (white-balanced using card)
- Spectral ratio estimates: R/G, R/B, G/B (crude spectrophotometry)

**Turbidity features:**
- Transmittance score: contrast of calibration card pattern visible through liquid
- Edge sharpness of cup bottom through liquid
- Scattering estimate: ratio of specular to diffuse reflection on liquid surface
- Tyndall effect proxy: lateral illumination scatter (if flash-off image shows scatter)

**Layla-range spectral proxy features (NEW — based on Layla et al. 2019):**
- R/(R+G+B) ratio — proxy for 590-670nm absorbance
- R/G ratio — pregnancy-related RI change indicator
- R-channel intensity delta from personal baseline
- R-channel variance within 7-day window
- If GoSpectro sub-study: true absorbance at 590, 620, 650, 670nm

**Foam features — EXPLORATORY ONLY (deprioritized post-research):**
- Foam area fraction (percentage of surface covered)
- Mean bubble diameter
- Foam persistence: area fraction at T=5s vs T=60s
- NOT included in primary model; retained for exploratory analysis only

**Sediment features:**
- Particle count in bottom 20% of cup (if visible)
- Particle size distribution
- Particle color classification (pink=urates, white=phosphates, red=hematuria)

**Capture quality features:**
- Blur score (Laplacian variance)
- Lighting uniformity (std of white reference patch)
- Color accuracy (deltaE of calibration patches vs known values)
- Angle deviation from perpendicular

### 6.2 Temporal features (computed over multi-day windows)

This is the core innovation. For each participant, compute rolling features over windows of 3, 7, 14 days:

**Delta features (change from personal baseline):**
- Delta mean hue (today vs. personal Day 1-3 mean)
- Delta saturation
- Delta value (brightness)
- Delta turbidity score
- Delta foam persistence
- Rate of change (slope) of each feature over the window
- Acceleration (change in slope) of each feature

**Trend features:**
- Linear regression slope of each color channel over window
- Variance of daily features within window (stability metric)
- Autocorrelation of daily features (periodicity detection)
- Break-point detection: did a feature shift abruptly? When?

**Pattern features:**
- Similarity of current window to known pregnancy temporal profiles (template matching)
- Cycle-phase alignment: are changes consistent with luteal phase? With post-implantation?
- Consistency score: are multiple features changing in the same direction simultaneously?

### 6.3 Metadata features (from questionnaire + EXIF)

- Hydration level (self-reported, 4-level ordinal)
- Vitamin use (binary)
- Nausea severity (4-level ordinal)
- Menstrual status (5-level ordinal)
- Time since void (minutes)
- Ambient light level (lux, from sensor)
- Device model (categorical)
- Days since LH surge (computed)

---

## 7. Analysis Plan

### 7.1 Primary analysis: Single-image vs. Longitudinal AUC comparison

**Null hypothesis:** AUC(longitudinal model) = AUC(single-image model)
**Alternative hypothesis:** AUC(longitudinal model) > AUC(single-image model)

**Method:**
1. Train single-image CNN on individual images with binary pregnancy label
2. Train longitudinal model (LSTM/Transformer) on 14-day image sequences with binary pregnancy label
3. Compare AUC using DeLong test on held-out test set
4. Use nested cross-validation (outer 5-fold by participant, inner 3-fold for hyperparameters)
5. **Critical:** Split by PARTICIPANT, never by image or day

**Success criterion for proceeding to pivotal:**
- Longitudinal model AUC ≥ 0.82 (lower 95% CI ≥ 0.78)
- AND longitudinal AUC statistically significantly higher than single-image AUC (p < 0.05)

**Decision matrix:**

| Longitudinal AUC | Single-image AUC | Decision |
|---|---|---|
| ≥ 0.85 | Any | Proceed to pivotal validation with longitudinal approach |
| 0.82-0.85 | < 0.75 | Proceed cautiously; longitudinal signal confirmed but modest |
| 0.78-0.82 | < 0.72 | Consider hybrid approach (image + metadata model); additional data collection |
| < 0.78 | Any | Signal insufficient for clinical utility; pivot to strip-reader strategy |

### 7.2 Secondary analyses

**A. Feature importance ranking**
- SHAP values for each feature category (color, turbidity, foam, temporal, metadata)
- Ablation study: which feature groups contribute most to AUC?
- Hypothesis: temporal delta features will outrank static features

**B. Earliest detection window**
- At what day post-implantation does the model first achieve AUC ≥ 0.75?
- Compare with: standard hCG strip detection (typically day 12-14 post-ovulation)
- If model detects LATER than hCG strips → no clinical advantage
- If model detects EARLIER or SIMULTANEOUSLY without chemistry → potential advantage

**C. Confounder isolation — CO-PRIMARY ANALYSIS (elevated post-research)**
This is now co-primary because research finding #6 showed RGB colorimetry works WITH reagents but is unproven for native urine. The risk that "longitudinal AUC" is driven entirely by behavioral metadata (nausea reports, vitamin timing) is real.

- Train THREE models:
  1. **Visual-only:** Images + temporal features, NO questionnaire data
  2. **Metadata-only:** Questionnaire data + cycle timing, NO images
  3. **Combined:** Both
- Compare AUC of all three with DeLong tests
- **Critical gate:** If AUC(visual-only) ≤ AUC(metadata-only) → no visual signal exists
- If AUC(combined) > AUC(metadata-only) but AUC(visual-only) ≈ chance → signal is behavioral not visual

**D. Device robustness**
- Stratify performance by phone model
- If AUC drops >0.05 for any major device class → calibration strategy needed

**E. Subgroup equity**
- Performance by age group, BMI category
- Flag any subgroup with AUC drop >0.05

### 7.3 Anti-leakage controls

Per forensic failures analysis [forensic_failures_medical_ai.md, Section 6]:

1. **Participant-level splitting only** — all images from one participant are in train OR test, never both
2. **Temporal ordering** — no future data leaks into past predictions (causal training)
3. **No test-set tuning** — hyperparameters selected only on validation fold
4. **Duplicate detection** — hash-based deduplication of images
5. **Site-level cross-validation** — if multi-site, leave-one-site-out analysis to test generalization
6. **Confound probing** — explicitly test if model is predicting pregnancy or predicting "took vitamins" / "feels nauseous" → if removing questionnaire collapses performance, the signal is metadata, not visual

### 7.4 Reporting standards

All results reported with:
- Point estimate + 95% CI (bootstrap, 10,000 iterations)
- Calibration plot (reliability diagram, 10 bins)
- Brier score
- Sensitivity at fixed specificity thresholds (90%, 95%, 99%)
- Specificity at fixed sensitivity thresholds (90%, 95%, 99%)
- Full confusion matrix at operating point
- SHAP summary plots for feature importance

---

## 8. Ethical Framework

### 8.1 Core principle

**No participant will ever receive an AI pregnancy prediction.** All pregnancy information comes from serum hCG and clinical follow-up.

### 8.2 IRB submission requirements

- Full protocol
- Informed consent form (must explain: images are for research only; no AI results returned; serum results returned per standard clinical practice)
- Data handling plan (GDPR-aligned even if US-only, for future international use)
- Participant compensation plan
- Adverse event plan

### 8.3 Informed consent highlights

Participants must understand:
1. Images of their urine will be stored, analyzed by AI, and may be used in future research
2. They will NOT receive AI predictions about pregnancy
3. They WILL receive their serum hCG results (which is standard of care)
4. If pregnancy is confirmed, standard prenatal care referral is provided
5. They can withdraw at any time; their data will be de-identified but retained per consent terms
6. Images will be de-identified (no face, no identifying features) but are inherently biological specimens

### 8.4 Incidental findings

If lab urinalysis reveals clinically significant findings (e.g., heavy proteinuria, hematuria, significant bacteriuria):
- Participant is notified by study physician
- Referral to appropriate care
- Finding documented as incidental
- Does NOT affect study participation unless exclusion criteria now met

### 8.5 Data security

- All images encrypted at rest (AES-256) and in transit (TLS 1.3)
- Participant IDs are pseudonymized; mapping file stored separately with restricted access
- No cloud storage in consumer platforms (dedicated research infrastructure)
- Access limited to study team (role-based)
- Data Processing Agreement with any sub-processors
- Annual security audit

---

## 9. App Specifications

### 9.1 Core features

1. **Guided capture mode:** AR overlay showing cup placement, angle feedback, quality check
2. **Daily reminder:** Push notification at user-preferred morning time
3. **Quick questionnaire:** 6 questions, <60 seconds
4. **LH strip logging:** Photograph LH strip + auto-read result
5. **Compliance dashboard:** Calendar view showing captured/missed days
6. **Secure upload:** Background upload with retry logic; end-to-end encryption

### 9.2 What the app does NOT do

- Does NOT display any pregnancy prediction
- Does NOT analyze urine images on-device during the study
- Does NOT provide medical advice
- Does NOT connect to social media or share data

### 9.3 Device compatibility

- iOS 16+ (iPhone 12 and newer — for LiDAR/depth data if available, and consistent camera pipeline)
- Android 12+ with Camera2 API support and ≥12MP main camera
- App controls: manual white balance lock, exposure compensation, RAW capture if available

---

## 10. Timeline and Milestones

| Month | Milestone | Deliverable |
|---|---|---|
| 1-2 | Protocol finalization + IRB submission | Approved protocol |
| 2-3 | App development (MVP for capture + questionnaire) | TestFlight/beta app |
| 3-4 | Calibration card production + cup procurement | Standardized kit |
| 3-4 | Site setup (1-2 fertility clinics + 1 OB/GYN) | Trained staff, signed agreements |
| 4 | Pilot (20 participants, 2 weeks) | Protocol feasibility report |
| 4-5 | Protocol refinement based on pilot | Updated SOP |
| 5-10 | Main enrollment (450 participants) | Rolling data collection |
| 8-12 | Ongoing pregnancy follow-up | Serum + ultrasound data |
| 10-14 | Feature extraction + model training | ML pipeline + initial results |
| 14-15 | Analysis + reporting | Discovery study report |
| 15-16 | Go/No-Go decision | Pivotal study plan OR pivot strategy |

---

## 11. Budget Estimate (Discovery Phase Only)

| Item | Estimated cost | Notes |
|---|---|---|
| App development (MVP) | $50,000-80,000 | iOS + Android, capture + questionnaire |
| Calibration cards (500 units) | $2,000-3,000 | Laminated color-calibrated cards |
| Specimen cups (5,000 units) | $1,000-2,000 | Standardized polypropylene |
| Serum beta-hCG tests (~2,500 tests) | $50,000-75,000 | ~$20-30/test, CLIA lab |
| Lab urinalysis (~800 tests) | $16,000-24,000 | ~$20-30/test |
| LH test strips (4,500 strips) | $5,000-8,000 | ~15 strips/participant/cycle |
| Ultrasound (100 scans) | $15,000-25,000 | For pregnancy confirmation |
| Participant compensation | $90,000-135,000 | $200-300/participant for full compliance |
| Site costs (3 sites × 12 months) | $150,000-250,000 | Staff, space, coordination |
| IRB + regulatory consulting | $20,000-40,000 | |
| Cloud infrastructure + security | $15,000-25,000 | 12 months, encrypted research storage |
| Data science / ML team | $150,000-250,000 | 6-8 months of focused analysis |
| Project management | $50,000-80,000 | |
| **Total estimated range** | **$615,000-$1,000,000** | |

---

## 12. Risk Registry

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Low compliance with daily imaging | Incomplete longitudinal data | Medium | App reminders, compensation tied to compliance, weekly check-ins |
| No detectable visual signal | Study produces negative result | Medium-High | This is a valid scientific outcome; protocol designed to be informative either way |
| Confounders dominate signal | AUC driven by vitamins/nausea, not visual | Medium | Explicit confounder ablation analysis; visual-only model tested separately |
| Insufficient pregnancies | <80 pregnancies in dataset | Low-Medium | 300 TTC women × 3 cycles × 30% per-cycle rate = ~90-120 expected; can extend enrollment |
| Phone model variability | Performance varies by device | Medium | Calibration card normalizes; include device as feature; stratified analysis |
| Participant drops out during pregnancy | Missing critical pregnancy-phase data | Low | Compensation increases during pregnancy; weekly touchpoints |
| Data breach | Privacy violation, regulatory consequences | Low | Encryption, pseudonymization, security audit, incident response plan |
| IRB delays | Timeline extension | Medium | Early pre-submission consultation; experienced regulatory consultant |

---

## 13. Go/No-Go Decision Framework

At the end of the Discovery study, the following decision framework applies:

### GO — Proceed to Pivotal Validation
**ALL of the following must be true:**
- Longitudinal visual-ONLY model AUC ≥ 0.80 (lower 95% CI ≥ 0.75) — revised post-research
- Visual features (without questionnaire metadata) contribute ≥ 0.05 AUC above metadata-only model
- R-channel ratio features show statistically significant pregnancy correlation (p < 0.01)
- No single subgroup (age, BMI, device) shows AUC drop > 0.08
- At least 80 pregnancies in dataset with complete longitudinal coverage

### CONDITIONAL GO — Proceed with Hybrid Strategy
**If longitudinal combined (visual + metadata) AUC is 0.75-0.80 OR visual-only contribution < 0.05:**
- Add lightweight chemistry: pH strip + protein strip as minimal chemical enhancement
- Design Phase 1.5 study with hybrid (image + minimal strip) approach
- Explore GoSpectro add-on for enhanced spectral capture in subset
- Do NOT proceed directly to visual-only pivotal

### NO-GO — Pivot to Strip Reader
**If longitudinal AUC < 0.75 even with metadata OR visual features contribute < 0.02 AUC above chance:**
- Publish negative results (scientific integrity clause — mandatory)
- Pivot to Strategy B: AI-enhanced strip reader for existing hCG tests
- Retain longitudinal dataset as research asset (still world's first)
- Dataset supports future strip-reader + longitudinal monitoring product

### Post-Research Probability Assessment
- **GO probability: ~30%** — Signal exists with useful AUC
- **CONDITIONAL probability: ~25%** — Modest signal, needs hybrid approach
- **NO-GO probability: ~45%** — Insufficient visual signal for clinical utility
- **Even NO-GO produces:** First-ever dataset, published science, credibility, pivot-ready strategy

---

## 14. GoSpectro Spectral Sub-Study (NEW — Post-Research Addition)

### 14.1 Rationale

Layla et al. (2019) demonstrated pregnancy-related absorbance changes at 590-670nm using laser biosensor. The critical question is: **can a smartphone camera capture this signal, or do we need true spectrophotometry?**

### 14.2 Design

- **Participants:** 50 from Arm A (TTC), selected to include early pregnancies
- **Equipment:** GoSpectro smartphone spectrometer accessory (~$200/unit)
  - Range: 400-750nm
  - Resolution: ~10nm
  - Reproducibility: 1nm
- **Protocol:** At each home capture session, participant also captures GoSpectro spectrum of same urine sample
- **Duration:** Full study duration for these 50 participants

### 14.3 Analysis

1. Compare true spectrum (GoSpectro) vs RGB-derived pseudo-spectrum for each sample
2. Quantify: does pregnancy shift the 590-670nm absorbance measurably via GoSpectro?
3. If yes: can RGB R-channel ratio approximate this measurement?
4. Correlation between GoSpectro pregnancy signal and RGB features

### 14.4 Decision impact

- If GoSpectro detects pregnancy signal AND RGB approximates it → GO with RGB-only product
- If GoSpectro detects pregnancy signal BUT RGB cannot → product needs spectral accessory (different business model)
- If GoSpectro does NOT detect pregnancy signal → Layla et al. findings don't replicate in consumer conditions

### 14.5 Additional cost

| Item | Cost |
|------|------|
| GoSpectro units (50) | $10,000 |
| Additional training/support | $3,000 |
| Spectral analysis pipeline | Included in data science budget |
| **Total** | **~$13,000** |

---

## 15. What This Protocol Does NOT Cover

This Discovery protocol intentionally excludes:
1. Clinical claims or intended use statements
2. Regulatory submission planning (covered in `regulatory_roadmap_pregnancy_ai.md`)
3. Pivotal validation design (covered in `ai_pregnancy_validation_protocol.md`)
4. Commercial product design
5. Marketing or positioning

The sole purpose is to **answer the scientific question** before committing resources to clinical validation.

---

## 15. Alignment with Existing Research Base

| Knowledge base document | How this protocol aligns |
|---|---|
| Engineering Anatomy of HPTs | Protocol uses serum hCG (not strips) as ground truth, avoiding strip limitations documented in this paper |
| Urinary Biochemical Changes | All physiological changes documented here are targeted by our feature extraction plan (proteinuria → foam, glucosuria → SG, pH shifts, crystalluria → turbidity) |
| Validation Protocol | Discovery feeds directly into pivotal; sample size, participant criteria, and ground truth methods are consistent; Discovery data informs power calculations for pivotal |
| Forensic Failures | Anti-leakage controls, participant-level splitting, confounder probing, and Go/No-Go decision matrix directly address Theranos/Watson/Babylon failure patterns |
| Regulatory Roadmap | Discovery is designed as a pre-regulatory research study; no diagnostic claims; data structured to support future De Novo submission if warranted |
| Market Intelligence | Protocol fills the specific whitespace identified: no longitudinal urine imaging dataset exists; this will be the first |
| Urine Appearance Atlas | Capture protocol designed around Atlas findings: calibration card (Section 7), controlled timing (Section 6), foam analysis (Section 3), color normalization (Section 1) |

---

## Appendix A: Calibration Card Specifications

```
+-----------------------------------------------+
|                                                 |
|  [White patch]  [18% Gray]  [Black patch]       |
|                                                 |
|  [Red] [Green] [Blue] [Cyan] [Magenta] [Yellow] |
|                                                 |
|  |----|----|----|----|----|  (mm ruler)          |
|  0    10   20   30   40   50                    |
|                                                 |
|  [QR Code: participant_id + card_batch]         |
|                                                 |
+-----------------------------------------------+
```

- Material: Laminated card stock with UV-stable inks
- Color patches: Pantone-matched, verified by spectrophotometer
- Size: 100mm × 100mm
- Tolerance: deltaE < 2 from reference for each patch
- Shelf life: 12 months (replace if faded)
- Production: Professional print house with color management

## Appendix B: Daily App Workflow (User Experience)

```
1. Wake up notification: "Good morning! Time for your daily capture"
2. Open app → "Prepare your sample" (instructions with illustrations)
3. Place cup on card → app shows camera preview with AR guide
4. App checks angle (green = good, red = tilt detected)
5. App auto-captures 3 bracketed images → quality check
6. If quality OK → "Great! Now the foam test" (if applicable day)
7. Swirl, wait, capture, wait 60s, capture again
8. Quick questionnaire (6 taps)
9. "All done! See you tomorrow" → upload in background
10. Total time: 3-5 minutes
```

## Appendix C: Statistical Code Repository Structure

```
/analysis/
├── 01_data_ingestion/
│   ├── image_loader.py
│   ├── metadata_parser.py
│   └── ground_truth_linker.py
├── 02_feature_extraction/
│   ├── color_features.py
│   ├── turbidity_features.py
│   ├── foam_features.py
│   ├── temporal_features.py
│   └── calibration_normalizer.py
├── 03_modeling/
│   ├── single_image_cnn.py
│   ├── longitudinal_transformer.py
│   ├── metadata_fusion.py
│   └── cross_validation.py
├── 04_evaluation/
│   ├── auc_comparison.py
│   ├── calibration_analysis.py
│   ├── subgroup_analysis.py
│   ├── confounder_ablation.py
│   └── shap_analysis.py
├── 05_reporting/
│   ├── figures.py
│   ├── tables.py
│   └── go_nogo_decision.py
└── config/
    ├── feature_config.yaml
    ├── model_config.yaml
    └── study_config.yaml
```

---

**Document status:** Draft v0.1
**Next review:** Upon team feedback
**Owner:** Research Lead
**Classification:** Confidential — Internal Research Use Only
