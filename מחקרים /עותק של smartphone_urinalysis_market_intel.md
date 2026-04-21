# Smartphone-Based Urinalysis: Market, Technical & IP Landscape

A synthesized market, technical, and IP landscape for smartphone-based urinalysis, with a specific lens on what has and has not worked, and how close anyone has come to smartphone-based pregnancy detection.

---

## 1. Commercial Products and Companies

### 1.1 Summary Table: Major Smartphone-Urinalysis Players

| Company / Product | Founded / HQ | Funding (approx) | Core use-case | Regulatory status (US/EU) | Current status (2026) | High-level outcome |
|---|---|---|---|---|---|---|
| **Healthy.io (Dip.io, Minuteful Kidney)** | 2013, Tel Aviv | ≥$90M raised (Series D 2025; prior C/B) [1][2][3] | Home urinalysis (10-parameter dipstick), CKD albumin-creatinine ratio (ACR) | Dip.io: FDA 510(k) Class II; CE-marked. Minuteful Kidney: 510(k) for home ACR on iOS/Android [4][5][6][7] | Active; focusing on US CKD screening; significant UK/IL layoffs in 2025 as they pivot to US commercialization [2] | Technically and regulatorily the clear category leader; proven clinical deployments and reimbursement pilots, but scale-up economically and operationally non-trivial. |
| **Scanadu / Inui Health (urine platform)** | 2011, Mountain View (renamed Inui ~2018) [8][9] | ≈$56M total funding [10] | Home urinalysis paddle + smartphone app (protein, glucose, leukocytes, nitrite, ketones) [11][9] | FDA 510(k) for smartphone-enabled urine platform (multi-analyte) [11][9] | Acquired by Healthy.io in 2025 for ≈$9M cash + milestones [10] | Demonstrated technical and regulatory success for multi-analyte home urinalysis; business outcome modest, with IP & know-how folded into Healthy.io. |
| **Scanwell Health (UTI test)** | ~2018, Los Angeles | Seed $3.5M+ [12][13] | OTC UTI testing: smartphone reads leukocyte/nitrite pads, links to telehealth [13][12] | First OTC diagnostic smartphone app with FDA 510(k) for urinalysis; UTI strip + app [13] | Active as of 2020; UTI test sold via Amazon/online; later partnered with Lemonaid Health telemedicine [13][12] | Technically validated equivalence to clinic analyzers; positioned as narrow UTI service rather than general urinalysis; strong example of successful niche. |
| **TestCard (UK)** | 2017, Scarborough UK [14][15] | ≥£1.25M seed + £1.6M follow-on; total ≈$15M [14][16][17][15] | "Postcard" urine tests (UTI, pregnancy, glucose, drugs) read by smartphone app [14][16][17] | CE-marked for UTI; serving European markets; limited public FDA activity as of 2024 [17] | Active; expanding across Europe; 2020 funding to build out pipeline [17] | Technically sound smartphone strip-reader; commercial traction modest; pregnancy and fertility messaging mainly marketing; clinical validation publications limited. |
| **uChek (Biosense, India)** | ~2012, Mumbai [18][19][20] | Small private; no large venture rounds reported | App to read Siemens/Bayer urine dipsticks via iPhone camera for multiple analytes (glucose, protein, blood, pH, etc.) [18][19][21] | Received FDA "It has come to our attention" letter in 2013; no 510(k) for full system [18][19][22] | App remained in India/other markets; US ambitions effectively stopped by FDA scrutiny [18][19] | Textbook regulatory failure: using cleared strips with an un-cleared automated reader triggered FDA; forced to treat phone+strip as a device requiring 510(k). |
| **Vivoo (US/Turkey)** | ~2018, SF + Istanbul [23][24] | Undisclosed; VC-backed wellness startup | Subscription wellness urinalysis (hydration, pH, ketones, etc.) via smartphone strip imaging [23][24] | Positioned as wellness; no FDA diagnostic claims. Validation study vs. lab (2618 strips) showed 87.6-99.6% matching within ±1 color block [24] | Active; marketed as nutrition/hydration/wellness app [23][24] | Demonstrates technically high strip-reading accuracy, but deliberately avoids diagnostic/regulatory complexity. |
| **Yocheck (Korea)** | 2020s, Sejong, South Korea [25] | Not disclosed | "11 Urine Test Smart App": analyzes urine test strip results, tracks history, marketed as health/fitness [25] | No US FDA; likely domestic/regional regulatory positioning as wellness app | Active on Google Play as of 2026 [25] | Example of Asian wellness-oriented urinalysis app; unclear clinical validation. |
| **VivoSens (Turkey)** | 2018+, Turkey/US [26][27][28] | Not public | Smartphone urinalysis with reference chart and AI recommendations; strong patent portfolio [26][27][28] | Focus appears on CE/wellness; no explicit FDA clearance seen | Active as of 2022 patents; commercial footprint limited in English-language press | Significant patent activity around strip imaging + personalized recommendations; less evidence of scaled clinical deployments. |
| **Siemens Healthineers (CLINITEK, partnership)** | Siemens legacy | N/A (large medtech) | CLINITEK Status/Status+ analyzers (benchtop), plus 2018 partnership with Healthy.io for home smartphone urinalysis using Siemens strips [29][30][31] | CLINITEK analyzers long-approved; partnership products rely on Healthy.io's 510(k) clearances [31] | Ongoing; Siemens uses Healthy.io as smartphone front-end in some programs [31] | Strategy is partnership rather than in-house smartphone imaging; underscores that legacy IVD majors view camera-based readout as niche / partnerable competency. |

Below are more detailed "card-style" profiles for the key names.

---

### 1.2 Healthy.io (Dip.io, Minuteful Kidney)

**Founding, funding, leadership**

- Founded 2013 by Yonatan Adiri (former Israeli President's chief tech officer). HQ in Tel Aviv with offices in London and Boston. [3]
- Funding: Series B $18M (2019) → total $33M; Series C $60M (2019) → total ≈$90M by 2019; additional $95M Series D-related raises by 2025 for a total well north of $140M. [1][2][32][3]
- 2025: raised $50M (plus undisclosed $45M earlier), while simultaneously laying off ~70 employees (~1/3 staff) in UK/Israel to focus on U.S. CKD commercialization. [2]

**Technical approach**

- Core product Dip.io: kit includes cup, multi-parameter dipstick, and a printed color calibration board. [4][33][34]
- User workflow: urinate in cup, dip strip, place on color board, then scan with app; app uses computer vision + color calibration to map pad colors into lab-equivalent analyte values. [7][34][35]
- Underlying IP: patented calibration arrays and algorithms enabling accurate colorimetry under uncontrolled lighting and heterogeneous phone cameras (e.g., US9972077B2, US20210241456A1). [36][37]
- Analytes: up to 10 parameters for general urinalysis (glucose, protein, blood, pH, specific gravity, ketone, nitrite, leukocytes, bilirubin, urobilinogen). [5][34]

**Products & indications**

- **Dip.io**: home urinalysis kit, initially prescription-use (CKD risk, UTI, pregnancy-related complications) with results delivered to clinician; marketed for CKD detection, UTI, and prenatal urinalysis support. [34][38][4][5]
- **Minuteful Kidney**: home ACR (albumin-creatinine ratio) test for CKD risk in diabetic/hypertensive patients, using Siemens or Bayer ACR strips plus smartphone board and app. [6][39][1][2]

**Clinical validation**

- CKD/ACR: London inner-city diabetes population quality-improvement project; 2,370 patients consented, 1,244 completed home ACR tests (61% uptake), 37% with albuminuria; 98% found the home test "easy or very easy". [40]
- Prenatal care: Johns Hopkins AJOG pilot: 179 pregnant women, 87% attempted Dip.io test, 96% of completers found it easy; most preferred at-home testing vs clinic urinalysis. [38]
- Glomerular disease remote monitoring during COVID-19: UK nephrology center provided smartphone-based Dip.io kits; 25 patients, 95% gave feedback, 100% rated app "easy/very easy"; allowed remote proteinuria monitoring. [41]

**Regulatory status**

- 2018: FDA 510(k) Class II for Dip.io as a home-based urinalysis kit (qualitative/semi-quantitative detection of glucose, specific gravity, blood, pH, protein, nitrite, leukocytes). [4][5][7][34]
- 2019: second 510(k) clearance for smartphone-based ACR testing (Minuteful Kidney) in clinical settings. [32][1]
- 2022: Minuteful Kidney 510(k) expanded to home use; first "smartphone-powered home kidney test" cleared across all current iOS and Android devices. [6]
- CE-marked and ISO 13485-certified for EU markets; used in NHS pilots. [35][3]

**Commercial outcome / where succeeded or struggled**

- Successes:
  - Demonstrated clinical-grade performance, improved testing uptake, strong usability across diverse populations. [38][40][41]
  - Secured multiple large payor/NHS pilots and deep partnership with Siemens Healthineers for integrating Siemens strips into home kits. [31][33][34]
- Challenges:
  - Despite "first-in-class" status, heavy regulatory and commercialization costs; 2025 layoffs and strategic refocus on US CKD highlight the difficulty of scaling remote urinalysis to sustainable revenue. [2]

---

### 1.3 Scanadu, Scanadu Urine / Scanaflo → Inui Health

**Company history and funding**

- Scanadu founded 2011 in Mountain View, CA; known for Scanadu Scout, a tricorder-like vitals device launched via Indiegogo and X-Prize. [8][42]
- Total financing about $56M before pivot/acquisition. [10]

**Urinalysis products**

- **Scanaflo** (prototype): multi-analyte urine paddle + smartphone app (iPhone) that could detect pregnancy, diabetes markers, kidney function, UTI, drugs, etc., by imaging up to 12 reagents (glucose, protein, leukocyte, nitrite, blood, bilirubin, urobilinogen, microalbumin, creatinine, ketone, specific gravity, pH). [42]
- Later commercialized as **Inui Health home urine platform**: single-use cup + paddle, smartphone app does colorimetric analysis. [9][11]
- Analytes in cleared product: protein, glucose, leukocytes, nitrite, ketones. [11][9]

**Regulatory & validation**

- Scanadu Scout failed to obtain timely FDA clearance; device shipped as investigational, then support was discontinued at end of study, causing PR backlash. [8][9]
- Rebranded as **Inui Health**; 2018: received FDA clearance for smartphone-enabled urine testing platform (five tests, across multiple smartphones). [9][11]
- Emphasized equivalence to lab urinalysis analyzers and ability for patients to self-view results instantaneously; specifics of performance metrics were not all published in peer-reviewed form but underlying 510(k) required method comparison and accuracy data. [11]

**Outcome**

- Despite being technically advanced and FDA-cleared, Inui did not achieve large independent commercial scale; 2025: acquired by Healthy.io for ≈$9M cash plus milestones. [10]
- Likely failure drivers: very high regulatory and support costs for hardware plus app; crowded landscape; need for strong enterprise distribution; limited brand trust following Scout episode. [43][10]

---

### 1.4 Scanwell Health (UTI smartphone urinalysis)

**Company & funding**

- U.S. startup (Los Angeles), Y Combinator-backed; seed round $3.5M in 2019 for smartphone-enabled UTI testing and telehealth service. [12]

**Technical approach**

- At-home UTI kit: standard leukocyte/nitrite urine test strip plus smartphone app. [13][12]
- App replicates performance of clinic analyzers using phone camera and CV algorithms; validated to match lab urinalysis for UTI screening. [13]

**Regulatory & validation**

- First and only company to receive **FDA 510(k) clearance for an over-the-counter diagnostic smartphone application** for urinalysis (UTI). [13]
- Clearance based on demonstrating **same diagnostic accuracy as a clinic urinalysis** for leukocyte and nitrite pads. [13]

**Commercial outcome**

- Product available OTC via Scanwell's site and later Amazon; US-wide telehealth integration via Lemonaid Health. [12][13]
- Example of a focused, narrow-indication smartphone urinalysis achieving both regulatory clearance and commercial use, but limited to UTI rather than broad or pregnancy-specific claims.

---

### 1.5 TestCard (Avantari/TestCard)

**Company & funding**

- Founded 2017, UK-based (Scarborough) with earlier tech development in Bulgaria. [14][17]
- Funding: £1.25M seed round (2018) + £1.6M follow-on (2019); later £4.5M round (2020); aggregated estimates ≈$15M+. [15][16][17]

**Technical approach**

- "Postcard" format test card with embedded urine test strips (UTI, pregnancy, glucose, drug tests).
- User peels off relevant strip, dips in urine, scans QR code so app knows which test type, then app uses smartphone camera and CV to read colors; results presented instantly and can be shared with clinicians. [16][17][14]

**Regulatory & indications**

- CE-marked in EU for UTI and possibly other analytes (UTI kit widely marketed). [17]
- Claims for at-home pregnancy testing and estimated due date appear in press releases/marketing, but no public evidence of specific pregnancy-test 510(k) in the US; pregnancy component relies on standard hCG strips read by smartphone, not novel chemistry. [16]

**Commercial outcome**

- Active, with NHS pilots and retail distribution for UTI testing; still relatively small player vs. Healthy.io. [17]
- No major academic clinical validation publications beyond internal/marketing material identified; emphasis is more on user convenience and connectivity than fundamentally new diagnostic capabilities. [14][17]

---

### 1.6 Siemens Healthineers CLINITEK + smartphone collaboration

**CLINITEK products**

- CLINITEK Status and Status+ analyzers are benchtop urinalysis analyzers for point-of-care use, performing automated timing and reading of Siemens test strips. [30]
- CLINITEK Status Connect adds wired/wireless connectivity to LIS/EHR, QC lockouts, operator management, etc. [29][44][45]

**Smartphone dimension**

- Siemens itself does not offer a direct "smartphone urinalysis app" for consumers; instead, it partnered with Healthy.io in 2018. [33][31]
- Partnership: Siemens supplies urinalysis strips; Healthy.io supplies smartphone-based imaging and cloud analytics; results are delivered into medical records. [31][34]

**Implication**

- Big IVD players treat smartphone imaging as an **adjacent layer** rather than core competency; they prefer to work via partnerships rather than building their own regulated camera-based readers.

---

### 1.7 Asian & other entrants

**uChek (Biosense Technologies, India)**

- Semi-automated urinalysis app that uses iPhone camera to read standard Siemens/Bayer strips; analytes include glucose, pH, blood, protein, etc., for conditions including pregnancy, UTI, diabetes. [18][19][21]
- 2013: FDA letter (public "It Has Come to Our Attention") requiring 510(k) clearance for the combined system; strips were cleared only for visual reading, not automated analysis. [19][20][22][18]
- As a result, uChek did not pursue US clearance; remained largely in Indian and perhaps other non-US markets, effectively becoming an example of **regulatory overreach risk** if you treat smartphone analysis as "just software". [22][18][19]

**Yocheck (Korea)**

- Korean app "Yocheck - HealthCare" analyzes urine test strip results (11 urine tests) and stores/plots history; marketed as health/fitness, explicitly stating it "does not provide health functions" (i.e., avoids diagnostic claims). [25]
- Appears on Google Play, updated in 2026; no English-language regulatory filings found. [25]

**Vivoo (US/Turkey)**

- Wellness-focused: hydration, nutrition, UTI risk, liver/kidney function proxies using smartphone-read strips. [23]
- 2024 validation study (2618 strips) showed exact-match agreement ~87.6-99.6% depending on analyte, and ~99.6% within ±1 color block, sufficient for wellness, but not pitched as regulated diagnostic. [24]

**Scanostics UTI C (K170118)**

- 510(k) for a UTI urinalysis system (Scanostics UTI C) that uses a smartphone-type optical reader plus dedicated test strips; label indicates same chemical formulation as predicate analyzer strips; essentially CLIA-waived UTI chemistry with a new reader form factor. [46]

**Israeli medtech beyond Healthy.io**

- No other Israeli company appears to have a substantial smartphone-urinalysis product comparable to Healthy.io; other Israeli digital diagnostics players (e.g., TytoCare, EKO, etc.) focus on auscultation/tele-exam, not urinalysis.
- Healthy.io's patent portfolio (dipstick imaging and illumination compensation) plus its acquisition of Inui consolidates most Israel-linked IP around smartphone urinalysis. [37][3][36][4][10]

---

### 1.8 Owlet Baby: urinalysis?

- Owlet is focused on baby monitoring (pulse oximetry "Smart Sock" and camera) with FDA-cleared home pulse-ox system. [47][48]
- There is **no evidence** of a commercial Owlet urinalysis product; occasional media speculation about "smart diapers" and at-toilet sensors exists in the broader industry, but not as an Owlet product line.
- For completeness: other in-toilet urinalysis systems have been patented (e.g., Hall Labs' in-toilet capillary urinalysis system, US11224370B2) but not commercialized with smartphone-only readout. [49][50]

---

## 2. Academic Research on Smartphone Urinalysis

### 2.1 Key technical directions

Broad themes in the literature (2013-2025):

- **Colorimetric dipstick reading:** using smartphone cameras to read standard urinalysis strips with color calibration and CV. [51][52][53]
- **Prenatal / prenatal-care-oriented urinalysis:** smartphone-based strip analysis specifically for prenatal care (protein, glucose, etc.), not hCG. [54][55]
- **CKD and ACR:** smartphone-based albumin-creatinine ratio (ACR) measurement and remote CKD management. [56][40]
- **Wellness and nutrition:** hydration, pH, ketones; often marketed as wellness and not medical devices (e.g., Vivoo). [23][24]
- **AI/deep learning for strip interpretation:** region-based CNNs to detect strip location and orientation and to classify pad colors under varied lighting. [52][57][58][51]

### 2.2 Selected publications and groups

**Table: Representative academic work**

| Year | Group / Institution | Focus & approach | Sample / setting | Performance | Notes |
|---|---|---|---|---|---|
| 2017 | Ra et al., Hanyang Univ., Korea, IEEE J Transl Eng Health Med | "Smartphone-Based Point-of-Care Urinalysis Under Variable Illumination": algorithm to normalize lighting and read strip colors via phone [53] | Laboratory + controlled imaging | Demonstrated robust color correction and interpretation across lighting conditions; detailed accuracy per analyte not given for hCG, focused on standard analytes [53] | Early foundational work showing feasibility of calibrated smartphone strip reading. |
| 2018 | Shaymaa (Flinders Univ., PhD thesis) | Smartphone-based urinalysis for CKD monitoring: design of device + app to measure CKD-relevant analytes [56] | Prototype stages; limited clinical sample | Reported proof-of-concept accuracy vs lab analyzers for creatinine/albumin in pilot studies [56] | More engineering thesis than deployed product; informs design choices for ACR systems. |
| 2019 | Healthy.io + Johns Hopkins AJOG pilot | Feasibility/acceptability of Dip.io among pregnant women in prenatal care [38] | 179 pregnant women, 2 clinics; 87% attempted test, 96% of completers found it easy; high preference for home testing [38] | Feasibility/UX outcome; analytic accuracy vs lab not the main endpoint (had been established in 510(k)). |
| 2021 | UK nephrology center, glomerular disease, Clin Kidney J | Remote digital urinalysis for 25 glomerular disease patients using Dip.io during COVID-19; single-center experience [41] | 25 patients; repeated home tests | 95% provided feedback; all rated app "easy/very easy"; allowed remote proteinuria monitoring; lab concordance reported as acceptable for clinical decisions [41] | Focus on service delivery and patient experience rather than algorithmic innovation. |
| 2022 | Hoffmann et al., FAU Erlangen-Nürnberg, IEEE J Transl Eng Health Med | "Smartphone-Based Colorimetric Analysis of Urine Test Strips for At-Home Prenatal Care": automated pipeline with a region-based CNN, reference card detection and color matching [54][52][51] | Lab + user studies: 26 participants (150 images) + lab images (135) [52][55] | Strip detection/orientation accuracy 85.5%; reference card detection 98.6%; per-pad color classification F1-scores up to 0.81 (Hue metric) [52][54] | Strong evidence that fully automated smartphone strip reading is feasible for prenatal urinalysis; no hCG-specific chemistry (focus on standard urine analytes). |
| 2024 | Caf et al., Vivoo validation, Int J Life Sci & Biotech | Validation of Vivoo smartphone urinalysis app vs expected color block results in artificial urine [24] | 2,618 strip measurements | Exact match 87.6-99.6% depending on analyte; within ±1 block 99.6% [24] | Validates wellness-grade smartphone colorimetry; not diagnostic claims. |
| 2024 | Korean AI urinalysis strip interpreter, J Lab Med (AI in Diagnostics) | AI system to interpret urine test strips via smartphone cameras; targeted to automated analysis in clinics [57][58] | Clinical image sets | Reported high accuracy (near-perfect qualitative interpretation for most analytes); details vary by parameter [58] | Shows mainstream adoption of AI to remove operator subjectivity. |

**Review papers and broader context**

- 2017-2022: multiple reviews on smartphone point-of-care testing (POCT) highlight urine dipstick imaging as one of the more mature image-based diagnostics, but still emphasize the need for calibration targets and controlled workflows. [53][59][56]
- 2021-2024: reviews on AI in urinalysis (especially in Korean and European lab medicine journals) describe AI-based interpretation of dipsticks as promising, but not yet a complete replacement for dedicated analyzers in regulated lab environments. [57][58]

**Replicability / external validation**

- Healthy.io's approach has multiple independent clinical implementations (CKD, prenatal, glomerular disease) across different health systems, giving relatively strong external validation. [40][41][38]
- Academic CS papers (e.g., FAU's prenatal pipeline) have not yet been widely replicated across independent groups, but methods (CNN detection + calibrated color matching) are consistent with industry practice and have been conceptually adopted in other prototypes. [60][52][53]
- Wellness apps like Vivoo now have peer-reviewed equivalence vs "expected colors" in artificial samples; however, these are not clinical endpoint trials against patient outcomes. [24]

---

## 3. Patent Landscape: Smartphone Urinalysis and Pregnancy

### 3.1 Core smartphone-urinalysis patent families

**Table: Representative patent families**

| Publication / Fam. | Assignee | Focus | Status |
|---|---|---|---|
| **US9972077B2 / WO2015173801**: "Method and system for automated visual analysis of a dipstick using standard user equipment" | Healthy.io Ltd. | Core method of placing dipstick on specially designed calibration array and using smartphone camera to derive illumination parameters and map pad colors to calibrated values; addresses uncontrolled lighting and device heterogeneity. [36] | Granted (US, EP); foundational to Dip.io and Minuteful Kidney. |
| **US20210241456A1 / US10991096B2**: "Utilizing personal communications devices for medical testing" | Healthy.io Ltd. | Generalized method for analyzing visible chemical reactions on a reagent pad using colored reference elements; regulates for smartphone variation and ambient light. [37] | Granted in US, continuation family active. |
| **US20180049723A1 / WO2016154262A1**: "Smartphone Enabled Urinalysis Device, Software, and Test Platform" | Wellmetrix LLC | Device body holding test strip with physical port to smartphone; multiple analytes (inflammation, oxidative stress); urinalysis test strip plus smartphone connection. [61][62] | Applications and grants across US, EP, CA, etc.; more hardware-centric smartphone urinalysis platform. |
| **WO2019221676A1 / US20210208081A1 / US20220405973A1**: "Analysis of urine test strips with mobile camera and providing recommendation" | Vivosens Bioteknoloji & Vivosens Inc. | Smartphone urinalysis based on recognizing strip and reaction areas, reference chart mapping, and generating personalized recommendations from a "recommendation pool". [26][27][28] | Mixed grant/pending; strong focus on image processing plus personalized health advice. |
| **US20250205699A1**: "Smartphone-Compatible Urine Test Strip with Integrated Calibration and Enhanced Biomarker Analysis" | Vivosens authors | Next-gen strip design with QR code, calibration bars, protective overlay, optimized for smartphone scanning and batch-specific calibration. [63] | Application filed 2025; at-home multi-biomarker system explicitly designed for smartphone integration. |
| **US11224370B2 / WO2018140524A1**: "In-toilet urinalysis system with capillary dispenser" | Hall Labs LLC / Guardian Health | In-toilet system with capillary and test strip dispenser; some embodiments include optical sensors for automated analysis, potentially smartphone-linked. [49][50] | Granted US patent; no widely known commercial product. |
| **US20230146924A1 / WO2022010997A1**: "Neural network analysis of LFA test strips" | Gauss Surgical / Exa Health | End-to-end neural networks for analyzing LFA strip images across varying lighting, angles, BRDFs; directly mentions pregnancy tests as one LFA use case. [64][65] | Applications active; targets general LFA imaging, not just urine. |
| **WO2023034441A1**: "Imaging test strips" | (Likely Gauss/Exa or similar) | Neural network calibration of analyte strength vs smartphone identifier and image; uses scan cards with color and radiometric calibration guides. [66] | PCT application; aims at cross-phone generalization for many strip types. |

### 3.2 Pregnancy-related smartphone/testing patents

- **WO2018075554A1: "Pregnancy test to assess disease risk"**
  - Multi-strip pregnancy test device with alignment target; smartphone app aligns camera, captures image, computes pixel intensity/color of multiple test lines and uses them to estimate pregnancy plus additional disease risks (e.g., certain birth defects). [67]
  - Includes explicit claims where at least one strip has antibodies for hCG and smartphone processing of test-line intensity gives qualitative/quantitative hCG result. [67]
  - Represents a clear **pregnancy LFA + smartphone imaging** architecture, but still depends on conventional hCG chemistry; does not claim pregnancy detection from native urine color alone.

- **EP3904878A1 / US20220146509A1: multi-test-line pregnancy strip**
  - PROTIA/Proteometech: hCG strip with two test lines (anti-hCG monoclonal and immobilized hCG) to counter false negatives from hCG variants (e.g., β-core fragment); analyzable by naked eye or sensor. [68][69]
  - While not smartphone-specific, aligns with direction of more complex pregnancy strips that smartphone CV could interpret (multiple lines, semi-quantitative).

- **US20170023542A1: "Smartphone dock and diagnostic-test reader"**
  - Generic test-strip dock that positions a smartphone camera and light source against a test card; smartphone software interprets strip images and displays diagnosis; includes pregnancy tests as an example. [70]

- **US20150010441A1: "Electronic pregnancy test device"**
  - Not smartphone-based; it's a handheld electronic reader for blood hCG test strips with on-board CPU and display; relevant as an example of non-smartphone digital pregnancy testing. [71]

Overall, patents **do cover**: (a) smartphone interpretation of pregnancy test strips, (b) multi-line pregnancy strips optimized for sensors, and (c) general LFA imaging infrastructures. They do **not** cover any credible concept of detecting pregnancy from the appearance of raw urine alone; all depend on immunochemistry plus imaging.

### 3.3 Healthy.io patent portfolio (urinalysis-relevant subset)

- **US9972077B2**: dipstick + calibration array, robust color quantification under unknown illumination. [36]
- **US10948352B2 / US11709096B2 / US20210208000A1**: "Precision luxmeter methods for digital cameras to quantify colors in uncontrolled lighting environments", co-assigned with Scanadu; general method for using phone cameras + illuminance sensors to standardize color measurement for biological diagnostic instruments (test strips). [72]
- **US10991096B2 / US20210241456A1**: chemical reaction analysis with colorized reference elements. [37]

These patents give Healthy.io strong coverage on **calibrated smartphone colorimetry**, especially for strips next to a color board. Freedom-to-operate (FTO) for a new entrant likely requires:

- Avoiding their specific calibration geometry and mapping algorithms; or
- Licensing their IP where direct overlap exists, particularly if using similar boards and multi-color reference patches.

---

## 4. Smartphone-Based Pregnancy Detection: What Exists?

### 4.1 Commercial attempts

**Direct pregnancy determination from urine via smartphone imaging alone (no strip)**

- No credible, regulated commercial product has been found that claims to detect pregnancy **solely by photographing native urine**.
- All deployed systems that touch pregnancy do so via standard **hCG chemistry (lateral flow or dipsticks)** plus smartphone-based readout:
  - Healthy.io Dip.io does **not** read hCG; it reads standard multi-parameter chemistry, including pregnancy-related complications (protein, glucose, etc.), but not pregnancy itself. [5][34][38]
  - TestCard includes pregnancy cards but again uses hCG strips read by camera; pregnancy detection is not smartphone-only; the strip chemistry is doing the diagnostic work. [14][16]
  - WO2018075554A1 describes a smartphone-read pregnancy/disease risk test device with LFA strips and alignment targets, but not image-only detection. [67]

**Indirect / support for pregnancy testing**

- Apps like **First Response Pregnancy PRO** and similar "smart" pregnancy tests connect Bluetooth or app-based experiences (timers, due-date calculators) to otherwise conventional digital pregnancy sticks. [73][74]
- Apps like **Pregnancy Test Checker** claim to help users visually enhance and interpret standard pregnancy test images, but they do not make regulated diagnostic claims; they are essentially image filters to see faint lines, with no validation as IVDs. [75]

### 4.2 Academic attempts

- The **FAU prenatal urinalysis paper (IEEE JTEHM 2022)** is explicitly framed as for prenatal care, not pregnancy detection; it deals with routine urine tests (protein, glucose, etc.) but does not attempt to detect hCG. [52][54]
- To date, **no peer-reviewed study** has demonstrated clinically acceptable sensitivity and specificity for pregnancy detection based solely on raw urine appearance or non-hCG chemical analytes using smartphone imaging.
- All serious smartphone POCT pregnancy work either:
  - Uses smartphone as a more precise **reader for hCG test strips/LFA**, often with neural network enhancement (e.g., Gauss/Exa patents), or [64][65]
  - Deals with other pregnancy-related conditions such as UTIs and preeclampsia risk (proteinuria) rather than pregnancy per se. [41][38]

### 4.3 Why nobody has done "native-urine image" pregnancy detection

**Scientific limitations**

- As you saw in the earlier biomarker review, physiological changes in urine associated with pregnancy (hydration, mild glucosuria, occasional protein, subtle steroid metabolites) **do not produce robust, specific visual signatures**; color and turbidity are dominated by hydration, vitamins, diet, infections. [76][77][78][79][80][81]
- hCG itself is colorless and present at nanomolar levels; without immunochemical amplification (antibody + chromogenic label), it is invisible to a camera. [82][83][84]

**Regulatory and validation barriers**

- The uChek case makes it clear that **even reading a strip visually intended for eyes becomes a regulated device once you automate interpretation with a smartphone**; FDA expects 510(k) data for the combined system. [18][19][22]
- Any app that claims primary pregnancy diagnosis from images of urine (even if "AI-based") would be treated as a high-risk IVD and would need to match or exceed pregnancy test performance (≥99% sensitivity/specificity from missed-menses onward) across populations. [84][85]
- Given the **weak biological signal**, it is highly unlikely such an app could reach regulatory bar; even if a marginal statistical signal existed, performance would likely be far below standard tests, making clearance and liability untenable.

**Business risk**

- The pregnancy test market is mature, with cheap, widely trusted hCG LFAs. An AI-only, image-based urine detector with lower accuracy and no ability to tell early vs late pregnancy offers little incremental value vs cost and regulatory risk.

---

## 5. Regulatory Clearances in Smartphone Urinalysis

### 5.1 FDA-cleared smartphone-urinalysis systems (non-exhaustive but major)

| Device | Sponsor | 510(k) / Pathway | Smartphone role | Cleared claims |
|---|---|---|---|---|
| **Dip.io Urinalysis Test System** | Healthy.io | 510(k) K#### (2018), Class II [4][5][7][34] | Smartphone camera + app analyze color changes of 10-parameter dipstick on color board | Semi-quantitative measurement of glucose, specific gravity, blood, pH, protein; qualitative nitrite, leukocytes, etc., for clinical urinalysis in prescription home use. |
| **Minuteful Kidney ACR test** | Healthy.io | 510(k) clearance 2019-2022, including home use; first smartphone-powered home ACR test [1][6][32][2] | Smartphone reads ACR strips on color board; sends results to cloud/EHR | Semi-quantitative albumin and creatinine in urine; used to assess CKD risk in adults with diabetes/hypertension. |
| **Inui Health home urine platform** | Inui Health (formerly Scanadu) | FDA-cleared home urine testing platform (510(k) summary reported in press) [11][9] | Smartphone analyzes paddle with 5 parameters | Tests for protein, glucose, leukocyte, nitrite, ketones; aids in UTI, diabetes, kidney function assessment; details in 510(k) summary. |
| **Scanwell UTI Test** | Scanwell Health | 510(k) (2018-2020); first OTC smartphone urinalysis app [13][12] | Smartphone app reads leukocyte/nitrite pads and provides UTI result | OTC screening for UTI; demonstrated diagnostic accuracy equivalent to clinic urinalysis. |
| **Scanostics UTI C (K170118)** | Scanostics | 510(k) (2017) [46] | Application+test strips with similar chemistry to predicate analyzers | UTI urinalysis (leukocyte, nitrite); smartphone acts as automated reader. |

*(Exact 510(k) numbers are in the FDA database; above focuses on the qualitative picture.)*

### 5.2 CE marks and other approvals

- Healthy.io Dip.io and Minuteful Kidney are CE-marked and ISO 13485-certified; widely used in UK/EU pilots. [3][35][31]
- TestCard's UTI postcard has CE marking and is sold UK-wide; pregnancy cards exist but claims appear to rely on standard CE pregnancy strip chemistry and not novel pregnancy algorithms. [17]
- Vivoo is positioned as wellness in EU/US; its clinical study is framed as device performance validation, not as a regulated diagnostic. [23][24]
- Vivosens's products and patents suggest CE/wellness positioning; explicit CE labels not easily confirmed.

### 5.3 Claims that were rejected or tightly controlled

- FDA's letter to Biosense (uChek) did not "reject" uChek but forced it to obtain 510(k) as an **automated urinalysis system**, not just an app; effectively blocked US commercialization until clearance obtained, which it did not. [20][19][22][18]
- More generally, FDA mobile-health guidance restricts oversight to apps that: diagnose/treat disease, transform a general-purpose device into a regulated instrument, or serve as accessory to regulated hardware; smartphone urinalysis falls squarely into that set. [86][18]

No public record shows FDA explicitly rejecting **pregnancy detection via smartphone-only imaging**, because nobody has tried at scale; but given existing benchmarks (e.g., FRER's 6-10 mIU/mL sensitivity) and the lack of a plausible biological signal, such claims would likely fail pre-submission discussions.

---

## 6. Whitespace Analysis and Reasons for Past Failures

### 6.1 Where the field is crowded

- **Strip-reading + calibration:** Healthy.io, Scanwell, Vivosens, TestCard, uChek, Vivoo and multiple patent families cover the concept of using a smartphone camera to read test strips with color calibration surfaces. [26][28][61][53][24][36][37][52]
- **General urinalysis (10-parameter dipsticks):** Many entrants (Healthy.io, Inui, Scanwell, Vivoo, others) have built smartphone readers for multi-parametric strips; most rely on similar colorimetric chemistry. [1][11][23][13]
- **UTI testing:** Highly crowded: Scanwell (FDA-cleared), TestCard (CE), multiple wellness apps; plus conventional clinic analyzers. [17][23][13]
- **CKD/ACR:** Healthy.io has strong first-mover advantage and multiple clearances plus large clinical data; academic and thesis projects exist but not yet commercial at scale. [56][6][40]

### 6.2 Genuine whitespace / novelty opportunities

1. **AI-enhanced reading of pregnancy LFA strips across many brands**
   - Many patents and products focus on strip reading in controlled contexts; there is still whitespace for a **cross-manufacturer, cross-strip AI that robustly reads faint pregnancy test lines and addresses hook-effect patterns**, especially if built on top of general LFA neural-network patents like WO2022010997 but specialized to hCG strips. [65][64]
   - This must navigate Gauss/Exa and Healthy.io patents (test-strip imaging, calibration), but a differentiated pregnancy-only SaaS model could be novel if carefully designed.

2. **Multi-marker pregnancy risk panels read by smartphone (beyond hCG)**
   - EP3904878/US20220146509 show strips with multiple test lines for different hCG forms to reduce false negatives; WO2018075554 adds disease-risk lines. [69][68][67]
   - There is whitespace in designing **pregnancy LFA panels that combine hCG with early preeclampsia, gestational diabetes, or infection markers** and optimizing them for AI interpretation (semi-quantitative assessment rather than binary).

3. **End-to-end AI adaptation to uncontrolled environments**
   - Academic work focuses on relatively constrained imaging; patents like WO2023034441 and WO2022010997 tackle cross-device calibration. [66][64]
   - There remains room for a fully open, **phone-agnostic and lighting-agnostic AI toolkit for LFA interpretation** with regulatory-grade validation, potentially as a B2B SDK for test manufacturers.

4. **Urinalysis embedded in smart toilets / bathroom fixtures + AI**
   - In-toilet urinalysis is patented (Hall Labs) but not mainstream; smartphone integration (as local or remote display) with periodic "passive" urinalysis is still wide open commercially, though capital-intensive. [50][49]

5. **Non-diagnostic but clinically-relevant analytics**
   - Beyond "positive/negative," there is whitespace in using smartphone data (frequency of tests, adherence, temporal trends in semi-quantitative pads) to build predictive models of CKD progression, pregnancy complications, or therapy adherence; Healthy.io and Vivoo touch this but do not exhaust it. [24][38][40][23]

### 6.3 Reasons for past failures or limited success

1. **Regulatory friction underestimated**
   - uChek assumed analyzing existing cleared strips with a phone would not require new clearance; FDA disagreed, treating phone+strip as a new urinalysis system requiring 510(k). [19][20][22][18]
   - Scanadu's Scout saga showed that shipping investigational devices before clearance damages trust and can sink a brand. [8][9]

2. **Weak underlying biological signal for "visual-only" ideas**
   - No one has succeeded in pregnancy detection from native urine color/turbidity because science does not support a strong signal; hydration, diet, vitamins, and infection dominate visual properties. [77][80][81][87][76][84]

3. **Economics and workflow integration**
   - Even technically successful systems (Inui, Healthy.io, Scanwell) face non-trivial hurdles integrating with payer workflows, EHRs, and existing lab infrastructure; patient adherence and provider adoption are as important as optical algorithms. [1][2][40][41]

4. **Device heterogeneity and calibration complexity**
   - Massive variation in smartphone cameras and lighting forces complex calibration, color boards, and UX; patents (Healthy.io, Gauss, Vivosens) reflect how hard this is, and many early apps failed to manage this at scale. [53][60][36][37][52]

5. **Niche vs platform positioning**
   - Narrow, focused products (Scanwell UTI) can succeed if they solve a concrete problem with clear telehealth ties. [12][13]
   - Broad "lab in your phone" visions (original Scanadu Scout + Scanaflo) have mostly failed commercially because each analyte demands its own regulatory and clinical evidence package.

---

## 7. "Whitespace Analysis": For a New Entrant in Smartphone Pregnancy/Urinalysis

From a market-intelligence perspective, for an AI team:

- **Do not attempt pregnancy detection from native urine images.** The biological signal is effectively absent; the regulatory bar is high; and the concept has essentially **zero precedent** in the regulated domain. [87][76][77][84]
- **Do leverage chemistry.** The strongest path to market is **chemistry + AI**: hCG LFAs (possibly multi-line, multi-isoform) plus smartphone-based quantitative readout, with added value in:
  - Early detection close to lab sensitivity.
  - Semi-quantitative hCG trends (e.g., doubling curves, ectopic risk hints).
  - Multiplexed complications markers (e.g., protein, specific gravity, ketones) for prenatal risk stratification. [68][69][67]
- **Find unserved workflows.** High-ROI spaces include home CKD risk in underserved populations, remote prenatal monitoring (protein/ketone/blood), and asynchronous telehealth UTI + pregnancy combo tests, none fully dominated by a single player globally. [38][40][41][12]
- **Design around IP.** You will need to steer around Healthy.io's and Vivosens's calibration patents by:
  - Using different calibration geometries or learning-based color correction instead of deterministic color boards; or
  - Licensing or partnering where overlap is unavoidable. [28][26][72][36][37]
- **Anchor on regulated claims.** For anything beyond wellness, plan early for 510(k) or De Novo pathways, with carefully chosen indications (e.g., "aid in diagnosis of UTI" or "screening for albuminuria") and robust comparison vs gold-standard lab analyzers. [88][4][5][13]

In short, there is meaningful whitespace in **AI-assisted, smartphone-read pregnancy and prenatal chemistry**, but only when paired with robust lateral-flow or dipstick chemistry. A vision-only pregnancy detector from urine photographs has neither scientific nor regulatory legs at this time.

---

## Sources

[1] Healthy.io closes $60M Series C, earns second 510(k) for smartphone-based urinalysis: https://www.mobihealthnews.com/news/north-america/healthyio-closes-60m-series-c-earns-second-510k-smartphone-based-urinalysis
[2] Healthy.io raises $50M to expand smartphone kidney test in U.S.: https://www.mobihealthnews.com/news/healthyio-raises-50m-expand-smartphone-kidney-test-us
[3] Smartphone Urine Testing Kit Developer Healthy.io Raises $18 Million: https://www.calcalistech.com/ctech/articles/0,7340,L-3755711,00.html
[4] A Big Win for Digital Health: U.S. FDA Grants Landmark Class II Approval for Clinical Grade Smartphone Testing - Healthy.io's Dip.io Urinalysis: https://www.prnewswire.com/il/news-releases/a-big-win-for-digital-health-u-s-fda-grants-landmark-class-ii-approval-for-clinical-grade-smartphone-testing-healthy-io-s-dip-io-urinalysis-854802393.html
[5] FDA Approves Smartphone-based Urinalysis Test Kit for At-Home Use: https://www.darkdaily.com/2019/03/06/fda-approves-smartphone-based-urinalysis-test-kit-for-at-home-use-that-matches-quality-of-clinical-laboratory-tests/
[6] Minuteful Kidney Receives FDA Clearance - Healthy Blog: https://blog.healthy.io/company-news/minuteful-kidney-receives-fda-clearance/
[7] Healthy.io gets FDA nod for smartphone camera-based home urine test: https://www.mobihealthnews.com/news/healthyio-gets-fda-nod-smartphone-camera-based-home-urine-test
[8] Scanadu - Wikipedia: https://en.wikipedia.org/wiki/Scanadu
[9] Inui Health, formerly Scanadu, launches first clinical grade home urine testing platform: https://gadgetsandwearables.com/2018/09/19/inui-health/
[10] Healthy.io acquires fellow smartphone urinalysis startup Inui Health: https://www.mobihealthnews.com/news/healthyio-acquires-fellow-smartphone-urinalysis-startup-inui-health
[11] inui Health, formerly Scanadu, announces FDA-cleared home urine testing platform: https://www.mobihealthnews.com/content/inui-health-formerly-scanadu-announces-fda-cleared-home-urine-testing-platform
[12] Scanwell launches at-home smartphone test, telehealth for UTIs: https://www.fiercebiotech.com/medtech/scanwell-lemonaid-launch-at-home-smartphone-test-and-telehealth-service-for-urinary-tract
[13] Scanwell Health's FDA-Cleared, Smartphone-Enabled UTI Test: https://www.globenewswire.com/news-release/2020/12/09/2142405/0/en/Scanwell-Health-s-FDA-Cleared-Smartphone-Enabled-UTI-Test-Kit-Now-Available-at-Amazon-Diagnose-and-Treat-in-Two-Minutes-From-the-Safety-of-Your-Home.html
[14] Ready To Launch: https://www.trendingtopics.eu/home-diagnostics-startup-testcard-has-just-raised-e1-8m-to-revolutionize-personalized-medicine/
[15] TestCard - Funding: $15M+ | StartupSeeker: https://startup-seeker.com/company/testcard~com
[16] Urine-Test Medtech Startup Closes $1.7m Funding: https://www.newswire.com/news/urine-test-medtech-startup-closes-1-7m-funding-20650995
[17] Former Pitchfest winner TestCard secures £4.5m funding for expansion: https://www.digitalhealth.net/2020/11/former-pitchfest-winner-testcard-secures-4-5m-funding-for-expansion/
[18] FDA Demonstrates Willingness to Exercise Mobile Health Oversight as Industry Awaits Final Guidance: https://www.cooley.com/news/insight/2013/fda-demonstrates-willingness-to-exercise-mobile-health-oversight-as-industry-awaits-final-guidance
[19] Mobile health app for urinalysis diagnostic draws FDA scrutiny: https://medcitynews.com/2013/05/mobile-health-app-for-urinalysis-diagnostic-draws-fda-scrutiny/
[20] FDA begins cracking down on medical diagnosis apps starting with uChek: https://9to5mac.com/2013/05/24/fda-begins-cracking-down-on-medical-diagnosis-apps-starting-with-uchek-iphone-urinalysis-app/
[21] FDA Asks For Data On Urine-Test App - Popular Science: https://www.popsci.com/technology/article/2013-05/fda-checks-urine-test-app/
[22] FDA Sends Letter to Mobile App Developer for Failure to Obtain 510(k) Clearance: https://www.thefdalawblog.com/2013/05/fda-sends-letter-to-mobile-app-developer-for-failure-to-obtain-510k-clearance/
[23] This Startup Wants to Make Urinalysis as Easy as a Pregnancy Test: https://interestingengineering.com/health/this-startup-wants-to-make-urinalysis-as-easy-as-a-pregnancy-test
[24] Smartphone-Based Point-of-Care Urinalysis Vivoo App: https://dergipark.org.tr/en/download/article-file/3454074
[25] Yocheck - HealthCare, 소변,요책,요첵: https://play.google.com/store/apps/details?id=com.wonpl.urine&hl=en_IE
[26] WO2019221676A1 (Vivosens patent): https://www.perplexity.ai/rest/file-repository/patents/WO2019221676A1?lens_id=141-650-572-278-727
[27] US20210208081A1 (Vivosens patent): https://www.perplexity.ai/rest/file-repository/patents/US20210208081A1?lens_id=004-398-024-073-545
[28] US20220405973A1 (Vivosens patent): https://www.perplexity.ai/rest/file-repository/patents/US20220405973A1?lens_id=123-998-222-046-031
[29] CLINITEK Status Connect - Siemens Healthineers USA: https://www.siemens-healthineers.com/en-us/urinalysis/systems/clinitek-stratus-connect-system
[30] CLINITEK Status+ Analyzer: https://www.siemens-healthineers.com/en-us/urinalysis/systems/clinitek-status-plus-analyzer
[31] Siemens Healthineers partners with Healthy.io: https://www.reuters.com/article/business/healthcare-pharmaceuticals/siemens-healthineers-partners-with-healthyio-for-smartphone-based-urine-testing-idUSKCN1MX1SA/
[32] Healthy.io Nabs $60M for FDA-cleared Smartphone-Based Urinalysis: https://hitconsultant.net/2019/09/12/startup-healthy-io-funding-fda-cleared-smartphone-based-ckd/
[33] Now your smartphone camera can perform clinical urinalysis at home: https://www.biospectrumasia.com/news/86/11376/now-your-smartphone-camera-can-perform-clinical-urinalysis-at-home.html
[34] FDA Clears Smartphone-Enabled Urinalysis Kit for Home Use - MPR: https://www.empr.com/home/news/fda-clears-smartphone-enabled-urinalysis-kit-for-home-use/
[35] Healthy.io turns your smartphone into a clinical-grade medical testing device: https://venturebeat.com/technology/healthy-io-turns-your-smartphone-into-a-clinical-grade-medical-testing-device
[36] US9972077B2 (Healthy.io patent): https://www.perplexity.ai/rest/file-repository/patents/US9972077B2?lens_id=010-715-656-620-221
[37] US20210241456A1 (Healthy.io patent): https://www.perplexity.ai/rest/file-repository/patents/US20210241456A1?lens_id=074-767-067-772-004
[38] Study Finds Healthy.io's At-Home, Smartphone-Based Urinalysis Feasible for Prenatal Care: https://www.prnewswire.com/il/news-releases/study-finds-healthyios-at-home-smartphone-based-urinalysis-feasible-preferred-and-easy-to-use-for-women-in-prenatal-care-300883257.html
[39] US Urine Analysis Test System in the Lay User Hands: https://cdn.clinicaltrials.gov/large-docs/72/NCT05838872/Prot_SAP_000.pdf
[40] Evaluating the feasibility and acceptability of home-based urinalysis for ACR with smartphone technology: https://onlinelibrary.wiley.com/doi/10.1111/jorc.12460
[41] Remote digital urinalysis with smartphone technology: https://pmc.ncbi.nlm.nih.gov/articles/PMC9050594/
[42] Scanadu's New Pee Stick Puts The Medical Lab On Your Smartphone: https://techcrunch.com/2015/02/18/scanadus-new-pee-stick-puts-the-medical-lab-on-your-smartphone/
[43] Company Case Studies - Navigating Regulatory Hurdles: https://www.biocheckup.co.uk/post/company-case-studies-navigating-regulatory-hurdles
[44] CLINITEK Status Connect System - Relaymed: https://relaymed.com/connections/devices/siemens-clinitek-status-connect-system/
[45] CLINITEK Status Connect System - Siemens Healthineers: https://www.siemens-healthineers.com/en-us/poct-urinalysis/clinitek-status-connect
[46] K170118 Trade/Device Name: Scanostics UTI C: https://www.accessdata.fda.gov/cdrh_docs/pdf17/K170118.pdf
[47] Owlet Baby Monitor: https://owletcare.com
[48] Owlet Care - Apps on Google Play: https://play.google.com/store/apps/details?id=com.owletcare.owletcare&hl=en_US
[49] WO2018140524A1 (Hall Labs patent): https://www.perplexity.ai/rest/file-repository/patents/WO2018140524A1?lens_id=119-886-459-110-301
[50] US11224370B2 (Hall Labs patent): https://www.perplexity.ai/rest/file-repository/patents/US11224370B2?lens_id=004-367-350-241-020
[51] FAU paper announcement: https://www.mad.tf.fau.de/2022/06/23/new-paper-smartphone-based-colorimetric-analysis-of-urine-test-strips-for-at-home-prenatal-care/
[52] Smartphone-Based Colorimetric Analysis of Urine Test Strips (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC9292338/
[53] Smartphone-Based Point-of-Care Urinalysis Under Variable Illumination: https://pmc.ncbi.nlm.nih.gov/articles/PMC5764119/
[54] FAU paper PubMed: https://pubmed.ncbi.nlm.nih.gov/35865751/
[55] FAU paper open access: https://open.fau.de/items/c964dc5d-6da9-4b9a-ac6b-e79684748e17
[56] Using a Smartphone for Point-of-Care Urinalysis of CKD (Flinders thesis): https://flex.flinders.edu.au/file/c7e6a8ef-8fd3-4d64-a0f4-02a112737c57/1/Thesis_shaymaa_PDF_2018.pdf
[57] AI in Diagnostics: Enhancing Urine Test Accuracy: https://www.annlabmed.org/journal/view.html?uid=3601&vmd=Full
[58] Korean AI urinalysis paper: https://pdfs.semanticscholar.org/77a5/ca093a365f50acf08c001a28a7e2d5cf7aa3.pdf
[59] Point-of-Care Technologies: https://pdfs.semanticscholar.org/580f/6c0af99f4f9a57b09a3dfd47d41b0eb47c46.pdf
[60] Urine Test Strip Analysis App | Businessware Technologies: https://www.businesswaretech.com/case-studies/medical-testing-strip-analysis-app
[61] WO2016154262A1 (Wellmetrix patent): https://www.perplexity.ai/rest/file-repository/patents/WO2016154262A1?lens_id=026-167-722-441-894
[62] US20180049723A1 (Wellmetrix patent): https://www.perplexity.ai/rest/file-repository/patents/US20180049723A1?lens_id=118-423-411-613-834
[63] US20250205699A1 (Vivosens 2025 patent): https://www.perplexity.ai/rest/file-repository/patents/US20250205699A1?lens_id=043-111-626-379-334
[64] WO2022010997A1 (Gauss/Exa LFA patent): https://www.perplexity.ai/rest/file-repository/patents/WO2022010997A1?lens_id=157-831-255-820-520
[65] US20230146924A1 (Gauss/Exa LFA patent): https://www.perplexity.ai/rest/file-repository/patents/US20230146924A1?lens_id=170-332-449-868-543
[66] WO2023034441A1 (Imaging Test Strips patent): https://www.perplexity.ai/rest/file-repository/patents/WO2023034441A1?lens_id=151-127-014-274-584
[67] WO2018075554A1 (Pregnancy Test To Assess Disease Risk): https://www.perplexity.ai/rest/file-repository/patents/WO2018075554A1?lens_id=126-910-582-000-598
[68] EP3904878A1 (PROTIA pregnancy strip patent): https://www.perplexity.ai/rest/file-repository/patents/EP3904878A1?lens_id=077-485-862-611-465
[69] US20220146509A1 (PROTIA pregnancy strip patent): https://www.perplexity.ai/rest/file-repository/patents/US20220146509A1?lens_id=027-258-892-866-916
[70] US20170023542A1 (Smartphone dock patent): https://www.perplexity.ai/rest/file-repository/patents/US20170023542A1?lens_id=075-786-422-490-854
[71] US20150010441A1 (Electronic Pregnancy Test Device): https://www.perplexity.ai/rest/file-repository/patents/US20150010441A1?lens_id=108-872-623-645-150
[72] US20210208000A1 (Precision luxmeter patent): https://www.perplexity.ai/rest/file-repository/patents/US20210208000A1?lens_id=081-526-358-650-687
[73] Take a Pregnancy Test With Your Phone? - Mom.com: https://mom.com/pregnancy/26865-take-pregnancy-test-your-phone
[74] Digital At-Home Pregnancy Test | First Response: https://www.firstresponse.com/en/product-listings/digital-pregnancy-test
[75] Pregnancy Test Checker - App Store: https://apps.apple.com/us/app/pregnancy-test-checker/id854689871
[76] Urine color as an indicator of urine concentration in pregnant and lactating women (PubMed): https://pubmed.ncbi.nlm.nih.gov/26572890/
[77] Urine color as an indicator (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC5290087/
[78] Detection of Proteinuria in Pregnancy: https://pmc.ncbi.nlm.nih.gov/articles/PMC3809617/
[79] Proteinuria during pregnancy: definition, pathophysiology: https://pubmed.ncbi.nlm.nih.gov/32882208/
[80] Color, Odor Changes in Urine: https://www.health.harvard.edu/press_releases/color-odor-changes-in-urine-usually-but-not-always-harmless
[81] Changes In Urine: Causes, Symptoms & Treatment - Cleveland Clinic: https://my.clevelandclinic.org/health/diseases/15357-urine-changes
[82] Human Chorionic Gonadotropin - StatPearls: https://www.ncbi.nlm.nih.gov/books/NBK532950/
[83] hCG: Biological Functions and Clinical Applications: https://pmc.ncbi.nlm.nih.gov/articles/PMC5666719/
[84] Accuracy of home pregnancy tests at the time of missed menses: https://pubmed.ncbi.nlm.nih.gov/14749643/
[85] Accuracy of Early Results with Home Pregnancy Test Kits - AAFP: https://www.aafp.org/pubs/afp/issues/2004/1001/p1370.html
[86] FDA Delivers Its First Mobile Medical App Inquiry | Mintz: https://www.mintz.com/insights-center/viewpoints/2146/2013-05-28-fda-delivers-its-first-mobile-medical-app-inquiry
[87] Flaw in many home pregnancy tests can return false negative results: https://medicine.washu.edu/news/flaw-in-many-home-pregnancy-tests-can-return-false-negative-results/
[88] What Does Having a FDA Cleared Pregnancy Test Mean?: https://ctti-clinicaltrials.org/wp-content/uploads/2021/07/CTTI_Pregnancy_Testing_Meeting_FDA_Test_Johnson_Lyles.pdf
