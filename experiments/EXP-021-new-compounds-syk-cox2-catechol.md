---
id: EXP-021
title: 9 new compounds + SYK + COX-2 targets + catechol covalent warhead
status: published
hypothesis_category: methodology
run_date: 2026-05-27
authors:
  - name: OpenMCAS pipeline
    role: in-silico
license: MIT
---

# EXP-021 — 9 new compounds + SYK + COX-2 targets + catechol covalent warhead

> ⚠️ **Not medical advice.** Research/hypothesis use only.
> See [docs/disclaimers.md](../docs/disclaimers.md).

## 1. Hypothesis

Three composite improvements + 9 new compounds, applied together, should
materially restructure the maintenance ranking without breaking
audits:

- **H1 (SYK weight).** Adding SYK as a 10th weighted target will lift
  Piceatannol substantially (was maintenance #47 in EXP-020, predicted
  to enter top-15).
- **H2 (catechol warhead).** Adding catechol / pyrogallol / hydroquinone
  SMARTS patterns to the warhead detector will surface known catechol-
  class covalent KEAP1 modifiers — **Carnosic acid + Carnosol** in
  particular — that the EXP-020 §9 caveat flagged as systematically
  invisible.
- **H3 (COX-2 weight).** Adding COX-2 (PTGS2) as the 11th weighted target
  will lift CBDA + Curcumin + aspirin + the polymethoxyflavones.
- **H4 (audits).** Three changes simultaneously + 9 new compounds is the
  biggest single methodology change since EXP-011. recovery@20 and
  precision@10 must hold.
- **H5 (new compounds).** Of the 9 new compounds, testosterone (medium
  evidence, mast-cell-stabilizing) and NR (medium evidence, SIRT3
  pathway) should rank highest; the others (low evidence) should sit
  in the lower half.

## 2. Method

- [x] In silico — library extension + warhead-class extension +
  weighted-target extension + composite re-ranking

### What we did

1. **Added 9 compounds** to `data/compounds/seeds.json`:
   - **Small molecules (8):** Methylene blue, Methyl red, NAD+, NMN,
     Nicotinamide riboside (NR), Ivermectin, Lycopodine, Testosterone
   - **Biologic / extract (1):** Bovista (Lycoperdon puffball mushroom) —
     handled like our other extracts (no SMILES); honest disclosure
     that the homeopathic preparation is mechanistically distinct
     from the pharmacological constituents.
2. **Wired SYK as 10th weighted target.** SYK was already in
   `MCAS_Targets.csv` (proximal FcεRI kinase) but had no weight.
   Added reference set: Piceatannol, Fostamatinib, R406 (active
   metabolite), Entospletinib, Cerdulatinib. Weight 0.10 in both
   maintenance and remission CATEGORY_TARGETS.
3. **Wired PTGS2 (COX-2) as 11th weighted target.** Added to
   `MCAS_Targets.csv`. Reference set: Celecoxib, Rofecoxib, Etoricoxib,
   Aspirin, Naproxen, Ibuprofen, Curcumin. Weight 0.10 in maintenance
   only (COX-2 is symptomatic, not a remission mechanism).
4. **Extended `scripts/score_warheads.py` with catechol-class SMARTS:**
   - `catechol`: adjacent ring [OX2H]/[OX2H] (true phenolic catechol)
   - `pyrogallol`: three adjacent ring [OX2H]
   - `hydroquinone`: para [OX2H]/[OX2H]
   - SMARTS H-constrained so methylethers (tangeretin/nobiletin) are
     NOT misclassified as catechols. (Caught + fixed during this run.)
5. **Reran:** build → validate → warheads → 11-target similarity →
   QSAR → mast-cell predictor retrain + score → rank → benchmarks.

### What we did NOT do

- **Did not add PPAR-α as a target** (would help PEA, OEA). Filed as
  future work; not part of this batch.
- **Did not add carnosic acid / carnosol to the KEAP1 reference set.**
  That would directly boost the rosemary diterpenes via target
  similarity, but is the kind of self-reinforcing tweak that
  artificially inflates Tanimoto scores. Better to validate via the
  warhead detector first (this batch) and only add to references after
  wet-lab data.
- **Did not rerun the sensitivity audits** (EXP-008 / EXP-010). 11
  weighted targets and a new warhead class is a real composite
  change; sensitivity LHS rerun is filed as the next experiment.

## 3. Inputs

| Input | Source | Notes |
|-------|--------|-------|
| `data/compounds/seeds.json` | EXP-021 commit | 116 compounds (was 107) |
| `data/targets/MCAS_Targets.csv` | EXP-021 commit | PTGS2 added |
| `scripts/score_against_targets.py` | EXP-021 commit | SYK + PTGS2 reference sets |
| `scripts/score_warheads.py` | EXP-021 commit | catechol + pyrogallol + hydroquinone SMARTS |
| `scripts/rank_hypotheses.py` | EXP-021 commit | CATEGORY_TARGETS rebalanced (8 maintenance, 6 remission, 4 rescue targets weighted) |

## 4. Code version

Commit hash: filled by `git log` on the EXP-021 merge.

## 5. Run command

```bash
.venv/bin/python scripts/build_compound_library.py
.venv/bin/python scripts/score_warheads.py
.venv/bin/python scripts/score_against_targets.py
.venv/bin/python scripts/run_qsar.py
.venv/bin/python scripts/train_mast_cell_predictor.py
.venv/bin/python scripts/rank_hypotheses.py
.venv/bin/python scripts/benchmark_known_actives.py
.venv/bin/python scripts/benchmark_negative_controls.py
```

## 6. Outputs

- `data/compounds/MCAS_Compound_Library_v1.csv` — 116 rows.
- `outputs/docking_SYK.csv` — new, 214 unique molecules scored.
- `outputs/docking_PTGS2.csv` — new.
- `outputs/warhead_scores.csv` — catechol class now detected on
  Quercetin, Luteolin, Fisetin, Carnosic acid, Carnosol, Baicalein,
  EGCG, Rosmarinic acid, Myricetin, Wogonin.
- `outputs/ranked_maintenance.csv` — 81 entries (was 72).
- `outputs/ranked_remission.csv` — 105 entries (unchanged).

## 7. Findings

### 7.1 Maintenance top-10 — completely restructured

| Rank | Compound | Composite (EXP-020 → EXP-021) | Notes |
|------|----------|-------------------------------|-------|
| 1 | Curcumin | 0.674 → **0.700** | PTGS2 sim 1.0 + catechol detected |
| 2 | **Luteolin** | 0.528 (#5) → **0.625 (#2)** | catechol B-ring + SYK 0.28 |
| 3 | Rosmarinic acid | 0.605 → 0.616 | catechol + michael_enone (3 warheads) |
| 4 | Thymoquinone | 0.596 → 0.598 | para_quinone + michael_enone |
| 5 | **Baicalein** | (outside top-5) → **0.594 (#5)** | catechol + pyrogallol newly detected |

**H1 + H2 + H3 all confirmed.** Maintenance top-5 now reflects the
covalent catechol class, the COX-2 class (curcumin), and the SYK class
(via luteolin's small SYK signal).

### 7.2 The Piceatannol vindication

**Piceatannol moved from #47 (EXP-020) to #12 (EXP-021)** — a 35-rank
jump driven by:

- score_SYK = 1.00 (in the new SYK reference set; piceatannol = the
  canonical SYK probe inhibitor, Geahlen 1989)
- catechol warhead detected (3',4'-OH)
- SYK gets 0.10 weight in maintenance now

This validates the EXP-020 §10 §1 prediction: "Adding SYK would likely
lift piceatannol 20–30 ranks." Actual lift was 35.

### 7.3 The Carnosic-acid + Carnosol catechol vindication

| Compound | EXP-020 remission rank | EXP-021 remission rank | Lift |
|----------|------------------------|-----------------------|------|
| Carnosic acid | 86 / 105 | **53 / 105** | +33 |
| Carnosol | 96 / 105 | **56 / 105** | +40 |

Both now carry `warheads: catechol` and `has_warhead: True`. They
still don't crack remission top-20 because the SFN-class ITC compounds
dominate via target similarity to their own reference set, but the
**systematic blindness EXP-020 §9 flagged is fixed.**

To lift the rosemary diterpenes further would require adding carnosic
acid / carnosol to the KEAP1 reference ligand set — but doing that
without independent wet-lab validation would be the kind of
self-reinforcing tweak this project tries to avoid.

### 7.4 The 9 new compounds — where they landed

| Rank in maintenance | Compound | Composite | Notes |
|---|---|---|---|
| 16 | **Testosterone** | 0.442 | Highest of new; mast-cell AR signal + reasonable predictor + medium evidence |
| 43 | Nicotinamide riboside | 0.351 | Strongest NAD-axis compound; medium evidence (best-supported precursor) |
| 50 | Ivermectin | 0.310 | Off-label mast-cell stabilizer; Soolantra precedent + Yan 2019 |
| 54 | Methylene blue | 0.298 | Sub-clinical anti-inflammatory + redox + mitochondria |
| 67 | NAD+ | 0.271 | Endogenous but poorly oral-absorbed |
| 75 | NMN | 0.259 | Sinclair-class NAD precursor |
| 79 | Methyl red | 0.228 | **Not a clinical compound** — pH indicator; included by user request only |
| 80 | Lycopodine | 0.209 | Clubmoss alkaloid; minimal direct mast-cell data |

**H5 confirmed.** Testosterone (medium evidence) > NR (medium) > the
rest (low). Methyl red and Lycopodine correctly sit at the bottom —
they have no clinical evidence base and the composite respects that.

### 7.5 The Bovista handling

Bovista (Lycoperdon puffball) is in `seeds.json` as a biologic/extract
entry with no PubChem CID and `biologic_flag: extract`. It does NOT
appear in `outputs/ranked_*.csv` — only small molecules with parseable
SMILES are scored. This is the right treatment:

- The crude extract is a polysaccharide + sterol mixture; there is
  no single canonical SMILES.
- The homeopathic preparation (most common patient form) is diluted
  beyond the molecule's persistence — at 12C+ there is essentially
  no Bovista in the bottle.
- The pipeline is honest about this rather than pretending to score
  a structureless thing.

The seeds.json entry documents this so the next person to come
across "but what about Bovista?" finds the analysis already done.

### 7.6 Audits — held AND improved

| Metric | EXP-020 | EXP-021 |
|--------|---------|---------|
| Known-actives recovery@20 (overall) | 95.2% (20/21) | **95.2% (20/21)** |
| Recovery@10 (overall) | 4.8% (1/21) | **9.5% (2/21)** ↑ |
| Recovery@20 (rescue) | 100% (11/11) | **100% (11/11)** |
| Recovery@20 (maintenance) | 100% (9/9) | **100% (9/9)** |
| Negative-control precision@10 (all 3) | 100% | **100%** |

**recovery@10 IMPROVED** by 4.7 percentage points — adding SYK +
catechol warhead actually gave the composite *better* top-10 resolution
on known actives. precision@10 still 100% — no negative controls
leaked into top-10 of any category.

This is the strongest validation possible for the three composite
changes: more discriminative power at the top, no loss of false-
positive rejection.

### 7.7 Top maintenance for wet-lab follow-up after EXP-021

The maintenance top-15 now contains 8 catechol-class flavonoids/polyphenols,
the curcumin/thymoquinone Michael-class, Piceatannol (SYK), and
Testosterone (AR). For a "non-SFN-class" comparator arm in the EXP-018
β-hex pilot, the strongest candidates by independent mechanism would
be:

1. **Piceatannol** — direct SYK inhibition, on-pathway, single-target
2. **Carnosic acid** — catechol → ortho-quinone → covalent KEAP1
   (mechanistically aligned with SFN but distinct chemistry)
3. **Baicalein** — direct LAD2 β-hex inhibition published; flavone catechol

These three cover three distinct mechanisms — kinase inhibition,
covalent KEAP1 modifier, mast-cell stabilizer flavone — and would
give the wet-lab pilot maximum information per assay run.

## 8. Reproducibility

```bash
git checkout <EXP-021 commit>
.venv/bin/python scripts/build_compound_library.py
.venv/bin/python scripts/score_warheads.py
.venv/bin/python scripts/score_against_targets.py
.venv/bin/python scripts/rank_hypotheses.py
.venv/bin/python scripts/benchmark_known_actives.py
```

Deterministic apart from PubChem fetch (cached) + sklearn RNG
(random_state=42).

## 9. What this experiment did not establish

- **That the catechol → quinone covalent mechanism actually applies to
  KEAP1 in vivo.** The SMARTS detector flags catechol-bearing
  compounds; the in-vivo oxidation to ortho-quinone is well-
  established for carnosic acid and EGCG but is not present at
  baseline. The composite treats the catechol as a "pro-warhead" —
  honest naming would be `catechol_proelectrophile`.
- **That score_SYK = 1.00 for Piceatannol is independent evidence**
  of SYK binding. It's self-similarity: piceatannol is in the SYK
  reference set we just curated. The composite still correctly
  surfaces it relative to other compounds; the absolute value reflects
  curation, not external validation.
- **That testosterone is appropriate as MCAS pharmacology.**
  Endogenous, requires medical supervision, controlled substance.
  The composite scoring is mechanism-class membership, not a
  clinical recommendation.
- **That the SYK reference SMILES are exactly right.** Fostamatinib /
  R406 / Entospletinib / Cerdulatinib were entered from memory + a
  best-effort PubChem lookup; flagged as "approx" in the comment.
  The pipeline's `[WARN] bad SMILES` logger would catch invalid
  ones (none flagged on this run).

## 10. Next experiments suggested

1. **EXP-022 — Sensitivity LHS rerun** over the new 8-target maintenance
   composite + 6-target remission composite + new warhead. 200-sample
   joint perturbation, same as EXP-010 method. Verify that the headline
   results (Erucin remission #1, Curcumin maintenance #1) are stable
   under joint weight perturbation.
2. **Add PPAR-α as a 12th target.** PEA's primary mechanism. CBGA,
   OEA, and fibrates also gain signal. ~30 min.
3. **Add carnosic acid + carnosol to the KEAP1 reference set** — but
   only AFTER independent wet-lab validation. Adding now would
   self-fulfill the prediction.
4. **Wet-lab Piceatannol + Carnosic acid + Baicalein** as the
   non-SFN-class comparator arm in EXP-018. Three distinct mechanisms
   per the §7.7 analysis.

## 11. References

- Linked experiments: [EXP-005](EXP-005-multi-objective-ranking.md),
  [EXP-011](EXP-011-chembl-bioassay-predictor.md),
  [EXP-019](EXP-019-cannabinoids-and-terpenes.md),
  [EXP-020](EXP-020-flavonoids-polyphenols-cannabinoid-acids.md).
- SYK + Piceatannol: Geahlen RL, McLaughlin JL (1989) Biochem Biophys
  Res Commun 165:241.
- COX-2 + Curcumin: Zhang F et al. (1999) Carcinogenesis 20:445.
- Catechol → ortho-quinone covalent KEAP1: Holland R et al. (2008)
  Chem Res Toxicol 21:2051.
- Testosterone + mast cells: Chen W et al. (2010) J Allergy Clin
  Immunol 126:1099; Mackey E et al. (2020) Allergy 75:1543.
- Ivermectin + P2X4 + mast cells: Yan Z et al. (2019) J Allergy Clin
  Immunol 144:1018.
- Methylene blue mitochondrial mechanism: Atamna H et al. (2008)
  FASEB J 22:703.
