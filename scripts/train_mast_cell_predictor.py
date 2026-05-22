"""Train a dedicated mast-cell-stabilizer classifier from ChEMBL assays.

Pipeline:
1. Load outputs/chembl_mast_cell/mast_cell_compounds.csv (EXP-016 input).
2. Filter to assays measuring true mast-cell readouts (β-hex / histamine /
   tryptase release; LAD2 / HMC-1 / RBL-2H3 / mast cell degranulation).
   Drop osteoclast / RANKL / BMMC-osteoclast false positives that
   description-text matching caught.
3. Convert per-compound activity to binary 'mast cell stabilizer
   active' label using:
     - If pchembl_value or standard_value present + standard_type ∈
       {IC50, Ki, EC50}: active iff pIC50 ≥ 5 (≤10 µM potency).
     - Else if standard_type = 'Inhibition' (% inhibition): active iff
       value ≥ 50.
     - Else if activity_comment is 'Active' or 'active': active.
     - Else if activity_comment is 'Inactive' or 'inactive': inactive.
     - Else skip.
4. Aggregate per-compound: majority vote across assays.
5. Train RandomForestClassifier on Morgan fingerprints.
6. Predict for library + generated compounds.
7. Write outputs/mast_cell_predictions.csv + outputs/mast_cell_model_metrics.csv.

This trains on assays that measure WHAT WE CARE ABOUT (mast cell
stabilization), not target-binding proxies.
"""
from __future__ import annotations

import csv
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = REPO_ROOT / "outputs" / "chembl_mast_cell" / "mast_cell_compounds.csv"
LIB_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
GEN_CSV = REPO_ROOT / "outputs" / "reinvent_generated.csv"
OUT_PRED = REPO_ROOT / "outputs" / "mast_cell_predictions.csv"
OUT_METRICS = REPO_ROOT / "outputs" / "mast_cell_model_metrics.csv"

# Keep assays whose description mentions a true mast-cell readout
MAST_CELL_INCLUDE = re.compile(
    r"hexosaminidas|β-hexosaminidase|histamine release|tryptase release|"
    r"mast cell|LAD2|HMC-1|HMC1|RBL[- ]?2H3|degranulat",
    re.IGNORECASE,
)
# Drop osteoclast / RANKL / bone-marrow-osteoblast false positives
OSTEO_EXCLUDE = re.compile(
    r"RANKL|osteoclast|osteoblast|osteopro|OPG protein|c-FOS|NFATc1|"
    r"bone marrow.+(mononuclear|osteo)|RAW 264|RAW264",
    re.IGNORECASE,
)


def classify_record(rec) -> str | None:
    """Return 'active' / 'inactive' / None for a single assay record."""
    stype = (rec.get("standard_type") or "").strip()
    comment = (rec.get("activity_comment") or "").strip().lower()
    sv = rec.get("standard_value", "")
    units = (rec.get("standard_units") or "").strip().lower()

    # Comment-based classification (most explicit when present)
    if comment in ("active", "highly active", "potent"):
        return "active"
    if comment in ("inactive", "not active"):
        return "inactive"

    # Numeric IC50/Ki/EC50 → pIC50 → threshold at 10 µM
    if stype in ("IC50", "Ki", "EC50", "Kd"):
        try:
            v = float(sv)
        except (TypeError, ValueError):
            return None
        if v <= 0:
            return None
        # Convert to nM
        if units in ("nm", "nmol/l"):
            nm = v
        elif units in ("um", "umol/l", "μm"):
            nm = v * 1000
        elif units in ("mm", "mmol/l"):
            nm = v * 1_000_000
        elif units in ("m",):
            nm = v * 1e9
        elif units in ("pm",):
            nm = v / 1000
        else:
            return None
        if nm > 1e9:
            return None
        pic50 = -math.log10(nm * 1e-9)
        return "active" if pic50 >= 5.0 else "inactive"

    # % inhibition → threshold at 50%
    if stype.lower() in ("inhibition", "percent inhibition", "% inhibition"):
        try:
            v = float(sv)
        except (TypeError, ValueError):
            return None
        return "active" if v >= 50 else "inactive"

    return None


def main() -> int:
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import KFold
        from sklearn.metrics import roc_auc_score
        from rdkit import Chem, RDLogger, DataStructs
        from rdkit.Chem import AllChem
        RDLogger.DisableLog("rdApp.*")
    except ImportError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # 1. Load + filter mast-cell records
    if not INPUT_CSV.exists():
        print(f"ERROR: missing {INPUT_CSV}. Run pull_mast_cell_assays.py first.", file=sys.stderr)
        return 1

    raw = list(csv.DictReader(INPUT_CSV.open()))
    print(f"loaded {len(raw)} raw records ({len({r['smiles'] for r in raw})} unique compounds across {len({r['assay_chembl_id'] for r in raw})} assays)")

    kept = []
    n_osteo = 0
    n_no_match = 0
    for r in raw:
        desc = r.get("assay_description", "") or ""
        if OSTEO_EXCLUDE.search(desc):
            n_osteo += 1
            continue
        if not MAST_CELL_INCLUDE.search(desc):
            n_no_match += 1
            continue
        kept.append(r)
    print(f"after filtering: {len(kept)} records  (dropped {n_osteo} osteoclast/RANKL + {n_no_match} non-matching)")

    # 2. Classify each record
    classed = []
    n_unclassified = 0
    for r in kept:
        label = classify_record(r)
        if label is None:
            n_unclassified += 1
            continue
        classed.append({**r, "_label": label})
    print(f"classified: {len(classed)} active/inactive records  (dropped {n_unclassified} unclassifiable)")

    # 3. Per-compound aggregate: majority vote across assays
    per_compound = defaultdict(list)
    for r in classed:
        per_compound[r["smiles"]].append(r["_label"])
    rows = []
    for smi, labels in per_compound.items():
        active_frac = sum(1 for l in labels if l == "active") / len(labels)
        # Majority vote: ≥50% active → active
        rows.append({
            "smiles": smi,
            "n_assays": len(labels),
            "frac_active": active_frac,
            "label": 1 if active_frac >= 0.5 else 0,
        })

    n_active = sum(1 for r in rows if r["label"] == 1)
    n_inactive = sum(1 for r in rows if r["label"] == 0)
    print(f"per-compound: {len(rows)} compounds  ({n_active} active, {n_inactive} inactive)  active rate {100*n_active/len(rows):.1f}%")
    if n_active < 20 or n_inactive < 20:
        print("WARNING: dataset is heavily imbalanced; model will be unreliable.", file=sys.stderr)

    # 4. Featurize
    X = np.zeros((len(rows), 2048), dtype=np.float32)
    y = np.zeros(len(rows), dtype=int)
    mask = np.zeros(len(rows), dtype=bool)
    for i, r in enumerate(rows):
        mol = Chem.MolFromSmiles(r["smiles"])
        if mol is None:
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        arr = np.zeros(2048, dtype=np.int8)
        DataStructs.ConvertToNumpyArray(fp, arr)
        X[i] = arr.astype(np.float32)
        y[i] = r["label"]
        mask[i] = True
    X, y = X[mask], y[mask]
    print(f"featurized: {len(y)} compounds with parseable SMILES")

    # 5. 5-fold CV
    kf = KFold(n_splits=5, shuffle=True, random_state=0)
    aucs = []
    for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X), start=1):
        m = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=0)
        m.fit(X[train_idx], y[train_idx])
        proba = m.predict_proba(X[val_idx])
        if proba.shape[1] == 1:  # all-one-class fold
            print(f"  fold {fold_idx}: single-class, skipping")
            continue
        auc = roc_auc_score(y[val_idx], proba[:, 1])
        aucs.append(auc)
        print(f"  fold {fold_idx}: AUC {auc:.3f}")
    print(f"\nCV mean AUC: {sum(aucs)/len(aucs):.3f} ± {(sum((a-sum(aucs)/len(aucs))**2 for a in aucs)/len(aucs))**0.5:.3f}  (over {len(aucs)} folds)")

    # 6. Final model + score library
    final = RandomForestClassifier(n_estimators=400, n_jobs=-1, random_state=0)
    final.fit(X, y)

    targets = []
    with LIB_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("canonical_smiles") or row.get("smiles") or ""
            if smi:
                targets.append((row["name"], smi, "library"))
    if GEN_CSV.exists():
        with GEN_CSV.open() as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                smi = row.get("smiles", "")
                if smi:
                    targets.append((f"GEN_{i:04d}", smi, "reinvent_generated"))

    Xt = np.zeros((len(targets), 2048), dtype=np.float32)
    mt = np.zeros(len(targets), dtype=bool)
    for i, (_, smi, _) in enumerate(targets):
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        arr = np.zeros(2048, dtype=np.int8)
        DataStructs.ConvertToNumpyArray(fp, arr)
        Xt[i] = arr.astype(np.float32)
        mt[i] = True

    proba = final.predict_proba(Xt)[:, 1]

    OUT_PRED.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PRED.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "smiles", "source", "mast_cell_stabilizer_prob"])
        for (name, smi, src), p, ok in zip(targets, proba, mt):
            w.writerow([name, smi, src, round(float(p), 4) if ok else ""])
    print(f"wrote {OUT_PRED.relative_to(REPO_ROOT)}  ({len(targets)} compounds)")

    with OUT_METRICS.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["metric", "value"])
        w.writerow(["n_train_compounds", len(y)])
        w.writerow(["n_train_active", int(y.sum())])
        w.writerow(["n_train_inactive", int((1 - y).sum())])
        w.writerow(["cv_mean_auc", round(sum(aucs)/len(aucs), 4) if aucs else "n/a"])
        w.writerow(["cv_folds_evaluated", len(aucs)])
    print(f"wrote {OUT_METRICS.relative_to(REPO_ROOT)}")

    # Print anchor predictions
    anchors = ["Sulforaphane","Erucin","Phenethyl isothiocyanate","Iberin","Benzyl isothiocyanate",
               "Cetirizine","Fexofenadine","Diphenhydramine","Hydroxyzine","Famotidine",
               "Quercetin","Luteolin","Curcumin","Resveratrol","Cromolyn sodium","Ketotifen",
               "Masitinib","Midostaurin","Avapritinib","Montelukast","Aspirin (acetylsalicylic acid)"]
    name_idx = {t[0]: i for i, t in enumerate(targets)}
    print()
    print(f"Anchor predictions (mast cell stabilizer probability):")
    print(f"  {'compound':<32}  prob_active")
    for a in anchors:
        i = name_idx.get(a)
        if i is None or not mt[i]:
            continue
        print(f"  {a:<32}  {proba[i]:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
