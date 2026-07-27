# Roadmap

A living document. Things at the top of each section are higher priority.

## Now (v0.2.x) — shipped

- ✅ Curated **118-compound** MCAS library + SFN-class generation + multi-target scoring.
- ✅ Multi-objective ranking with ChEMBL, mast-cell RF, Kelch Vina, C151 adduct.
- ✅ Streamlit viewer v0.2 + HF Space + CI audit gates + metric honesty.
- ✅ **EXP-023** — KEAP1 BTB Cys-151 encounter docking (PDB 5DAD) fused with adduct energy.
- ✅ **EXP-024** — Expanded known-actives (≥50) + negative controls (≥100) + self-similarity de-bias.
- ✅ **EXP-025** — Generated novelty filter + Enamine REAL flags on rankings / UI.
- ✅ **Zenodo snapshot prep** — `.zenodo.json` + `scripts/deposit_zenodo.py` + `outputs/zenodo/`.
- ✅ **Wet-lab partner pack** — panel CSV, academic/CRO emails, tracker under `docs/wet-lab-partner-pack/`.

## Next (v0.3) — after first partner engagement

1. **True covalent docking** (CovDock / GNINA covalent / OpenMM) — replace encounter proxy.
2. **ChEMBL-auto expansion** of recovery set to 100+ actives with assay-level labels.
3. **Execute wet-lab partner run** — first β-hex panel results as EXP-026+ (positive or negative).
4. **Mint Zenodo DOI** — run `python scripts/deposit_zenodo.py --deposit` with `ZENODO_TOKEN` + GitHub release.
5. **Package refactor** — installable `openmcas/` library + unit tests beyond SMILES/audit floors.
6. **CYP / GST / UGT** metabolism QSAR for SFN-class liability.

## Then (v0.x+2)

- DeepChem GraphConv QSAR delta vs RandomForest.
- Real REINVENT 4 RL on Colab GPU.
- PubMed auto-scan per top compound.
- Combination scoring (pairs / triples).

## Later (v0.5)

- Patient-data infrastructure beyond GitHub issues.
- iPSC-derived mast cell readouts.
- Quarterly Zenodo DOI snapshots.
- 501(c)(3) fiscal home exploration.

## Big-picture (v1.0)

- Continuous wet-lab validation campaign on top-30 each quarter.
- First wet-lab-validated remission candidate (pos or neg) as 1.0 release.

## Not on the roadmap (intentionally)

- Selling anything.
- Recommending self-experimentation.
- Patenting compounds.
- Closed-source forks.
- Embargoed results.

## How to push something onto the roadmap

Open an [issue tagged `roadmap`](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?labels=roadmap)
with: (a) what, (b) why, (c) who would do it, (d) what success looks like.
