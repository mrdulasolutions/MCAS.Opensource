"""Pull ChEMBL assays specifically measuring mast-cell-relevant readouts.

EXP-011 pulled per-target binding. This goes after assays measuring the
actual MCAS-relevant biology:

  - β-hexosaminidase release
  - Histamine release
  - Tryptase release
  - LAD2 / HMC-1 / RBL-2H3 / BMMC / mast cell degranulation

Strategy: search ChEMBL assays by description-text matching MCAS-readout
keywords. For each matched assay, pull activity records (active /
inactive flag + numeric value). Store per-assay records into
outputs/chembl_mast_cell/<keyword>_<assay_id>.csv plus an aggregated
outputs/chembl_mast_cell/mast_cell_compounds.csv.

Output → trains a dedicated mast-cell stabilizer predictor in
scripts/train_mast_cell_predictor.py (EXP-016).
"""
from __future__ import annotations

import csv
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "outputs" / "chembl_mast_cell"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Description-text keywords to search ChEMBL assays for.
KEYWORDS = [
    "beta-hexosaminidase",
    "β-hexosaminidase",
    "hexosaminidase release",
    "histamine release",
    "tryptase release",
    "mast cell degranulation",
    "LAD2",
    "HMC-1",
    "RBL-2H3",
    "BMMC",
]


def main() -> int:
    try:
        from chembl_webresource_client.new_client import new_client
    except ImportError:
        print("ERROR: pip install chembl_webresource_client", file=sys.stderr)
        return 1

    assay_client = new_client.assay
    activity_client = new_client.activity

    aggregate: list[dict] = []
    seen_assay_ids: set[str] = set()

    for kw in KEYWORDS:
        print(f"\n=== keyword: '{kw}' ===")
        try:
            assays = list(assay_client.filter(description__icontains=kw).only([
                "assay_chembl_id",
                "assay_type",
                "assay_organism",
                "target_chembl_id",
                "description",
                "confidence_score",
            ]))
        except Exception as e:
            print(f"  search failed: {e}")
            continue
        print(f"  matched {len(assays)} assays in ChEMBL")
        new_assays = [a for a in assays if a["assay_chembl_id"] not in seen_assay_ids]
        print(f"  {len(new_assays)} new (not yet seen)")
        for a in new_assays[:50]:  # cap per keyword to keep this tractable
            aid = a["assay_chembl_id"]
            seen_assay_ids.add(aid)

            # Pull activities for this assay
            try:
                acts = list(activity_client.filter(assay_chembl_id=aid).only([
                    "activity_id",
                    "molecule_chembl_id",
                    "canonical_smiles",
                    "standard_type",
                    "standard_value",
                    "standard_units",
                    "standard_relation",
                    "activity_comment",
                    "pchembl_value",
                ]))
            except Exception as e:
                print(f"    {aid}: activity fetch failed ({e})")
                continue

            kept = 0
            for rec in acts:
                smi = rec.get("canonical_smiles", "") or ""
                if not smi:
                    continue
                aggregate.append({
                    "keyword": kw,
                    "assay_chembl_id": aid,
                    "assay_description": (a.get("description", "") or "")[:200],
                    "molecule_chembl_id": rec.get("molecule_chembl_id", ""),
                    "smiles": smi,
                    "standard_type": rec.get("standard_type", ""),
                    "standard_value": rec.get("standard_value", ""),
                    "standard_units": rec.get("standard_units", ""),
                    "standard_relation": rec.get("standard_relation", "="),
                    "activity_comment": rec.get("activity_comment", ""),
                    "pchembl_value": rec.get("pchembl_value", ""),
                })
                kept += 1
            if kept:
                print(f"    {aid}: {kept} compound records ({(a.get('description','') or '')[:80]})")

    # Aggregate output
    if not aggregate:
        print("\nNo matching activity records found.")
        return 0

    out_path = OUT_DIR / "mast_cell_compounds.csv"
    fields = list(aggregate[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(aggregate)
    print(f"\nwrote {out_path.relative_to(REPO_ROOT)}  ({len(aggregate)} rows across {len(seen_assay_ids)} assays)")
    print(f"  unique compounds: {len({r['smiles'] for r in aggregate})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
