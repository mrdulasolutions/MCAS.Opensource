# Maintenance hypotheses

> ⚠️ **Not medical advice.** Research/hypothesis use only. See [docs/disclaimers.md](../docs/disclaimers.md).

**Goal:** daily stabilization. Raise the degranulation threshold, reduce
background mediator load, attenuate downstream inflammation, and keep the
"histamine bucket" from overflowing. Maintenance compounds must be safe for
chronic dosing (months → years) and ideally affect multiple complementary nodes
so that mast cell escape via any single pathway is dampened.

## Baseline (clinical / approved)

| Compound | Class | Primary target | Rationale |
|---|---|---|---|
| Montelukast | Leukotriene receptor antagonist | CYSLTR1 | Standard MCAS maintenance; respiratory + GI. |
| Ketotifen | Dual H1 + stabilizer | HRH1 + membrane | See rescue.md; also chronic. |
| Aspirin (low-dose) | COX inhibitor | COX1/2 | **Only in PGD2-high subset under clinical supervision** (NSAID-tolerant patients only). |
| Low-dose naltrexone (LDN) | TLR4 antagonist + opioid receptor modulator | TLR4 / mu / kappa | Anecdotal; growing case-series evidence. |

## Natural / non-controlled maintenance

### The flavonoid backbone

Flavonoids are the workhorse class for natural mast cell stabilization. Stack
hypothesis: **quercetin (broad) + luteolin (BBB-crossing for neuro) + curcumin
(NF-kB + Nrf2) + EGCG (Nrf2)** as a daily four-compound polyphenol regimen.

| Compound | Mechanism notes |
|---|---|
| Quercetin | PKC / Ca²⁺ / histamine / tryptase / cytokine inhibition. |
| Luteolin | Stronger on PKC + Ca²⁺; BBB-crossing → neuro-MCAS phenotype. |
| Curcumin (Meriva phytosome) | NF-kB inhibition + Nrf2 activation. |
| EGCG (green tea) | Catechin mast cell stabilization + Nrf2 activation. |
| Resveratrol | Sirtuin + Nrf2 + **MRGPRX2 inhibition** (huge for chemical/smell sensitivity). |
| Apigenin | Chamomile flavone; synergistic with quercetin/luteolin. |
| Baicalein | 12-LOX inhibitor + potent stabilizer (Scutellaria baicalensis). |
| Rosmarinic acid | Anti-allergic (Perilla, rosemary). |
| Thymoquinone | Black cumin; NF-kB inhibition. |
| 6-Gingerol | COX modulation + GI support. |

### Supportive supplements

| Compound | Why |
|---|---|
| Vitamin D3 / calcitriol | Deficiency common; mast cell stability + Treg support. |
| Omega-3 (DHA + EPA) | SPM precursors; reduces LTB4 and systemic inflammation. |
| Magnesium (glycinate) | Membrane / NMDA modulation; common deficiency. |
| Butyrate | HDAC inhibition + gut barrier reinforcement. |
| NAC + α-lipoic acid | Antioxidant network; supports the Nrf2 axis. |
| Taurine | Membrane stabilization. |
| Biotin | Mast cell modulation (animal data). |

## Hypotheses to test in the AI pipeline

1. **Quercetin-luteolin hybrid analog:** Seed REINVENT 4 with both anchors;
   optimize for chromone-flavone hybrids with QED > 0.6 and synthesizable
   in Enamine REAL Space. Filter through hERG + BBB QSAR.
2. **Polyphenol bioavailability optimization:** Major flaw of quercetin /
   curcumin is gut absorption. Use REINVENT to grow ester / glycoside
   pro-drugs with improved Caco-2 permeability (proxy QSAR from PyTDC).
3. **Multi-target "neuro-MCAS" candidate:** BBB-crossing + H3 + microglial
   modulation. Seed on luteolin; score with both BBB_Martins and
   MRGPRX2-docking weight.

## Top AI-ranked candidates

> 🤖 **Auto-generated artifact.** Produced by `scripts/rank_hypotheses.py` on 2026-07-05 06:13 UTC from commit `50b7129`. Inputs: `data/compounds/MCAS_Compound_Library_v1.csv`, `outputs/reinvent_generated.csv`, `outputs/docking_*.csv`, `outputs/warhead_scores.csv`, `outputs/qsar_predictions.csv`. Composite formula and weights documented in [EXP-005](../experiments/EXP-005-multi-objective-ranking.md). Recovery benchmark: [EXP-006](../experiments/EXP-006-known-actives-recovery.md).

_Higher composite = better hypothesis. Edit `scripts/rank_hypotheses.py` to change weights or category target mix; the next run will overwrite this table._

| # | Name | Composite | KEAP1 | MRGPRX2 | KIT | HRH1 | Warhead | hERG | AMES | BBB | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Curcumin | 0.700 | 1.00 | 0.28 | 0.12 | 0.14 | yes | 0.69 | 0.09 | 0.81 | library |
| 2 | Luteolin | 0.625 | 0.18 | 1.00 | 0.09 | 0.09 | yes | 0.35 | 0.70 | 0.54 | library |
| 3 | Rosmarinic acid | 0.616 | 0.37 | 0.23 | 0.12 | 0.14 | yes | 0.53 | 0.41 | 0.60 | library |
| 4 | Thymoquinone | 0.598 | 0.09 | 0.09 | 0.08 | 0.10 | yes | 0.31 | 0.22 | 0.93 | library |
| 5 | Baicalein | 0.594 | 0.16 | 0.54 | 0.13 | 0.13 | yes | 0.54 | 0.37 | 0.74 | library |
| 6 | EGCG | 0.571 | 0.15 | 0.19 | 0.12 | 0.12 | yes | 0.76 | 0.42 | 0.71 | library |
| 7 | Montelukast | 0.540 | 0.14 | 0.11 | 0.15 | 0.21 | — | 0.64 | 0.34 | 0.77 | library |
| 8 | Eicosapentaenoic acid (EPA) | 0.521 | 0.16 | 0.07 | 0.07 | 0.12 | — | 0.24 | 0.16 | 0.91 | library |
| 9 | Docosahexaenoic acid (DHA) | 0.517 | 0.17 | 0.08 | 0.08 | 0.12 | — | 0.21 | 0.23 | 0.91 | library |
| 10 | Cholecalciferol (Vitamin D3) | 0.506 | 0.12 | 0.12 | 0.07 | 0.11 | — | 0.49 | 0.04 | 0.68 | library |


## Wet-lab validation

LAD2 cell histamine + tryptase + IL-6 release over 24h with chronic
sub-stimulating substance P / LPS / IgE-crosslink — measure threshold shift vs.
no-treatment control. See [docs/wet_lab_protocols.md](../docs/wet_lab_protocols.md).
