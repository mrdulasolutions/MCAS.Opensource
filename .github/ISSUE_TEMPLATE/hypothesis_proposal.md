---
name: Hypothesis proposal
about: Propose or critique a rescue / maintenance / remission hypothesis
title: '[hypothesis] '
labels: hypothesis
---

## Hypothesis

One sentence. e.g. "Sulforaphane reverses MCAS priming in oxidative / post-viral
phenotypes by restoring Nrf2 tone via combined KEAP1 binding and DNMT
inhibition."

## Category

- [ ] Rescue
- [ ] Maintenance
- [ ] Remission
- [ ] Injury mechanism
- [ ] Trigger
- [ ] Cross-cutting

## Falsifiable predictions

What experiment, if it returned a negative result, would refute this hypothesis?

## Existing evidence

- Linked compounds (by name in `data/compounds/seeds.json`):
- Linked injury mechanisms (by row in `data/injury_mechanisms/`):
- Linked triggers:
- Key citations:

## Proposed AI tests

How could this be evaluated via `notebooks/02_qsar_deepchem.ipynb`,
`03_reinvent_generation_colab.ipynb`, `04_virtual_screening.ipynb`, or
`05_hypothesis_ranking.ipynb`?

## Proposed wet-lab tests

If we get bench time, what assay would test this? See
[docs/wet_lab_protocols.md](../../docs/wet_lab_protocols.md).

---
> ⚠️ This is hypothesis-generation only — not medical advice.
