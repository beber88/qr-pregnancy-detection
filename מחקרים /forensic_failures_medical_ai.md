# Forensic Briefing: Recurring Failures in Medical AI and Diagnostics

A forensic briefing focused on failures that recur in medical AI and diagnostics, with particular attention to what is dangerous for a product aimed at detecting pregnancy from urine photographs. The direct conclusion: your project will fail if it relies on "impressive" accuracy on clean data, on marketing headlines, or on the assumption that photo-only urine contains a strong enough biological signal. [1][2][3]

---

## 1. Central Failure Cases

### Theranos

Theranos was not just a "fraud" but a deep technical failure: the system claimed to perform dozens of tests from tiny blood samples but suffered from severe signal-to-noise problems, volumes too small for many assays, unstable dilution and sampling, and method validation that was not shown to be consistent against gold standards. In 2015 FDA determined that the nanotainer was a Class II device, not Class I as the company claimed, and CMS imposed severe sanctions, including revoking the CLIA certificate and restrictions on lab ownership; in parallel, SEC and criminal investigations were opened. [4][5][6][7]

**Lesson for your project:** if the biological measurement is weak or indirect, you cannot "cover" it with UX and narrative. Regulators and forensic auditors will look for proof that the system actually measures the biological target, not a misleading proxy. [5][8]

### uBiome

uBiome collapsed due to a combination of billing fraud, tests that were not validated as required, and the use of partial/misleading reports to physicians and insurers to justify reimbursement for unnecessary tests. The federal indictment described practices such as "upgrades" on archived samples, writing misleading notes, and changing service dates to conceal the business model. [9][10][11]

**Lesson:** even if the product works technically, if the reimbursement chain or business workflow is built on exaggerated benefit or on an unproven clinical claim, the failure can be financial and criminal, not just medical. [11][9]

### IBM Watson Health

Watson for Oncology failed because it was trained on synthetic cases and a limited number of experts, rather than on real-world, multi-institutional outcomes; internal documents described inaccurate and even unsafe recommendations. The public saw "strong AI," but in practice the system was riding on curated knowledge rather than generalizable clinical decision-making. [12][13]

**Lesson:** if you train on a narrow set of "pretty" examples, you get the illusion of performance. The moment the product moves to a real home, real lighting, real users, and real variability, accuracy collapses. [14][15][12]

### Babylon Health

Babylon was presented to the public as a fast and effective symptom checker, but a systematic review of symptom checkers found that primary diagnosis accuracy was very low across most systems, and only a portion of the tools provided safe and useful triage. Babylon also drew criticism for under-triage and misclassification in dangerous cases. [16][17][18]

**Lesson:** a digital triage system can look convincing on vignettes, but when the real situation includes vague symptoms, missing context, and human variability, performance disappears. [17][14]

### Scanadu

Scanadu promised a consumer "tricorder," raised hype, but struggled to meet regulatory and clinical requirements for a consumer product that measures medical parameters. Scout was discontinued, and the company informed users that the investigational device would be shut down with the end of the study; this reflects a product whose go-to-market relied on a study that did not translate into an approved, sustainable product. [19][20]

**Lesson:** if the business model depends on "a little more time until approval," and you sell a consumer experience before there is truly a clearance path, you build trust debt that is hard to repay. [14][19]

### Tricorder XPRIZE

The XPRIZE generated imagination and interesting prototypes, but also exposed the gap between demo engineering and a regulated healthcare product. In many entries, the problem was not only sensors but complete measurement: repeatability, user variability, data quality, and the ability to prove clinical utility outside the competition. [19][14]

**Lesson:** a competition can prove feasibility, not viability. For a pregnancy product via camera of urine, this is critical: a pretty prototype does not equal a predicate, and does not equal clinical validation. [8][14]

### 23andMe Health Claims

23andMe received a warning letter in 2013 after making broad health claims without adequate analytical and clinical validity. FDA required a halt to marketing of the health reports pending marketing authorization; the company subsequently rebuilt a regulatory path with narrower claims and more organized evidence. [21][22][23]

**Lesson:** once a medical claim crosses the evidence, FDA treats it as a medical device rather than consumer information. This is directly relevant to AI pregnancy detection: "just an app" will not hold if the output is a diagnosis. [23][24][21]

---

## 2. Accuracy Failures

The recurring pattern across all of medical AI is "works on curated dataset, fails in the wild." This happens when there is data leakage, spectrum bias, site bias, or when the model learns metadata and artifacts rather than a clinical signal. Medical AI studies show again and again that removing clearly healthy patients or mixing train/test data at image level rather than patient level produces overestimated accuracy. [2][3][25][26]

Therefore, if you build a pregnancy detector from urine photos and test it only on well-lit lab samples, you will get tempting numbers that do not survive field conditions. [3][15][2]

---

## 3. Regulatory Enforcement

FDA and other regulators tend to act in three patterns: marketing without clearance, claims beyond the cleared intended use, and failures in QMS/complaint handling/validation. 2024 warning letter reports show that the common types include devices without appropriate marketing submission, claims beyond cleared use, and CAPA/complaint failures. [27][28]

In digital health, enforcement does not have to be dramatic to kill a company: a single warning letter can shut down a distribution channel, freeze investments, and cause partners to withdraw. [28][27]

---

## 4. Ethical and Legal Failures in Pregnancy

A false negative in pregnancy is not just inconvenient; in jurisdictions with time limits on abortion, it may shift the medical and legal decision window. A false positive can cause psychological distress, relationship harm, unnecessary medical decisions, and reliance on an unverified result. [8][14]

For a pregnancy product, liability can attach quickly: if a user acts on an incorrect result, a lawsuit will rest on negligence, misrepresentation, failure to warn, design defect, and lack of human factors safeguards. [8]

**Lesson:** there is no room for "best effort" messaging; gating, disclaimers, and a confirmatory workflow are required. [24][8]

---

## 5. Bias Failures

Pulse oximetry showed that even devices with decades of use can systematically misread in darker skin, prompting FDA scrutiny and draft guidance. This teaches that optical systems tend to drift with pigmentation, reflectance, and environmental effects, even when the physics appear simple. [29][30][31][32]

In AI dermatology too, performance gaps across skin tone appear when the data is unrepresentative and the model learns shortcuts. [33][1]

For urine, the analogy is not "skin tone" but a combination of bottle color, toilet background, lighting, hydration state, vitamins, and medications. If you do not collect data across these conditions, your system will fail the same way pulse oximeters failed when the underlying population reality shifted. [34][1][2]

---

## 6. Data Integrity Failures

Data leakage, especially patient-level leakage, routinely inflates medical AI metrics. Spectrum bias occurs when you train or validate on extreme positives and extreme negatives, then deploy into the messy middle where equivocal cases dominate. [26][2][3]

Publication problems are also real: medical literature has a substantial retraction burden due to fraud, data problems, and peer-review defects, which means "published" is not synonymous with "trustworthy." [35][36]

For your project, this means: split by person, by sample episode, and by site; never by image alone; never tune on the validation set; and never use "obvious" positives/negatives only. [37][2]

---

## 7. Commercial Failures Despite Technical Success

Many products work technically but do not find a market. Scanadu is an example: consumer enthusiasm was real, but regulatory closure and product deactivation killed momentum. Babylon had market presence but trust erosion, lawsuit risk, and mixed clinical confidence created commercial fragility. [18][16][19]

uBiome also teaches that revenue built on flawed reimbursement is not durable revenue. When payer trust collapses, the business model collapses with it. [9][11]

For AI pregnancy detection, the consumer-friendly market may look huge, but without reimbursement, liability protection, and credible clinical proof, it can become a low-margin, high-risk app with poor retention. [24][8]

---

## 8. What a Skeptical FDA Reviewer, Short-Seller, and Plaintiff's Attorney Will Build

### FDA Reviewer

Will ask: what exactly is the biological measurement? Is this diagnosis or wellness? Is there a predicate? Is the dataset representative of real use? Does performance hold across phones, lighting, and demographics? Is there human factors evidence, CAPA, complaint handling, a postmarket plan, and a locked model version? [38][28][24]

If the answers are weak, they will see a product with intended-use overreach.

### Short-Seller

Will look for: inflated claims, cherry-picked metrics, no external validation, undisclosed adverse events, weak unit economics, and hidden dependency on one device model or one capture environment. They will also look for whether the company is calling a diagnostic a wellness feature to dodge regulation. [27][28][14]

For pregnancy detection, the easiest attack is: "their model is just learning dehydration, vitamins, and phone artifacts, not pregnancy."

### Plaintiff's Attorney

Will build a case around foreseeable harm: missed pregnancy, delayed prenatal care, missed ectopic pregnancy workup, false reassurance, or unnecessary distress from false positives. They will subpoena training data, misclassification rates, complaints, model version history, and internal emails about limitations. [8]

If the product is marketed DTC, they will also focus on misleading consumer advertising and insufficient warnings. [21][23]

---

## 9. Top 20 Specific Risks for AI Pregnancy Detection

| Rank | Risk | Severity | Likelihood | Why it matters | Mitigation |
|---:|---|---|---|---|---|
| 1 | No real biological signal in native urine photo | Critical | High | Core concept may be invalid | Use chemistry-based hCG assay instead of urine appearance alone |
| 2 | False negatives near implantation/very early pregnancy | Critical | High | Missed time-sensitive care | Require confirmatory testing and conservative claims |
| 3 | False positives from vitamins/diet/drugs | High | High | Consumer distress and liability | Explicit confounder screening and limited claims |
| 4 | Spectrum bias from curated data | High | High | Inflated validation metrics | Recruit full-spectrum, multi-site cohort |
| 5 | Patient/image-level leakage | High | High | Artificially high accuracy | Split by participant and episode only |
| 6 | Device and ISP variation | High | High | Model breaks on new phones | Locked phone matrix, calibration, OOD rejection |
| 7 | Lighting and glare shift | High | High | Optical artifacts dominate signal | Capture protocol, reference card, quality gate |
| 8 | Regulatory misclassification of software | High | Medium | Wrong pathway, delayed clearance | Early regulatory strategy and intended-use lock |
| 9 | Overclaiming "pregnancy diagnosis" | Critical | Medium | Enforcement, litigation | Use narrow claims and confirmatory language |
| 10 | Inadequate clinical truth standard | High | Medium | Validation not acceptable | Serum beta-hCG with ultrasound follow-up |
| 11 | Bias across demographics | High | Medium | Equity and performance gaps | Stratified sampling and subgroup dashboards |
| 12 | Poor model calibration | Medium | High | Confidence score misleading | Brier score, calibration curves, threshold validation |
| 13 | Model drift after launch | High | Medium | Real-world performance erosion | Postmarket monitoring and change control |
| 14 | Weak usability / user error | High | High | Bad photos, bad outputs | Human factors testing and guided capture |
| 15 | Non-evaluable rate too high | Medium | High | Real-world usefulness low | Improve guidance and repeat-capture logic |
| 16 | Privacy/security breach | High | Medium | Trust and regulatory issues | Encryption, minimization, access controls |
| 17 | Inadequate adverse-event handling | High | Medium | Harm escalates | Support, escalation, and referral pathways |
| 18 | Overfitting to menstrual timing metadata | Medium | Medium | Shortcuts instead of biology | Restrict features and use ablation tests |
| 19 | Business model dependent on optimism | High | Medium | Startup failure | Conservative claims and validated economics |
| 20 | Competitor or regulator reframing product as IVD | High | Medium | Pathway changes midstream | Plan from day one as regulated diagnostic |

---

## 10. Bottom Line for Your Product

If you build an AI pregnancy detector from urine photographs and tell yourself it is "just a camera app," you are following the same mental path that broke Theranos, 23andMe's early health claims, and multiple symptom-checking or AI triage startups. The safe path is to assume the biology is weak, the regulation is real, the validation bar is high, and the market will punish any gap between demo and deployment. [5][17][21][24]

The winning pattern is not "more AI." It is: tightly defined intended use, chemistry-backed signal, locked model, honest labeling, multi-site validation, and continuous postmarket surveillance. [39][38][24]

---

## Sources

[1] Reducing misdiagnosis in AI-driven medical diagnostics - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12615213/
[2] Spectrum bias in algorithms derived by artificial intelligence - PubMed: https://pubmed.ncbi.nlm.nih.gov/36713099/
[3] Spectrum bias in algorithms derived by artificial intelligence - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC9707965/
[4] Patient Advocacy Lies at Heart of FDA Agent's Theranos Case: https://www.fda.gov/about-fda/regulatory-news-stories-and-features/patient-advocacy-lies-heart-fda-agents-theranos-case
[5] How Theranos' faulty blood tests got to market - The Conversation: https://theconversation.com/how-theranos-faulty-blood-tests-got-to-market-and-what-that-shows-about-gaps-in-fda-regulation-168050
[6] Theranos - Wikipedia: https://en.wikipedia.org/wiki/Theranos
[7] FDA Releases Theranos Inspection Reports - Forbes: https://www.forbes.com/sites/sarahhedgecock/2015/10/27/fda-releases-theranos-inspection-reports/
[8] Trust and medical AI: the challenges we face and the expertise needed - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC7973477/
[9] uBiome Co-Founders Charged With Federal Securities, Health Care Fraud: https://www.justice.gov/usao-ndca/pr/ubiome-co-founders-charged-federal-securities-health-care-fraud-conspiracies
[10] SEC charges co-founders of uBiome with $60 million fraud: https://www.statnews.com/2021/03/18/ubiome-sec-fraud-charges/
[11] SEC Charges Co-Founders of San Francisco Biotech Company: https://www.sec.gov/newsroom/press-releases/2021-49
[12] IBM's Watson recommended 'unsafe and incorrect' cancer treatments: https://www.statnews.com/2018/07/25/ibm-watson-recommended-unsafe-incorrect-treatments/
[13] Watson Supercomputer Recommended Unsafe Treatments: https://ashpublications.org/ashclinicalnews/news/4026/Watson-Supercomputer-Recommended-Unsafe-Treatments
[14] Who's at Fault when AI Fails in Health Care? - Stanford HAI: https://hai.stanford.edu/news/whos-fault-when-ai-fails-health-care
[15] Artificial Intelligence and Diagnostic Errors - PSNet: https://psnet.ahrq.gov/perspective/artificial-intelligence-and-diagnostic-errors
[16] Case Study 1 Babylon Health (PDF): https://static.ie.edu/CGC/Case-Study-1-Babylon-Health.-IE-CGC.pdf
[17] The diagnostic and triage accuracy of digital and online symptom checkers (Nature): https://www.nature.com/articles/s41746-022-00667-w
[18] Digital health, peer-reviewed study reveals disparities in symptom assessment apps: https://about.ada.com/press/201216-peer-reviewed-study-reveals-disparities-in-symptom-assessment-apps/
[19] Scanadu to shut down support for its Scout device - TechCrunch: https://techcrunch.com/2016/12/13/fda-orders-scanadu-to-shut-down-support-for-its-scout-device-and-customers-are-mad/
[20] Scanadu - Wikipedia: https://en.wikipedia.org/wiki/Scanadu
[21] Reflections on the US FDA's Warning on Direct-to-Consumer - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC4330248/
[22] Frustrated U.S. FDA Issues Warning to 23andMe - Science: https://www.science.org/content/article/frustrated-us-fda-issues-warning-23andme
[23] 23andMe FDA warning letter (PDF - Audet Law): https://audetlaw.com/wp-content/uploads/23andme-class-action-fda-warning-letter.pdf
[24] Artificial Intelligence in Software as a Medical Device - FDA: https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-software-medical-device
[25] Data leakage in machine learning studies creep into meta-analytic evidence - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12602356/
[26] Effect of data leakage in brain MRI classification using 2D - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC8604922/
[27] FDA Oversight, Understanding the Regulation of Health AI Tools: https://bipartisanpolicy.org/issue-brief/fda-oversight-understanding-the-regulation-of-health-ai-tools/
[28] US FDA CDRH Warning Letters, A Review of 2024 - Emergo by UL: https://www.emergobyul.com/news/us-fda-cdrh-warning-letters-review-2024
[29] Racial Bias in Pulse Oximetry Measurement - PubMed: https://pubmed.ncbi.nlm.nih.gov/33326721/
[30] FDA Executive Summary Performance Evaluation of Pulse Oximeters (PDF): https://www.fda.gov/media/175828/download
[31] Pulse oximeters may misread oxygen levels in people of color - AP: https://apnews.com/article/oximeters-race-skin-blood-oxygen-fda-color-d5fde9b81251ac9d4e39c11264638909
[32] Pulse Oximeters - FDA: https://www.fda.gov/medical-devices/products-and-medical-procedures/pulse-oximeters
[33] Over-Detection of Melanoma-Suspect Lesions by a CE-Certified Device - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC9367531/
[34] Data encoding for healthcare data democratization and information leakage - Nature: https://www.nature.com/articles/s41467-024-45777-z
[35] Fifty Years of Retracted Medical Publications From 1975 to 2024 - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12669648/
[36] Why AI like ChatGPT Still Quotes Retracted Papers - Zendy: https://zendy.io/blog/why-ai-like-chatgpt-still-quotes-retracted-papers
[37] The Hidden Threat in AI Healthcare, Data Leakage in Medical Imaging - LinkedIn: https://www.linkedin.com/pulse/hidden-threat-ai-healthcare-data-leakage-medical-imaging-ahmed-i0tre
[38] Good Machine Learning Practice for Medical Device Development - FDA: https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles
[39] Guidance for OTC Human Chorionic Gonadotropin (hCG) 510(k)s - FDA: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/guidance-over-counter-otc-human-chorionic-gonadotropin-hcg-510ks-guidance-industry-and-fda
[40] Theranos Experience Exposes Weaknesses in FDA Regulatory (Wiley): https://accp1.onlinelibrary.wiley.com/doi/full/10.1002/cpdd.374
[41] Theranos Reddit thread on FDA approval: https://www.reddit.com/r/Theranos/comments/rbqvdd/with_no_fda_approval_how_did_she_test_so_many/
[42] Challenges Faced by Medical Device Startups Due to Regulatory - LinkedIn: https://www.linkedin.com/pulse/challenges-faced-medical-device-startups-due-regulatory-qrnef
[43] An FDA Overreaction to Theranos's Implosion Would Harm Patients - Scientific American: https://www.scientificamerican.com/article/an-fda-overreaction-to-theranoss-implosion-would-harm-patients/
[44] Clinicians Warned About Potential Weaknesses in Medical AI Tools: https://www.renalandurologynews.com/features/medical-ai-weaknesses/
[45] Case Study, Theranos and Elisabeth Holmes (PDF - UPF-BSM): https://www.bsm.upf.edu/documents/2024-case-study-elisabeth-holmes-theranos.pdf
[46] This Story Smells a Lot Like Theranos - MDDI: https://www.mddionline.com/regulatory-quality/we-ve-seen-this-one-before-it-doesn-t-end-well
[47] uBiome, Anatomy of an Alleged Fraud - LinkedIn: https://www.linkedin.com/pulse/ubiome-anatomy-alleged-fraud-jason-calacanis
[48] uBiome, how microbiome testing becomes fraud - Out-Of-Pocket: https://www.outofpocket.health/p/ubiome---how-microbiome-testing-becomes-fraud
[49] Pinnacle Labs of Tennessee warning letter - FDA: https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/pinnacle-labs-tennessee-llc-dba-pinnacle-biolabs-676367-04172024
[50] IBM Watson Oncology's AI Failures (LinkedIn post): https://www.linkedin.com/posts/rashmeetsangari_ai-lifesciences-processexcellence-activity-7419839450043641858-TiHT
[51] 23andMe Statement Regarding FDA Warning Letter: https://mediacenter.23andme.com/press-releases/fda-letter-2013/
[52] FDA Tells 23andMe To Stop Selling Popular Genetic Test - NPR: https://www.npr.org/sections/health-shots/2013/11/25/247198237/fda-tells-23andme-to-stop-selling-popular-genetic-test
[53] Racial Bias with Pulse Oximetry? - REBEL EM: https://rebelem.com/racial-bias-with-pulse-oximetry/
[54] FDA Issues Warning Letter to 23andMe Genomic Service - Avalere: https://advisory.avalerehealth.com/insights/fda-issues-warning-letter-to-23andme-genomic-service-other-ldts-on-the-radar
[55] Pulse oximeter study on accuracy on darker skin - STAT: https://www.statnews.com/2026/01/12/pulse-oximeter-study-accuracy-on-dark-skin/
[56] FDA Warning Letters for Medical Devices, Complete Guide 2025: https://www.complizen.ai/post/fda-warning-letters-for-medical-devices-complete-guide-2025
[57] 23andMe ordered to halt sales of DNA tests - Nature: https://www.nature.com/articles/nature.2013.14236
[58] Systematic reviews cited retracted articles, new study finds - STAT: https://www.statnews.com/2025/06/12/researchers-examine-scientific-rigor-of-systematic-reviews-new-ai-tool-may-help/
[59] FDA Proposes Updated Recommendations for Pulse Oximeters: https://www.fda.gov/news-events/press-announcements/fda-proposes-updated-recommendations-help-improve-performance-pulse-oximeters-across-skin-tones
[60] FDA urged to move faster to fix pulse oximeters - STAT: https://www.statnews.com/2024/02/02/fda-urged-to-move-faster-to-fix-pulse-oximeters-for-darker-skinned-patients/
[61] FDA proposed new guidelines on pulse oximeter (Facebook): https://www.facebook.com/yourrightscamp/posts/the-fda-proposed-new-guidelines-requiring-pulse-oximeter-manufacturers-to-gather/1172398714249042/
[62] FDA panel recommends new standards for pulse oximeters - MedTech Dive: https://www.medtechdive.com/news/fda-advisory-panel-pulse-oximeter-bias-recommendations/706575/
[63] 38 AI-enabled medical devices recalled 2020-2024 (LinkedIn): https://www.linkedin.com/posts/hadarfriedman-qaboost_38-ai-enabled-medical-devices-were-recalled-activity-7374160845813137408-j_O_
[64] Over 90% of recalled AI-enabled medical devices were from public companies - Healthcare Brew: https://www.healthcare-brew.com/stories/2025/09/03/recalled-ai-enabled-medical-devices-public-companies
[65] Comment to Docket FDA-2023-N-4976 Pulse Oximeters (PDF): https://www.citizen.org/wp-content/uploads/2718.pdf
[66] Regulatory Insights From 27 Years of AI/ML SaMD - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12274014/
[67] 2024 Warning Letters Health Fraud - FDA: https://www.fda.gov/consumers/health-fraud-scams/2024-warning-letters-health-fraud
[68] Early Recalls and Clinical Validation Gaps in Artificial Intelligence - JAMA: https://jamanetwork.com/journals/jama-health-forum/fullarticle/2837802
[69] Evaluating transparency in AI/ML model characteristics for FDA - Nature: https://www.nature.com/articles/s41746-025-02052-9
[70] A review on generative AI models for synthetic medical text, time - Nature: https://www.nature.com/articles/s41746-024-01409-w
[71] Guidelines and quality criteria for AI-based medical devices - Nature: https://www.nature.com/articles/s41746-021-00549-7
[72] When AI Knows Too Much, Safeguarding Sensitive Health Data - Springer: https://communities.springernature.com/posts/when-ai-knows-too-much-safeguarding-sensitive-health-data-becomes-critical
[73] Medical large language models are vulnerable to data-poisoning - Nature: https://www.nature.com/articles/s41591-024-03445-1
[74] Data Leakage in Deep Learning for Alzheimer's Disease Diagnosis - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12468286/
[75] Impact of spectrum bias on deep learning-based stroke MRI analysis - ScienceDirect: https://www.sciencedirect.com/science/article/pii/S0720048X25002475
[76] Academia loses its grip on digital health solutions - Nature: https://www.nature.com/articles/s41746-025-02168-y
[77] Retracted Deep Neural Networks for Medical Image Segmentation - Wiley: https://onlinelibrary.wiley.com/doi/10.1155/2022/9580991
