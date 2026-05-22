"""Validate every SMILES in MCAS_Compound_Library_v1.csv.

Two checks:
  (A) RDKit parse — every non-biologic SMILES must parse cleanly.
  (B) Identity sanity — for known ITC-class anchors, the canonical SMILES
      must actually contain the expected functional group (isothiocyanate
      `N=C=S` or thioether for erucin). This catches the class of bug
      where a wrong PubChem CID returns a valid-but-wrong SMILES (e.g.
      arsanilic acid sneaking in as 'Erucin').

Exit codes:
  0 = all checks pass
  1 = one or more rows failed
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"


IDENTITY_CHECKS = {
    # name → required SMARTS the canonical SMILES must contain
    "Sulforaphane":                "[CH3][S](=[O])CCCCN=C=S",
    "Iberin":                      "[CH3][S](=[O])CCCN=C=S",
    "Erucin":                      "[CH3]SCCCCN=C=S",
    "Sulforaphene":                "[CH3][S](=[O])/C=C/CCN=C=S",
    "Allyl isothiocyanate":        "C=CCN=C=S",
    "Benzyl isothiocyanate":       "c1ccccc1CN=C=S",
    "Phenethyl isothiocyanate":    "c1ccccc1CCN=C=S",
    # Note: glucoraphanin (SFN precursor) deliberately excluded — it carries an
    # S-glucosinolate, not the free isothiocyanate, so an N=C=S check would
    # wrongly flag it.
}


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
    identity_checked = 0

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

            # Identity sanity check for known anchors
            if name in IDENTITY_CHECKS:
                expected_smarts = IDENTITY_CHECKS[name]
                # Glucoraphanin row in our library is the precursor; only enforce ITC presence
                # for the actual ITCs. Use a more permissive pattern via direct SMILES match.
                patt = Chem.MolFromSmarts(expected_smarts) or Chem.MolFromSmiles(expected_smarts)
                if patt is None:
                    failures.append(f"{name}: bad identity SMARTS in validator '{expected_smarts}'")
                    continue
                if not mol.HasSubstructMatch(patt):
                    failures.append(
                        f"{name}: SMILES '{smiles}' does NOT contain expected substructure "
                        f"'{expected_smarts}'. This usually means the PubChem CID in seeds.json "
                        f"points to the wrong compound."
                    )
                    continue
                identity_checked += 1

    print(f"Validated {total} rows")
    print(f"  small molecules with parseable SMILES: {smiles_rows}")
    print(f"  identity-sanity-checked anchors:        {identity_checked}/{len(IDENTITY_CHECKS)}")
    print(f"  biologics / extracts (skipped):         {biologic_rows}")
    print(f"  failures:                                {len(failures)}")
    for f in failures:
        print(f"  [FAIL] {f}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
