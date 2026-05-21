# Pull request

## What this PR does

One or two sentences.

## Audience this touches

- [ ] Patients / caregivers (changes to `audiences/for-patients.md`, `hypotheses/*`, glossary, FAQ)
- [ ] Clinicians
- [ ] Researchers / academics
- [ ] Nonprofits / funders
- [ ] Industry
- [ ] Developers (`scripts/`, `notebooks/`, CI)
- [ ] All (top-level README, license, governance)

## Type of change

- [ ] New compound in `data/compounds/seeds.json`
- [ ] New trigger / injury mechanism row in `data/`
- [ ] New experiment report under `experiments/EXP-NNN-*.md`
- [ ] Code change (`scripts/` / `notebooks/`)
- [ ] Documentation change (`docs/` / `audiences/` / `hypotheses/`)
- [ ] Governance / process change (`CODE_OF_CONDUCT.md`, `SECURITY.md`, `ROADMAP.md`)
- [ ] Other:

## Reproducibility checklist (for code + data + experiment changes)

- [ ] Ran `python scripts/build_compound_library.py` (if `seeds.json` changed)
- [ ] Ran `python scripts/validate_smiles.py` — 0 failures
- [ ] Ran `python scripts/rank_hypotheses.py` (if scoring weights or methods changed)
- [ ] Updated `experiments/README.md` Index (if new experiment)
- [ ] Updated relevant `hypotheses/*.md` (if new top-rated compound)
- [ ] No PHI committed
- [ ] No proprietary / patent-encumbered data committed

## What an independent reviewer should check

(Make it easy for them to verify your work.)

## Linked issues

Closes #
References #

---
> See [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md). By submitting this PR
> you agree your contribution is MIT-licensed.
