# Regulatory Roadmap: AI Vision Product for Pregnancy Detection from Smartphone Urine Photographs

A practical and **conservative** regulatory roadmap for an AI vision product that aims to detect pregnancy from smartphone photographs of urine. The central conclusion is that this is almost certainly a **Device + IVD/SaMD combination** if the claim is "pregnancy detection." In the US there is currently no reasonable pathway for a direct 510(k) for "AI pregnancy test from photograph" without changing the intended use or building a predicate very closely anchored to hCG home tests and a software reader.

---

## 1. Regulatory Classification

### United States: FDA

From FDA's perspective, a home hCG-based pregnancy test is a Class II IVD under 21 CFR 862.1155, and FDA guidance requires home hCG devices to file a 510(k) with sensitivity/precision/interference/stability evidence; the historical default cut-off for pregnancy tests is 25 mIU/mL, with newer products going down to 10 mIU/mL. [1][2][3]

If your product is "urine photograph + AI" that infers pregnancy **without** an hCG immunochemical strip, that is no longer the same intended use, and therefore does not sit comfortably on a home pregnancy test predicate. [2][1]

For the software layer itself, FDA treats AI/ML as SaMD/Software functions through the traditional regulatory pathways of 510(k), De Novo, or PMA, depending on risk level and similarity to predicate; FDA also indicates that adaptive models may require premarket review for material changes. [4]

On AI/ML specifically, FDA has published an AI/ML SaMD Action Plan, Good Machine Learning Practice principles, and a 2025 draft guidance on lifecycle management and marketing submission recommendations; these are especially relevant if you plan model updates or a PCCP. [5][4]

**Realistic classification assessment:**

- If the product is an **hCG strip reader** using a smartphone camera, it is likely Class II with a feasible 510(k). [1][2]
- If the product is a **vision-only pregnancy detector from urine image**, the likelihood of a sufficient predicate is low; De Novo is more likely if safety/efficacy can be demonstrated at all. [6][4]
- PMA is plausible only if the claim/risk is extraordinary, which does not appear likely here. [4]

### EU MDR 2017/745

Under EU MDR, software providing information for diagnostic decisions generally falls under Rule 11 and is usually classified at least Class IIa, and sometimes IIb if the decision could cause serious deterioration of health. [7][8]

If your product is intended to detect pregnancy for a clinical/therapeutic decision, it is almost certainly software with diagnostic purpose, hence Class IIa or higher, with full clinical evaluation, PMS, PMCF, and technical documentation. [8][9][7]

If the claim is direct IVD on a specimen, IVDR 2017/746 may also apply, and performance evaluation will be required under analytical performance, clinical performance, and scientific validity. [10][11]

### UK, Israel, Japan, Brazil

UK MHRA's approach is close to EU: software diagnostics are assessed by intended purpose and Rule 11-style logic, with emphasis on clinical risk, evidence, and the distinction between wellness and medical device. [7][8]

In Israel, AMAR typically aligns with similar pathways to EU/FDA for software/IVD, but such a product would require full regulation, not "app store only."

In Japan, PMDA, and in Brazil, ANVISA, software diagnostics are expected to be treated as regulated medical devices/IVDs, with requirements for quality system, clinical evidence, and local registration; in plain terms: not an easy path.

---

## 2. Predicate Analysis in the US

There are plenty of predicate devices for **home pregnancy tests**: FDA publishes many 510(k) documents for OTC hCG urine tests, including devices with a typical 25 mIU/mL cut-off, and sometimes 10 mIU/mL. [3][12][13][1]

There are also clearances for **digital pregnancy tests** and OTC hCG systems, but these still rely on the same hCG immunoassay chemistry and not on interpretation from a photograph of raw urine. [12][13][3]

Is there a predicate for "AI pregnancy test from photograph"? Currently there is no clear predicate describing **raw urine photography** as a primary detection method. The closest pathway is:

1. hCG home pregnancy test, then
2. smartphone reader as accessory/software to read the strip. [2][1][4]

If no suitable predicate exists, De Novo is the more sensible US path. De Novo will require demonstrating low-to-moderate risk, defining a special controls framework, and proving analytical and clinical performance against a quantitative serum or urine hCG reference. [6][4]

If you insist on "vision-only urine pregnancy detection," expect FDA to request exceptional evidence and possibly block the submission upfront if the intended use does not align with known clinical performance.

---

## 3. Required Standards

For QMS, ISO 13485 is the baseline in almost every major market, including FDA/QMSR direction, EU MDR, and global manufacturing expectations.
For software lifecycle, IEC 62304 is almost certainly required, and IEC 82304-1 is particularly relevant for standalone health software.
For risk management, ISO 14971 is a practical must; for usability, IEC 62366-1; for IVD performance studies, ISO 20916. [11][14][15][16]

On data, expect GDPR if you collect/process images in Europe, and HIPAA if operating with covered entities or PHI in the US.
If you store images of urine or pregnancy results, privacy by design and data minimization are not "nice to have" but operational requirements.

---

## 4. Required Clinical Evidence

### Analytical validation

For a product like this you will need to show:

- Precision/repeatability across phones, lighting conditions, and hCG levels.
- Limit of detection / cut-off performance.
- Interference testing: lighting, glare, compression, motion blur, urine color confounders.
- Stability of image capture and algorithm output. [13][12][1]

### Clinical validation

The reference standard should be **quantitative serum beta-hCG** or a well-validated urine hCG assay; in pregnancy detection contexts, FDA historically uses clinical positive/negative status plus hCG comparison. [1][2]

In practice, 510(k) studies for pregnancy tests use large numbers of samples from pregnant and nonpregnant subjects, with spiking studies around the cut-off, and sometimes 30+ samples around sensitivity claims. [17][1]

If you plan to claim "earlier detection than standard OTC tests," you will need to show this against a comparator device and/or serum confirmation, otherwise the claim will not hold.

### Minimum performance

For OTC pregnancy tests, historical practice relies on very high sensitivity/specificity near the claimed cut-off, typically around 25 mIU/mL and sometimes 10 mIU/mL. [3][1]

For an AI reader, the software cannot be weaker than the chemistry it reads; you must show that the algorithm does not degrade the device's effective sensitivity/specificity.

---

## 5. AI-Specific Expectations

FDA AI/ML expectations now revolve around lifecycle management, transparency, data quality, robustness, and change control. [5][4]

If you plan updates after deployment, you will need PCCP logic: what is allowed to change, which validation prefix/postfix applies, and how updates are released without triggering a new submission each time. [18][4]

For GMLP, the central principles are representative data, appropriate training/validation separation, human factors, monitoring for drift, and clear labeling of limitations. [19][5]

---

## 6. Labeling and Marketing

You cannot claim the product "diagnoses pregnancy" if it is actually wellness only, and you cannot substitute a reference hCG assay with an image-only claim without evidence.
If the product is clinician-directed, you may claim "aid in detection of pregnancy-related hCG strip results" only if you have a clear predicate and clinical validation.
In DTC, labeling must be conservative, with disclaimers about not replacing laboratory confirmation, timing relative to missed period, and factors that affect results. [2][4][1]

---

## 7. Cost and Timeline

Full regulatory pathway for a product like this, if it is genuinely novel:

- **IRB + study setup:** 2-4 months.
- **Analytical validation:** 3-6 months.
- **Clinical validation:** 6-12 months.
- **Submission preparation and review:** 6-12+ months for 510(k); De Novo typically longer.
- **Total:** approximately 12-24 months for a similar 510(k), and 18-30 months for a realistic De Novo.

On costs:

- **Study and site costs:** hundreds of thousands of dollars up to low millions, depending on the number of sites and sample size.
- **Regulatory + QMS + software documentation:** often several hundred thousand to over a million dollars.
- **For a De Novo with multiple phone models and AI controls:** a total budget of several million dollars is prudent.

---

## Gantt-style Phases

| Phase | Duration | Key deliverables |
|---|---:|---|
| Feasibility / intended use locking | 4-8 weeks | Intended use, claims, risk analysis, predicate search |
| Architecture and QMS setup | 8-12 weeks | ISO 13485, IEC 62304, ISO 14971, cybersecurity plan |
| Analytical validation | 8-16 weeks | Interference, precision, repeatability, robustness, cut-off studies |
| Pilot clinical study | 3-5 months | Concordance vs serum/IVD comparator |
| Pivotal clinical study | 4-8 months | Multi-site validation, subgroup analysis, consumer usability |
| Submission prep | 2-4 months | 510(k) or De Novo dossier, labeling, summaries |
| FDA review | 3-9+ months | Deficiency responses, interactive review, clearance/order |
| Postmarket monitoring | ongoing | Drift, complaints, CAPA, update governance |

---

## 8. Document Checklist

You will need:

- Intended use statement and claims matrix.
- Device description and architecture.
- Software requirements specification.
- Algorithm training/validation report.
- Data management plan.
- Risk management file.
- Usability engineering file.
- Clinical protocol and SAP.
- Analytical performance report.
- Cybersecurity file.
- Labeling, IFU, limitations, contraindications.
- Postmarket surveillance plan.
- PCCP if using updateable ML. [14][15][4][5]

---

## 9. Fastest Legal Path to First Revenue

The fastest legitimate route is **not** "pregnancy diagnosis from urine photos." It is:

1. Launch as **software reader for an already-cleared hCG pregnancy strip**;
2. Keep the claim narrow: read/interpret strip, reduce user error, provide timing and documentation;
3. Position DTC only if the device and claims fit the existing clearance or a minor modification pathway. [4][1][2]

That path minimizes novelty, leverages existing hCG predicates, and gets you to revenue faster.

---

## 10. Fastest Path to Full FDA Clearance

The fastest path to full, defensible clearance is:

1. Choose a **predetermined hCG immunoassay strip** as the core diagnostic component;
2. Make the smartphone AI the **reader/accessory**;
3. Run analytical comparison against predicate strips and serum beta-hCG;
4. Submit under **510(k)** if you can stay close enough to a predicate, otherwise De Novo. [12][3][1][4]

If the business insists on "vision-only from raw urine photo," the path is longer, riskier, and likely ends in De Novo or non-approval unless the claim is softened to a wellness or triage use.

---

## Sources

[1] Guidance for OTC Human Chorionic Gonadotropin (hCG) 510(k)s: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/guidance-over-counter-otc-human-chorionic-gonadotropin-hcg-510ks-guidance-industry-and-fda
[2] What Does Having a FDA Cleared Pregnancy Test Mean? (PDF): https://ctti-clinicaltrials.org/wp-content/uploads/2021/07/CTTI_Pregnancy_Testing_Meeting_FDA_Test_Johnson_Lyles.pdf
[3] 510(k) Number K251040 (PDF): https://www.accessdata.fda.gov/cdrh_docs/reviews/K251040.pdf
[4] Artificial Intelligence in Software as a Medical Device - FDA: https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-software-medical-device
[5] Good Machine Learning Practice for Medical Device Development: https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles
[6] FDA De Novo Pathway Explained, Complete 2025 Guide: https://www.complizen.ai/post/de-novo-fda-pathway-complete-guide
[7] EU MDR & AI Act Compliance for AI Medical Devices - IntuitionLabs: https://intuitionlabs.ai/articles/ai-medical-device-compliance-eu-mdr-ai-act
[8] How to Classify Software as a Medical Device Under the MDR: https://openregulatory.com/articles/mdcg-2021-24-examples-for-software-classification-of-software-as-a-medical-device-samd
[9] Do AI Medical Devices Need Clinical Data for CE Mark? - Hardian Health: https://www.hardianhealth.com/insights/ai-device-ce-mark-clinical-data
[10] The FDA & EU IVDR Regulatory Frameworks For IVD SaMD: https://www.medsyscon.com/en/blog-ivd-samd/
[11] IVDs, A Comparison of Requirements between the US and EU: https://blog.pqegroup.com/medical-device/ivds-a-comparison-of-requirements-between-the-us-and-eu
[12] REVIEW MEMORANDUM K102760 (PDF): https://www.accessdata.fda.gov/cdrh_docs/reviews/K102760.pdf
[13] 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION K040866 (PDF): https://www.accessdata.fda.gov/cdrh_docs/reviews/K040866.pdf
[14] AI Device Standards You Must Know, ISO 13485, 14971, 62304 - Hardian: https://www.hardianhealth.com/insights/regulatory-ai-medical-device-standards
[15] ISO 14971 and AI in Medical Device Risk Management - Censinet: https://www.censinet.com/perspectives/iso-14971-ai-medical-device-risk-management
[16] ISO 13485 for Software Companies - Momentum: https://www.themomentum.ai/blog/iso-13485-for-software-companies
[17] 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION K051963 (PDF): https://www.accessdata.fda.gov/cdrh_docs/reviews/K051963.pdf
[18] FDA's 2025 Draft Guidance on AI/ML SaMD Lifecycle: https://www.linkedin.com/pulse/fdas-2025-draft-guidance-aiml-samd-lifecycle-updated-prajapati-vyhbc
[19] What Is IMDRF? 2025 AI/ML & SaMD Guide (N88 GMLP + N81 Risk): https://www.complizen.ai/post/what-is-imdrf-ai-medical-device-guide-2025
[20] FDA Cleared an AI Ultrasound Tool (Facebook post): https://www.facebook.com/FDA/posts/the-fdas-ai-stance-in-actionthe-agency-just-cleared-an-ai-ultrasound-tool-that-e/1354991363324885/
[21] Radiological software system DEN250007 (PDF): https://www.accessdata.fda.gov/cdrh_docs/pdf25/DEN250007.pdf
[22] Smart Pregnancy: AI-Driven Approaches to Personalised Maternal Care - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12524951/
[23] Understanding FDA regulations for AI in SaMD - ICON plc: https://www.iconplc.com/insights/blog/2025/06/24/fda-regulations-ai-medical-devices
[24] AI-Driven Advances in Women's Health Diagnostics - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12691360/
[25] Policy for Device Software Functions and Mobile Medical Applications (PDF): https://www.fda.gov/media/80958/download
[26] Clinical data requirements for medical device CE marking - LinkedIn: https://www.linkedin.com/pulse/clinical-data-requirements-medical-device-ce-marking-aurahealthch-ecxxf
[27] Ultrasound AI receives FDA De Novo clearance for delivery date AI: https://www.eurekalert.org/news-releases/1118241
[28] Artificial Intelligence-Enabled Medical Devices - FDA: https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices
[29] Jack Shuang Hou's Post - LinkedIn: https://www.linkedin.com/posts/jack-shuang-hou-75314a2b3_wins-de-novo-activity-7434268444960776192-q8u2
[30] FDA Expectations for AI/ML Model Training in SaMD 2025 guide: https://rookqs.com/blog-rqs/fda-expectations-for-ai/ml-model-training-in-samd-2025-guide
[31] Are fertility tracking apps regulated as devices - Hardian Health: https://www.hardianhealth.com/insights/fertility-apps-medical-device-regulation
[32] The FDA AI/ML SaMD Framework, What Companies Need to Know - Berkley LS: https://www.berkleyls.com/blog/fda-aiml-samd-framework-what-companies-need-know-now
[33] Classification of software medical devices, MDR Guideline: https://quickbirdmedical.com/en/medical-device-class-software-app-mdr/
[34] Ultrasound AI Earns FDA De Novo Nod for Delivery Date AI Tech: https://www.mpo-mag.com/breaking-news/ultrasound-ai-earns-fda-de-novo-nod-for-delivery-date-ai-tech/
[35] FDA AI Guidance 2025, What Life Sciences Must Do Now - USDM: https://usdm.com/resources/blogs/fda-ai-guidance-2025-life-sciences-compliance
[36] 510(k) Premarket Notification K203246 - FDA: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=k203246
[37] 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION K050305 (PDF): https://www.accessdata.fda.gov/cdrh_docs/reviews/K050305.pdf
[38] 510(k) Number K240242 (PDF): https://www.accessdata.fda.gov/cdrh_docs/reviews/K240242.pdf
[39] K023944 (PDF): https://www.accessdata.fda.gov/cdrh_docs/pdf2/K023944.pdf
[40] K972748 (PDF): https://www.accessdata.fda.gov/cdrh_docs/pdf/K972748.pdf
[41] 510(k) SUBSTANTIAL EQUIVALENCE DETERMINATION K131236 (PDF): https://www.accessdata.fda.gov/cdrh_docs/reviews/K131236.pdf
[42] True Diagnostics K182328 (PDF): https://www.accessdata.fda.gov/cdrh_docs/pdf18/K182328.pdf
[43] How To Get a Pregnancy Test to Market in USA and Canada - dicentra: https://dicentra.com/blog/medical-device/how-to-get-a-pregnancy-test-to-market-in-the-united-states-and-canada
[44] REVIEW MEMORANDUM K081150 (PDF): https://www.accessdata.fda.gov/cdrh_docs/reviews/k081150.pdf
