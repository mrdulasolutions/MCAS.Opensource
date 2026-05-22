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
