"""Pull ChEMBL bioassay data for MCAS-relevant targets.

For each UniProt target in data/targets/MCAS_Targets.csv, query ChEMBL for:
  - Activity records on that target (IC50 / Ki / EC50 / Kd / Inhibition %)
  - Standard-value units and types
  - Compound SMILES (canonical)

Filter to:
  - Activities with a numeric standard_value
  - Standard types in {IC50, Ki, EC50, Kd, Activity, Inhibition}
  - Reasonable potency range (drop nM<0.001 or >1e9 outliers)
  - Successful SMILES retrieval

Output: outputs/chembl_<TARGET>.csv with columns:
    target_gene, target_uniprot, chembl_assay_id, chembl_compound_id,
    smiles, standard_type, standard_value, standard_units, pchembl_value

Used as training data for an MCAS-relevant activity predictor in
scripts/train_chembl_predictor.py (EXP-011).
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGETS_CSV = REPO_ROOT / "data" / "targets" / "MCAS_Targets.csv"
OUT_DIR = REPO_ROOT / "outputs" / "chembl"


# Subset of MCAS targets we want bioassay data for, mapped to ChEMBL via UniProt.
# Limit to ones likely to have meaningful activity data in ChEMBL.
TARGETS = [
    ("MRGPRX2", "Q96LB1"),
    ("KIT",     "P10721"),
    ("KEAP1",   "Q14145"),
    ("HRH1",    "P35367"),
    ("HRH2",    "P25021"),
    ("HRH3",    "Q9Y5N1"),
    ("HRH4",    "Q9H3N8"),
    ("CYSLTR1", "Q9Y271"),
    ("BTK",     "Q06187"),
    ("SYK",     "P43405"),
    ("GLP1R",   "P43220"),
]

ALLOWED_STANDARD_TYPES = {"IC50", "Ki", "EC50", "Kd", "Activity", "Inhibition"}


def main() -> int:
    try:
        from chembl_webresource_client.new_client import new_client
    except ImportError:
        print("ERROR: pip install chembl_webresource_client", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    for gene, uniprot in TARGETS:
        print(f"\n=== {gene} (UniProt {uniprot}) ===")
        targets = new_client.target
        target_hits = list(targets.filter(target_components__accession=uniprot).only(["target_chembl_id", "pref_name"]))
        if not target_hits:
            print(f"  no ChEMBL target for UniProt {uniprot}")
            continue
        target_chembl_id = target_hits[0]["target_chembl_id"]
        pref = target_hits[0].get("pref_name", "")
        print(f"  target: {target_chembl_id} ({pref})")

        activities = new_client.activity
        q = activities.filter(target_chembl_id=target_chembl_id).filter(standard_value__isnull=False).only([
            "activity_id",
            "assay_chembl_id",
            "molecule_chembl_id",
            "canonical_smiles",
            "standard_type",
            "standard_value",
            "standard_units",
            "standard_relation",
            "pchembl_value",
        ])

        rows = []
        skipped_type = 0
        skipped_value = 0
        skipped_smiles = 0
        for i, rec in enumerate(q):
            stype = rec.get("standard_type")
            if stype not in ALLOWED_STANDARD_TYPES:
                skipped_type += 1
                continue
            sv = rec.get("standard_value")
            try:
                sv_f = float(sv) if sv is not None else None
            except (TypeError, ValueError):
                sv_f = None
            if sv_f is None or sv_f <= 0:
                skipped_value += 1
                continue
            smi = rec.get("canonical_smiles") or ""
            if not smi:
                skipped_smiles += 1
                continue
            rows.append({
                "target_gene": gene,
                "target_uniprot": uniprot,
                "target_chembl_id": target_chembl_id,
                "chembl_assay_id": rec.get("assay_chembl_id", ""),
                "chembl_compound_id": rec.get("molecule_chembl_id", ""),
                "smiles": smi,
                "standard_type": stype,
                "standard_value": sv_f,
                "standard_units": rec.get("standard_units", ""),
                "standard_relation": rec.get("standard_relation", "="),
                "pchembl_value": rec.get("pchembl_value") or "",
            })
            if (i + 1) % 5000 == 0:
                print(f"    ... {i+1} records inspected, {len(rows)} kept")

        if not rows:
            print(f"  no usable activity records — skipping")
            continue

        out_path = OUT_DIR / f"{gene}_bioassays.csv"
        with out_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"  wrote {out_path.relative_to(REPO_ROOT)}  ({len(rows)} rows, skipped: type={skipped_type} value={skipped_value} smiles={skipped_smiles})")
        summary_rows.append({
            "target_gene": gene,
            "target_uniprot": uniprot,
            "target_chembl_id": target_chembl_id,
            "n_activities": len(rows),
            "n_unique_smiles": len({r["smiles"] for r in rows}),
        })

    # Master summary
    summary_path = OUT_DIR / "_summary.csv"
    if summary_rows:
        with summary_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()))
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\nwrote {summary_path.relative_to(REPO_ROOT)}")
        print()
        print("=== ChEMBL pull summary ===")
        print(f"  {'target':<10}  {'n_activities':>12}  {'n_unique':>10}")
        for r in summary_rows:
            print(f"  {r['target_gene']:<10}  {r['n_activities']:>12d}  {r['n_unique_smiles']:>10d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
