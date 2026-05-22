---
id: EXP-008
title: Sensitivity analysis on the six composite weights
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

# Sensitivity analysis — how fragile is the composite ranking?

> ⚠️ **Not medical advice.** Research/hypothesis use only.

## 1. Hypothesis

The composite ranking from EXP-005 weights six signals:

| Weight | Nominal | What it weights |
|--------|---------|-----------------|
| `w_evidence` | 0.30 | Curated `evidence_level` (`high` / `medium` / `low`) |
| `w_target` | 0.35 | Per-category target-similarity mix |
| `w_qed` | 0.10 | QED for generated analogs only |
| `w_warhead` | 0.10 | Covalent-warhead score (KEAP1 axis) |
| `w_safety` | 0.15 | (1 − hERG) + (1 − AMES) average |
| `w_bbb_context` | 0.05 | BBB penetration (signed by category) |

EXP-006 + EXP-007 showed the ranking discriminates correctly at the
nominal weights. The question now is: **how much do those rankings
depend on the particular weight values we chose?**

> A defensible ranking should survive ±50% perturbations of any single
> weight with Spearman ρ ≥ 0.9 against the baseline ranking, in every
> category. Top-1 picks should rarely change.

Falsifiable: if any single weight perturbation drops ρ below 0.9 or
flips the top-1 candidate in remission (sulforaphane), the ranking is
fragile and the report needs that caveat surfaced.

## 2. Method

In silico — weight-sensitivity sweep.

For each of the six weights:
1. Multiply by 0.5 (half) and 1.5 (one-and-a-half), holding the other
   five at nominal.
2. Re-compute composite for every compound in
   `data/compounds/MCAS_Compound_Library_v1.csv` + every
   SFN-class generated analog.
3. Re-rank within each category.
4. Compare to the baseline ranking on three metrics:
   - **Spearman ρ** — full-list rank correlation.
   - **Top-10 Jaccard** — |perturbed ∩ baseline| / |perturbed ∪ baseline| for the top-10 sets.
   - **Top-1 stability** — does the #1 candidate change?

Total: 6 weights × 2 scales × 3 categories = **36 perturbations**.

## 3. Inputs

| Input | File / commit |
|-------|--------------|
| Library | `data/compounds/MCAS_Compound_Library_v1.csv` |
| Generated analogs | `outputs/reinvent_generated.csv` |
| Target scores | `outputs/docking_*.csv` |
| Warhead scores | `outputs/warhead_scores.csv` |
| QSAR | `outputs/qsar_predictions.csv` |

## 4. Parameters

```bash
python scripts/sensitivity_analysis.py
```

No randomness. Fully deterministic given the inputs.

## 5. Environment

```text
Python: 3.9.6
RDKit:  2023.9.6
Hardware: Apple Silicon Mac, CPU only
```

## 6. Outputs

| File | Description |
|------|-------------|
| `outputs/sensitivity_analysis.csv` | One row per (weight, scale, category) — Spearman ρ, Top-10 Jaccard, Top-1 changes, lists of entered/left compounds |
| `outputs/sensitivity_top10_changes.csv` | Detail rows: every compound that entered or left a top-10 across all 36 perturbations |

## 7. Interpretation

### Per-weight robustness (mean across 6 perturbations per weight)

| Weight | Mean ρ | **Min ρ** | Mean Top-10 J | Top-1 stable |
|--------|--------|-----------|---------------|--------------|
| `w_evidence` | 0.981 | **0.933** | 0.858 | 100% |
| `w_target` | 0.984 | 0.958 | 0.970 | 83% |
| `w_qed` | 0.996 | 0.985 | 1.000 | 100% |
| `w_warhead` | 0.994 | 0.982 | 0.970 | 100% |
| `w_safety` | 0.990 | 0.985 | 1.000 | 83% |
| `w_bbb_context` | 0.995 | 0.988 | 1.000 | 100% |

**Every Spearman ρ across every perturbation in every category is
≥ 0.933.** The pre-registered floor was 0.9 — the actual floor is
0.933. The ranking is **robust** to single-weight perturbations.

### Top-1 stability

Of 36 perturbations:
- **34 keep the same top-1 candidate** in their category.
- 2 perturbations flip top-1, both involving `w_target` or
  `w_safety` at extreme scales. Specifically:
  - `w_safety × 1.5` swaps the top of rescue (still inside the H1
    backbone) and maintenance (curcumin still in top 3).
  - **Sulforaphane stays #1 in remission across all 12 perturbations**
    that affect the remission category (every weight × every scale).

The headline claim (`SFN is the top remission candidate`) is therefore
not weight-sensitive — it survives every ±50% weight perturbation we
tested.

### Highest-leverage weight changes

The six largest Spearman drops:

| Weight | Scale | Category | ρ | Top-10 J |
|--------|-------|----------|---|----------|
| `w_evidence` | 0.5 | remission | 0.933 | 0.33 |
| `w_target` | 0.5 | maintenance | 0.958 | 1.00 |
| `w_evidence` | 0.5 | rescue | 0.973 | 1.00 |
| `w_target` | 1.5 | rescue | 0.982 | 1.00 |
| `w_warhead` | 0.5 | remission | 0.982 | 0.82 |
| `w_target` | 1.5 | remission | 0.982 | 1.00 |

**The most influential weight is `w_evidence`**, especially in remission
(Top-10 Jaccard 0.33). Halving the evidence weight reshuffles ~7 of 10
remission top-10 entries — generated SFN-class analogs (which carry
`evidence_level = ""` → 0) climb up as the evidence boost on library
compounds shrinks. Top-1 still stays SFN.

This is consistent with EXP-007: evidence weighting is the dominant
defense against unrelated drugs scoring high on incidental safety +
drug-likeness signal. Cutting it down lets more generative analogs
into the top-10 (which is *fine* in principle, but means library
anchors lose their lead).

### What's robust, what isn't

**Robust (perturbing has near-zero effect):**
- `w_qed`, `w_warhead`, `w_bbb_context`. Each touches a subset of the
  population (generated analogs only, KEAP1 axis only, contextual BBB
  weight), so dialing the weight up or down rearranges very little.

**Moderately sensitive:**
- `w_target`, `w_safety`. These touch every compound, so changes
  propagate through the full ranking — but never enough to flip
  top-1 in remission.

**Most sensitive (and informative):**
- `w_evidence`. As discussed in EXP-007, this is the dominant signal.
  Anyone wanting to fit a more principled weighting (e.g. against
  real clinical-response data) should start by re-estimating this
  weight.

## 8. Reproduction

```bash
git clone https://github.com/mrdulasolutions/MCAS.Opensource.git
cd MCAS.Opensource
.venv/bin/python scripts/sensitivity_analysis.py
```

Wall-clock: < 5 seconds on a CPU laptop. No PyTDC / model training
required — uses the cached scoring outputs from prior pipeline runs.

## 9. Limitations

- **Single-weight sweeps only.** Joint perturbations (e.g. halving
  `w_evidence` *and* doubling `w_warhead` simultaneously) are not
  explored. A full Latin-hypercube design over the 6-D weight space
  is the natural follow-up.
- **±50% range chosen by convention.** Wider sweeps (e.g. ±90%) would
  surface different fragilities.
- **Composite formula structure is fixed.** We perturb weights, not
  the formula — so non-linear interactions (e.g. moving from sum to
  product) aren't tested.
- **Baseline weights are author-chosen.** Sensitivity tells you how
  much the *ranking* depends on the *weights*, not how good the
  weights are in absolute terms. That requires real clinical
  response data to fit against (none currently available for MCAS at
  scale).

## 10. Next experiments suggested

1. **Joint-perturbation Latin-hypercube design** — 200-point sweep
   over all six weights simultaneously; report 95% CI on each
   compound's rank.
2. **Wider sweep** — ±90% on each weight to find the rank-breaking
   threshold.
3. **EXP-009** — real Vina / smina KEAP1 docking on top-50 remission
   candidates. Replace `score_KEAP1` from similarity with physics; rerun
   the sensitivity analysis on the new ranking.
4. **Weight fitting** — when MCAS case-series response data becomes
   available (see [audiences/for-academia.md](../audiences/for-academia.md)),
   fit weights against real outcomes via ordinal regression.

## 11. References

- Linked experiments: [EXP-005](EXP-005-multi-objective-ranking.md),
  [EXP-006](EXP-006-known-actives-recovery.md),
  [EXP-007](EXP-007-negative-control-benchmark.md).
- Composite formula definition: [`scripts/rank_hypotheses.py`](../scripts/rank_hypotheses.py).
