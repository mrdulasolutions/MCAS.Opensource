# OpenMCAS — Claude Code skill pack

Drop this repository into [Claude Code](https://claude.ai/code) and you get
four turnkey contribution skills. They guide you through the most common
contribution flows so you don't need to learn the repo's internals first.

## Skills included

| Skill | When to use |
|---|---|
| `openmcas-add-compound` | Add a pharma drug, herb, supplement, or biologic to the curated library. |
| `openmcas-report-trigger` | Record a trigger pattern (food / smell / physical / chemical / etc.) with anonymized provenance. |
| `openmcas-run-experiment` | Run the full pipeline (build + score + rank) end-to-end and produce a clean diff. |
| `openmcas-new-experiment-report` | Scaffold a new `experiments/EXP-NNN-*.md` from the standard template, prefilled with your hypothesis. |

## How to use them

Inside Claude Code (in this repo):

```text
/openmcas-add-compound
/openmcas-report-trigger
/openmcas-run-experiment
/openmcas-new-experiment-report
```

Or just say in natural language: *"Add montelukast to the library"* or
*"I want to report a new trigger pattern"* and Claude will pick up the
relevant skill.

## Want to add a skill?

Skills are just markdown files in `.claude/skills/<name>/SKILL.md`. Open a
PR with yours. Useful candidates we'd merge:
- `openmcas-validate-paper` — compare a paper's findings against the
  current ranking.
- `openmcas-pull-chembl-bioassay` — fetch + import ChEMBL mast-cell assays.
- `openmcas-docking-job` — wrapper to launch a smina docking batch.
