# Experiments

Every computational test we run is documented here as a **standardized
experiment report**. The format is non-negotiable so any reader — patient,
clinician, academic, or auditor — can answer four questions at a glance:

1. **What was the hypothesis?**
2. **What method was used?**
3. **What inputs / parameters / code versions produced the result?**
4. **How do I reproduce it on my machine?**

Plus what it found and what it didn't.

## How to add a new experiment

1. Copy `EXPERIMENT_TEMPLATE.md` → `EXP-NNN-short-slug.md` (next free number).
2. Fill out every section. Don't skip — if a section is "n/a" say so explicitly.
3. Drop your output artifacts in `outputs/exp_NNN/` or reference existing ones
   in `outputs/`.
4. Commit. Open a PR. CI validates the experiment frontmatter schema.

## Index

| ID | Title | Method | Status | Run date |
|----|---|---|---|---|
| [EXP-001](EXP-001-sfn-seeded-analog-generation.md) | SFN-class analog generation | local BRICS + bioisostere + warhead-graft | published | 2026-05-21 |
| [EXP-002](EXP-002-ligand-based-target-screening.md) | Ligand-based virtual screening across 8 MCAS targets | Tanimoto / Morgan 2048-bit vs curated reference ligands | published | 2026-05-21 |
| [EXP-003](EXP-003-covalent-warhead-scoring.md) | Covalent-warhead + KEAP1 pharmacophore scoring | RDKit SMARTS + Lipinski filter | published | 2026-05-21 |
| [EXP-004](EXP-004-admet-qsar.md) | ADMET QSAR (hERG / AMES / BBB) | RandomForest on Morgan FP, PyTDC training data | published | 2026-05-21 |
| [EXP-005](EXP-005-multi-objective-ranking.md) | Multi-objective ranking → rescue / maintenance / remission | composite of evidence + target similarity + warhead + safety | published | 2026-05-21 |
| [EXP-006](EXP-006-known-actives-recovery.md) | Known Actives Recovery benchmark — 21 held-out mast-cell drugs | blind scoring of compounds *not* in seeds or reference sets | published | 2026-05-21 |
| [EXP-007](EXP-007-negative-control-benchmark.md) | Negative-control benchmark — 20 unrelated drugs blind-scored | precision@N for compounds with no plausible MCAS mechanism | published | 2026-05-22 |
| [EXP-008](EXP-008-sensitivity-analysis.md) | Sensitivity analysis on the six composite weights | ±50% per-weight sweep — Spearman, top-10 Jaccard, top-1 stability | published | 2026-05-22 |
| [EXP-009](EXP-009-keap1-vina-docking.md) | KEAP1 Kelch-pocket Vina docking + 3-CID data-bug fix | Real AutoDock Vina v1.2.7 docking on PDB 4L7B for top-50; ligand-efficiency normalization; SFN class confirmed | published | 2026-05-22 |
| [EXP-010](EXP-010-joint-perturbation-lhs.md) | Joint-perturbation Latin-hypercube weight sweep | 200-sample LHS over all 6 weights; Erucin holds remission #1 in 91.5% of samples | published | 2026-05-22 |
| [EXP-011](EXP-011-chembl-bioassay-predictor.md) | ChEMBL bioassay pull + per-target activity predictors | 67k records · 11 targets · CV R² 0.52–0.80 (median 0.69) · integrated as +0.10 potency bonus | published | 2026-05-22 |
| [EXP-012](EXP-012-covalent-c151-adduct.md) | Covalent KEAP1-C151 dithiocarbamate adduct energy proxy | MMFF94 reaction-energy proxy for the actual SFN mechanism | published | 2026-05-22 |
| [EXP-013](EXP-013-rl-generation.md) | Iterative REINVENT-style policy improvement (CPU + Colab paths) | 4-iter generate-and-select; 265 candidates; drug-like aromatic ITCs emerge | published | 2026-05-22 |
| [EXP-014](EXP-014-chronic-rescue-dependency.md) | Chronic rescue dependency — patient-reported survey on long-term first-gen H1 use | Pre-registered observational survey; analysis pending n ≥ 30 | running | 2026-05-22 |
| [EXP-015](EXP-015-audit-retread.md) | Audit retread on post-ChEMBL composite | Rerun EXP-006/007/008/010; 3 of 4 hold; remission recovery regression diagnosed as category-label issue | published | 2026-05-22 |
| [EXP-016](EXP-016-mast-cell-predictor.md) | Mast-cell-specific bioassay predictor | 1101 compounds, CV AUC **0.916** ± 0.019 (strongest single model in repo); integrated as +0.05 universal bonus | published | 2026-05-22 |
| [EXP-017](EXP-017-enamine-availability-check.md) | Procurement check for top generated SFN-class analogs | RDKit envelope + InChIKey-keyed vendor lookup; 20/25 (80%) REAL-Space-plausible; procurement packet ready for CRO | published | 2026-05-23 |
| [EXP-019](EXP-019-cannabinoids-and-terpenes.md) | Cannabinoid + terpene library expansion + CB2 (CNR2) target | 24 compounds added (8 phytocannabinoids + 4 endocannabinoid-likes + 12 terpenes); CB2 wired as 9th target. **PEA #9 in maintenance**; β-caryophyllene #25. All audits hold (recovery@20 = 95.2%, precision@10 = 100%). | published | 2026-05-23 |
| [EXP-020](EXP-020-flavonoids-polyphenols-cannabinoid-acids.md) | Flavonoid + Nrf2 polyphenol + cannabinoid-acid library expansion | 29 compounds added (16 mast-cell flavonoids + 8 Nrf2 polyphenols/triterpenes + 5 cannabinoid acids). **CBDA #24 in maintenance**, Xanthohumol #28 (Michael-acceptor warhead), Fisetin #38. Surfaced piceatannol-SYK + carnosic-acid-quinone mechanism gaps. All audits hold. | published | 2026-05-27 |
| [EXP-021](EXP-021-new-compounds-syk-cox2-catechol.md) | 9 new compounds (methylene blue, NAD+/NMN/NR, ivermectin, testosterone, ...) + SYK + COX-2 as 10th + 11th weighted targets + catechol covalent warhead | **Piceatannol jumped #47 → #12** (SYK weight); **Luteolin #5 → #2**, Baicalein entered top-5 (catechol warhead); **Carnosic acid #86 → #53** (catechol warhead). recovery@10 *improved* 4.8% → 9.5% with audits intact (precision@10 = 100%, recovery@20 = 95.2%). | published | 2026-05-27 |
