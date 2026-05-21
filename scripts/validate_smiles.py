"""Validate every SMILES in MCAS_Compound_Library_v1.csv with RDKit.

Exit codes:
  0 = all small-molecule rows parse cleanly
  1 = one or more rows failed RDKit parsing
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"


def main() -> int:
    try:
        from rdkit import Chem
    except ImportError:
        print("[FAIL] rdkit not installed. pip install rdkit", file=sys.stderr)
        return 1

    if not CSV_PATH.exists():
        print(f"[FAIL] missing {CSV_PATH}. Run build_compound_library.py first.", file=sys.stderr)
        return 1

    failures: list[str] = []
    total = 0
    smiles_rows = 0
    biologic_rows = 0

    with CSV_PATH.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            total += 1
            name = row["name"]
            smiles = row["smiles"]
            biologic = row["biologic_flag"]

            if biologic and not smiles:
                biologic_rows += 1
                continue
            if not smiles:
                failures.append(f"{name}: no SMILES and not flagged as biologic")
                continue

            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                failures.append(f"{name}: RDKit could not parse SMILES '{smiles}'")
                continue
            smiles_rows += 1

    print(f"Validated {total} rows")
    print(f"  small molecules with parseable SMILES: {smiles_rows}")
    print(f"  biologics / extracts (skipped): {biologic_rows}")
    print(f"  failures: {len(failures)}")
    for f in failures:
        print(f"  [FAIL] {f}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
