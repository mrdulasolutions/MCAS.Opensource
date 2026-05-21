---
name: openmcas-new-experiment-report
description: Scaffold a new experiments/EXP-NNN-*.md from the standard template and prefill it with the user's hypothesis, method, inputs, parameters, environment, and reproduction steps. Triggers when the user says "new experiment", "create an experiment report", "document this run", "EXP-006", or similar.
---

# Create a new standardized experiment report

Guide the contributor through scaffolding a new
`experiments/EXP-NNN-*.md` from `experiments/EXPERIMENT_TEMPLATE.md` and
fill it out from what they describe.

## Steps

1. **Determine the next free EXP-NNN.** Read `experiments/README.md` and
   find the highest existing ID; the new one is `EXP-(N+1)`. Zero-pad to 3
   digits.

2. **Determine the slug.** Short kebab-case description of what the
   experiment does. e.g. `keap1-docking-top50`, `chembl-mast-cell-import`,
   `polypharmacology-bonus`. Final filename:
   `experiments/EXP-NNN-<slug>.md`.

3. **Ask the contributor for the seven core fields, if not provided:**
   - **Hypothesis** — what they expected, falsifiably.
   - **Method** — in silico (ligand-based / structure-based / generative /
     QSAR), wet-lab (which cell line + readout), clinical (case observation),
     or observational.
   - **Inputs** — files + commits + external data sources used.
   - **Parameters** — actual command-line invocation or config.
   - **Environment** — Python / RDKit / hardware.
   - **Outputs** — files produced + schema of each.
   - **Interpretation** — what was learned. Be honest about whether the
     hypothesis survived.

4. **Copy `EXPERIMENT_TEMPLATE.md`** → `EXP-NNN-<slug>.md` and fill in
   every section from the contributor's answers. Leave nothing blank;
   "n/a — see section X" is acceptable if a section truly doesn't apply.

5. **Update `experiments/README.md`** — add a row to the Index table.

6. **Cross-link** if relevant:
   - If the experiment depends on a prior `EXP-NNN`, list it under
     "References."
   - If it suggests follow-ups, name them with placeholder IDs.

7. **Pre-registration vs published.** If the contributor is running the
   experiment *now*, mark `status: running`. If results are already in,
   mark `status: published`. Pre-registration is encouraged for wet-lab
   and any single-shot analysis where cherry-picking is a risk.

## Sections that contributors often skip — push back on these

- **Limitations.** Every method has them. Make them write a real one.
- **Reproduction.** Must include exact commands + commit hash + expected
  wall-clock + memory. If a non-author can't reproduce in a half-day,
  it isn't a proper experiment report.
- **Next experiments suggested.** Even a one-liner is useful.

## Sanity checks before commit

- The YAML frontmatter parses cleanly.
- `status` is one of: `draft`, `running`, `published`, `retracted`.
- `hypothesis_category` is one of: `rescue`, `maintenance`, `remission`,
  `injury_mechanism`, `trigger`, `methodology`.
- The Index table in `experiments/README.md` is updated.
- All referenced files in `Inputs` exist at the named commit.

## Commit + PR

```bash
git add experiments/EXP-NNN-<slug>.md experiments/README.md
git commit -m "EXP-NNN: <short title>"
```

PR title should be `EXP-NNN: <short title>`. PR body links to the
experiment file and summarizes the hypothesis + result in 3 sentences.

## When you should NOT create a new experiment

- For a trivial parameter tweak (just commit the change to the existing
  script — don't ceremoniously call it an experiment).
- For a refactor (use a conventional commit).
- For a doc edit (use a conventional commit).

The bar for `experiments/EXP-NNN` is: there's a hypothesis, a method, a
result, and they could be replicated by an independent party.
