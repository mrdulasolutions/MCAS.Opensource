# How to contribute

This project is open by design. Patients, clinicians, chemists, ML researchers,
and skeptics are all welcome. Below is the fastest path in for each role.

## Patients & families

- Open a [trigger report](../.github/ISSUE_TEMPLATE/trigger_report.md) with what
  set off your flare, how long after exposure, and any patterns you've noticed.
- Open a [compound suggestion](../.github/ISSUE_TEMPLATE/compound_suggestion.md)
  if there's a pharma drug, herb, or supplement you've found helpful (or
  harmful) that isn't in the library.
- We never ask for personal medical data. You don't have to share anything you
  don't want to. Anonymous contributions are fine.

## Clinicians

- Same routes as above, plus case-series data (de-identified) on response to
  any compound listed in the library.
- Push back on hypotheses you think are wrong — open an issue and explain.

## Chemists & medicinal chemists

- Audit `data/compounds/seeds.json` for SMILES / CID errors.
- Propose SAR studies on the flavonoid + isothiocyanate scaffolds.
- Vet any REINVENT-generated SMILES (in `outputs/`) for synthetic
  accessibility and obvious red flags before they get cited in a hypothesis doc.

## ML / cheminformatics

- Improve `notebooks/02_qsar_deepchem.ipynb` — better featurizers, multi-task
  models, calibration.
- Improve `notebooks/03_reinvent_generation_colab.ipynb` — better priors,
  better scoring config, fragment-based design seeds.
- Improve `notebooks/04_virtual_screening.ipynb` — better pocket
  identification, ensemble docking, free-energy perturbation.
- Train a real mast-cell-degranulation predictor: scrape ChEMBL / PubChem
  bioassays tagged with mast cell readouts, build a model, publish it here.

## Wet-lab labs / CROs

- Propose a validation campaign on top hits from `outputs/ranked_*.csv`. See
  [docs/wet_lab_protocols.md](wet_lab_protocols.md).
- Pre-registration is required before unblinded results.

## PR flow

1. Fork → branch off `main` → make changes.
2. If touching `data/`, run:
   ```bash
   python scripts/build_compound_library.py
   python scripts/validate_smiles.py
   ```
   and commit any updated CSVs.
3. Open a PR with a clear description and (if relevant) link to the issue.
4. CI runs the SMILES validator on data PRs.
5. A maintainer will review and merge.

## Style notes

- New compounds / mechanisms / triggers go in the data CSVs first, then prose
  in the corresponding `hypotheses/*.md`. Data is the source of truth.
- Cite sources concisely in `evidence_notes` and `source_refs`. Author + year
  is enough; we can chase the PMID.
- No marketing language. No "miracle cure" claims. Frame everything as
  hypothesis + evidence level + how it can be falsified.

## License

MIT. By contributing, you agree your contribution is MIT-licensed too.
