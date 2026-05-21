# For researchers

Quick orientation for cheminformaticians, immunologists, mast-cell
biologists, and ML / AI folks who want to scrutinize, fork, or extend this
work.

## What this repo is

A reproducible, MIT-licensed in silico pipeline for hypothesis generation
in MCAS / MCAD. Five standardized experiments are published as of the
latest commit; each carries its own pre-registration-style report:

| ID | Method | Result |
|----|---|---|
| [EXP-001](../experiments/EXP-001-sfn-seeded-analog-generation.md) | RDKit BRICS + bioisosteric enumeration + warhead grafting from 7 natural ITC seeds | 113 ranked SFN-class candidate analogs |
| [EXP-002](../experiments/EXP-002-ligand-based-target-screening.md) | Tanimoto (Morgan r=2, 2048 bits) vs curated reference ligands per target | 157 compounds × 8 MCAS targets |
| [EXP-003](../experiments/EXP-003-covalent-warhead-scoring.md) | 13 cysteine-reactive SMARTS + KEAP1 pharmacophore filter | 79 compounds carry warhead + pass filter |
| [EXP-004](../experiments/EXP-004-admet-qsar.md) | RandomForest on Morgan FP, trained on PyTDC hERG / AMES / BBB | Valid AUC 0.89–0.91 |
| [EXP-005](../experiments/EXP-005-multi-objective-ranking.md) | Composite (evidence + target + warhead + safety + drug-likeness) | Ranked rescue / maintenance / remission CSVs |

Every result CSV is in [`outputs/`](../outputs/) and rebuilds from a single
seeds file + 5 scripts.

## Reproduce the whole pipeline in 5 minutes

```bash
git clone https://github.com/mrdulasolutions/MCAS.Opensource.git
cd MCAS.Opensource
python -m venv .venv && source .venv/bin/activate
pip install -e . PyTDC scikit-learn 'setuptools<81'

python scripts/build_compound_library.py    # PubChem fetch + RDKit validation
python scripts/validate_smiles.py
python scripts/generate_sfn_analogs.py      # SFN-class analog generation
python scripts/score_warheads.py            # covalent warhead detection
python scripts/score_against_targets.py     # ligand-based screening (8 targets)
python scripts/run_qsar.py                  # PyTDC ADMET QSAR
python scripts/rank_hypotheses.py           # composite ranking + hypothesis-doc updates
```

Wall-clock: ~3 minutes on a CPU laptop after the one-time PyTDC download.

## Things we'd love independent eyes on

1. **Composite weighting in EXP-005** — author-chosen. Run a sensitivity
   analysis (±50% per weight) and tell us where the ranking is fragile.
2. **Reference ligand sets** in `scripts/score_against_targets.py` — we
   missed compounds. Add what we missed.
3. **QSAR baselines** — RandomForest on Morgan FP is a strong baseline,
   not state-of-the-art. ChemProp / DeepChem GraphConv / 3D models likely
   add 1–3 AUC points. Train a better one and we'll merge it.
4. **Covalent reactivity ranking** — EXP-003's SMARTS detector is binary.
   xTB / DFT electrophilicity indices would let us rank reactivity, not just
   detect presence. We don't have the compute; you might.
5. **KEAP1 docking** — Kelch-domain crystal structures (PDB 4L7B, 5FNQ,
   6T7V) exist. Vina/smina or CovDock against Cys-151 for the top-50
   ranked compounds would convert ligand similarity into a structure-based
   estimate.
6. **Mast-cell-specific bioactivity data** — pull every ChEMBL assay
   tagged "β-hexosaminidase release," "LAD2," "histamine release," or
   "tryptase release" and train a true mast-cell-stabilizer predictor.
7. **Selectivity / polypharmacology score** — promiscuous binders should
   be penalized. We don't have a kinome / NHR / GPCR-panel proxy in here.

## Datasets you can cite directly

- [`data/compounds/MCAS_Compound_Library_v1.csv`](../data/compounds/MCAS_Compound_Library_v1.csv) (n=54 anchors)
- [`data/injury_mechanisms/MCAS_Injury_Mechanisms_v1.csv`](../data/injury_mechanisms/MCAS_Injury_Mechanisms_v1.csv)
- [`data/triggers/MCAS_Triggers_v1.csv`](../data/triggers/MCAS_Triggers_v1.csv)
- [`data/targets/MCAS_Targets.csv`](../data/targets/MCAS_Targets.csv)
- All [`outputs/`](../outputs/) CSVs (predictions, rankings)

## Citation

See [`CITATION.cff`](../CITATION.cff). Cite the repo + the commit hash you
used; we re-tag with a Zenodo DOI quarterly.

## How to contribute back

1. Fork.
2. Make your change — ideally as a new experiment under `experiments/EXP-NNN-*.md`
   so other researchers can replicate.
3. Open a PR with an explicit hypothesis + falsifiability statement.
4. CI runs SMILES validation on `data/` changes.

If you want to set up a formal academic collaboration (data sharing
agreement, MTA logistics, joint authorship), see
[for-academia.md](for-academia.md).

## What we will refuse

- Patent-encumbered contributions.
- Closed-data validation (we will publish our predictions; you publish
  yours, even if negative).
- Predictions claimed as clinical recommendations.
