---
id: EXP-007
title: Negative-control benchmark — 20 unrelated drugs blind-scored
status: published
hypothesis_category: methodology
run_date: 2026-05-22
authors:
  - name: MR Dula Medical
    role: provider
    affiliation: "DBA of MR Dula Enterprise, LLC; Raleigh, NC, USA"
  - name: OpenMCAS contributors
    role: maintainer
license: MIT
---

# Negative-control benchmark — does the pipeline correctly reject unrelated drugs?

> ⚠️ **Not medical advice.** Research/hypothesis use only.

## 1. Hypothesis

EXP-006 showed 100% recovery@20 for 21 known mast-cell drugs the pipeline
had never seen. That answers *can it find what it should*. The symmetric
question is *does it stay quiet about what it shouldn't*:

> Given 20 widely-used drugs from therapeutic areas with no plausible
> MCAS / MCAD mechanism (statins, antihypertensives, anticonvulsants,
> stimulants, anticoagulants, bisphosphonates, etc.), the pipeline
> should rank every one of them **outside** the top-10 of every
> category — i.e. **precision@10 = 100%**.

Falsifiable: if more than ~5% of negative controls land in any top-10,
the composite is over-rewarding generic drug-likeness or safety profile
rather than mechanism-specific signal.

## 2. Method

In silico — held-out negative-control benchmark.

For each of 20 controls in
[`data/benchmarks/negative_controls.json`](../data/benchmarks/negative_controls.json):

1. Fetch SMILES from PubChem (same code path as the master library).
2. Score blind against the 8 target reference sets, covalent-warhead
   SMARTS, and ADMET QSAR — exactly the EXP-002 + EXP-003 + EXP-004
   pipelines.
3. Compute the composite score for **each of the three categories**
   (rescue, maintenance, remission) using
   [`scripts/rank_hypotheses.py`](../scripts/rank_hypotheses.py)'s
   formula, in **two scoring scenarios**:
   - **Realistic** (`evidence_weight = 0.0`): the production scenario.
     A previously-unknown compound has no curated evidence in
     `seeds.json`, so it gets the same evidence weight as a brand-new
     SMILES from a community contribution — namely **zero**.
   - **Strict** (`evidence_weight = 1.0`): an artificial steelman in
     which we generously credit the control with the same evidence
     weight a clinical drug would get. This stress-tests how much of
     the composite is doing real mechanistic work vs. just rewarding
     existence.
4. Insert each control into the existing
   [`outputs/ranked_<category>.csv`](../outputs/) lists, find its rank
   position.
5. Report **precision@N**: fraction of controls correctly ranked
   **outside** the top-N of that category.

Exclusion criteria for the control list are encoded in
[`negative_controls.json`](../data/benchmarks/negative_controls.json):
not in seeds, not in any reference ligand set, no published mast-cell
or histamine activity, not from a class with incidental anti-allergic
binding.

## 3. Inputs

| Input | File / version |
|-------|----------------|
| Control set | [`data/benchmarks/negative_controls.json`](../data/benchmarks/negative_controls.json) |
| Reference sets | `scripts/score_against_targets.py` |
| Warhead patterns | `scripts/score_warheads.py` |
| QSAR training | PyTDC v1.1.15 (hERG, AMES, BBB_Martins) |
| Comparison rankings | `outputs/ranked_<category>.csv` |

## 4. Parameters

```bash
python scripts/benchmark_negative_controls.py
```

Deterministic: `random_state=0` on all RF models.

## 5. Environment

```text
Python:       3.9.6
RDKit:        2023.9.6
scikit-learn: 1.6.1
PyTDC:        1.1.15
huggingface_hub: 1.8.0
Hardware:     Apple Silicon Mac, CPU only
```

## 6. Outputs

| File | Description |
|------|-------------|
| `outputs/benchmark_negative_controls.csv` | Per-control diagnostic: realistic + strict composites, ranks per category, target hits, warhead, ADMET |

Schema (key columns): `name, pubchem_cid, therapeutic_class, rationale,
smiles, has_warhead, score_KEAP1, score_MRGPRX2, score_KIT, score_HRH1,
score_HRH2, score_CYSLTR1, hERG_score, AMES_score, BBB_score,
composite_<category>, rank_<category>, size_<category>,
composite_<category>_with_high_evidence`.

## 7. Interpretation

### Headline (realistic scenario, `evidence_weight = 0`)

| Category | precision@5 | precision@10 | rank > category size |
|----------|-------------|--------------|----------------------|
| Rescue | **20/20 = 100%** | **20/20 = 100%** | 20/20 = 100% |
| Maintenance | **20/20 = 100%** | **20/20 = 100%** | 20/20 = 100% |
| Remission | **20/20 = 100%** | **20/20 = 100%** | 20/20 = 100% |

**Every negative control ranked *below* every existing entry in every
category.** Zero leaks into any top-10. Combined with the EXP-006
100% recovery@20 result, the pipeline now passes **both directions** of
the credibility test:

- Recovers known actives into the top of expected categories.
- Rejects unrelated drugs from the top of every category.

### Strict scenario (`evidence_weight = 1.0` — generous to controls)

In this artificial steelman where we credit each unknown control with
the same evidence weight as a clinically-validated drug, the picture
is very different:

- **42 of 60** category × control checks land in the top-10.
- Acetaminophen ranks #3 in remission (composite 0.515).
- Finasteride ranks #3 in remission (composite 0.567).
- Amlodipine ranks #3 in remission (composite 0.519).

The takeaway is methodologically important: **evidence weighting is
the dominant signal in the composite**. When a compound has neither
strong target similarity nor a covalent warhead, the only thing keeping
random safe drugs out of the top of the ranking is the evidence
weight being zero by default.

This is a healthy property as long as one rule is enforced:

> **A new compound added to `seeds.json` must not have its
> `evidence_level` defaulted to `high`. Curated evidence requires a
> citation.**

The current schema in
[`data/compounds/seeds.json`](../data/compounds/seeds.json) and the
`compound_suggestion` issue template both make this explicit; the
Claude skill `openmcas-add-compound` also surfaces it. We have not
changed `rank_hypotheses.py` as a result of this experiment because
the production behavior (empty `evidence_level` → weight 0) was
already correct.

### Per-class breakdown (realistic)

All 20 controls ranked *below the bottom* of every existing category
under the production-realistic scoring. The ranks reported as
"15/14" (rescue), "26/25" (maintenance), "100/99" (remission) mean
the control would slot in *after* the last legitimate entry — they
didn't beat any real candidate.

Three controls had a covalent warhead (Amlodipine, Isotretinoin,
Finasteride — each via a Michael acceptor / α,β-unsaturated motif),
which slightly boosted their KEAP1-axis composite, but the absence
of target similarity AND of an evidence boost still kept them out
of the top of the remission list.

## 8. Reproduction

```bash
git clone https://github.com/mrdulasolutions/MCAS.Opensource.git
cd MCAS.Opensource
python -m venv .venv && .venv/bin/pip install -e . PyTDC scikit-learn 'setuptools<81'
.venv/bin/python scripts/benchmark_negative_controls.py
```

Wall-clock: ~2.5 minutes (PyTDC download cached after first run + RF
training + per-control scoring). Memory: ~1.5 GB.

## 9. Limitations

- **20 controls is a small sample.** A 50–100 control set drawn
  randomly from FDA-approved drugs in non-allergic indications
  would tighten the confidence interval.
- **Curation bias.** We selected drugs that *we* believe have no
  MCAS mechanism. A truly random sample of approved drugs would be
  more rigorous.
- **Mechanistic blindness check.** Some controls (e.g. acetaminophen)
  have weak / anecdotal anti-inflammatory effects. The benchmark
  treats them as pure negatives; a reviewer might disagree on edge
  cases.
- **Strict-vs-realistic asymmetry.** The strict result reveals a real
  fragility: the composite is *not* a self-defensive scoring function
  against artificially-boosted controls. We rely on schema discipline
  (citation-required evidence) to prevent that.

## 10. Next experiments suggested

1. **EXP-008** — sensitivity analysis on the six composite weights.
   Now that we know evidence weight is dominant, quantify exactly how
   the ranking shifts when each weight changes ±50%.
2. **EXP-009** — real Vina / smina KEAP1 docking on the top-50
   remission candidates. Replace ligand similarity with physics-based
   binding scores.
3. **Future** — expand the negative-control set to 100 randomly-drawn
   FDA-approved drugs from non-immune indications.
4. **Future** — add a structural-novelty penalty so that compounds
   visually unrelated to *any* anchor (real or generated) get a
   small downweight; reduces the surface area for evidence-weight
   exploits.

## 11. References

- Linked experiments: [EXP-002](EXP-002-ligand-based-target-screening.md),
  [EXP-003](EXP-003-covalent-warhead-scoring.md),
  [EXP-004](EXP-004-admet-qsar.md),
  [EXP-005](EXP-005-multi-objective-ranking.md),
  [EXP-006](EXP-006-known-actives-recovery.md).
- Per-control rationale + therapeutic-class citations in
  [`negative_controls.json`](../data/benchmarks/negative_controls.json).
