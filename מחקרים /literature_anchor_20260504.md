# Literature anchor — surfaced by Perplexity council session 2026-05-04

> Five peer-reviewed sources surfaced by Perplexity during the LLM Council
> session on the smartphone-urine pregnancy detection project. Each entry
> includes full metadata, the URL where the paper can be retrieved, the
> finding as Perplexity reported it, and how it modifies the project's
> methodology and risk assessment.
>
> **Note.** PMC and Nature are not on this sandbox's network allowlist,
> so the PDFs themselves were not auto-downloaded. To pull the full
> texts, open each URL in the browser (free public access for all five)
> and save the PDF into this folder under the suggested filename.

---

## 1. Bustam et al., 2023 — smartphone urine photo colorimetry for dehydration

| Field | Value |
|-------|-------|
| Title | Accuracy of smartphone camera urine photo colorimetry as indicators of dehydration |
| Authors | Bustam A. et al. |
| Year | 2023 |
| Journal | Digital Health (Sage) |
| URL | https://pmc.ncbi.nlm.nih.gov/articles/PMC10474791/ |
| Suggested filename | bustam_2023_smartphone_urine_dehydration.pdf |

**Finding (per Perplexity).** Smartphone capture of urine images inside a
customized photo box, under controlled lighting, can predict dehydration
status from RGB values with good diagnostic accuracy. Performance depends
strongly on illumination and device conditions.

**Relevance to our project.** Reinforces that uncontrolled "natural daylight"
protocols are a major noise source. Our Q3 falsification experiment must
adopt a lightbox-style standardized capture or risk mistaking lighting
variance for biological signal. Directly supports Phase B of the action plan
(noise-floor reduction) and Phase E (lightbox + color card kit for the next
data collection wave).

---

## 2. Ra et al., 2017 — point-of-care urinalysis under variable illumination

| Field | Value |
|-------|-------|
| Title | Smartphone-Based Point-of-Care Urinalysis Under Variable Illumination |
| Authors | Ra M. et al. |
| Year | 2017 |
| Journal | IEEE Journal of Translational Engineering in Health and Medicine |
| URL | https://pmc.ncbi.nlm.nih.gov/articles/PMC5764119/ |
| Suggested filename | ra_2017_smartphone_urinalysis_illumination.pdf |

**Finding (per Perplexity).** Smartphone analysis of urine test strips
achieves reliable results only when algorithms correct for variable
illumination and device-specific color responses, using reference regions
and calibration.

**Relevance to our project.** Strengthens the argument that phone and
lighting confounding is a real, nontrivial leakage path in our current
dataset. The Q3 experiment must either fix illumination (lightbox plus
calibration card) or explicitly model illumination as a nuisance factor.
This is the canonical citation for why the lightbox + color card approach
is not optional but standard practice.

---

## 3. Pohanka, 2024 — quantitative urine assay with smartphone camera

| Field | Value |
|-------|-------|
| Title | Urine Test Strip Quantitative Assay with a Smartphone Camera |
| Authors | Pohanka M. |
| Year | 2024 |
| Journal | International Journal of Analytical Chemistry |
| URL | https://pmc.ncbi.nlm.nih.gov/articles/PMC10963100/ |
| Suggested filename | pohanka_2024_urine_strip_smartphone_quantitative.pdf |

**Finding (per Perplexity).** Smartphone cameras can quantitatively read
urine test-strip analytes (glucose, albumin) with low limits of detection
when RGB channels are analyzed under controlled conditions.

**Relevance to our project.** Confirms smartphones can support quantitative
urinalysis, but only when the signal comes from designed colorimetric
chemistry (test strips), not bulk urine appearance. Our pregnancy task is
inherently harder and should be evaluated with stricter skepticism.
Strengthens the case for a confound-only baseline (Phase A2) before any
modeling claim.

---

## 4. Kim, 2024 — AI for mobile-phone urine test reading

| Field | Value |
|-------|-------|
| Title | Artificial Intelligence in Diagnostics: Enhancing Urine Test Accuracy Using a Mobile Phone-Based Reading System |
| Authors | Kim H. |
| Year | 2024 |
| Journal | Annals of Laboratory Medicine |
| URL | https://pmc.ncbi.nlm.nih.gov/articles/PMC11788702/ |
| Suggested filename | kim_2024_ai_mobile_phone_urine_reading.pdf |

**Finding (per Perplexity).** AI models on smartphone-captured urine strip
images can improve standardization and accuracy across settings, but extensive
validation and device-robust calibration are required.

**Relevance to our project.** Direct precedent for the validation framework
we proposed in Q5 (multi-device validation, calibration assessment, sub-group
reporting). Useful as a benchmark when we eventually publish: the bar this
paper sets is the bar we will be compared to.

---

## 5. Prabhakar et al., 2022 — early pregnancy detection in buffalo urine via NMR metabolomics

| Field | Value |
|-------|-------|
| Title | Exploration of urinary metabolite dynamicity for early detection of pregnancy in Murrah buffaloes |
| Authors | Prabhakar S. et al. |
| Year | 2022 |
| Journal | Scientific Reports (Nature) |
| URL | https://www.nature.com/articles/s41598-022-20298-1 |
| Suggested filename | prabhakar_2022_buffalo_urine_metabolomics_pregnancy.pdf |

**Finding (per Perplexity).** 1H-NMR metabolomics on urine from Murrah
buffaloes identified urinary metabolite signatures that distinguish pregnant
from non-pregnant animals, with combined biomarker AUC around 0.8 for early
pregnancy detection.

**Relevance to our project.** This is the most consequential single citation
in the set. With direct molecular access via NMR, AUC tops out near 0.8 in
a different but related species. Our 0.95 target from bulk RGB smartphone
photography is therefore biologically aspirational and should be treated
as the hypothesis under attack, not the fixed milestone. This single number
re-anchors realistic expectations for the project.

**Project-level implication.** The action plan target should be reframed
from "AUC 0.95 internal" to "external sensitivity at specificity 0.95 >= 0.70".
The latter is harder, more honest, and aligned with what the literature
suggests is even physically achievable.

---

## How to fold these into the project

1. Read papers 1, 2, and 5 first. They directly affect our protocol and
   target-setting decisions.
2. Paper 5 (the buffalo NMR study) should be cited explicitly in any
   internal slide where we still use 0.95 as the target. It is the
   biological ceiling argument.
3. Update urine_appearance_atlas_cv.md and
   discovery_research_findings_synthesis.md with the lightbox / color
   card prior-art evidence from papers 1 and 2.
4. When the Gemini and ChatGPT council responses arrive, append any
   *new* citations they surface to this file under additional sections.

---

## How to download the PDFs

Open each URL in your browser. All five sources are free public access
(PMC and Nature). Save each to this folder under the suggested filename.
Then come back to the council session and the action plan with the actual
papers in hand.

---

# Additional citations from ChatGPT (GPT-5) - 2026-05-04

## 6. Noor Azhar et al., 2023 - color card calibration for smartphone urinalysis

| Field | Value |
|-------|-------|
| Title | Improving the reliability of smartphone-based urine colorimetry using a colour card calibration method |
| Authors | Noor Azhar A.M. et al. |
| Year | 2023 |
| Journal | Digital Health |
| URL | https://ai.jmir.org/2023/1/e49023/pdf |
| Suggested filename | noor_azhar_2023_color_card_calibration_smartphone.pdf |

**Finding (per ChatGPT).** A small color card placed in the same frame as the urine
sample materially improves both inter-phone agreement and intra-phone agreement.
For some color channels the resulting ICC is very high.

**Relevance.** Direct evidence that the color-card move (Phase B in our action plan)
is not optional and not a marginal nice-to-have. It is the single move that
demonstrably collapses phone-model variance to manageable levels.

---

## 7. Flaucher et al., 2022 - smartphone urinalysis for at-home prenatal care

| Field | Value |
|-------|-------|
| Title | Smartphone-Based Colorimetric Analysis of Urine Test Strips for At-Home Prenatal Care |
| Authors | Flaucher M. et al. |
| Year | 2022 |
| Journal | IEEE Journal of Translational Engineering in Health and Medicine |
| URL | https://www.researchgate.net/publication/360954306_Smartphone-Based_Colorimetric_Analysis_of_Urine_Test_Strips_for_At-Home_Prenatal_Care |
| Suggested filename | flaucher_2022_smartphone_urinalysis_prenatal.pdf |

**Finding (per ChatGPT).** At-home smartphone urinalysis works when there is a
reagent strip that creates a strong colorimetric target plus dedicated processing.
The performance comes from designed chemistry, not from raw urine appearance.

**Relevance.** This is the single most important paper for our strategic question.
It establishes that successful smartphone urine CV in the prenatal-care context
exists, but always relies on reagent strips. There is no published precedent for
detecting pregnancy from raw urine appearance alone via smartphone.

---

## 8. Shen et al., 2025 - longitudinal urine metabolomics for gestational age

| Field | Value |
|-------|-------|
| Title | Longitudinal urine metabolic profiling and gestational age prediction in human pregnancy |
| Authors | Shen X. et al. |
| Year | 2025 |
| Journal | Briefings in Bioinformatics |
| URL | https://academic.oup.com/bib/article/26/1/bbaf059/8016252 |
| Suggested filename | shen_2025_longitudinal_urine_metabolomics_gestational_age.pdf |

**Finding (per ChatGPT).** LC-MS untargeted metabolomics on 346 urine samples shows
that urinary metabolites carry rich information about pregnancy progression and
can predict gestational age.

**Relevance.** Confirms that there IS a real molecular pregnancy signal in urine,
which is consistent with the existence claim. But the signal is at LC-MS resolution,
not at smartphone-RGB resolution. This is the bridge between "urine biology contains
pregnancy information" and "we cannot necessarily see it with a phone camera."

---

## 9. Zhang et al., 2023 - urine metabolomics for preeclampsia

| Field | Value |
|-------|-------|
| Title | Development of a Urine Metabolomics Biomarker-Based Prediction Model for Preeclampsia during Early Pregnancy |
| Authors | Zhang Y. et al. |
| Year | 2023 |
| Journal | Metabolites |
| URL | https://www.mdpi.com/2218-1989/13/6/715/notes |
| Suggested filename | zhang_2023_urine_metabolomics_preeclampsia.pdf |

**Finding (per ChatGPT).** A urine-metabolomics-based prediction model can identify
preeclampsia risk already in early pregnancy.

**Relevance.** Adjacent finding. Strengthens the broader claim that urine carries
pregnancy-state information at molecular level. Does not directly address our
visible-light task but supports the molecular-signal reality.

---

# Additional citations from Gemini Hebrew research review - 2026-05-04

Gemini did not produce a numbered citation list in the same format, but its review
surfaced these biomedical references that should be tracked:

## 10. Stanford gestational dating study (XGBoost on 6 metabolites)

**What Gemini reported.** A Stanford study applied untargeted LC-MS/MS metabolomics,
identified 37 significantly correlated metabolites, and reduced to a panel of 6
critical metabolites: DHEA-S, alpha-lactose, estriol-3-glucuronide, acetylcholine,
L-carnitine, hydroxyhexanoyl-carnitine. XGBoost achieved Pearson R=0.95 in California
cohort and R=0.79 in Alabama validation cohort. Estimated gestational age within +/-1
week in 40% of T2/T3 cases.

**Relevance.** This is the strongest published precedent for "predict pregnancy
information from urine biology." But it uses LC-MS/MS, not smartphone images.
The R=0.95 number sometimes shown in our internal slides as a target needs to be
qualified: that R=0.95 is from molecular metabolomics, not from photos.

## 11. Hexadecanal volatilomics for preeclampsia

**What Gemini reported.** Untargeted volatilomics found hexadecanal (a lipid-peroxidation
aldehyde) as a statistically significant biomarker for PE. Consistent with prior
evidence on lipid-derived aldehydes for placental dysfunction.

**Relevance.** Confirms multi-biomarker reality of pregnancy-related urine signal.
Not directly actionable for our visible-light task.

## 12. KIM-1 and MCP-1 for early kidney injury in preeclampsia

**What Gemini reported.** KIM-1 (Kidney Injury Molecule-1) is upregulated in damaged
tubular epithelium and changes already after week 20 in PE-prone women. MCP-1 is
a inflammatory mediator in PE. Combined urine PE-prediction meta-analysis AUC ~0.93.

**Relevance.** Same as above. Establishes that urine has rich PE signal, all at
the molecular/protein level.

## 13. CIE Lab* turbidity threshold

**What Gemini reported.** L*<89.165 separates clear vs turbid urine with AUC 0.984,
accuracy 96%. Strong inverse correlation between turbidity and L* lightness.

**Relevance.** Directly applicable. We should add CIE Lab* L* as an explicit
turbidity feature to our feature stack and check whether it discriminates pregnant
vs non-pregnant.

## 14. HSV vs RGB for color analysis robustness

**What Gemini reported.** Hue (in HSV space) is more robust than RGB to shadows
and lighting variation. Multiple smartphone-urinalysis systems use HSV for this
reason.

**Relevance.** Direct feature engineering recommendation. Convert all our color
feature computations from RGB to HSV (or include both) and let the ablation tell
us which is stronger.

## 15. YOLOv8 + SimAM attention for strip detection

**What Gemini reported.** Real-time strip detection benefits from YOLO-family
detectors plus SimAM attention to suppress background and emphasize reagent pads.

**Relevance.** Applicable if we ever pivot to a strip-based system. Not directly
relevant to current cup-based pipeline.

## 16. FDA SaMD framework + Healthy.io 510(k) precedent

**What Gemini reported.** Software as a Medical Device (SaMD) is the FDA category
for our type of product. Risk classes I-IV. Critical precedent: 2013 FDA warning
to Biosense (uChek) ruled that a smartphone reading reagent strips IS a medical
device requiring 510(k). Healthy.io subsequently obtained 510(k) clearance by
demonstrating substantial equivalence to dedicated lab readers (e.g., ACON Mission
U500), using physical color calibration cards to control phone illumination.

**Relevance.** Critical regulatory pathway intelligence for any future product
launch. The Healthy.io precedent shows the path: demonstrate substantial
equivalence to a cleared device + use physical calibration. We should fold this
into the regulatory roadmap document.

## 17. DataSAIL and nestedcv R packages

**What Gemini reported.** Python and R packages built specifically for preventing
data leakage and running nested CV in biomedical data: DataSAIL (Python) and
nestedcv (R/CRAN).

**Relevance.** Implementation references. Worth checking nestedcv against our
current scikit-learn pipeline for any anti-leakage tricks we might be missing.

