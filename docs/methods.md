# Methods

End-to-end pipeline for going from "we suspect compound X might help" to a
ranked, AI-evaluated hypothesis, with a clear handoff to wet-lab validation.

## Pipeline diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                   data/compounds/seeds.json                          │
│             (hand-curated anchors + PubChem CIDs)                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ scripts/build_compound_library.py
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│        data/compounds/MCAS_Compound_Library_v1.csv                   │
│   (SMILES auto-fetched + RDKit-canonicalized; biologics flagged)     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ scripts/export_for_ai.py
                               ▼
                  outputs/library.smi    outputs/library.sdf
                               │
                               ├───► notebook 01 (load + explore)
                               │
                               ├───► notebook 02 (DeepChem QSAR on PyTDC tasks)
                               │            └─► outputs/qsar_predictions.csv
                               │
                               ├───► notebook 03 (REINVENT 4 on Colab GPU)
                               │            └─► outputs/reinvent_generated.csv
                               │
                               ├───► notebook 04 (AlphaFold + DiffDock / smina)
                               │            └─► outputs/docking_<target>.csv
                               │
                               ▼
                       notebook 05 (multi-objective ranking)
                               │
                               └─► outputs/ranked_<category>.csv
                                   + updates to hypotheses/<category>.md
                                   │
                                   ▼
                     handoff to wet-lab validation
                     (LAD2 β-hex, CD63, tryptase ELISA — see
                      docs/wet_lab_protocols.md)
```

## Why this design

1. **Reproducible from a single seeds file.** Anyone can rebuild the master
   library and rerun every prediction with `python scripts/build_compound_library.py`.
2. **Auto-fetched SMILES, not hand-curated SMILES.** Hand-entered SMILES drift,
   collide with PubChem updates, and introduce stereo errors. PubChem PUG-REST
   is the canonical source.
3. **Biologics flagged, not hidden.** Omalizumab, semaglutide, tirzepatide,
   DAO, bromelain, and plant extracts have no usable SMILES — they're still in
   the library with a `biologic_flag`, so they survive merges but bypass
   chemistry-only pipelines.
4. **CPU-first path is canonical.** `scripts/generate_sfn_analogs.py`,
   `score_against_targets.py`, `run_qsar.py`, `rank_hypotheses.py` reproduce
   rankings on a laptop. Notebooks 03–04 (REINVENT / DiffDock) remain optional
   GPU enrichment; Vina KEAP1 docking is available via `scripts/dock_keap1.py`.
5. **Category-aware multi-target scoring.** Rescue weights H1/H2/CysLT1/MRGPRX2;
   maintenance adds BTK/SYK/PTGS2/CNR2/KEAP1; remission is KEAP1/KIT-heavy.
   Composite ranking (`scripts/rank_hypotheses.py`) is category-aware.
6. **Evidence weighting persists through the pipeline.** A compound with
   strong human clinical evidence keeps that boost even if QSAR or docking is
   middling — we're hunting for hypotheses, not pretending in silico beats real
   data.
7. **Audit gates in CI.** `scripts/check_audit_gates.py` fails the build if
   recovery@20, recovery@10, negative precision@10, or library size fall below
   documented floors.

## CPU-only path (no GPU, no Colab)

If you don't have access to a GPU or Colab, two helper scripts replace the
GPU-bound notebooks (03 + 04) end-to-end on a laptop:

```bash
python scripts/generate_sfn_analogs.py     # local SFN-seeded analog generator (BRICS + bioisostere + warhead-graft)
python scripts/score_against_targets.py    # ligand-based virtual screening vs. curated reference ligands per target
python scripts/rank_hypotheses.py          # multi-objective ranking → ranked_<category>.csv + hypothesis-doc updates
```

The ligand-based screen uses Tanimoto similarity (Morgan fingerprint, radius 2,
2048 bits) against curated reference ligands per target (e.g. imatinib /
nilotinib / dasatinib for KIT; bardoxolone / dimethyl fumarate / SFN for
KEAP1-Nrf2; cetirizine / fexofenadine for HRH1). It's standard pharma early-
triage when target structures are uncertain — every output row carries a
`method` column making the methodology explicit. When a GPU + DiffDock pose
becomes available, the same `outputs/docking_<target>.csv` file is overwritten
by physics-based scores and notebook 05 keeps working unchanged.

## Updating the pipeline

Add a compound → edit `seeds.json` → rerun `build_compound_library.py` and
`validate_smiles.py`. Open a PR. CI runs the validator.

Add a target → edit `data/targets/MCAS_Targets.csv` (UniProt ID + role) → rerun
notebook 04 to fetch the AlphaFold structure and dock.

Add a hypothesis → edit the relevant `hypotheses/*.md` and reference compounds
by name; rerun notebook 05 to refresh the ranked CSV.
