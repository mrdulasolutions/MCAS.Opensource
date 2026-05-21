---
name: openmcas-add-compound
description: Add a pharma drug, herb, supplement, or biologic to the OpenMCAS curated compound library. Use when the user wants to extend data/compounds/seeds.json with a new compound. Triggers when the user says "add a compound", "I want to add X to the library", "include curcumin", or similar.
---

# Add a compound to the OpenMCAS library

You are guiding a contributor through adding a new compound to the
curated MCAS library. The source of truth is `data/compounds/seeds.json`.
The build pipeline auto-fetches SMILES from PubChem and validates with
RDKit, so the contributor should not hand-paste SMILES unless absolutely
necessary.

## Steps to take

1. **Ask the contributor for the basics, if not already provided:**
   - Compound name (common name is fine).
   - Category: `rescue` / `maintenance` / `remission`.
   - Mechanism (one-line: pathway / receptor / target).
   - Evidence level: `high` (human / clinical / approved), `medium` (in vitro on human mast cells + animal + anecdotal), `low` (mechanistic only).
   - Source references (author + year is enough).

2. **Look up the PubChem CID.** Ask the contributor if they know it. If
   not, you can search PubChem (`https://pubchem.ncbi.nlm.nih.gov/`) for
   the canonical name and use the CID from the first hit. **Always
   verify the CID resolves to the expected compound before committing.**

3. **Determine whether it's a small molecule or a biologic.**
   - Small molecule: leave `biologic_flag` unset; pubchem_cid filled.
   - Peptide / protein / antibody / enzyme / plant extract: set
     `biologic_flag` to one of `peptide_*`, `monoclonal_antibody_*`,
     `enzyme`, `enzyme_mixture`, `plant_extract` and leave `pubchem_cid: null`.

4. **Edit `data/compounds/seeds.json`** — insert a new entry into the
   `compounds` array following the existing schema. Keep alphabetical-ish
   ordering by category (rescue compounds together, etc.).

5. **Run the build:**

   ```bash
   .venv/bin/python scripts/build_compound_library.py
   .venv/bin/python scripts/validate_smiles.py
   ```

   Confirm `validate_smiles.py` reports 0 failures.

6. **Optionally re-run the scoring + ranking** if the contributor wants
   to see how the new compound ranks:

   ```bash
   .venv/bin/python scripts/score_against_targets.py
   .venv/bin/python scripts/score_warheads.py
   .venv/bin/python scripts/run_qsar.py
   .venv/bin/python scripts/rank_hypotheses.py
   ```

7. **Update the relevant hypothesis doc** (`hypotheses/<category>.md`)
   with a short note about the compound if it's a substantive addition.
   The ranking script already auto-updates the Top 10 table.

8. **Commit + open a PR** with a clear message: "Add <Name> to library
   under <category>" + the citation reference.

## Sanity checks

- SMILES must be valid (RDKit parses cleanly).
- Evidence level must be honest — if there's only a single anecdote,
  it's `low`, not `medium`.
- No medical claims in `evidence_notes`. Pharmacology / mechanism only.
- For supplements with safety caveats, mention them in `evidence_notes`
  (e.g. "high-dose PEITC has documented mutagenicity at high concentrations").

## If the contributor isn't sure about category

- "Helps me when I'm flaring acutely" → likely **rescue**.
- "I take it daily for prevention" → likely **maintenance**.
- "Targets the upstream cause / immune dysregulation" → **remission**.
- Edge cases (LDN, omega-3, vitamin D) usually land in **maintenance**.

## When NOT to add

- Compounds with no published mechanism *and* no human reports — let
  them know we'd love to see the mechanism worked out first.
- Anything that's only relevant outside the MCAS axis — politely
  decline + point to the [hypothesis_proposal](../../../.github/ISSUE_TEMPLATE/hypothesis_proposal.md)
  template instead.

## Reminders to surface explicitly

- This is hypothesis-generation, not a treatment list.
- Per the disclaimers, **never** recommend self-experimentation.
- Patient-reported responses are anonymized at intake.
