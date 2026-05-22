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

> 🤖 **Auto-generated artifact.** Produced by `scripts/rank_hypotheses.py` on 2026-05-22 01:17 UTC from commit `5f27a40`. Inputs: `data/compounds/MCAS_Compound_Library_v1.csv`, `outputs/reinvent_generated.csv`, `outputs/docking_*.csv`, `outputs/warhead_scores.csv`, `outputs/qsar_predictions.csv`. Composite formula and weights documented in [EXP-005](../experiments/EXP-005-multi-objective-ranking.md). Recovery benchmark: [EXP-006](../experiments/EXP-006-known-actives-recovery.md).

_Higher composite = better hypothesis. Edit `scripts/rank_hypotheses.py` to change weights or category target mix; the next run will overwrite this table._

| # | Name | Composite | KEAP1 | MRGPRX2 | KIT | HRH1 | Warhead | hERG | AMES | BBB | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Fexofenadine | 0.540 | 0.11 | 0.13 | 0.17 | 1.00 | — | 0.90 | 0.17 | 0.12 | library |
| 2 | Cetirizine | 0.539 | 0.14 | 0.09 | 0.19 | 1.00 | — | 0.86 | 0.16 | 0.33 | library |
| 3 | Diphenhydramine | 0.534 | 0.18 | 0.10 | 0.13 | 1.00 | — | 0.98 | 0.10 | 1.00 | library |
| 4 | Hydroxyzine | 0.532 | 0.13 | 0.09 | 0.19 | 1.00 | — | 0.90 | 0.19 | 0.94 | library |
| 5 | Loratadine | 0.523 | 0.14 | 0.09 | 0.22 | 1.00 | — | 0.97 | 0.28 | 0.33 | library |
| 6 | Famotidine | 0.462 | 0.10 | 0.07 | 0.08 | 0.08 | — | 0.38 | 0.52 | 0.90 | library |
| 7 | Quercetin | 0.461 | 0.18 | 1.00 | 0.09 | 0.08 | — | 0.25 | 0.86 | 0.61 | library |
| 8 | Cromolyn sodium | 0.431 | 0.14 | 0.20 | 0.14 | 0.14 | — | 0.64 | 0.20 | 0.71 | library |
| 9 | Ketotifen | 0.414 | 0.09 | 0.09 | 0.17 | 0.25 | — | 0.76 | 0.26 | 0.91 | library |
| 10 | Ranitidine | 0.394 | 0.13 | 0.11 | 0.09 | 0.13 | — | 0.51 | 0.12 | 0.21 | library |


## Wet-lab validation

LAD2 cell β-hexosaminidase release after substance P (MRGPRX2 trigger) or
anti-IgE crosslink (FcεRI trigger), measured vs. cromolyn baseline. See
[docs/wet_lab_protocols.md](../docs/wet_lab_protocols.md).
