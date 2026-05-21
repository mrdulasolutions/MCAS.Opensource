---
name: openmcas-run-experiment
description: Run the full OpenMCAS computational pipeline end-to-end (build library, generate analogs, score warheads, screen targets, QSAR, rank) and produce a clean diff for review. Triggers when the user says "run the pipeline", "regenerate the rankings", "rerun everything", or similar.
---

# Run the OpenMCAS pipeline end-to-end

Walk the contributor through a clean re-run of every script + report on
the resulting diff.

## Order of operations

```bash
.venv/bin/python scripts/build_compound_library.py    # PubChem fetch + RDKit canonicalization
.venv/bin/python scripts/validate_smiles.py           # CI-style validation
.venv/bin/python scripts/generate_sfn_analogs.py      # SFN-class analog generation
.venv/bin/python scripts/score_warheads.py            # 13 cysteine-reactive SMARTS + KEAP1 pharmacophore filter
.venv/bin/python scripts/score_against_targets.py     # ligand-based screening (8 targets)
.venv/bin/python scripts/run_qsar.py                  # PyTDC ADMET QSAR (hERG / AMES / BBB)
.venv/bin/python scripts/rank_hypotheses.py           # composite ranking + hypothesis-doc updates
```

Expected wall-clock: ~3 minutes on a CPU laptop (after the first PyTDC
download).

## Before running

1. Confirm `.venv/` exists and has the right deps. If not:

   ```bash
   python -m venv .venv
   .venv/bin/pip install -e . PyTDC scikit-learn 'setuptools<81'
   ```

2. Confirm you're on a clean working tree, OR explicitly accept that you'll
   commit the regenerated outputs.

## After running

1. **Inspect the diff.** Outputs that changed are typically:
   - `outputs/reinvent_generated.csv`
   - `outputs/docking_*.csv`
   - `outputs/warhead_scores.csv`
   - `outputs/qsar_predictions.csv`
   - `outputs/ranked_*.csv`
   - `hypotheses/rescue.md`, `maintenance.md`, `remission.md` (Top-10 tables)

2. **Run sanity checks** on the rankings before committing:
   - Rescue top 5 should be H1 antihistamines.
   - Maintenance top 5 should include polyphenols + Michael-acceptor compounds.
   - Remission top 5 should be SFN / ITC family + KIT inhibitors.

   If any of these look wrong, stop and investigate before committing —
   it usually means a weight is off in `rank_hypotheses.py` or a
   reference ligand set drifted in `score_against_targets.py`.

3. **Open a PR or commit** with a message that captures *why* this rerun
   was triggered, not just *what* changed:

   ```
   Rerun pipeline after <reason> — <key delta>
   ```

   e.g. "Rerun pipeline after adding 6 new natural ITCs — SFN-class candidates 80→113, remission top-5 unchanged."

## When the run produces something surprising

A new top-1 in any category warrants an experiment report:

```bash
/openmcas-new-experiment-report
```

…to document hypothesis + method + result.

## Failure modes

| Symptom | Likely cause |
|---|---|
| `pkg_resources` not found | setuptools 81+ removed it. `pip install 'setuptools<81'`. |
| PubChem returns empty SMILES | API change; check `fetch_smiles.py` is using `SMILES` / `ConnectivitySMILES`, not the deprecated `IsomericSMILES` / `CanonicalSMILES`. |
| `validate_smiles.py` reports failures | new compound in `seeds.json` has wrong CID or unparseable SMILES. Re-verify CID resolves to expected compound. |
| Generated analog count drops | something in `generate_sfn_analogs.py`'s seeds list got mangled; check the `SEEDS` array. |
| Ranking script raises CSV field mismatch | a new column was added downstream but `write_ranked` is missing it. Use `extrasaction="ignore"` or expand the field union. |
