---
id: EXP-025
title: Generated-analog novelty filter + Enamine availability on rankings/UI
status: published
hypothesis_category: methodology
run_date: 2026-07-27
authors:
  - name: MR Dula Medical
    role: maintainer
license: MIT
---

# Novelty filter + Enamine cards

> ⚠️ **Not medical advice.**

## 1. Hypothesis

Many top `GEN_*` remission candidates are near-exact chain variants of
sulforaphane / erucin / iberin. Ranking them as if they were novel scaffolds
misleads readers. Tagging **Tanimoto-to-SFN-class**, **novelty_score**, and
**Enamine REAL plausibility** (EXP-017), plus a small composite penalty for
near-duplicates, should surface true neighbors honestly.

## 2. Method

1. In `rank_hypotheses.py`, compute per compound:
   - `max_tanimoto_to_library`
   - `tanimoto_to_sfn_class` (max vs 7 ITC seeds)
   - `novelty_score = 1 − max(lib, seed)`
   - `near_duplicate_of_seed` if seed T ≥ 0.90
2. For generated compounds: composite −0.04 if T_seed ≥ 0.90, −0.06 if ≥ 0.95.
3. Join EXP-017 `enamine_lookup.csv` → `real_space_plausible`, `enamine_real_search`.
4. Surface fields in Streamlit cards / deep-dive.

## 3. Outputs

- Extra columns on `outputs/ranked_*.csv`
- Viewer UI updates

## 4. Limitations

- Novelty is fingerprint-based, not scaffold-network MCS.
- Enamine flags are envelope/plausibility URLs, not live vendor stock checks.
