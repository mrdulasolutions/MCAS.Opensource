"""Joint-perturbation Latin-hypercube sweep of the six composite weights.

Extends EXP-008 (single-weight sweeps) by perturbing all six weights
simultaneously. Each weight is sampled uniformly from [0.5 × nominal,
1.5 × nominal] via a Latin-hypercube design — covers the joint space
much more efficiently than a full grid.

For each compound the script reports:
  - baseline_rank      rank at nominal weights
  - mean_rank          mean rank across N LHS samples
  - rank_95_ci_low     2.5 percentile rank
  - rank_95_ci_high    97.5 percentile rank
  - rank_spread        rank_95_ci_high - rank_95_ci_low (smaller = more stable)
  - top_n_membership   fraction of samples that placed the compound in top-N

Per-category. Output: outputs/sensitivity_lhs.csv + console summary.

Used as the methodology check in EXP-010.
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sensitivity_analysis import (  # noqa: E402
    BASELINE_WEIGHTS,
    CATEGORY_TARGETS,
    composite,
    load_records,
    rank_by_category,
)

OUT_CSV = REPO_ROOT / "outputs" / "sensitivity_lhs.csv"
OUT_SUMMARY_JSON = REPO_ROOT / "outputs" / "sensitivity_lhs_summary.json"


def latin_hypercube(n_samples: int, n_dims: int, seed: int = 42) -> list[list[float]]:
    """Stratified Latin-hypercube samples in [0, 1]^n_dims."""
    rng = random.Random(seed)
    # Each dimension gets each strip exactly once, shuffled independently.
    cols = []
    for _ in range(n_dims):
        col = [(i + rng.random()) / n_samples for i in range(n_samples)]
        rng.shuffle(col)
        cols.append(col)
    return [[cols[d][i] for d in range(n_dims)] for i in range(n_samples)]


def percentile(values: list[int], pct: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    k = (len(s) - 1) * pct / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(s[int(k)])
    return s[f] + (s[c] - s[f]) * (k - f)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Joint LHS weight perturbation.")
    parser.add_argument("--n-samples", type=int, default=200, help="LHS samples per category (default 200).")
    parser.add_argument("--scale-low", type=float, default=0.5, help="Lower scale (0.5 = halve weight).")
    parser.add_argument("--scale-high", type=float, default=1.5, help="Upper scale (1.5 = increase 50%).")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    records = load_records()
    weight_names = list(BASELINE_WEIGHTS.keys())
    n_dims = len(weight_names)
    lhs = latin_hypercube(args.n_samples, n_dims, args.seed)

    # Map [0,1] → [scale_low, scale_high]
    def scale_sample(s):
        return [args.scale_low + u * (args.scale_high - args.scale_low) for u in s]

    print(f"LHS sweep: {args.n_samples} samples × {n_dims} weights")
    print(f"  scale range: ×{args.scale_low} → ×{args.scale_high}")
    print(f"  seed: {args.seed}")
    print()

    # Baseline rankings
    baseline = {}
    for cat in ("rescue", "maintenance", "remission"):
        order, scores = rank_by_category(records, BASELINE_WEIGHTS, cat)
        baseline[cat] = {n: i + 1 for i, n in enumerate(order)}
        print(f"  baseline {cat:<11}  {len(order)} candidates")

    # Per compound + category, collect ranks across LHS samples
    rank_lists: dict[tuple[str, str], list[int]] = {}
    top1_counts: dict[tuple[str, str], int] = {}
    top10_counts: dict[tuple[str, str], int] = {}
    sample_progress_every = max(1, args.n_samples // 10)

    for s_idx, sample in enumerate(lhs, start=1):
        scales = scale_sample(sample)
        weights = {name: BASELINE_WEIGHTS[name] * scale for name, scale in zip(weight_names, scales)}
        for cat in ("rescue", "maintenance", "remission"):
            order, _ = rank_by_category(records, weights, cat)
            for rank, name in enumerate(order, start=1):
                rank_lists.setdefault((name, cat), []).append(rank)
                if rank == 1:
                    top1_counts[(name, cat)] = top1_counts.get((name, cat), 0) + 1
                if rank <= 10:
                    top10_counts[(name, cat)] = top10_counts.get((name, cat), 0) + 1
        if s_idx % sample_progress_every == 0:
            print(f"  ... {s_idx}/{args.n_samples} samples done")

    # Roll up
    rows = []
    for (name, cat), ranks in rank_lists.items():
        baseline_rank = baseline[cat].get(name, len(baseline[cat]) + 1)
        mean_r = sum(ranks) / len(ranks)
        lo = percentile(ranks, 2.5)
        hi = percentile(ranks, 97.5)
        rows.append({
            "name": name,
            "category": cat,
            "baseline_rank": baseline_rank,
            "mean_rank": round(mean_r, 2),
            "rank_95_ci_low": int(lo),
            "rank_95_ci_high": int(hi),
            "rank_spread": int(hi - lo),
            "top1_frac": round(top1_counts.get((name, cat), 0) / args.n_samples, 3),
            "top10_frac": round(top10_counts.get((name, cat), 0) / args.n_samples, 3),
            "n_samples": args.n_samples,
        })

    rows.sort(key=lambda r: (r["category"], r["mean_rank"]))
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print()
    print(f"wrote {OUT_CSV.relative_to(REPO_ROOT)}  ({len(rows)} rows)")

    # Per-category summary
    summary = {}
    for cat in ("rescue", "maintenance", "remission"):
        sub = [r for r in rows if r["category"] == cat]
        top1_winners = sorted(sub, key=lambda r: -r["top1_frac"])[:3]
        top10_anchor = sorted(sub, key=lambda r: -r["top10_frac"])[:10]
        # Median rank spread (smaller = more stable)
        spreads = sorted(r["rank_spread"] for r in sub)
        median_spread = spreads[len(spreads) // 2] if spreads else None
        summary[cat] = {
            "n_candidates": len(sub),
            "top1_winners_by_frequency": [
                {"name": r["name"], "frac_at_top1": r["top1_frac"], "baseline_rank": r["baseline_rank"]}
                for r in top1_winners
            ],
            "top10_most_stable": [
                {"name": r["name"], "top10_frac": r["top10_frac"], "rank_spread": r["rank_spread"]}
                for r in top10_anchor
            ],
            "median_rank_spread": median_spread,
        }

    OUT_SUMMARY_JSON.write_text(json.dumps(summary, indent=2))
    print(f"wrote {OUT_SUMMARY_JSON.relative_to(REPO_ROOT)}")
    print()
    print("=== Per-category top-1 winners (% of LHS samples placing them at #1) ===")
    for cat in ("rescue", "maintenance", "remission"):
        print(f"  {cat}:")
        for w in summary[cat]["top1_winners_by_frequency"]:
            print(f"    {w['name']:<35}  top1 in {100*w['frac_at_top1']:.1f}% of samples  (baseline rank {w['baseline_rank']})")
    print()
    print("=== Top-10 stability (compounds present in top-10 of ≥X% of LHS samples) ===")
    for cat in ("rescue", "maintenance", "remission"):
        print(f"  {cat}:")
        for r in summary[cat]["top10_most_stable"][:10]:
            print(f"    {r['name']:<35}  top10 in {100*r['top10_frac']:5.1f}% of samples  (95%CI spread {r['rank_spread']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
