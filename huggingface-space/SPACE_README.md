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
short_description: "Open hypothesis browser for MCAS/MCAD compounds."
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

# OpenMCAS — Hypothesis Browser

> ⚠️ **Not medical advice.** Research / hypothesis-generation only. Not a substitute for clinical care. Do not self-treat. Full disclaimer: [docs/disclaimers.md](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/disclaimers.md).

This Space is a read-only browser for the [**OpenMCAS** open hypothesis engine](https://github.com/mrdulasolutions/MCAS.Opensource) — an MIT-licensed pipeline that ranks compounds (pharma + herbs + supplements + AI-generated analogs) for MCAS / MCAD rescue, maintenance, and remission potential.

## What you can do here

- Browse the **Top-N ranked candidates** per category with composite scores, per-target similarity, covalent-warhead flags, and ADMET safety predictions (hERG / AMES / BBB).
- Filter by source (library vs. AI-generated), evidence level, warhead presence, or substring match on name / mechanism.
- Inspect any single compound's full prediction profile as JSON.
- Read the held-out **Known-Actives Recovery benchmark** results — 21 clinical mast-cell drugs scored blind, with **100% recovery@20**.
- See the underlying **target index**, **trigger map**, and **injury-mechanism framework**.

## What this Space is NOT

- Not a hosted compute endpoint. It serves pre-computed predictions only.
  Re-running the pipeline happens in the [GitHub repo](https://github.com/mrdulasolutions/MCAS.Opensource); the Space refreshes whenever new outputs are pushed.
- Not a clinical decision tool. Every value is a research hypothesis, not a recommendation.

## Provider

**MR Dula Medical** (a DBA of MR Dula Enterprise, LLC), Raleigh, NC, USA.
Independent open-research project. MIT license. No pharma affiliation, no patents, no paywalls.

## Source

- Code + data: https://github.com/mrdulasolutions/MCAS.Opensource
- Documentation: https://github.com/mrdulasolutions/MCAS.Opensource#readme
- Agent Card (Agent2Agent protocol): https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/AGENT_CARD.md
- Contribute: https://github.com/mrdulasolutions/MCAS.Opensource/issues/new/choose
