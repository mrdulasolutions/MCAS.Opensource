# Triggers

Real-world triggers reported by MCAS/MCAD patients and described in the
literature, mapped to the pathway / receptor they act through and to candidate
counter-compounds from the library.

## File

- **`MCAS_Triggers_v1.csv`** — categorized triggers + pathway + linked compounds + hypothesis seed.

## Schema

| Column | Description |
|--------|-------------|
| `trigger_category` | Top-level group (food, smell, physical, stress, infection, toxin, hormonal, medication) |
| `specific_trigger` | Plain-language examples |
| `pathway_receptor` | Mechanism / receptor / signaling node |
| `evidence_level` | `high` / `medium` / `low` |
| `linked_injury` | Foreign key into `data/injury_mechanisms/MCAS_Injury_Mechanisms_v1.csv` |
| `linked_compounds` | Semicolon-separated names from `data/compounds/seeds.json` |
| `hypothesis_seed` | One-line testable hypothesis for the AI pipeline |

## Contributing

The trigger list is alive. Patient-reported triggers are gold — we'll triage and
validate before merging. Open a [trigger report issue](../../.github/ISSUE_TEMPLATE/trigger_report.md).
