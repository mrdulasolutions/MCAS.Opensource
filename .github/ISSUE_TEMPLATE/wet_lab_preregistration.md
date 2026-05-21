---
name: Wet-lab pre-registration
about: Pre-register a wet-lab validation campaign BEFORE running, to prevent cherry-picking and lock in the protocol.
title: '[wet-lab] '
labels: wet-lab-preregistration
---

## Pre-registration

> Filing this issue **before** unblinded results is required. After-the-fact
> filings are accepted but get tagged `post-hoc` in the published record.

## Lab + responsible scientist

- Institution / CRO:
- Responsible scientist:
- IRB / IBC reference (if applicable):
- MTA status for cell lines:

## Hypothesis being tested

State plainly and *falsifiably*.

## Compounds being tested

List the compounds from the OpenMCAS library (and their rank in
`outputs/ranked_*.csv` at the time of pre-registration):

| Compound | Source | Current composite rank | Justification |
|---|---|---|---|

## Method

- Cell system: LAD2 / HMC-1 / primary CD34+ / iPSC-derived / other
- Stimulus: substance P / anti-IgE / Compound 48/80 / Ca²⁺ ionophore / LPS / H₂O₂ / SCF
- Readouts: β-hex / histamine ELISA / tryptase ELISA / CD63 flow / cytokine multiplex / Ca²⁺ flux / Nrf2 readouts (HMOX1, NQO1)
- Reference compound for normalization (e.g. cromolyn, quercetin)
- Replicates per condition:
- Dose response (range, # points):

## Statistical analysis

How will you decide what counts as a positive result?

## Pre-specified primary endpoint

The single endpoint that decides whether the hypothesis is supported.
No moving goalposts.

## Pre-specified secondary endpoints

Useful but not decisive.

## Conflicts of interest

Disclose any.

## Funding source

Who's paying. (Per [audiences/for-industry.md](../../audiences/for-industry.md),
industry funding is welcome with no exclusivity or embargo beyond 90 days.)

## Expected completion + publication

When you expect to finish, when you'll post results to this repo.

---
> Once the campaign concludes, follow up with a `experiments/EXP-NNN-*.md`
> report regardless of result direction. Negative results are publishable
> here. See [`audiences/for-academia.md`](../../audiences/for-academia.md).
