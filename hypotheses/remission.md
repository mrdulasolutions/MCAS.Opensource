# Remission hypotheses

> ⚠️ **Not medical advice.** Research/hypothesis use only. See [docs/disclaimers.md](../docs/disclaimers.md).

**Goal:** **disease modification, not symptom control.** Reverse the upstream
injury that primes mast cells for inappropriate activation. This is the
"cure" target — and where the biggest wins (and biggest unknowns) live.

Three distinct mechanistic axes worth pursuing in parallel, because MCAS is
heterogeneous and a single remission compound is unlikely to work for everyone.

---

## Axis 1: KIT-driven (clonal MCAS / mastocytosis subset)

For patients with KIT D816V or other gain-of-function KIT variants, the mast
cell itself is intrinsically dysregulated. Direct kinase inhibition is the
established remission path.

| Compound | Status |
|---|---|
| **Avapritinib** | FDA-approved 2021 for advanced systemic mastocytosis. Selective for KIT D816V. |
| **Midostaurin** | Approved for advanced systemic mastocytosis; multi-kinase. |
| **Masitinib** | Phase 3 trials in severe MCAS / mastocytosis. |

**AI hypothesis (Axis 1):** Seed REINVENT 4 with the masitinib core; optimize
for selectivity over off-targets (PDGFR, FYN) using QSAR + KIT docking
(notebook 04 against UniProt P10721). Goal: clonal-MCAS-specific scaffold with
better safety than the parent.

---

## Axis 2: GLP-1 receptor agonism (the 2025 surprise)

A 2025 case series of refractory MCAS reported ~89% response to GLP-1 receptor
agonists (semaglutide / tirzepatide). Mechanism is incompletely understood —
likely a combination of:

- Direct GLP-1R signaling on mast cells (GLP1R expression confirmed).
- Systemic anti-inflammatory effect (reduces IL-6, TNF).
- Gut barrier reinforcement, indirectly reducing endotoxin-driven activation.

| Compound | Class |
|---|---|
| **Semaglutide** | GLP-1RA (peptide). |
| **Tirzepatide** | GLP-1/GIP dual agonist (peptide). |

**AI hypothesis (Axis 2):** Peptides are hard to optimize with small-molecule
generative AI — but small-molecule GLP-1R agonists exist (e.g., orforglipron
class). Worth screening published GLP1R small-molecule scaffolds against the
GLP1R AlphaFold structure (P43220) and seeding REINVENT on candidates that
clear ADMET. Also: investigate whether the *downstream* anti-inflammatory
profile can be recapitulated more cheaply with a polyphenol + SCFA stack.

---

## Axis 3: Upstream injury reversal (Nrf2 / epigenetic — the SFN hypothesis)

This is the "leave no stone unturned" axis. The hypothesis:

> Chronic oxidative + epigenetic injury (post-viral, toxin, mold, mitochondrial)
> suppresses Nrf2 via KEAP1 oxidation **and** promoter methylation, which
> lowers the mast cell activation threshold and primes MRGPRX2 hypersensitivity.
> Restoring Nrf2 tone — by direct activation **and** by demethylating the
> Nrf2 promoter — undoes the priming and produces durable remission.

| Compound | Mechanism |
|---|---|
| **Sulforaphane (SFN)** | Most potent natural Nrf2 activator. Inhibits caspase-1, NF-kB, MAPKs; upregulates HO-1; suppresses TSLP, TNF-α, IL-1β, IL-6, IL-8 in mast cells. Also a DNMT inhibitor → epigenetic demethylation. **The strongest natural candidate for upstream MCAS rescue.** |
| Glucoraphanin (+ myrosinase) | SFN precursor; bioactivated by gut flora / mustard seed enzyme. |
| Resveratrol | Sirtuin + Nrf2 + MRGPRX2 inhibition. |
| Curcumin | NF-kB + Nrf2; needs phytosomal formulation. |
| EGCG | Nrf2 activator + catechin. |
| NAC + α-lipoic acid | GSH replenishment supports the Nrf2 axis. |

**AI hypothesis (Axis 3):** Seed REINVENT 4 with **sulforaphane** + curcumin +
resveratrol — generate covalent KEAP1 binders with the isothiocyanate or
Michael-acceptor pharmacophore preserved but improved BBB penetration and
metabolic stability (SFN is rapidly conjugated by GST). Dock against KEAP1
(UniProt Q14145 — Kelch BTB domain) or directly against Nrf2 transcription
factor (Q16236) via the binding interface. Filter for low covalent off-target
risk.

---

## Hypotheses (cross-axis)

1. **SFN + masitinib combo:** Upstream epigenetic reset (SFN) + KIT inhibition
   (masitinib) in clonal MCAS. AI pipeline: score the combo's composite QSAR
   safety + dual-target docking.
2. **GLP-1RA + polyphenol stack:** GLP-1RA-naïve patients get the polyphenol
   stack first as a cheaper hypothesis test; non-responders escalate.
3. **MRGPRX2 antagonist scaffold:** Seed REINVENT on resveratrol; multi-objective
   optimize for MRGPRX2 docking + selectivity over other GPCRs.

## Top AI-ranked candidates

> 🤖 **Auto-generated artifact.** Produced by `scripts/rank_hypotheses.py` on 2026-07-19 05:31 UTC from commit `58840dc`. Inputs: `data/compounds/MCAS_Compound_Library_v1.csv`, `outputs/reinvent_generated.csv`, `outputs/docking_*.csv`, `outputs/warhead_scores.csv`, `outputs/qsar_predictions.csv`. Composite formula and weights documented in [EXP-005](../experiments/EXP-005-multi-objective-ranking.md). Recovery benchmark: [EXP-006](../experiments/EXP-006-known-actives-recovery.md).

_Higher composite = better hypothesis. Edit `scripts/rank_hypotheses.py` to change weights or category target mix; the next run will overwrite this table._

| # | Name | Composite | KEAP1 | MRGPRX2 | KIT | HRH1 | Warhead | hERG | AMES | BBB | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Erucin | 0.730 | 1.00 | 0.03 | 0.03 | 0.05 | yes | 0.27 | 0.41 | 0.92 | library |
| 2 | Sulforaphane | 0.726 | 1.00 | 0.04 | 0.05 | 0.07 | yes | 0.23 | 0.55 | 0.92 | library |
| 3 | Phenethyl isothiocyanate | 0.687 | 1.00 | 0.08 | 0.08 | 0.17 | yes | 0.70 | 0.75 | 0.95 | library |
| 4 | Iberin | 0.618 | 1.00 | 0.04 | 0.05 | 0.07 | yes | 0.23 | 0.47 | 0.93 | library |
| 5 | Benzyl isothiocyanate | 0.583 | 1.00 | 0.08 | 0.09 | 0.18 | yes | 0.69 | 0.58 | 0.95 | library |
| 6 | GEN_0005 | 0.563 | 1.00 | 0.04 | 0.05 | 0.07 | yes | 0.23 | 0.47 | 0.93 | reinvent_generated |
| 7 | Midostaurin | 0.556 | 0.10 | 0.12 | 0.56 | 0.15 | — | 0.68 | 0.62 | 0.75 | library |
| 8 | GEN_0002 | 0.554 | 1.00 | 0.03 | 0.03 | 0.05 | yes | 0.27 | 0.41 | 0.92 | reinvent_generated |
| 9 | GEN_0006 | 0.553 | 0.95 | 0.03 | 0.03 | 0.04 | yes | 0.27 | 0.37 | 0.92 | reinvent_generated |
| 10 | GEN_0004 | 0.552 | 1.00 | 0.04 | 0.05 | 0.07 | yes | 0.23 | 0.55 | 0.92 | reinvent_generated |


## Wet-lab validation

For SFN / Nrf2-axis hypotheses: LAD2 cells + 24h SFN pre-treatment → induce with
H₂O₂ (oxidative injury), substance P (MRGPRX2), or IgE-crosslink → measure
degranulation **plus** HMOX1 / NQO1 mRNA induction (Nrf2 readout). See
[docs/wet_lab_protocols.md](../docs/wet_lab_protocols.md).

---

### Why this matters

If the SFN / Nrf2 hypothesis is even partially right, we have a remission
candidate that already exists, costs cents per dose as broccoli sprouts, and
cannot be patented. That is exactly why this repo exists.
