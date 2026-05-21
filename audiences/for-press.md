# For journalists, science writers, and press

Short version: this is an open, MIT-licensed, public-research project for
MCAS / MCAD. Hypotheses only — no medical claims, no products, no patents.

## What's here

A reproducible AI + cheminformatics pipeline that ranks compounds
(pharma drugs, herbs, supplements, novel analogs) by their plausibility
as MCAS / MCAD rescue, maintenance, or remission candidates.

The headline finding so far: **sulforaphane** (the broccoli-sprout
isothiocyanate that covalently activates the cytoprotective Nrf2 pathway
via its KEAP1 target) ranks #1 in the remission category — ahead of
FDA-approved KIT inhibitors. The ranking is fully open and reproducible
on any laptop in three minutes.

## What this repository is NOT

- Not a treatment recommendation.
- Not a clinical study.
- Not a peer-reviewed paper.
- Not affiliated with pharma.
- Not a 501(c)(3) (yet).

If you write about this, **please do not frame it as a cure or a treatment**.
It is hypothesis-generation infrastructure that needs wet-lab and clinical
validation before any compound can be called a treatment for anyone.

## Quotable framing (use freely)

- "An MIT-licensed, public hypothesis-generation pipeline for MCAS / MCAD."
- "The team uses open chemistry databases (PubChem), AI safety prediction
  (PyTDC), and pharmacophore + warhead analysis to rank thousands of
  compounds across rescue, maintenance, and remission categories."
- "Top-ranked predictions are pre-registered as standardized experiment
  reports under [`experiments/`](../experiments/) — designed to be
  validated, falsified, or extended by any researcher."
- "Sulforaphane, the active compound in broccoli sprouts, currently ranks
  first in the remission category based on a composite of evidence,
  target similarity, covalent-warhead presence, and predicted safety."

## Quotable caveats (please include)

- "These are computational hypotheses. None have been validated in human
  trials specifically for MCAS."
- "MCAS patients are advised by clinicians and consensus guidelines not
  to self-experiment with supplements; even 'natural' compounds can
  trigger flares or interact dangerously with prescription medications."
- "The repository's authors explicitly disclaim medical advice and
  recommend that patients work with mast-cell specialists."

## Numbers as of the most recent push

(Check the commit log + repo for live numbers.)

- **54** anchor compounds (pharma + herbs + supplements + biologics) in
  the curated library.
- **113** locally-generated SFN-class candidate analogs.
- **8** MCAS-relevant targets scored.
- **5** standardized experiments published.
- **MIT** license.

## Contact

- **Responsible entity:** MR Dula Medical (a DBA of MR Dula Enterprise, LLC, Raleigh, NC, USA).
- **Canonical contact directory:** [CONTACT.md](../CONTACT.md).
- **Public discussion:** [GitHub issues](https://github.com/mrdulasolutions/MCAS.Opensource/issues).
- **Press inquiry:** open an [issue tagged `press`](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?labels=press)
  with your outlet and your deadline; we will respond within 48 hours.
- **Background:** the audience-specific docs in [`audiences/`](../audiences/)
  describe the project's posture toward patients, clinicians, researchers,
  nonprofits, industry, and developers.
