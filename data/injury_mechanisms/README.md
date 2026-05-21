# Injury mechanisms

Mechanisms that "injure" mast cells (prime them for inappropriate degranulation)
or that cause tissue damage downstream from chronic mediator release.

## File

- **`MCAS_Injury_Mechanisms_v1.csv`** — categorized mechanisms with linked compounds and hypothesis seeds.

## Schema

| Column | Description |
|--------|-------------|
| `mechanism_category` | `upstream_*` (priming) / `trigger_*` (acute) / `clonal_*` / `downstream_*` (tissue damage) |
| `specific_injury` | Plain-language description of the insult |
| `pathway` | Molecular pathway / signaling cascade |
| `target` | Primary druggable node (gene symbol where possible) |
| `evidence_level` | `high` / `medium` / `low` |
| `linked_compounds` | Semicolon-separated names from `data/compounds/seeds.json` |
| `hypothesis_seed` | One-line testable hypothesis for the AI pipeline |

## Adding a mechanism

1. Add a row to the CSV.
2. Reference compounds by their `name` in `seeds.json`.
3. Add the corresponding hypothesis prose to `hypotheses/injury_mechanisms.md`.
