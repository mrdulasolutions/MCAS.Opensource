# Agent Card — OpenMCAS Hypothesis Agent

> 🤖 This is the human-readable version of the [Agent2Agent (A2A) protocol](https://google.github.io/A2A/) agent card. The canonical machine-readable manifest lives at:
> - [`.well-known/agent-card.json`](.well-known/agent-card.json) (current A2A spec path)
> - [`.well-known/agent.json`](.well-known/agent.json) (legacy A2A path)
> - [`a2a.json`](a2a.json) (root convenience copy)

> ⚠️ **Not medical advice.** Hypothesis-generation only. See [docs/disclaimers.md](docs/disclaimers.md).

---

## Identity

| Field | Value |
|---|---|
| **Name** | OpenMCAS Hypothesis Agent |
| **Version** | 0.1.0 |
| **License** | MIT |
| **Provider** | MR Dula Medical (DBA of MR Dula Enterprise, LLC) — Raleigh, NC, USA |
| **Repository** | https://github.com/mrdulasolutions/MCAS.Opensource |
| **Documentation** | [README.md](README.md) |
| **Code of Conduct** | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| **Security / safety reporting** | [SECURITY.md](SECURITY.md) |

## Status

**This is a manifest, not a hosted service (yet).** All skills described
below are implemented as scripts in this repository and runnable locally
on a CPU laptop in about 3 minutes. A hosted A2A endpoint is on the
[roadmap](ROADMAP.md). Until then, treat the agent card as a contract: any
A2A-compliant orchestrator can wire against the skill names and parameters
described here, and the underlying behavior is what `scripts/` already does.

## Provider details

- **Doing business as:** MR Dula Medical
- **Legal entity:** MR Dula Enterprise, LLC
- **Location:** Raleigh, North Carolina, USA
- **Contact:** [GitHub issues](https://github.com/mrdulasolutions/MCAS.Opensource/issues) (open, traceable, audience-routed)
- **Press contact:** [audiences/for-press.md](audiences/for-press.md)
- **Academic / clinical / nonprofit / industry contact:** see [audiences/](audiences/)

## Capabilities

- **Streaming responses:** no (batch only)
- **Push notifications:** no
- **State transition history:** no
- **Multi-modal input:** text, JSON
- **Output formats:** text, JSON, CSV, Markdown
- **Authentication:** public — no key required; contributions land via GitHub PRs
- **Data provenance:** PubChem PUG-REST · AlphaFold DB · PyTDC · hand-curated MCAS literature

## Skills

The agent exposes 10 skills. Each maps to a script (or scripts) in the
repository — meaning every skill is independently reproducible from a
clean checkout.

### 1. `library.search`
Search the curated MCAS / MCAD compound library by name, PubChem CID,
category, target, mechanism, or evidence level.
- **Backing:** [`data/compounds/MCAS_Compound_Library_v1.csv`](data/compounds/MCAS_Compound_Library_v1.csv)
- **Examples:** "list rescue compounds with high evidence", "find compounds targeting KEAP1", "get SMILES for sulforaphane"

### 2. `library.add_compound`
Propose a new compound for the library. Validates PubChem CID,
auto-fetches canonical SMILES, opens a GitHub PR.
- **Backing:** [`scripts/build_compound_library.py`](scripts/build_compound_library.py), [`scripts/fetch_smiles.py`](scripts/fetch_smiles.py)
- **Skill guide:** [`.claude/skills/openmcas-add-compound/SKILL.md`](.claude/skills/openmcas-add-compound/SKILL.md)

### 3. `triggers.report`
Submit an anonymous trigger pattern. **No PHI captured.**
- **Backing:** [`data/triggers/MCAS_Triggers_v1.csv`](data/triggers/MCAS_Triggers_v1.csv)
- **Skill guide:** [`.claude/skills/openmcas-report-trigger/SKILL.md`](.claude/skills/openmcas-report-trigger/SKILL.md)

### 4. `screen.ligand_based`
Ligand-based virtual screening against 8 MCAS targets (MRGPRX2, KIT,
KEAP1, HRH1, HRH2, CYSLTR1, BTK, GLP1R). Tanimoto / Morgan radius 2,
2048 bits.
- **Backing:** [`scripts/score_against_targets.py`](scripts/score_against_targets.py)
- **Experiment report:** [EXP-002](experiments/EXP-002-ligand-based-target-screening.md)

### 5. `screen.warhead`
Covalent-warhead SMARTS detection (13 patterns) + KEAP1 pharmacophore
filter. Returns warhead score in [0, 1].
- **Backing:** [`scripts/score_warheads.py`](scripts/score_warheads.py)
- **Experiment report:** [EXP-003](experiments/EXP-003-covalent-warhead-scoring.md)

### 6. `qsar.predict`
ADMET QSAR — predicts hERG (cardiac), AMES (mutagenicity), BBB (blood-brain
barrier). RandomForest on Morgan FP, trained on PyTDC tasks. Validation
AUC 0.89–0.91.
- **Backing:** [`scripts/run_qsar.py`](scripts/run_qsar.py)
- **Experiment report:** [EXP-004](experiments/EXP-004-admet-qsar.md)

### 7. `generate.sfn_analogs`
Generate SFN-class candidate analogs via BRICS recombination + bioisosteric
substitution + warhead grafting. Seeds: SFN, iberin, erucin, sulforaphene,
allyl-ITC, benzyl-ITC, phenethyl-ITC.
- **Backing:** [`scripts/generate_sfn_analogs.py`](scripts/generate_sfn_analogs.py)
- **Experiment report:** [EXP-001](experiments/EXP-001-sfn-seeded-analog-generation.md)

### 8. `rank.hypotheses`
Multi-objective composite ranking: evidence + target similarity + warhead
score + ADMET safety + drug-likeness. Auto-updates the Top-10 tables in
`hypotheses/*.md`.
- **Backing:** [`scripts/rank_hypotheses.py`](scripts/rank_hypotheses.py)
- **Experiment report:** [EXP-005](experiments/EXP-005-multi-objective-ranking.md)
- **Skill guide:** [`.claude/skills/openmcas-run-experiment/SKILL.md`](.claude/skills/openmcas-run-experiment/SKILL.md)

### 9. `experiment.create_report`
Scaffold a new standardized experiment report (`EXP-NNN-*.md`) from the
11-section template.
- **Backing:** [`experiments/EXPERIMENT_TEMPLATE.md`](experiments/EXPERIMENT_TEMPLATE.md)
- **Skill guide:** [`.claude/skills/openmcas-new-experiment-report/SKILL.md`](.claude/skills/openmcas-new-experiment-report/SKILL.md)

### 10. `hypothesis.propose`
Submit a falsifiable hypothesis (rescue / maintenance / remission /
injury / trigger / cross-cutting) for community review.
- **Backing:** [`.github/ISSUE_TEMPLATE/hypothesis_proposal.md`](.github/ISSUE_TEMPLATE/hypothesis_proposal.md)

## Authentication

Public. No key required. Contribution provenance comes from GitHub.

When the hosted endpoint is deployed (see roadmap), authentication
options under consideration:
- **Bearer tokens** for sustained contributors.
- **GitHub App** auth for PR-creating skills.
- Read-only skills (search, score, predict) remain unauthenticated.

## A2A integration example

For any A2A-compatible orchestrator, the agent card at
`.well-known/agent-card.json` is the contract. Once the hosted endpoint
ships, calling `screen.ligand_based` will look like:

```json
{
  "skill": "screen.ligand_based",
  "input": {
    "smiles": "CS(=O)CCCCN=C=S",
    "targets": ["KEAP1", "MRGPRX2", "KIT"]
  }
}
```

Until then, the equivalent CLI invocation is:

```bash
python scripts/score_against_targets.py
```

(scoring the full library + generated analogs against all 8 targets in one shot).

## Disclaimers (do not strip)

- **Medical advice:** None. Hypothesis-generation only.
- **Self-experimentation:** Outputs of this agent must not be acted on
  for self-treatment.
- **Patient safety:** No PHI is ever captured. Trigger reports are
  pattern-only.
- **IP:** MIT license. No patents shall encumber compounds whose
  hypothesis-stage discovery is published in this repository.

## Versioning

The agent card version (`0.1.0`) increments according to:
- **Major** — breaking skill schema changes.
- **Minor** — new skills, new fields.
- **Patch** — documentation, reference-data refreshes, contact updates.

Cite the agent card + the git commit hash for reproducibility.
