# Urine Appearance: Human-Eye Atlas for a Computer Vision Team

A "human-eye atlas" of urine appearance, structured for an AI vision team. It focuses on what a trained pathologist actually reads from a sample and how those signals translate into quantifiable image features.

---

## 1. Urine Color Atlas

### 1.1 Overview and color-hydration relationship

In normal adults, urine color is determined predominantly by concentration of urochrome pigments (urobilin, urobilinogen), which darken as urine osmolality and specific gravity (SG) increase. [1][2]
Well-hydrated urine is nearly colorless to pale straw (SG ~1.003-1.010), while concentrated urine is deep yellow to amber (SG up to ~1.030). [2][3][4]

For computer vision:

- **Hue:** usually in the yellow-amber range (roughly HSV hue ≈ 40-60°).
- **Saturation/value:** increase with concentration (darker, more saturated with dehydration).

Below, each color category includes:

- **Approximate visual description** (so you can later map to RGB/HSV).
- **Major differentials** (physiologic, pathologic, exogenous).

### 1.2 Colorless or very pale yellow

**Appearance**

- Nearly water-clear or faint straw; HSV ≈ hue 45-55°, saturation 0-0.15, value high (0.9-1.0).

**Associations**

- **Physiologic**
  - High fluid intake, over-hydration. [4][2]
  - Diuretic use (loop, thiazide).
- **Pathologic**
  - Diabetes insipidus or uncontrolled diabetes with polyuria (if persistent with high volumes). [2]

### 1.3 Pale straw to standard yellow

**Appearance**

- Pale straw to "light beer" yellow; moderate saturation, high value.

**Associations**

- Normal, adequately hydrated urine. [1][2]
- SG typically ~1.010-1.020; osmolality ~300-600 mOsm/kg. [3][5]

### 1.4 Dark yellow to amber

**Appearance**

- Deep straw, amber, or "apple juice" colored; higher saturation, lower value.

**Associations**

- **Dehydration / volume depletion**, most common; urine color charts for hydration use this range as early dehydration signal. [5][6][7]
- **Concentrated urine from fever, sweating, vomiting/diarrhea.** [2]
- **Mild bilirubinuria** can shift toward yellow-brown (see below). [2]

### 1.5 Orange

**Appearance**

- Orange to copper; hue shifts toward red (HSV ~20-40°).

**Differential**

- **Medications**
  - Rifampin, phenazopyridine (UTI analgesic), some sulfasalazine formulations, warfarin, isoniazid. [8][2]
- **Dehydration**: very concentrated urochrome + urobilin. [9][10]
- **Bilirubinuria**: conjugated bilirubin in cholestatic liver disease can give "dark yellow to orange" or yellow-brown urine. [9][2]

### 1.6 Pink to red urine

**Appearance**

- Pale pink through "rose wine," to frankly red.

**Differential**

- **Foods / benign pigments**
  - Beetroot, rhubarb, blackberries ("beeturia"). [10][11][9]
- **Hematuria** (RBCs in urine): glomerular or urologic sources:
  - UTI, nephrolithiasis, glomerulonephritis, tumors of kidney/bladder, trauma, BPH. [9][2]
- **Hemoglobinuria / myoglobinuria**: intravascular hemolysis, rhabdomyolysis (often more brown/cola-colored; see below). [9][2]
- **Porphyria**: porphyrins can produce red or port-wine urine, often darkening on standing. [2]
- **Drugs**: rifampin, phenazopyridine, senna laxatives, doxorubicin. [8][2]

### 1.7 Brown, tea-colored, cola-colored

**Appearance**

- Tea, cola, or "strong iced tea"; brown or brown-red.

**Differential**

- **Myoglobinuria**: rhabdomyolysis, crush injury; often brown or tea-colored with positive blood on dipstick but few RBCs microscopically. [9][2]
- **Hemoglobinuria**: intravascular hemolysis (similar strip-microscope discrepancy). [2]
- **Liver disease / cholestasis**: conjugated bilirubinuria, particularly with pale stools; "dark brown" or "brown-green" urine. [9][2]
- **Drugs**: metronidazole, nitrofurantoin, levodopa, some antimalarials, metronidazole, chloroquine; cascara and senna laxatives. [8][2]
- **Severe dehydration**: extreme concentration plus urobilin can appear deep brownish yellow. [9]

### 1.8 Brown-black or truly black

**Appearance**

- Dark brown to black; often intensifies on standing.

**Differential**

- **Alkaptonuria**: oxidation of homogentisic acid causes black urine on standing. [2][9]
- **Melanoma / melanuria**: melanin or its precursors can darken urine. [2]
- **Methemoglobinuria**, severe hemolysis or rhabdomyolysis. [9][2]
- High doses of certain laxatives (cascara, senna) and levodopa can give brown-black. [2]

### 1.9 Green, blue, and purple

**Green**

- **Causes**
  - UTIs with Pseudomonas (pyocyanin pigment). [1][2]
  - Drugs: propofol, amitriptyline, indomethacin, cimetidine, promethazine, methylene-blue-containing medications. [10][8]
  - Food dyes. [10]

**Blue**

- **Causes**
  - Methylene blue (dyes, some meds), triamterene. [10]
  - Familial benign hypercalcemia ("blue diaper syndrome"). [2]

**Purple**

- **Purple urine bag syndrome**: in catheterized patients with UTIs by bacteria that produce indigo and indirubin from tryptophan metabolites, staining the bag/tubing; urine itself can appear purple or deep blue-red. [2]

### 1.10 White, milky, or opalescent

**Appearance**

- White, cloudy, "milk-like" urine.

**Differential**

- **Phosphaturia**: amorphous phosphates in alkaline urine; clears with acidification. [2]
- **Chyluria**: lymphatic-urinary fistula (e.g., filariasis) causing chyle; remains milky after acidification. [2]
- **Heavy pyuria**: pus from severe UTI; may have visible clumps or strands. [12][1][2]
- **Lipiduria**: nephrotic syndrome (microscopically "Maltese crosses"); grossly can contribute to cloudy/milky appearance. [2]

### 1.11 Color stability over time

- **Within 1-2 hours:** color generally stable if kept at room temperature and protected from light; CLSI and AAFP recommend analyzing urine within 2 hours or refrigerating. [2]
- **Several hours to 24 h (unrefrigerated):**
  - Urobilinogen oxidizes to urobilin → darkening. [2]
  - RBCs lyse; red urine due to hematuria may become more uniformly reddish-brown. [2]
  - Bacterial growth increases turbidity and can alter pH (more alkaline), leading to phosphate precipitation and cloudiness. [1][2]
  - Bilirubin degrades with light exposure, potentially lightening yellow-brown. [2]

For computer vision, any color-based inference must either enforce a short, standardized time from void to capture, or explicitly model time-dependent drift.

---

## 2. Turbidity

### 2.1 Clinical grading scales

Most labs use semi-quantitative descriptors:

- **Clear**: transparent, text readable through tube.
- **Slightly cloudy / hazy**: mild loss of clarity, text still legible.
- **Cloudy**: obvious haziness, text blurred or unreadable.
- **Turbid**: significant opacity, can't see through; particles may be visible.
- **Milky**: opaque white, often suggesting heavy phosphaturia, chyluria, or pyuria. [13][14][12][2]

These categories align well with CV features such as light transmission, scattering, and contrast of background objects behind the tube.

### 2.2 Causes

**Common contributors**: [14][12][1][2]

- **Crystals**
  - Amorphous phosphates (alkaline urine; "cloudy" that clears with acetic acid).
  - Amorphous urates (acidic urine; pink "brick dust" sediment, more evident when cooled).
- **Cells**
  - Leukocytes (pyuria): UTIs, interstitial nephritis.
  - RBCs: gross hematuria.
  - Epithelial cells.
- **Bacteria**
  - Heavy bacteriuria; can produce fine haze and micro-clumps.
- **Mucus**
  - Mucus threads/clumps, more common in women (vaginal contamination).
- **Lipids / chyle**
  - Nephrotic syndrome, chyluria (lymphatic fistula).

AAFP explicitly notes that "cloudy urine often is a result of precipitated phosphate crystals in alkaline urine, but pyuria also can be the cause." [2]

### 2.3 Effects of temperature and time

- Cooling acidic urine (e.g., in refrigerator) precipitates amorphous urates → pinkish sediment and cloudiness; warming clears it. [2]
- Warming alkaline urine may dissolve some phosphates; cooling alkaline urine can worsen phosphaturia cloudiness.
- Bacterial proliferation over hours to days markedly increases turbidity by adding bacteria and raising pH, which precipitates phosphates. [12][1][2]

For CV, turbidity can be quantified via:

- **Transmittance** of a standard background pattern.
- **Scattering** (e.g., intensity of back-scattered light at specific angles).
- Time-series images to distinguish reversible crystal precipitation (temperature-dependent) vs progressive bacterial turbidity.

---

## 3. Foam and Surface Characteristics

### 3.1 Normal vs abnormal foam

Foam is produced by agitation entraining air; persistence relates to surface-active substances (surfactants, proteins, bile salts).

**Normal foam**: [15][16]

- Bubble size: larger, irregular bubbles.
- Persistence: dissipates quickly (seconds to under 1-2 minutes).
- Common in concentrated urine or with vigorous stream.

**Proteinuria foam**: [17][18][15]

- Bubble size: fine, uniform, dense bubbles.
- Persistence: stable "beer head" or shaving-cream-like foam that persists minutes or more.
- Typically associated with significant proteinuria (albumin) and underlying renal disease (diabetic nephropathy, glomerulonephritis, CKD).

**Bilirubin-related foam**

- In marked conjugated hyperbilirubinemia, foam may be **yellowish** because pigments partition into the air-liquid interface. [2]

### 3.2 Reliability as a clinical sign

- Major references stress that **foamy urine alone is not a reliable diagnostic test**; many benign factors (fast stream, concentrated urine, detergent residues in the toilet) can cause transient foam without proteinuria. [16][15][17]
- Persistent foamy urine **plus** lab-confirmed proteinuria is meaningful; foam alone is insufficient. [18][2]

For CV:

- Potential features: bubble size distribution, foam area fraction, decay rate over time.
- Limitations: dependency on bowl geometry, water depth, cleaning agents; extremely environment-dependent, not easily standardized.

---

## 4. Odor (for completeness)

Although not visual, odor often co-varies with visual changes.

**Normal**

- Mild, slightly "nutty" or urea-like; stronger if concentrated. [1][2]

**Abnormal odors and associations**: [12][1][2]

- **Strongly ammoniacal**: stale urine; urease-positive bacteria creating ammonia; suggests UTI if in fresh sample.
- **Foul / putrid**: infection, especially with anaerobic organisms.
- **Sweet / fruity**: ketonuria (diabetic ketoacidosis, starvation).
- **"Maple syrup"**: maple syrup urine disease (in infants).
- **"Mousy"**: phenylketonuria.
- **"Cabbage-like" or pungent**: asparagus metabolites; also some drugs.

Vision cannot directly measure odor, but certain patterns (e.g., chronic turbidity + bubbles + color) might co-occur with specific odor states.

---

## 5. Sediment Visible to the Naked Eye

Most diagnostic work is microscopic; however, some elements are visible grossly.

**Visible crystals**

- **Amorphous urates**: fine pinkish "brick dust" sediment, especially in infants or after refrigeration; often benign. [2]
- **Amorphous phosphates**: whitish cloud or sediment in alkaline urine; dissolves with acetic acid. [2]
- **Larger crystals**: cystine (hexagonal), calcium oxalate (envelope-like), triple phosphate ("coffin lids") rarely visible macroscopically but can give the impression of fine sandy deposits on tube bottom.

**Visible cells / clots**

- **RBC clots**: stringy red clots, sometimes worm-like; indicate heavy hematuria from urinary tract sources.
- **Pus clumps**: yellowish-white flecks in severe pyuria. [14][12]

**Casts**

- Generally microscopic; occasionally **large tubular casts** may be part of visible clumps, but this is uncommon.

**Mucus threads**

- Long, thin, translucent strands; can be visible as floating filaments, especially in women (vaginal contamination).

For CV, sediment can be quantified with:

- **Particle counting** using thresholded images from clear tubes.
- **Morphologic classification** (size, shape, color) for coarse features like clots vs amorphous sediment.

---

## 6. Time-Dependent Visual Changes

### 6.1 1 minute after voiding

- Color essentially reflects **in vivo** state (modulo lighting).
- Turbidity, foam, and sediment represent the "fresh" sample.
- RBCs mostly intact; crystal distribution stable.

### 6.2 10 minutes

- Minor changes: some foam dissipates, small bubbles vanish.
- Evaporation at surface may slightly concentrate solutes, but bulk appearance still represents the original state.
- Clinical guidelines usually consider samples up to ~2 hours as acceptable for routine macroscopic exam. [2]

### 6.3 1 hour

- **At room temperature:**
  - Bacteria (if present) begin to multiply, but gross turbidity may not yet significantly increase.
  - CO₂ loss raises pH, especially in previously acidic urine, promoting phosphate precipitation → subtle cloudiness, especially near the meniscus or tube bottom. [1][2]
  - Some RBC lysis in hypotonic or alkaline urine; red urine from hematuria may become more homogeneously reddish/brown. [2]

### 6.4 24 hours (unrefrigerated)

- **Significant degradation**:
  - Marked bacterial growth → increased turbidity, sediment, and ammoniacal odor. [1][2]
  - Increased pH from urea hydrolysis and CO₂ loss → phosphaturia/cloudiness, potential precipitated magnesium ammonium phosphate (struvite).
  - Urobilinogen oxidizes → darker yellow-brown.
  - Bilirubin, cells, and casts degrade; microscopic exam becomes uninterpretable.
- Hence guidelines: examine within 2 hours or refrigerate at ~4 °C. [2]

For CV, time is a huge confounder; any model must either:

- Require capture within a fixed time window, or
- Accept only standardized pre-analytic conditions (e.g., clinic sample cups, known storage).

---

## 7. Standardization of Visual Assessment

### 7.1 Color charts and hydration scales

- **Armstrong 8-color urine color chart**: validated for hydration assessment; colors 1-8 correlate strongly with urine osmolality and SG. [6][5]
  - Uc ≥ 4 generally corresponds to Uosm ≥ 500 mOsm/kg and SG ≥ ~1.020 (dehydration). [7][5]
- Studies show **strong correlation between urine color, osmolality, and SG**, confirming that color is a low-cost hydration proxy. [5][6]

### 7.2 Inter-rater reliability

- Visual color matching against charts shows meaningful **inter- and intra-observer variability**; lighting, background, and individual color perception all affect grading. [19][6]
- Muhaimin Noor Azhar et al. demonstrated that using a smartphone-based colorimetry with a calibration card improved agreement with reference spectrophotometric measures compared to naked-eye scoring, especially under varied lighting. [6]
- Automated urinalysis readers significantly improve the proportion of correctly classified positives compared with visual reading of strips (e.g., an improvement from ~48% to 74% "real positive" rate in one study), highlighting substantial human variability in interpreting strip pads and color intensity. [19]

### 7.3 Turbidity and sediment

- Pathology SOPs usually give descriptive criteria for clarity (clear, hazy, cloudy, turbid, milky) but formal inter-rater statistics are limited; experience and training significantly affect consistency. [13][14][12][2]
- Automated analyzers (e.g., flow cytometry-based Sysmex UF systems) avoid subjective turbidity grading entirely by count-based reporting.

### 7.4 Implications for computer vision

- **Color metrics (mean HSV, distribution, contrast) are ideal for automation**, particularly if coupled with calibration targets. [20][21][6]
- Human observers are weak at repeatable fine color discrimination; CV can outperform humans when lighting and white balance are controlled.
- For strip pads, deep learning methods already achieve standardized strip segmentation, pad isolation, and robust color measurement under a range of conditions. [21][22][20]

---

## 8. Pregnancy-Specific Visual Observations

### 8.1 Published literature and evidence

- Systematic hydration studies show that **pregnant women have the same color-osmolality relationships as non-pregnant adults**: urine color correlates with hydration status but is not uniquely altered by pregnancy. [23][7]
- Clinical reviews and patient-education sources emphasize that **pregnancy itself does not inherently change urine color**, beyond effects of hydration, diet, vitamins, and comorbidities. [24][1][9]

### 8.2 Morning sickness and dehydration

- Early pregnancy nausea/hyperemesis gravidarum leads to vomiting, reduced oral intake, and dehydration. [25][26]
- Resulting urine often moves into the amber/deep yellow range, with elevated SG; ketonuria may occur (though ketones themselves are colorless; strip pads provide color change). [27][28][25]
- These changes are **non-specific**; identical appearances occur with any significant dehydration.

### 8.3 Prenatal vitamins and supplements

- Prenatal vitamins typically contain high doses of riboflavin (vitamin B2) and other B-complex vitamins; excess riboflavin is excreted in urine, producing **bright or fluorescent yellow to yellow-green urine**. [29][30][31][32][10]
- This is **not specific to pregnancy**; any B-complex supplement can have the same effect. However, pregnancy increases the prevalence of this state because prenatal supplementation is near-universal.

### 8.4 UTIs and cloudy urine in pregnancy

- Pregnancy predisposes to urinary stasis and vesicoureteral reflux, increasing UTI incidence. [33][34]
- Cloudy urine in pregnancy can result from increased leukocytes, bacteria, and phosphates; patient-facing sources explicitly note that cloudy/foamy urine may be more frequent in pregnancy but is not always pathologic. [12][1]

### 8.5 Clinical lore vs evidence

Common lore:

- "Pregnant urine looks cloudy or milky": mostly reflects higher UTI prevalence and occasional phosphaturia; no evidence of a specific "pregnancy urine look." [12][1][2]
- "Urine is darker in early pregnancy": due to dehydration from nausea; again non-specific. [26][7][25]
- "Foam means pregnancy": foam is related to protein and physical flow, not to pregnancy per se; evidence does not support foam as a pregnancy marker. [15][18][2]

Net: **pregnancy itself has no distinctive, reliable gross urine signature**. Visual differences stem from secondary factors (hydration, vitamins, UTIs, comorbid renal disease).

---

## 9. Features Most Amenable to Computer Vision Quantification

For your vision pipeline, it helps to prioritize what the camera can measure robustly, and how clinically meaningful each variable is.

### 9.1 High potential features

**1. Bulk color (hydration / pigment)**

- **Quantifiable:**
  - Mean and variance of HSV color across the liquid region.
  - Mapping to established urine color charts to infer hydration (e.g., Uc 1-8). [5][6]
- **Clinical correlation:**
  - Good surrogate for SG and osmolality (hydration state). [7][6][5]
  - Detection of extreme colors suggesting hematuria (red/pink), bilirubinuria (orange/brown), myoglobinuria (tea-colored), or unusual hues (blue/green/purple) that point to specific differentials. [10][9][2]
- **Caveats:**
  - Lighting, container color, and background require calibration; smartphone-based colorimetry with reference cards has been shown to significantly improve accuracy vs human scoring. [20][21][6]

**2. Turbidity / clarity**

- **Quantifiable:**
  - Transmittance metrics: how well a standard background / pattern is visible through the sample.
  - Light scattering measures from back-lighting.
- **Clinical correlation:**
  - Distinguishes clear vs cloudy vs turbid/milky states, which correlate with pyuria, bacteriuria, heavy crystalluria, or chyluria. [14][12][1][2]
- **Value for AI:**
  - As a triage tool: "seek evaluation for possible infection or stones if new cloudy urine is persistent."
  - As an input feature for multi-signal models (e.g., color + turbidity + symptom metadata).

**3. Visible sediment and particles**

- **Quantifiable:**
  - Particle counts and size distribution in a standardized cylindrical container.
  - Motion analysis (settling rates, Brownian motion) to differentiate cells vs crystals (though this drifts toward microscopy).
- **Clinical correlation:**
  - Coarse detection of heavy hematuria (red streaks/clots), gross pyuria (yellow clumps), or brick-dust urates. [14][2]

**4. Test strip pad colors (if used)**

- **Quantifiable:**
  - Per-pad color classification, RGB→semi-quantitative analyte levels (e.g., protein, glucose, blood, nitrite, leukocytes).
- **Clinical correlation:**
  - Already FDA-cleared in several systems; AI can match or exceed human performance under varied lighting. [35][36][21][20]
- **Relevance to pregnancy:**
  - Protein, glucose, ketone, leukocyte, and nitrite pads are directly relevant to prenatal risk (preeclampsia, gestational diabetes, UTI, HG).

### 9.2 Medium potential features

**5. Foam characteristics**

- **Quantifiable:**
  - Bubble size distribution, foam thickness, area fraction, persistence over time (time-lapse).
- **Clinical correlation:**
  - Persistent fine foam correlates with proteinuria, but confounded by detergents, stream velocity, and bowl geometry. [16][17][15]
- **Use case:**
  - Possibly as a weak feature in a multi-feature model for CKD or proteinuria; unlikely to stand alone.

**6. Meniscus shape and surface reflectance**

- **Quantifiable:**
  - Meniscus curvature, specular highlight area, and reflectance can reflect SG (denser fluids have slightly different wetting and meniscus curves), but this is subtle compared with straightforward SG measurement.
- **Clinical relevance:**
  - Very indirect; might offer incremental improvement in hydration estimation when combined with color and known cup geometry.

### 9.3 Low potential features

**7. Subtle time-dependent changes in a single sample**

- Changes over hours mainly reflect non-diagnostic degradation: bacterial growth, oxidation, CO₂ loss, rather than clinically actionable differences in the original physiology. [2]
- Attempting to infer anything from long-aged specimens is generally discouraged even in human practice.

**8. Pregnancy-specific "look"**

- As covered, there is **no pregnancy-specific gross appearance**; any model that claims to detect pregnancy from native urine without chemistry would be exploiting extremely weak, highly confounded correlations. [23][7][1][9]

---

### 9.4 Ranked list for your AI system

**High suitability for CV**

- Bulk color (for hydration, hematuria, bilirubin/myoglobin, rare pigment disorders).
- Turbidity (infection vs clear vs crystal-rich states).
- Strip pad colorimetry (multi-analyte urinalysis) in a controlled test context.

**Medium suitability**

- Sediment/particle detection and coarse classification.
- Foam morphology and persistence (only in carefully controlled setups).
- Surface/meniscus features as secondary hydration signals.

**Low or none**

- Any direct pregnancy detection from native urine appearance.
- Fine diagnostic distinctions based solely on odor-linked conditions or time-aged changes.

If you design your datasets and capture protocol around these high- and medium-value features, with standardized containers, reference color targets, tightly controlled capture timing, and metadata on diet/meds, you can approximate or improve upon what a human pathologist does at the bench for the **macroscopic** component of urinalysis. The microscopic and molecular layers still require chemistry and imaging beyond RGB cameras.

---

## Sources

[1] Common Causes of Cloudy Urine - WebMD: https://www.webmd.com/a-to-z-guides/cloudy-urine-causes
[2] Urinalysis: A Comprehensive Review - AAFP: https://www.aafp.org/pubs/afp/issues/2005/0315/p1153.html
[3] Urine specific gravity test: What is it, and what do results mean?: https://www.medicalnewstoday.com/articles/322125
[4] Urine-Specific Gravity: Purpose, Range & High Symptoms: https://my.clevelandclinic.org/health/diagnostics/specific-gravity-of-urine
[5] Validity of Urine Color Scoring Using Different Light Conditions: https://pmc.ncbi.nlm.nih.gov/articles/PMC8876881/
[6] Improving the reliability of smartphone-based urine colorimetry (Muhaimin Noor Azhar et al., 2023): https://journals.sagepub.com/doi/full/10.1177/20552076231154684
[7] Urine color as an indicator of urine concentration in pregnant and lactating women (PubMed): https://pubmed.ncbi.nlm.nih.gov/26572890/
[8] Urine Colour Chart: What Your Pee Says About Your Health - Medanta: https://www.medanta.org/patient-education-blog/urine-colour-chart-heres-what-your-urines-colour-can-say-about-your-health
[9] Urine color chart in pregnancy: https://www.medicalnewstoday.com/articles/urine-color-chart
[10] Urine Color Chart: What's Normal and When to See a Doctor - Healthline: https://www.healthline.com/health/urine-color-chart
[11] Food Idiosyncrasies: Beetroot and Asparagus (MIT): https://stuff.mit.edu/afs/athena/course/other/kitchen-chem/www/research_papers/Asparagus.pee.pdf
[12] Cloudy Urine - Cleveland Clinic: https://my.clevelandclinic.org/health/symptoms/21894-cloudy-urine
[13] Why Is My Urine Cloudy? Common Causes & Treatment Options: https://www.advancedurology.com/blog/why-is-my-urine-cloudy
[14] Cloudy Urine? Why Your Pee is Hazy: https://ubiehealth.com/doctors-note/cloudy-urine-why-pee-hazy-medical-approved-steps-7
[15] Foamy Urine: Bubbles, Causes, Diagnosis & What's Normal - Cleveland Clinic: https://my.clevelandclinic.org/health/symptoms/foamy-urine
[16] Why Is My Urine Bubbling If It's Not Proteinuria? | Ubie Doctor's Note: https://ubiehealth.com/doctors-note/bubbles-urine-foamy-without-protein-proteinuria-3832e5
[17] Foamy Urine Can Be a Sign of Kidney Disease | Proteinuria - Fresenius: https://www.freseniuskidneycare.com/thrive-central/foamy-urine-kidney-disease
[18] What Foamy Urine Means and When to Talk with a Doctor - Healthgrades: https://resources.healthgrades.com/right-care/kidneys-and-the-urinary-system/foamy-urine
[19] Interobserver Variability - Medipee: https://www.medipee.com/en/urinalysis/factors-of-influence/interobserver-variability
[20] Smartphone-Based Point-of-Care Urinalysis Under Variable Illumination - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC5764119/
[21] Smartphone-Based Colorimetric Analysis of Urine Test Strips for At-Home Prenatal Care: https://pmc.ncbi.nlm.nih.gov/articles/PMC9292338/
[22] WO2019221676A1 - Analysis of urine test strips with mobile camera: https://patents.google.com/patent/WO2019221676A1/en
[23] Urine color as an indicator of urine concentration in pregnant and lactating women (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC5290087/
[24] Changes In Urine: Causes, Symptoms & Treatment - Cleveland Clinic: https://my.clevelandclinic.org/health/diseases/15357-urine-changes
[25] Hyperemesis Gravidarum - StatPearls - NCBI Bookshelf: https://www.ncbi.nlm.nih.gov/books/NBK532917/
[26] Hyperemesis gravidarum - LITFL Fellowship Notes: https://litfl.com/hyperemesis-gravidarum/
[27] Ketonuria is not associated with hyperemesis gravidarum: https://www.sciencedirect.com/science/article/abs/pii/S0301211520305261
[28] Abnormal liver enzymes and ketonuria in hyperemesis (PubMed): https://pubmed.ncbi.nlm.nih.gov/2362099/
[29] Understanding the Color of Your Urine During Pregnancy - TENA: https://shop.tena.us/blogs/support-and-advice/pregnancy-urine-color
[30] Prenatal Vitamins: Urine Color Changes and What They Mean - Medshun: https://medshun.com/article/do-prenatal-vitamins-change-the-color-of-your-urine
[31] The Vitamin Behind Your Vibrant Urine Color - Swolverine: https://swolverine.com/blogs/blog/unveiling-the-yellow-mystery-the-vitamin-behind-your-vibrant-urine-color
[32] Tips for Choosing a Prenatal Vitamin - Dr. Peter K: https://www.drpeterk.com/blog/tips-for-choosing-a-prenatal-vitamin
[33] Urinary Tract Infections During Pregnancy - AAFP: https://www.aafp.org/pubs/afp/issues/2000/0201/p713.html
[34] Urinary Tract Infections in Pregnancy - Medscape Reference: https://emedicine.medscape.com/article/452604-overview
[35] Scanwell Health's FDA-Cleared, Smartphone-Enabled UTI Test: https://www.globenewswire.com/news-release/2020/12/09/2142405/0/en/Scanwell-Health-s-FDA-Cleared-Smartphone-Enabled-UTI-Test-Kit-Now-Available-at-Amazon-Diagnose-and-Treat-in-Two-Minutes-From-the-Safety-of-Your-Home.html
[36] FDA Approves Smartphone-based Urinalysis Test Kit for At-Home Use: https://www.darkdaily.com/2019/03/06/fda-approves-smartphone-based-urinalysis-test-kit-for-at-home-use-that-matches-quality-of-clinical-laboratory-tests/
