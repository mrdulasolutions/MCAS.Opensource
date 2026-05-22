---
id: EXP-010
title: Joint-perturbation Latin-hypercube sweep — full 6-D weight robustness
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

# Joint-perturbation Latin-hypercube — does the ranking survive simultaneous weight changes?

> ⚠️ **Not medical advice.** Research/hypothesis use only.

## Headline

200-sample Latin-hypercube sweep of **all six composite weights simultaneously**
in [0.5×, 1.5×] of nominal:

| Category | Top-1 winner | Frequency at #1 |
|----------|--------------|-----------------|
| Rescue | Fexofenadine | 74.5% (Cetirizine wins remaining 25.5%) |
| Maintenance | Curcumin | **100.0%** |
| Remission | **Erucin** | **91.5%** (Sulforaphane wins remaining 8.5%) |

The ITC family (Erucin / Sulforaphane / PEITC / Iberin / Benzyl-ITC) occupies
the remission top-10 in **≥99% of samples**, with 95% CI rank spread of 0–5.
Even under joint ±50% perturbation of every weight, no compound outside the
ITC + KIT-inhibitor + glucoraphanin set ever appears in the remission top-10.

## 1. Hypothesis

EXP-008 swept each weight individually and showed Spearman ρ ≥ 0.93 across
all 36 single-weight perturbations. The natural follow-up:

> When *all six* weights are perturbed simultaneously across a representative
> sample of the joint [0.5×, 1.5×]⁶ space, do the top-10s stay essentially
> the same compounds — and which compound wins #1 most often?

Falsifiable: if any compound outside the established ITC + KIT-inhibitor set
appears in the remission top-1 in >10% of samples, the ranking is fragile.
(None did.)

## 2. Method

In silico — Latin-hypercube design + full re-rank per sample.

- Generate **200 LHS samples** of `[scale_evidence, scale_target, scale_qed,
  scale_warhead, scale_safety, scale_bbb_context]` uniformly in [0.5, 1.5]^6.
  LHS guarantees each dimension's marginal is covered once per stratum.
- For each sample: compute `weight_i = nominal_i × scale_i`, re-rank each
  category from the cached scoring outputs, record per-compound rank.
- Roll up per (compound, category):
  - `mean_rank` across samples
  - 95% CI: [2.5%, 97.5%] percentile of the rank distribution
  - `top1_frac`: fraction of samples where the compound was #1
  - `top10_frac`: fraction of samples where the compound was in top-10
  - `rank_spread`: 95th − 5th percentile (smaller = more stable)

Sample size 200 was chosen so that the per-compound CI is tight (within ±1
rank for stable compounds) without exhausting Latin-hypercube budget — at
200 each weight gets ~33 strata in the 6-D layout, plenty for variance
estimation.

## 3. Inputs

| Input | File / commit |
|-------|---------------|
| Library + generated SMILES + scores | All cached `outputs/*.csv` from the most recent EXP-009 pipeline run |
| Composite formula + nominal weights | `scripts/sensitivity_analysis.py` (imported by `sensitivity_lhs.py`) |

## 4. Parameters

```bash
python scripts/sensitivity_lhs.py --n-samples 200 --scale-low 0.5 --scale-high 1.5 --seed 42
```

Deterministic: `random.Random(42)`.

## 5. Environment

```text
Python: 3.9.6
RDKit:  2023.9.6
Hardware: Apple Silicon Mac, CPU only
```

## 6. Outputs

| File | Description |
|------|-------------|
| `outputs/sensitivity_lhs.csv` | One row per (compound, category): baseline rank, mean rank, 95% CI, top1 / top10 frequencies, rank spread |
| `outputs/sensitivity_lhs_summary.json` | Per-category top-1 winners + top-10 most-stable anchors |

## 7. Interpretation

### Top-1 winner frequencies

| Rank | Compound | Category | Top-1 frequency |
|------|----------|----------|-----------------|
| 1 | Fexofenadine | rescue | **74.5%** |
| 2 | Cetirizine | rescue | 25.5% |
| 1 | Curcumin | maintenance | **100.0%** |
| 1 | **Erucin** | remission | **91.5%** |
| 2 | Sulforaphane | remission | 8.5% |

**Three category-winning candidates are essentially uncontested.** In the
8.5% of samples where Sulforaphane beats Erucin in remission, the weight
profile is one that depresses the safety bonus and lifts the target-
similarity weight — both anchors have KEAP1-similarity 1.0 because they
were in the reference set, but Sulforaphane has marginally lower hERG.

### Top-10 stability — remission

| Compound | Top-10 frequency | 95% CI rank spread |
|----------|------------------|---------------------|
| Erucin | **100%** | 1 |
| Sulforaphane | **100%** | 1 |
| Phenethyl-ITC | **100%** | 0 |
| Iberin | **100%** | 4 |
| Benzyl-ITC | 99.5% | 5 |
| Masitinib | 86.0% | 30 |
| Glucoraphanin | 81.5% | 41 |
| Midostaurin | 78.0% | 46 |
| Sulforaphene | 76.0% | 7 |
| Allyl-ITC | 58.5% | 10 |

The ITC family is rock-solid. The wider rank spread on Masitinib /
Glucoraphanin / Midostaurin (30–46) is informative: these are KIT TKIs
and a glycosidic precursor; their position depends heavily on which
weights are emphasized (large molecules win on Vina LE, but compete
with smaller ITCs on warhead + safety).

### Top-10 stability — rescue + maintenance

| Category | All top-10 in ≥99% of samples? | Tightest 95% CI | Loosest 95% CI |
|----------|-------------------------------|-----------------|----------------|
| Rescue | Yes (10/10) | 0 | 2 |
| Maintenance | 9/10 | 0 | 8 (resveratrol) |
| Remission | 5/10 (ITC family) | 0 | 46 (Midostaurin) |

The rescue category is the most stable — every H1 antagonist sits
within ±2 ranks of its baseline across all 200 samples. Maintenance is
nearly as stable; resveratrol's 95%CI spread of 8 is the widest in
that category and reflects its dependence on the warhead vs target-
similarity weight balance.

## 8. Reproduction

```bash
.venv/bin/python scripts/sensitivity_lhs.py --n-samples 200
```

Wall-clock: < 10 seconds. Memory: < 300 MB. No model training.

## 9. Limitations

- **200 samples** is adequate for marginal statistics but tighter joint
  inference would benefit from ≥1000.
- **Uniform scaling assumption.** We sample each weight uniformly in
  [0.5×, 1.5×] of nominal. A Bayesian prior centered on the nominal
  weights would be more principled if real ground-truth data existed.
- **Composite structure fixed.** We perturb weights, not the formula.
  Non-linear interactions (e.g., turning the additive composite into a
  geometric mean) aren't tested.
- **Cached scoring inputs.** The LHS doesn't re-run target / warhead /
  QSAR scoring; it uses the current outputs/*.csv. If the underlying
  scores change, this experiment must be rerun.

## 10. Next experiments suggested

1. **Bayesian optimization of weights against EXP-006 recovery** — fit the
   six weights to maximize known-actives recovery@10 (currently a hard
   limit because of reference-set self-similarity, but a real ML target).
2. **Wider scale range** — repeat with [0.1×, 5×] to find the true
   rank-breaking threshold.
3. **Add a 7th dimension** for the Vina LE weight (currently fixed at 0.10).
4. **Per-category weight LHS** — the rescue / maintenance / remission
   target weights are themselves a tunable mix; sweep those too.

## 11. References

- Linked experiments: [EXP-005](EXP-005-multi-objective-ranking.md),
  [EXP-008](EXP-008-sensitivity-analysis.md),
  [EXP-009](EXP-009-keap1-vina-docking.md).
- Latin-hypercube design: McKay MD et al. *A Comparison of Three Methods
  for Selecting Values of Input Variables in the Analysis of Output from
  a Computer Code.* Technometrics 1979.
