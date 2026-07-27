---
title: OpenMCAS Hypothesis Browser
emoji: 🧬
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.50.0
app_file: app.py
pinned: false
license: mit
short_description: "Open MCAS/MCAD hypothesis browser — rankings, audits, why + falsify."
hf_oauth: false
preload_from_hub: []
tags:
  - mcas
  - mcad
  - mast-cell-activation-syndrome
  - drug-discovery
  - cheminformatics
  - sulforaphane
  - keap1
  - open-science
---

# OpenMCAS — Hypothesis Browser (v0.2)

> ⚠️ **Not medical advice.** Research / hypothesis-generation only. Not a substitute for clinical care. Do not self-treat. Full disclaimer: [docs/disclaimers.md](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/disclaimers.md).

This Space is a read-only browser for the [**OpenMCAS** open hypothesis engine](https://github.com/mrdulasolutions/MCAS.Opensource) — an MIT-licensed pipeline that ranks compounds (pharma + herbs + supplements + AI-generated analogs) for MCAS / MCAD **rescue**, **maintenance**, and **remission** potential.

## What you can do here (v0.2)

- Browse **top-candidate cards** with a one-line “why this ranked”.
- Open **Drivers + Falsify me** on any compound (plain English, not just JSON).
- Filter by source (library vs AI-generated), evidence level, warhead, or name/mechanism.
- Read the **honest recovery curve** (@5 / @10 / @20 / @50) — coarse recovery@20 is strong; strict @5/@10 are weak and we show that.
- Inspect **negative-control precision@10** (unrelated drugs should stay out of every top-10).
- Deep-dive ADMET, ChEMBL pIC50, mast-cell stabilizer probability, KEAP1 Vina, C151 adduct scores.
- Browse targets, triggers, and injury-mechanism tables.

## Current headline numbers (committed artifacts)

- Library anchors: **118**
- Known-actives recovery@20: **~95.2%** (20/21) · recovery@10: **~9.5%** · recovery@5: **~4.8%**
- Negative-control precision@10: **100%**
- Remission leaders: **Erucin ≈ Sulforaphane** (SFN-class isothiocyanates)

## What this Space is NOT

- Not a hosted compute endpoint. It serves **pre-computed** predictions only.
  Re-running the pipeline happens in the [GitHub repo](https://github.com/mrdulasolutions/MCAS.Opensource); the Space refreshes whenever new outputs are pushed.
- Not a clinical decision tool. Every value is a research hypothesis, not a recommendation.
- Not wet-lab validation. In-silico only until a partner runs the preregistered assays.

## Provider

**MR Dula Medical** (a DBA of MR Dula Enterprise, LLC), Raleigh, NC, USA.
Independent open-research project. MIT license. No pharma affiliation, no patents, no paywalls.

## Source

- Code + data: https://github.com/mrdulasolutions/MCAS.Opensource
- Documentation: https://github.com/mrdulasolutions/MCAS.Opensource#readme
- Agent Card (Agent2Agent protocol): https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/AGENT_CARD.md
- Contribute: https://github.com/mrdulasolutions/MCAS.Opensource/issues/new/choose
