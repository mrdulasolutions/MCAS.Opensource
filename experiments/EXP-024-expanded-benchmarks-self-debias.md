---
id: EXP-024
title: Expanded recovery/control sets + self-similarity de-bias
status: published
hypothesis_category: methodology
run_date: 2026-07-27
authors:
  - name: MR Dula Medical
    role: maintainer
license: MIT
---

# Expanded benchmarks + self-similarity de-bias

> ⚠️ **Not medical advice.**

## 1. Hypothesis

recovery@5/@10 were weak (~5–10%) partly because library anchors that also sit
in `TARGET_REFERENCES` score Tanimoto ≈ 1.0 against themselves, crowding the
top of each ranked list. Expanding the held-out active set and **excluding
self-matches (T ≥ 0.99) in favor of the next-best reference** should improve
strict recovery without destroying coarse recovery@20 or negative-control precision.

## 2. Method

1. Expand `data/benchmarks/known_actives.json` to **≥50** held-out clinical /
   literature mast-cell drugs (not in the compound library).
2. Expand `data/benchmarks/negative_controls.json` to **≥100** unrelated drugs.
3. Change `best_similarity()` in `score_against_targets.py` to skip refs with
   Tanimoto ≥ 0.99; record `score_raw_with_self` for diagnostics.
4. Re-run target scoring, ranking, and both benchmark scripts.
5. Update CI audit floors if needed (still require recovery@20 ≥ 0.90 on the
   *original* metric definition; report expanded-set recovery separately).

## 3. Outputs

- Updated benchmark JSONs
- Rebuilt `outputs/docking_*.csv` with debiased scores
- `outputs/benchmark_known_actives.csv`
- `outputs/benchmark_negative_controls.csv`

## 4. Reproduction

```bash
python scripts/score_against_targets.py
python scripts/rank_hypotheses.py
python scripts/benchmark_known_actives.py
python scripts/benchmark_negative_controls.py
python scripts/check_audit_gates.py
```

## 5. Limitations

- Expanded actives still literature-curated, not ChEMBL-auto-pulled at scale.
- Self-debias can slightly lower scores of true class members that are
  near-duplicates of a single reference; second-best ref usually remains high.
- Benchmark composite in `benchmark_known_actives.py` must stay aligned with
  `rank_hypotheses.py` (drift risk as the composite grows).
