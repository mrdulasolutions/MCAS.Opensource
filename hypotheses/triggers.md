# Trigger hypotheses

> ⚠️ **Not medical advice.** Research/hypothesis use only. See [docs/disclaimers.md](../docs/disclaimers.md).

Real-world MCAS triggers mapped to the pathways they act through and to
candidate counter-compounds. The dataset behind this doc is
[data/triggers/MCAS_Triggers_v1.csv](../data/triggers/MCAS_Triggers_v1.csv).

## The "histamine bucket" model

Most MCAS patients describe a cumulative-load pattern: each trigger adds to a
bucket; symptoms erupt when the bucket overflows. **A useful counter-strategy is
to (a) shrink the bucket** (maintenance compounds raise the threshold) **and
(b) drain it faster** (rescue compounds + DAO + Vit C accelerate histamine
metabolism).

## Trigger → pathway → counter-compound

### Foods

| Trigger | Pathway | Counter-strategy |
|---|---|---|
| High-histamine: aged cheese, wine, cured meats, fermented foods, leftovers | Direct histamine load + DAO insufficiency | Pre-meal **DAO** + **vitamin C** + flavonoid base. Plus the low-histamine diet trial. |
| Liberators: citrus, strawberry, tomato, chocolate, shellfish, walnut, banana | Direct release + IgE cross-react | **Quercetin + luteolin** stabilizer stack 30–60 min pre-meal. |
| Additives: MSG, sulfites, benzoates, dyes, vinegar | MRGPRX2 + sulfite-driven ROS | **NAC + sulforaphane** + flavonoids; eliminate during diagnosis. |

### Smells / chemicals

| Trigger | Pathway | Counter-strategy |
|---|---|---|
| Fragrances, perfumes, scented detergents, air fresheners, smoke | MRGPRX2 + olfactory substance P | **Resveratrol + quercetin + cromolyn** (the resveratrol-class MRGPRX2 antagonist hypothesis). Environmental avoidance is primary. |
| Pesticides, solvents, formaldehyde, gasoline | MRGPRX2 + Nrf2 suppression + xenobiotic | **Sulforaphane + NAC + silibinin** (Nrf2 / phase II detox upregulation). |

### Physical

| Trigger | Pathway | Counter-strategy |
|---|---|---|
| Heat / cold / sudden temp shifts | TRP channels + direct sensitization | **Ketotifen + cromolyn + flavonoids**. |
| Pressure / friction / vibration (dermatographism) | Mechanosensor channels | Stabilizer base + avoid tight clothing. |
| Exercise | Substance P + thermal stress | **Pre-dose luteolin + quercetin** + slow warm-up protocol. |
| UV / sunlight | ROS + direct mast cell | **EGCG + sulforaphane** (Nrf2) + sunscreen. |

### Stress / infection

| Trigger | Pathway | Counter-strategy |
|---|---|---|
| Acute emotional stress | CRH + substance P + autonomic | **Luteolin + LDN + magnesium**; vagal + breathwork. |
| Viral (long-COVID, EBV, HHV-6) | TLR + ACE2 + substance P | **Resveratrol + SFN + famotidine** (the long-COVID MCAS stack). |
| Bacterial / fungal / SIBO | LPS + TLR4 + dysbiosis | Treat underlying infection + **butyrate + curcumin + quercetin + baicalein** for gut. |

### Toxin / hormone / medication

| Trigger | Pathway | Counter-strategy |
|---|---|---|
| Mold / mycotoxins | Phase II + Nrf2 + AhR | Remediate environment + **SFN + NAC + α-lipoic** + bile-acid binders. |
| Heavy metals | GSH depletion + ROS | **NAC + α-lipoic + SFN + vit C**. |
| Menstrual cycle, perimenopause | Estrogen-driven activation | Cycle-aware stabilizer dosing + **DIM + quercetin**. |
| NSAIDs (intolerant subset) | COX shunt to leukotrienes | **Montelukast + flavonoid pre-medication** (NSAID-tolerant patients only, clinical supervision). |
| Opioids (morphine, codeine, tramadol) | Direct MRGPRX2 | **Avoid**; if unavoidable, MRGPRX2 antagonist stack + cromolyn pre-medication. |
| Iodinated contrast / gadolinium | MRGPRX2 + complement | **Cromolyn + quercetin + ketotifen + H1/H2** pre-medication protocol. |

## Hypotheses to test in the AI pipeline

1. **MRGPRX2 antagonist scaffold (covers smells + opioids + contrast + venom):**
   Seed REINVENT 4 with resveratrol; optimize for MRGPRX2 docking (UniProt
   Q96LB1) + selectivity over related MRGPR family.
2. **DAO-mimic small molecule (covers high-histamine foods):** Histamine
   degradation in the gut without the cold-chain hassle of enzyme supplements.
   Difficult target but worth a virtual screen against histamine-degrading
   chemistry.
3. **Sulfite detoxification stack:** AI-scored combination of SFN + NAC for
   sulfite-sensitive patients; QSAR safety + composite Nrf2 activation.

## Top AI-ranked candidates per trigger class

_To be filled in by `notebook 05_hypothesis_ranking.ipynb` — outputs per target
in `outputs/`_

## Contribute a trigger

If a trigger isn't in [the dataset](../data/triggers/MCAS_Triggers_v1.csv),
open a [trigger report issue](../.github/ISSUE_TEMPLATE/trigger_report.md).
Patient-reported triggers are gold. Include category, what happened, how long
after exposure, and any pattern you've noticed.
