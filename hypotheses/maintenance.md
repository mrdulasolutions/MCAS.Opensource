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

_To be filled in by `notebook 05_hypothesis_ranking.ipynb` — output: `outputs/ranked_maintenance.csv`_

## Wet-lab validation

LAD2 cell histamine + tryptase + IL-6 release over 24h with chronic
sub-stimulating substance P / LPS / IgE-crosslink — measure threshold shift vs.
no-treatment control. See [docs/wet_lab_protocols.md](../docs/wet_lab_protocols.md).
