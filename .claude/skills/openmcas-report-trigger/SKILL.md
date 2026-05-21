---
name: openmcas-report-trigger
description: Capture a new MCAS trigger pattern (food, smell, physical, chemical, stress, infection, toxin, hormonal, medication) and add it to data/triggers/MCAS_Triggers_v1.csv with pathway mapping and linked counter-compounds. Triggers when the user says "report a trigger", "add this trigger", "I noticed when I'm around X I flare", or similar.
---

# Report a new MCAS trigger pattern

You are helping a contributor (often a patient or caregiver) record a
trigger they've noticed. Their pattern adds signal to the
trigger → pathway → counter-compound map.

## Guardrails (read first)

- **Never solicit PHI.** No names, diagnoses, dates of care, clinician
  identities, medical-record content.
- **Patterns only.** Category, onset, duration, what helps. Always.
- **Never give medical advice.** Surface counter-compound *hypotheses*
  from the library; never tell the contributor what to take.
- **Anonymize at intake.** The contributor's submission is their pattern,
  not their identity.

## Information to collect

Ask only what's missing:

1. **Trigger category** — food / smell-VOC / physical / stress /
   infection / toxin / hormonal / medication / other.
2. **Specific trigger** — e.g. "aged cheese", "perfumes", "hot showers",
   "morphine", "menstrual cycle".
3. **Onset after exposure** — minutes vs hours vs delayed (24+h).
4. **Duration** — how long the flare lasts.
5. **Symptom domain** — skin / GI / respiratory / neuro / cardiovascular
   (just dominant systems, no specifics).
6. **Anything that blunts it** — if the contributor identifies any
   counter-strategy (pre-medication, environmental control, specific
   supplement), capture it.
7. **Suspected pathway** (optional, only if they have a guess) —
   MRGPRX2, FcεRI, histamine liberator, substance P, etc.

## Where it goes

Add a row to `data/triggers/MCAS_Triggers_v1.csv` with columns:

| Column | Value |
|--------|-------|
| `trigger_category` | from step 1 |
| `specific_trigger` | from step 2 |
| `pathway_receptor` | suggested if known; otherwise leave generic ("direct mast cell sensitization", "unclear") |
| `evidence_level` | `high` (multiple patients / published), `medium` (single patient + published mechanism), `low` (one-off) |
| `linked_injury` | best-fit row id from `data/injury_mechanisms/MCAS_Injury_Mechanisms_v1.csv` |
| `linked_compounds` | semicolon-separated names from `data/compounds/seeds.json` that plausibly counter the pathway |
| `hypothesis_seed` | one-line: "[Trigger] activates [pathway]; [counter-compound] hypothesized to blunt via [mechanism]." |

## Updating the prose

Append a short note to `hypotheses/triggers.md` under the relevant
category section. Keep the tone neutral and the framing as hypothesis.

## Counter-compound suggestion logic

Use this lookup when proposing `linked_compounds`:

| Pathway | Reasonable counter-compounds (hypothesis only) |
|---|---|
| MRGPRX2 (chemicals / smells / opioids / contrast / venom) | resveratrol, quercetin, luteolin, cromolyn, ketotifen |
| FcεRI / IgE (allergens) | omalizumab, cromolyn, ketotifen, flavonoid stack |
| Histamine liberator / DAO insufficiency | DAO, vitamin C, quercetin, low-histamine diet |
| Substance P / neurogenic stress | luteolin (BBB), quercetin, LDN, baicalein |
| Oxidative / Nrf2 suppression | sulforaphane, NAC, α-lipoic, EGCG |
| Gut barrier / LPS | butyrate, curcumin, quercetin, baicalein, omega-3 |
| KIT-driven (clonal) | masitinib, avapritinib, midostaurin |
| Xenobiotic / mold / TILT | sulforaphane, NAC, silibinin, α-lipoic |

These are **hypotheses**, not recommendations. Always preface with
"hypothesized counter-strategy: …" in any user-facing message.

## After the row is in

Offer to commit + push:

```bash
git add data/triggers/MCAS_Triggers_v1.csv hypotheses/triggers.md
git commit -m "Add trigger: <category> / <specific>"
```

Or open a GitHub issue from the [trigger report template](../../../.github/ISSUE_TEMPLATE/trigger_report.md)
if the contributor would prefer that flow.

## When to escalate

If the contributor describes a *severe / anaphylactic* trigger pattern or
appears to be asking for medical advice on managing the trigger,
politely stop the intake and direct them to:

1. A mast-cell-knowledgeable clinician (TMS list at [tmsforacure.org](https://tmsforacure.org)).
2. Emergency care if a flare is active or imminent.

We are documenting patterns for research, not providing care.
