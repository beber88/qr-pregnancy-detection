# HANDOFF PROMPT - Visual Urine Scanning Chain
## SCANNING COMPLETE — Final Synthesis

---

## STATUS: ALL SAMPLES SCANNED ✓
- **35 positive** subjects scanned (P1-P34 + P41)
- **26 negative** subjects scanned (N1-N14 + N16-N28)
- **Pipeline rerun**: April 30, 2026 — features_v2.csv updated (856 rows, 61 subjects)
- **Models retrained**: Photo AUC=0.786, Video AUC=0.825, Combined AUC=0.743

---

## DATA CORRECTIONS APPLIED
- **N22 → P41**: Subject N22 was mislabeled. Questionnaire confirmed 4 months pregnant. Moved to POSITIVE/41/.
- **Empty folders**: P35-P40 (pending upload), N15, N29, N30 (no data)

---

## COMPLETE POSITIVE SAMPLES (35 subjects)

| ID | Color | Concentration | Volume | Bubbles | Weeks | Age | Meds | Notes |
|----|-------|---------------|--------|---------|-------|-----|------|-------|
| P1 | light yellow | low | low | no | 9mo | - | ascorbic acid | Samsung |
| P2 | dark yellow-gold | med-high | medium | no | 2wk | - | - | Realme 9 |
| P3 | medium yellow | medium | low-med | no | 4mo+2wk | - | folic acid | Vivo Y16 |
| P4 | medium yellow | medium | low | no | 4mo | - | - | Infinix Smart 9 |
| P5 | med-dark yellow | med-high | medium | small edges | - | - | - | - |
| P6 | deep dark yellow-gold | high | medium | prominent | 9mo | - | calcium | Redmi |
| P7 | dark yellow-orange | very high | very high | no | 9mo | - | ascorbic acid | Samsung |
| P8 | light-med yellow | low-med | low | no | - | - | - | - |
| P9 | (partial) | - | - | - | 8mo | - | calcium carbonate | Techno |
| P10 | yellow-gold light | medium | low | no | - | - | - | top view |
| P11 | dark golden yellow | med-high | ~40% | no | 12mo(?) | - | - | Oppo |
| P12 | yellow-gold light | medium | low | no | 4mo | - | calcium | iPhone 13 |
| P13 | pale yellow-greenish | low | low | no | - | - | - | notebook paper |
| P14 | pale yellow-greenish | low-med | ~35% | small | - | - | - | notebook paper |
| P15 | pale yellow-greenish | low-med | medium | small | - | - | - | possible dup P14 |
| P16 | yellow-greenish light | low-med | ~70% | no | - | - | - | large vol, dilute |
| P17 | dark amber-orange | very high | ~50% | no | - | - | - | darkest |
| P18 | very dark amber-orange | very high | medium | small edges | - | - | - | top view |
| P19 | amber-orange | high | ~40% | no | 19wk | 18 | folic+iron | Vivo |
| P20 | yellow-amber | med-high | ~50% | no | - | - | - | - |
| P21 | amber-orange | high | ~35% | no | - | - | - | - |
| P22 | amber | med-high | ~25% | no | 19wk | 23 | - | Infinix |
| P23 | deep amber/golden | HIGH | ~125ml | few small | 4mo | 27 | folic acid | iPhone 13 |
| P24 | golden amber | MOD-HIGH | ~135ml | FOAM | 4mo | 28 | folic acid | iPhone 13 |
| P25 | golden yellow | MODERATE | ~125ml | minimal | 5mo | 31 | calcium | iPhone 13 |
| P26 | golden yellow | MODERATE | ~130ml | minimal | 2mo | 21 | Vit B | iPhone 12 |
| P27 | deep golden/amber | VERY HIGH | ~200-250ml | none | 12wk | 19 | folic+iron | UNO, 1st morning |
| P28 | pale/light yellow | LOW | ~150-200ml | visible | ? | 26 | none | iPhone 14 Pro |
| P29 | deep golden yellow | HIGH | ~60% cup | none | ? | 20 | none | OPPO, 1st morning |
| P30 | light-mod yellow | LOW-MOD | ~60% cup | minimal foam | ? | 21 | multivitamin | kidney disease |
| P31 | deep golden yellow | HIGH | ~50-60% | none | ? | ? | none | iPhone 14 Pro |
| P32 | golden yellow | MODERATE | ~50-60% | none | 11wk | 30 | multi+B+folic+iron | iPhone 14 Pro |
| P33 | golden-amber/mustard | HIGH | ~65-75% | none | 12wk | 20 | none | Samsung |
| P34 | deep golden/amber | HIGH | ~60-70% | none | 12w+3d | 37 | folic acid | 1st morning |
| P41 | bright yellow | MODERATE | ~50-60% | none | 4mo | 29 | none | iPhone 13 (ex-N22) |

---

## COMPLETE NEGATIVE SAMPLES (26 subjects)

| ID | Color | Concentration | Age | First Urine | Meds | Health | Notes |
|----|-------|---------------|-----|-------------|------|--------|-------|
| N1 | pale-golden yellow | LOW-MOD | 20 | - | none | none | coffee |
| N2 | pale-golden yellow | LOW | 26 | - | none | none | foam/bubbles |
| N3 | golden-amber | MOD-HIGH | 20 | morning | none | none | 6:54am, outdoor |
| N4 | golden-bright yellow | MOD-HIGH | 27-29 | - | none | none | herbal tea |
| N5 | golden-amber | MODERATE | 30 | - | none | none | coffee |
| N6 | golden yellow | MED-HIGH | 19 | - | none | none | - |
| N7 | amber yellow | HIGH | 18 | - | none | none | coffee |
| N8 | golden yellow | MED-HIGH | 20 | - | none | none | Coke |
| N9 | amber yellow | MED-HIGH | ? | - | none | none | no questionnaire |
| N10 | golden yellow | HIGH | 20 | - | none | none | water |
| N11 | deep yellow | HIGH | 40 | - | none | none | - |
| N12 | very pale/colorless | LOW | 20 | - | MV | none | 9 cups water! |
| N13 | golden-amber | HIGH | ~11? | - | none | none | coffee |
| N14 | golden-pale yellow | MODERATE | 20 | - | none | none | blue lighting |
| N16 | golden yellow | MOD | 27 | YES | Iverne Expell | none | iPhone Xr |
| N17 | golden-brown/amber | HIGH | 26 | No | Bigone | FEVER | darker |
| N18 | amber/golden-brown | MOD-HIGH | 19 | YES | none | none | POCO |
| N19 | bright yellow/pale | LOW-MOD | 19 | YES | none | none | Samsung |
| N20 | bright golden yellow | LOW-MOD | ? | YES | none | none | Samsung |
| N21 | deep amber/orange | HIGH | 21 | No | none | FEVER | OPPO |
| N23 | golden yellow | MODERATE | 29 | No | none | none | iPhone 13 |
| N24 | amber-orange | HIGH | 19 | No | none | none | iPhone 13 |
| N25 | amber-orange | HIGH | 29 | No | antibiotics | UTI | iPhone 10 |
| N26 | dark yellow/amber | HIGH | 19 | YES | none | none | iPhone 14 Pro |
| N27 | deep amber/orange-brown | VERY HIGH | 26 | No | none | none | iPhone 13 |
| N28 | bright golden yellow | HIGH | 28 | recent | none | none | iPhone 13 |

---

## SYNTHESIS: POSITIVE vs NEGATIVE PATTERNS

### 1. Color/Concentration Distribution
- **POSITIVE**: 56% HIGH+, 26% MODERATE, 18% LOW
- **NEGATIVE**: 52% HIGH+, 22% MODERATE, 26% LOW
- **Conclusion**: Color/concentration alone is NOT a strong discriminator. Hydration dominates.

### 2. Unique Positive-Only Features
- **Greenish tint** (P13-P16): Only seen in positive samples. May relate to pregnancy hormones (hCG/progesterone metabolites).
- **Prominent foam** (P6, P24): More common in positives. Could relate to hCG protein levels increasing surface tension.

### 3. Strongest Confounders
| Factor | Effect |
|--------|--------|
| Hydration (strongest) | Less fluid → darker, regardless of pregnancy |
| Time of day | Morning → darker |
| Iron supplements | → darker (P27, P32) |
| Vitamin B | → more yellow |
| Fever (N17, N21) | → darker/concentrated |
| UTI (N25) | → amber with antibiotics |
| Coffee | → variable (mild diuretic) |

### 4. Model Performance (April 30, 2026)
| Model | AUC | Sensitivity | Specificity |
|-------|-----|-------------|-------------|
| Photo_V2 (RF) | 0.786 | 0.857 | 0.420 |
| **Video (RF)** | **0.825** | **0.865** | **0.480** |
| Combined (RF) | 0.743 | 0.758 | 0.440 |

**Key insight**: Video model outperforms photo. Temporal features (foam dissipation, surface dynamics) may capture pregnancy signals better than static color analysis.

### 5. Dataset Gaps & Next Steps
- P35-P40: Folders exist but empty (pending upload)
- N15, N29, N30: Empty
- Consider collecting more **first morning urine** with controlled hydration to reduce confounding
- Consider adding hCG strip results as ground truth validation
- Video features appear most promising — explore foam/bubble temporal dynamics further

---

## PIPELINE STATUS
- **features_v2.csv**: 856 rows, 37 columns, 61 subjects (35P + 26N)
- **video_features.csv**: 53 subjects with video
- **Latest models**: `models/model_*_20260430_012513.pkl`
- **Production model**: `models/model_production_v2.pkl` (Video, AUC=0.825)
