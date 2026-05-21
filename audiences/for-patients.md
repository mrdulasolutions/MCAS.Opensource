# For patients and caregivers

You're here because you or someone you love has MCAS / MCAD, and you want
something better than what you've been offered. We do too.

> ⚠️ **Read this first.** This repository is a computational research project.
> It does **not** prescribe, diagnose, treat, or cure anything. **Nothing
> here replaces a mast-cell specialist.** Self-experimenting with supplements
> or repurposed drugs can hurt you, especially when MCAS lowers your
> threshold to anything new. The Mastocytosis Society (TMSforacure.org)
> maintains a list of mast-cell-knowledgeable clinicians — start there.
> Full disclaimer in [docs/disclaimers.md](../docs/disclaimers.md).

## What we're trying to do, in plain English

MCAS / MCAD means mast cells release their contents (histamine, tryptase,
prostaglandins, cytokines) when they shouldn't, in response to triggers
that shouldn't trigger them. Current treatment is symptom-by-symptom: H1
and H2 blockers, leukotriene receptor antagonists, sometimes cromolyn or
ketotifen. None of these fix the underlying problem.

This repo is hunting for compounds that might:
- **Rescue** — stop a flare faster (acute mediator blockade).
- **Maintenance** — raise your baseline so triggers don't tip you over.
- **Remission** — reverse the upstream injury that primes the mast cells.

We're using AI + open chemistry databases + public protein structures
to scan thousands of compounds (pharma drugs, herbs, supplements, novel
analogs) and rank them by how plausibly they hit MCAS-relevant targets.
Every prediction is published openly so anyone — academic, clinician,
or another patient — can audit, falsify, or extend it.

## Three things you can do right now

### 1. Share a trigger pattern (anonymously)

If you've identified a trigger nobody seems to talk about — or a counter-
strategy that works for you — open a [trigger report](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?template=trigger_report.md).
We aggregate patterns across patients (you stay anonymous) to refine our
trigger → pathway → counter-compound map.

### 2. Suggest a compound

If a clinician put you on something that helped (or harmed), and we don't
have it in our library yet, [tell us](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?template=compound_suggestion.md).
Same for herbs and supplements. We score them through the AI pipeline and
add them to the ranking.

### 3. Read the hypotheses

The most patient-readable docs are:
- [hypotheses/rescue.md](../hypotheses/rescue.md) — acute flare control.
- [hypotheses/maintenance.md](../hypotheses/maintenance.md) — daily stabilization.
- [hypotheses/remission.md](../hypotheses/remission.md) — root-cause reversal.
- [hypotheses/triggers.md](../hypotheses/triggers.md) — foods, smells, etc.

If anything is jargon-heavy, [open an issue](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?labels=docs-clarification) and we'll rewrite it. Plain English is a feature here.

## What patient data looks like in this repo

- **Triggers**: we collect *patterns* (category + onset + duration), never
  PHI. No names, no diagnoses, no medical records.
- **Compound responses**: anonymous; we never link them to an individual.
- **Case reports**: only from clinicians, only de-identified, only with
  patient consent.

You always own your story. You can delete a contribution at any time by
opening an issue.

## If you want to go deeper

- **[docs/glossary.md](../docs/glossary.md)** — MCAS / mast-cell jargon decoded.
- **[docs/faq.md](../docs/faq.md)** — common patient questions.
- **[docs/wet_lab_protocols.md](../docs/wet_lab_protocols.md)** — what's needed
  to validate a hypothesis at the bench (in case you want to advocate for
  research at your university).

## Resources outside this repo

- **The Mastocytosis Society**: [tmsforacure.org](https://tmsforacure.org)
- **Mast Cell Action (UK)**: [mastcellaction.org](https://www.mastcellaction.org/)
- **Reddit /r/MCAS** and **/r/MastCell** — patient community + lay summaries.

You are not alone in this. We're building the open hypothesis layer so
that the next breakthrough can't be locked behind a patent. Pull up a
chair.
