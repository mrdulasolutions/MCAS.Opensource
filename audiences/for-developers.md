# For developers, ML engineers, cheminformaticians

The fastest onramp.

## 60-second tour of the code

```
scripts/
├── fetch_smiles.py            # PubChem PUG-REST client (throttled + cached)
├── build_compound_library.py  # seeds.json → master CSV with auto-fetched SMILES
├── validate_smiles.py         # RDKit canonicalization (CI-friendly)
├── export_for_ai.py           # CSV → .smi + 3D-embedded .sdf
├── generate_sfn_analogs.py    # local BRICS + bioisostere + warhead-graft generator
├── score_against_targets.py   # ligand-based screening across 8 MCAS targets
├── score_warheads.py          # 13 cysteine-reactive SMARTS + KEAP1 pharmacophore filter
├── run_qsar.py                # RandomForest QSAR on PyTDC tasks (hERG/AMES/BBB)
└── rank_hypotheses.py         # multi-objective composite ranking + hypothesis-doc updates

notebooks/                     # Same pipeline in Jupyter form (01-05)
experiments/                   # Standardized experiment reports (EXP-001 … EXP-005)
```

## Setup

```bash
git clone https://github.com/mrdulasolutions/MCAS.Opensource.git
cd MCAS.Opensource
python -m venv .venv && source .venv/bin/activate
pip install -e . PyTDC scikit-learn 'setuptools<81'
```

Python 3.9+ (3.10+ preferred). The .venv approach avoids macOS system Python.

## Run the whole pipeline end-to-end

```bash
python scripts/build_compound_library.py
python scripts/validate_smiles.py
python scripts/generate_sfn_analogs.py
python scripts/score_warheads.py
python scripts/score_against_targets.py
python scripts/run_qsar.py
python scripts/rank_hypotheses.py
```

Wall-clock on a CPU laptop: under 3 minutes after the first PyTDC download.

## High-leverage issues open right now

(Roughly in order of impact-for-effort.)

1. **Sensitivity analysis on the composite weights in `rank_hypotheses.py`.**
   Sweep each of the 6 weights ±50%, report which compounds enter/leave
   each top-10. Easy starter task.
2. **Better SA score.** Replace the proxy in `generate_sfn_analogs.py` with
   the actual RDKit-contrib Ertl SAS. ~30 lines.
3. **DeepChem / ChemProp QSAR.** Train a graph neural net on the same
   PyTDC tasks as `run_qsar.py`; commit as `run_qsar_graphconv.py`.
4. **Multi-target / polypharmacology score.** Count how many MCAS-relevant
   targets each compound hits above a threshold; reward in the composite.
5. **Selectivity penalty.** Score against a hERG, kinome, and NHR panel
   proxy; penalize promiscuous binders.
6. **REINVENT 4 on Colab.** [`notebooks/03_reinvent_generation_colab.ipynb`](../notebooks/03_reinvent_generation_colab.ipynb)
   is wired up but hasn't been run. Run it, commit the generated SMILES
   under a new `EXP-006` report.
7. **KEAP1 docking with smina or Vina.** Top-50 from
   [`outputs/ranked_remission.csv`](../outputs/ranked_remission.csv)
   against PDB 4L7B / 5FNQ / 6T7V. Replace the ligand-similarity score in
   `outputs/docking_KEAP1.csv` with a physics score.
8. **Pull ChEMBL mast-cell assays.** Train a real β-hex / tryptase
   release predictor.
9. **Enamine REAL availability API hook.** For each generated analog,
   flag whether it's catalog-orderable.
10. **PubMed auto-scan per top compound.** Surface prior MCAS literature.

Open an issue tagged `good-first-issue` if you want to claim one before
starting.

## Style + conventions

- Black-formatted Python; line length 100.
- Type hints on public functions.
- Docstrings describe **what + why**, not how.
- Every output CSV gets a `method` column making the methodology
  explicit.
- Every script is idempotent and re-runnable from a clean checkout.

## CI

`.github/workflows/validate.yml` runs `validate_smiles.py` on PRs touching
`data/compounds/`. We will expand CI to cover the full pipeline once
runtimes are predictable.

## Code of conduct + license

- MIT — see [LICENSE](../LICENSE).
- Code of Conduct — see [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).
- Security — see [SECURITY.md](../SECURITY.md).
