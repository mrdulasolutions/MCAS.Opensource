# Rescue hypotheses

> ⚠️ **Not medical advice.** Research/hypothesis use only. See [docs/disclaimers.md](../docs/disclaimers.md).

**Goal:** acute mediator blockade — stop a flare in progress by either antagonizing
mediator receptors (H1/H2/CysLT1) or halting further degranulation (mast cell
stabilizers + Ca²⁺ influx blockers).

Rescue compounds must work fast (minutes to hours), have a wide safety window at
acute doses, and ideally hit multiple downstream nodes so that single-pathway
escape is harder.

## Baseline (clinical / approved)

| Compound | Class | Primary target | Rationale |
|---|---|---|---|
| [Cetirizine](../data/compounds/MCAS_Compound_Library_v1.csv) | H1 antagonist (2nd-gen) | HRH1 | First-line; often 2-4× standard dose in MCAS per consensus. |
| Loratadine / Fexofenadine | H1 antagonist (2nd-gen) | HRH1 | Non-sedating alternatives. |
| Hydroxyzine / Diphenhydramine | H1 antagonist (1st-gen) | HRH1 | Sedating; useful for neuro symptoms + sleep. |
| Famotidine | H2 antagonist | HRH2 | Standard add-on; GI + systemic histamine. |
| Cromolyn sodium (oral) | Mast cell stabilizer | Ca²⁺ / membrane | GI MCAS; poorly systemic. |
| Ketotifen | Dual H1 + stabilizer | HRH1 + membrane | Off-label US; widely used. |

## Natural / non-controlled rescue

| Compound | Class | Hypothesis |
|---|---|---|
| **Quercetin** | Flavonoid stabilizer | Inhibits PKC, Ca²⁺ influx, histamine + tryptase + cytokines. **Outperforms cromolyn** in human mast cell assays for several readouts. Pair with vit C for synergistic histamine degradation. |
| Luteolin | Flavonoid stabilizer | Similar mechanism, slightly stronger on Ca²⁺/PKC, BBB-crossing → better for neuro flares. |
| Vitamin C | Antioxidant + DAO cofactor | Accelerates histamine degradation; useful adjunct. |
| DAO enzyme | Histamine degradation in gut | Pre-meal supplementation; useful in histamine-intolerance subset. |
| Stinging nettle | Multi-target herbal | Natural H1 antagonism + COX/LOX inhibition. |
| Bromelain | Pineapple protease | Anti-inflammatory adjunct. |

## Hypotheses to test in the AI pipeline

1. **Multi-target flavonoid analog (rescue):** Use REINVENT 4 (notebook 03) seeded
   on **quercetin** to generate analogs with improved oral bioavailability and
   metabolic stability, while preserving the catechol pharmacophore that drives
   PKC / Ca²⁺ inhibition. Filter through QSAR (notebook 02) for low hERG / AMES.
2. **Cromolyn-class scaffold expansion:** Seed REINVENT on cromolyn; explore
   chromone dimers with better systemic absorption (cromolyn's flaw is poor
   bioavailability — a rescue cromolyn that survives first-pass would be huge).
3. **Combo dosing protocol:** AI-predicted synergy stack of cetirizine +
   famotidine + quercetin + vitamin C as a "default rescue kit" — quantify
   composite QSAR score per regimen.

## Top AI-ranked candidates

_To be filled in by `notebook 05_hypothesis_ranking.ipynb` — output: `outputs/ranked_rescue.csv`_

## Wet-lab validation

LAD2 cell β-hexosaminidase release after substance P (MRGPRX2 trigger) or
anti-IgE crosslink (FcεRI trigger), measured vs. cromolyn baseline. See
[docs/wet_lab_protocols.md](../docs/wet_lab_protocols.md).
