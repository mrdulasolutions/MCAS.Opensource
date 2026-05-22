# Roadmap

A living document. Things at the top of each section are higher priority.

## Now (v0.x)

- ✅ Curated 54-compound MCAS library (pharma + herbs + supplements + biologics).
- ✅ Injury-mechanism + trigger frameworks.
- ✅ 7 natural ITC seeds for SFN-class generation (113 candidates).
- ✅ Ligand-based screening across 8 MCAS targets.
- ✅ Covalent-warhead SMARTS detection + KEAP1 pharmacophore filter.
- ✅ ADMET QSAR (hERG / AMES / BBB), AUC 0.89–0.91.
- ✅ Multi-objective ranking → rescue / maintenance / remission top-10s.
- ✅ Standardized experiment report format (6 published).
- ✅ Audience-segmented onboarding docs.
- ✅ A2A agent card + canonical contact info.
- ✅ **Known-Actives Recovery benchmark — 100% recovery@20** (EXP-006).
- ✅ Auto-generated hypothesis tables with timestamp + commit-hash provenance.
- ✅ Streamlit public viewer + Hugging Face Spaces deployment recipe.
- ✅ **Live public viewer deployed:** https://huggingface.co/spaces/MRDula/openmcas-browser
- ✅ **GitHub Actions auto-sync** of the HF Space on every pipeline rerun (sync-hf-space.yml).
- ✅ **Negative-control benchmark** (EXP-007) — 100% precision@10 across all categories under realistic scoring.
- ✅ **Sensitivity analysis** (EXP-008) — min Spearman ρ = 0.93 under ±50% weight sweeps; SFN #1 stable in 100% of remission perturbations.

## Next (v0.x+1) — credibility & accessibility first

These five are the next 2–4 weeks of high-leverage work (per the
"100x vision" framing — credibility, accessibility, polish):

1. **Real Vina/smina KEAP1 docking** on PDB 4L7B for the top-50 ranked
   remission candidates; replace the ligand-similarity score in
   `outputs/docking_KEAP1.csv` with physics for that one target. Biggest
   single scientific upgrade available — moves from ligand similarity
   to structure-based binding.
2. **Expand recovery + control sets via ChEMBL bioassay pull** (`β-hexosaminidase release`,
   `mast cell degranulation`, `LAD2`). Targets: 50+ actives, 100+ controls.
3. **Joint-perturbation Latin-hypercube weight sweep** — 200-point
   sweep over all six weights simultaneously; report 95% CI on each
   compound's rank (extends EXP-008).
4. **Pipeline-driven Space refresh** — extend the sync workflow to
   also rebuild the rankings (run the full pipeline) on a schedule,
   commit refreshed CSVs, and let the existing sync job pick them up.
5. **Real REINVENT 4 RL run on Colab** seeded on top-10 SFN-class
   analogs from EXP-001; replace the deterministic BRICS generator
   with policy-gradient generation for the next analog batch.

## Then (v0.x+2)

- ChEMBL bioassay pull → train a true mast-cell-degranulation predictor.
- Polypharmacology bonus + selectivity penalty in `rank_hypotheses.py`.
- DeepChem GraphConv QSAR for AUC delta vs. RandomForest.
- REINVENT 4 on Colab GPU — actual RL run seeded on top-10.
- Enamine REAL Space availability check for top generated analogs.
- PubMed auto-scan per top compound (prior art surfacing).

## Later (v0.5)

- Patient-data infrastructure beyond GitHub issues (structured intake,
  privacy-preserving, optional clinician validation).
- Multi-pred QSAR — CYP1A2 / 2C9 / 2C19 / 2D6 / 3A4 inhibition.
- xTB / DFT electrophilicity ranking for covalent warheads.
- KEAP1 covalent docking (CovDock or GOLD-Covalent at Cys-151).
- iPSC-derived mast cell readouts in the wet-lab protocol references.
- Combination scoring (synergy predictions for pairs / triples).
- Pre-registration registry with DOI minting per experiment.
- Quarterly Zenodo DOI snapshots.

## Big-picture (v1.0)

- A wet-lab partner running a continuous validation campaign on the
  current top-30 every quarter, published as new `EXP-NNN` reports.
- A 501(c)(3) fiscal home (or hosted under an existing one — see
  [audiences/for-nonprofits.md](audiences/for-nonprofits.md)).
- A patient-coreference network for trigger / response data without
  PHI capture.
- A 1.0 release with the first wet-lab-validated remission candidate
  (positive or negative — both are publishable).

## Not on the roadmap (intentionally)

- Selling anything.
- Recommending self-experimentation.
- Patenting compounds.
- Closed-source forks.
- Embargoed results.

## How to push something onto the roadmap

Open an [issue tagged `roadmap`](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?labels=roadmap)
with: (a) what, (b) why, (c) who would do it, (d) what success looks like.
