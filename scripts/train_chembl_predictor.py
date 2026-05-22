"""Train per-target activity predictors from the ChEMBL pull (EXP-011).

For each target with bioassay data in outputs/chembl/<TARGET>_bioassays.csv:

  1. Filter activities to a single canonical type per target (IC50 preferred,
     fall back to Ki / Kd / EC50).
  2. Convert to pIC50 (=−log10(IC50_nM × 1e-9)) — higher = more potent.
  3. Aggregate duplicate (compound, target) pairs via median pIC50.
  4. Featurize SMILES → Morgan fingerprint (radius 2, 2048 bits).
  5. Train a RandomForestRegressor with 5-fold CV; record per-fold R² + RMSE.
  6. Predict pIC50 for every compound in the master library + generated
     analogs.

Output:
  outputs/chembl_predictions.csv   per-compound predicted pIC50 per target
  outputs/chembl_model_metrics.csv per-target training R² + RMSE + n_train

Used as the predicted-activity signal in EXP-011's integration step.
"""
from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHEMBL_DIR = REPO_ROOT / "outputs" / "chembl"
LIB_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
GEN_CSV = REPO_ROOT / "outputs" / "reinvent_generated.csv"
OUT_PRED = REPO_ROOT / "outputs" / "chembl_predictions.csv"
OUT_METRICS = REPO_ROOT / "outputs" / "chembl_model_metrics.csv"

# Min usable training set size per target. Below this we skip — fitting a
# RandomForest on <30 examples gives unstable predictions.
MIN_N_TRAIN = 30

TYPE_PREFERENCE = ["IC50", "Ki", "Kd", "EC50"]


def to_pchembl(stype: str, value_nM: float) -> float | None:
    """Convert IC50/Ki/Kd/EC50 (nM) → pIC50-equivalent. Discard absurd values."""
    if value_nM is None or value_nM <= 0 or value_nM > 1e9:
        return None
    return -math.log10(value_nM * 1e-9)


def load_per_target_data(csv_path: Path):
    """Returns dict[smiles] = [pIC50 values...] for the preferred standard type."""
    rows = []
    with csv_path.open() as fh:
        for row in csv.DictReader(fh):
            try:
                v = float(row.get("standard_value") or "")
            except (TypeError, ValueError):
                continue
            stype = row.get("standard_type", "")
            units = (row.get("standard_units") or "").strip().lower()
            if units not in ("nm", "nmol/l", "nm/l"):  # only keep nM
                # try common Conversions
                if units in ("um", "umol/l", "μm"):
                    v *= 1000.0
                elif units in ("mm", "mmol/l"):
                    v *= 1_000_000.0
                elif units in ("m",):
                    v *= 1e9
                elif units in ("pm",):
                    v *= 0.001
                else:
                    continue
            rows.append({
                "smiles": row["smiles"],
                "type": stype,
                "value_nM": v,
                "relation": row.get("standard_relation", "="),
            })

    # Pick best preference per (smiles, type)
    by_smiles_type: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in rows:
        if r["type"] not in TYPE_PREFERENCE:
            continue
        if r["relation"] not in ("=", "<", ">", "<=", ">=", "~"):
            continue
        pv = to_pchembl(r["type"], r["value_nM"])
        if pv is None:
            continue
        by_smiles_type[(r["smiles"], r["type"])].append(pv)

    # For each smiles, pick preferred type (highest in TYPE_PREFERENCE) and median
    chosen: dict[str, float] = {}
    for smi in {s for s, _ in by_smiles_type}:
        for t in TYPE_PREFERENCE:
            vs = by_smiles_type.get((smi, t))
            if vs:
                chosen[smi] = sorted(vs)[len(vs) // 2]
                break
    return chosen


def featurize(smiles_list):
    from rdkit import Chem, RDLogger, DataStructs
    from rdkit.Chem import AllChem
    import numpy as np
    RDLogger.DisableLog("rdApp.*")

    mask = []
    X = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            mask.append(False)
            X.append(np.zeros(2048, dtype=np.float32))
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        arr = np.zeros(2048, dtype=np.int8)
        DataStructs.ConvertToNumpyArray(fp, arr)
        X.append(arr.astype(np.float32))
        mask.append(True)
    import numpy as np
    return np.array(X), np.array(mask)


def main() -> int:
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import KFold
        from sklearn.metrics import r2_score, mean_squared_error
    except ImportError:
        print("ERROR: pip install scikit-learn numpy", file=sys.stderr)
        return 1

    # Targets discovered from the ChEMBL pull directory
    bioassay_files = sorted(CHEMBL_DIR.glob("*_bioassays.csv"))
    if not bioassay_files:
        print(f"ERROR: no ChEMBL bioassay files in {CHEMBL_DIR}", file=sys.stderr)
        return 1

    # Load library + generated
    library_smiles = []
    library_names = []
    with LIB_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("canonical_smiles") or row.get("smiles") or ""
            if smi:
                library_smiles.append(smi)
                library_names.append(row["name"])
    if GEN_CSV.exists():
        with GEN_CSV.open() as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                smi = row.get("smiles", "")
                if smi:
                    library_smiles.append(smi)
                    library_names.append(f"GEN_{i:04d}")

    print(f"will predict for {len(library_smiles)} library + generated compounds")

    lib_X, lib_mask = featurize(library_smiles)

    metrics_rows = []
    # predictions[name][target] = predicted_pIC50
    predictions: dict[str, dict[str, float]] = defaultdict(dict)

    for bfile in bioassay_files:
        target = bfile.stem.replace("_bioassays", "")
        print(f"\n=== {target} ===")
        per_smiles = load_per_target_data(bfile)
        if len(per_smiles) < MIN_N_TRAIN:
            print(f"  only {len(per_smiles)} usable activities — skipping ({MIN_N_TRAIN}-min required)")
            metrics_rows.append({
                "target": target, "n_train": len(per_smiles), "status": "skipped_too_small",
                "cv_r2_mean": "", "cv_r2_std": "", "cv_rmse_mean": "",
            })
            continue

        smiles = list(per_smiles.keys())
        y = np.array([per_smiles[s] for s in smiles], dtype=np.float32)
        X, mask = featurize(smiles)
        X = X[mask]
        y = y[mask]
        print(f"  training on {len(y)} compounds (pIC50 range {y.min():.2f}–{y.max():.2f}, median {float(np.median(y)):.2f})")

        # 5-fold CV
        kf = KFold(n_splits=5, shuffle=True, random_state=0)
        r2s, rmses = [], []
        for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X), start=1):
            model = RandomForestRegressor(n_estimators=300, n_jobs=-1, random_state=0)
            model.fit(X[train_idx], y[train_idx])
            preds = model.predict(X[val_idx])
            r2 = r2_score(y[val_idx], preds)
            rmse = math.sqrt(mean_squared_error(y[val_idx], preds))
            r2s.append(r2)
            rmses.append(rmse)
        cv_r2_mean = float(np.mean(r2s))
        cv_r2_std = float(np.std(r2s))
        cv_rmse_mean = float(np.mean(rmses))
        print(f"  CV  R²={cv_r2_mean:.3f}±{cv_r2_std:.3f}  RMSE={cv_rmse_mean:.3f} pIC50")

        # Final model on all data
        final = RandomForestRegressor(n_estimators=400, n_jobs=-1, random_state=0)
        final.fit(X, y)

        # Predict for library + generated
        for i, name in enumerate(library_names):
            if not lib_mask[i]:
                continue
            pred = float(final.predict(lib_X[i].reshape(1, -1))[0])
            predictions[name][target] = pred

        metrics_rows.append({
            "target": target,
            "n_train": len(y),
            "status": "ok",
            "cv_r2_mean": round(cv_r2_mean, 4),
            "cv_r2_std": round(cv_r2_std, 4),
            "cv_rmse_mean": round(cv_rmse_mean, 4),
        })

    # Write metrics
    with OUT_METRICS.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(metrics_rows[0].keys()))
        writer.writeheader()
        writer.writerows(metrics_rows)
    print(f"\nwrote {OUT_METRICS.relative_to(REPO_ROOT)}")

    # Write predictions
    target_columns = sorted({t for tdict in predictions.values() for t in tdict})
    field_names = ["name", "smiles"] + [f"chembl_pIC50_{t}" for t in target_columns]
    pred_rows = []
    for name, smi in zip(library_names, library_smiles):
        row = {"name": name, "smiles": smi}
        for t in target_columns:
            row[f"chembl_pIC50_{t}"] = round(predictions.get(name, {}).get(t, float("nan")), 3) if name in predictions and t in predictions[name] else ""
        pred_rows.append(row)
    with OUT_PRED.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(pred_rows)
    print(f"wrote {OUT_PRED.relative_to(REPO_ROOT)}  ({len(pred_rows)} compounds × {len(target_columns)} targets)")

    # Print summary
    print()
    print("=== Model metrics ===")
    print(f"  {'target':<10}  {'n_train':>7}  {'R²':>6}  {'RMSE':>5}")
    for r in metrics_rows:
        if r["status"] != "ok":
            print(f"  {r['target']:<10}  {r['n_train']:>7}  ({r['status']})")
        else:
            print(f"  {r['target']:<10}  {r['n_train']:>7}  {r['cv_r2_mean']:>6.3f}  {r['cv_rmse_mean']:>5.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
