# Roadmap

A living document. Things at the top of each section are higher priority.

## Now (v0.1.x) — shipped

- ✅ Curated **118-compound** MCAS library (pharma + herbs + supplements + biologics + cannabinoids/terpenes/flavonoids expansions).
- ✅ Injury-mechanism + trigger frameworks.
- ✅ SFN-class generation (BRICS + bioisostere + RL-style local path; **176** generated SMILES in current outputs).
- ✅ Ligand-based screening across MCAS targets (incl. SYK, PTGS2, CNR2).
- ✅ Covalent-warhead SMARTS + catechol/pyrogallol + KEAP1 pharmacophore filter.
- ✅ ADMET QSAR (hERG / AMES / BBB).
- ✅ Multi-objective ranking → rescue / maintenance / remission.
- ✅ Experiment reports through **EXP-022** (+ template).
- ✅ Audience-segmented onboarding docs + A2A agent card.
- ✅ Known-actives recovery + negative-control + sensitivity + LHS audits.
- ✅ KEAP1 Vina (Kelch) + C151 adduct proxy + ChEMBL predictors + mast-cell RF (AUC 0.916).
- ✅ Enamine REAL procurement packet (EXP-017).
- ✅ Wet-lab prereg + CRO outreach packet + preprint draft + patient summary.
- ✅ Streamlit public viewer on HF Spaces + weekly pipeline refresh + auto-sync CI.
- ✅ **Viewer v0.2** — top cards, “why ranked”, honest recovery@5/10/20, negative-control table, falsify-me.
- ✅ **CI audit gates** (`scripts/check_audit_gates.py`) — floor checks on recovery@20, recovery@10, precision@10, library size.
- ✅ Metric honesty pass — badges / README / Space card no longer over-claim recovery@20 as 100% or library as 54.

## Next (v0.2+) — credibility & wet-lab bridge

These are the *actual* open work items (previous “Next” items that shipped were moved up):

1. **Covalent KEAP1 docking at C151** (BTB domain) — CovDock / GOLD-Covalent on PDB 4IFL or similar; non-covalent Kelch is already done (EXP-009).
2. **Expand recovery + control sets** via ChEMBL mast-cell assays — target **50+ actives, 100+ controls**; rebalance remission expected labels.
3. **Self-similarity de-bias** in composite / recovery — so recovery@5/@10 become meaningful without discarding anchors.
4. **Generated-analog novelty filter** in ranking + Space — flag near-duplicates of SFN/Erucin/Iberin; surface Enamine availability on cards.
5. **Zenodo DOI snapshot** of a frozen commit + preprint lockstep (n=118, current audits).
6. **First wet-lab partner run** of preregistered β-hex / LAD2 panel on SFN, Erucin, PEA, Luteolin + ≥2 negatives.

## Then (v0.x+2)

- Polypharmacology bonus + selectivity penalty in `rank_hypotheses.py`.
- DeepChem GraphConv QSAR delta vs RandomForest.
- Real REINVENT 4 RL on Colab GPU (replace remaining BRICS-heavy tops).
- PubMed auto-scan per top compound (prior-art surfacing).
- Multi-pred QSAR — CYP1A2 / 2C9 / 2C19 / 2D6 / 3A4 inhibition.
- Package refactor: installable `openmcas/` library + unit tests beyond SMILES/audit floors.

## Later (v0.5)

- Patient-data infrastructure beyond GitHub issues (structured, privacy-preserving).
- xTB / DFT electrophilicity ranking for covalent warheads.
- iPSC-derived mast cell readouts in wet-lab protocol references.
- Combination scoring (synergy for pairs / triples).
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
