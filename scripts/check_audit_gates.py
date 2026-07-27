"""CI audit gates for OpenMCAS rankings.

Reads committed benchmark CSVs and fails if headline audit metrics
regress below documented floors. This is a *floor* check, not a claim
of wet-lab validity.

Floors (as of EXP-021 / EXP-022 composite):
  - Known-actives recovery@20  >= 0.90   (currently ~95.2% = 20/21)
  - Known-actives recovery@10  >= 0.05   (currently ~9.5%  = 2/21; deliberately low floor)
  - Known-actives recovery@5   >= 0.0    (currently ~4.8%  = 1/21; tracked, not gated hard)
  - Negative-control precision@10 == 1.0 (no negative control in any category top-10)
  - Library size                >= 100

Exit codes:
  0  all gates pass
  1  one or more gates fail
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "outputs"
LIB = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"

# Floors — tighten only after a deliberate audit retread lands.
FLOOR_RECOVERY_20 = 0.90
FLOOR_RECOVERY_10 = 0.05
FLOOR_LIBRARY_N = 100


def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path}")
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def recovery_at(rows: list[dict], n: int) -> tuple[int, int, float]:
    valid = [r for r in rows if (r.get("rank_in_expected_category") or "").strip()]
    if not valid:
        return 0, 0, 0.0
    hits = sum(1 for r in valid if float(r["rank_in_expected_category"]) <= n)
    return hits, len(valid), hits / len(valid)


def negative_precision_at_10(rows: list[dict]) -> tuple[int, int, float]:
    """Fraction of negative controls that sit outside every category top-10.

    Ranks are 1-indexed within the category list; a rank > 10 (or equal to
    size+1 when the control ranks after the whole list) is a correct reject.
    """
    if not rows:
        return 0, 0, 0.0
    correct = 0
    for r in rows:
        ok = True
        for cat in ("rescue", "maintenance", "remission"):
            rank_s = (r.get(f"rank_{cat}") or "").strip()
            if not rank_s:
                ok = False
                break
            if float(rank_s) <= 10:
                ok = False
                break
        if ok:
            correct += 1
    return correct, len(rows), correct / len(rows)


def main() -> int:
    failures: list[str] = []
    reports: list[str] = []

    # Library size
    lib = _load_csv(LIB)
    lib_n = len(lib)
    reports.append(f"library_n={lib_n} (floor>={FLOOR_LIBRARY_N})")
    if lib_n < FLOOR_LIBRARY_N:
        failures.append(f"library size {lib_n} < floor {FLOOR_LIBRARY_N}")

    # Known-actives recovery
    actives = _load_csv(OUT / "benchmark_known_actives.csv")
    for n, floor in ((20, FLOOR_RECOVERY_20), (10, FLOOR_RECOVERY_10)):
        hits, total, rate = recovery_at(actives, n)
        reports.append(f"recovery@{n}={hits}/{total}={rate:.1%} (floor>={floor:.0%})")
        if rate < floor:
            failures.append(
                f"recovery@{n} {rate:.1%} ({hits}/{total}) below floor {floor:.0%}"
            )
    hits5, total5, rate5 = recovery_at(actives, 5)
    reports.append(f"recovery@5={hits5}/{total5}={rate5:.1%} (tracked, not hard-gated)")

    # Negative-control precision@10
    negatives = _load_csv(OUT / "benchmark_negative_controls.csv")
    ok, total_n, prec = negative_precision_at_10(negatives)
    reports.append(f"neg_precision@10={ok}/{total_n}={prec:.1%} (floor=100%)")
    if prec < 1.0:
        failures.append(
            f"negative-control precision@10 {prec:.1%} ({ok}/{total_n}) < 100%"
        )

    print("OpenMCAS audit gates")
    print("-------------------")
    for line in reports:
        print(f"  {line}")

    if failures:
        print("\nFAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nAll gates passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
