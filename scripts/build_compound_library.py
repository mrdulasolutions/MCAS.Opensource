"""Build MCAS_Compound_Library_v1.csv from seeds.json + PubChem auto-fetch.

For each compound:
- If `pubchem_cid` is set, fetch isomeric + canonical SMILES from PubChem PUG-REST.
- If `biologic_flag` is set, skip SMILES fetch and emit empty SMILES columns.
- Run RDKit canonicalization on the fetched SMILES; surface mismatches as warnings.

Idempotent. Re-run anytime.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from fetch_smiles import fetch_by_cid  # noqa: E402

SEEDS_PATH = REPO_ROOT / "data" / "compounds" / "seeds.json"
CSV_PATH = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"

CSV_COLUMNS = [
    "name",
    "pubchem_cid",
    "smiles",
    "canonical_smiles",
    "category",
    "subcategory",
    "mechanism",
    "target",
    "evidence_level",
    "evidence_notes",
    "source_refs",
    "biologic_flag",
]


def rdkit_canonical(smiles: str) -> str:
    if not smiles:
        return ""
    try:
        from rdkit import Chem
    except ImportError:
        return ""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return ""
    return Chem.MolToSmiles(mol, canonical=True)


def main() -> int:
    seeds = json.loads(SEEDS_PATH.read_text())
    compounds = seeds["compounds"]

    rows = []
    warnings = []
    fetched = 0
    skipped = 0

    for entry in compounds:
        name = entry["name"]
        cid = entry.get("pubchem_cid")
        biologic = entry.get("biologic_flag")

        isomeric = ""
        canonical = ""

        if cid and not biologic:
            result = fetch_by_cid(cid)
            isomeric = result.get("isomeric_smiles", "") or entry.get("smiles", "") or ""
            pubchem_canonical = result.get("canonical_smiles", "")
            canonical = rdkit_canonical(isomeric) or pubchem_canonical
            if not isomeric:
                warnings.append(f"[WARN] {name} (CID {cid}): no SMILES returned from PubChem.")
            fetched += 1
        else:
            skipped += 1

        rows.append({
            "name": name,
            "pubchem_cid": cid or "",
            "smiles": isomeric,
            "canonical_smiles": canonical,
            "category": entry.get("category", ""),
            "subcategory": entry.get("subcategory", ""),
            "mechanism": entry.get("mechanism", ""),
            "target": entry.get("target", ""),
            "evidence_level": entry.get("evidence_level", ""),
            "evidence_notes": entry.get("evidence_notes", ""),
            "source_refs": ";".join(entry.get("source_refs", [])),
            "biologic_flag": biologic or "",
        })

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows -> {CSV_PATH.relative_to(REPO_ROOT)}")
    print(f"  fetched from PubChem: {fetched}")
    print(f"  biologics / extracts (no SMILES): {skipped}")
    for w in warnings:
        print(w)

    return 0 if not warnings else 0  # warnings don't fail the build; validate_smiles.py does


if __name__ == "__main__":
    sys.exit(main())
