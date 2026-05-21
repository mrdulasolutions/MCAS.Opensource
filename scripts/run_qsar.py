"""Train safety/ADMET QSAR models on PyTDC tasks and score the library + analogs.

Uses RandomForest on Morgan fingerprints (r=2, 2048 bits) — CPU-friendly,
trains in under a minute per task on this hardware, and competitive with graph
neural nets for binary safety endpoints.

Tasks (all from PyTDC):
  - hERG          cardiac liability      lower = better (we want no hERG block)
  - AMES          mutagenicity            lower = better
  - BBB_Martins   blood-brain barrier     contextual — high = neuro-active (good for neuro-MCAS hypotheses), low = peripheral

Output: outputs/qsar_predictions.csv with columns:
    name, smiles, source, hERG_score, AMES_score, BBB_score
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")

REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
GENERATED_CSV = REPO_ROOT / "outputs" / "reinvent_generated.csv"
OUT_PATH = REPO_ROOT / "outputs" / "qsar_predictions.csv"

TASKS = {
    "hERG":        ("Tox",  "hERG"),
    "AMES":        ("Tox",  "AMES"),
    "BBB_Martins": ("ADME", "BBB_Martins"),
}


def fp(mol) -> np.ndarray:
    arr = np.zeros(2048, dtype=np.int8)
    bv = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    from rdkit.DataStructs import ConvertToNumpyArray
    ConvertToNumpyArray(bv, arr)
    return arr


def featurize(smiles_list: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Return X (n, 2048) and a mask of which inputs successfully parsed."""
    mask = np.zeros(len(smiles_list), dtype=bool)
    X = np.zeros((len(smiles_list), 2048), dtype=np.float32)
    for i, smi in enumerate(smiles_list):
        mol = Chem.MolFromSmiles(smi) if smi else None
        if mol is None:
            continue
        X[i] = fp(mol)
        mask[i] = True
    return X, mask


def train_one(task_module: str, task_name: str):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score
    if task_module == "Tox":
        from tdc.single_pred import Tox as TaskCls
    else:
        from tdc.single_pred import ADME as TaskCls

    task = TaskCls(name=task_name)
    split = task.get_split()
    train_df = split["train"]
    valid_df = split["valid"]

    print(f"  [{task_name}] train={len(train_df)} valid={len(valid_df)}")
    Xtr, mtr = featurize(train_df["Drug"].tolist())
    ytr = np.array(train_df["Y"].tolist(), dtype=np.float32)
    Xtr, ytr = Xtr[mtr], ytr[mtr]
    Xva, mva = featurize(valid_df["Drug"].tolist())
    yva = np.array(valid_df["Y"].tolist(), dtype=np.float32)[mva]
    Xva = Xva[mva]

    model = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0)
    model.fit(Xtr, ytr.astype(int))
    valid_proba = model.predict_proba(Xva)[:, 1]
    try:
        auc = roc_auc_score(yva, valid_proba)
        print(f"  [{task_name}] valid AUC = {auc:.3f}")
    except Exception:
        print(f"  [{task_name}] AUC not computable")
    return model


def load_targets() -> list[dict]:
    out = []
    seen = set()
    with LIBRARY_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("canonical_smiles") or row.get("smiles") or ""
            if not smi or smi in seen:
                continue
            seen.add(smi)
            out.append({"name": row["name"], "smiles": smi, "source": "library"})
    if GENERATED_CSV.exists():
        with GENERATED_CSV.open() as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                smi = row.get("smiles", "")
                if not smi or smi in seen:
                    continue
                seen.add(smi)
                out.append({"name": f"GEN_{i:04d}", "smiles": smi, "source": "reinvent_generated"})
    return out


def main() -> int:
    targets = load_targets()
    print(f"loading {len(targets)} unique SMILES to score")

    Xt, mask = featurize([t["smiles"] for t in targets])

    predictions: dict[str, np.ndarray] = {}
    for col_name, (module, task_name) in TASKS.items():
        print(f"training {col_name} ...")
        model = train_one(module, task_name)
        scores = np.full(len(targets), np.nan, dtype=np.float32)
        scores[mask] = model.predict_proba(Xt[mask])[:, 1]
        predictions[col_name] = scores

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cols = ["name", "smiles", "source"] + [f"{k}_score" for k in TASKS]
    with OUT_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(cols)
        for i, t in enumerate(targets):
            row = [t["name"], t["smiles"], t["source"]]
            for k in TASKS:
                v = predictions[k][i]
                row.append(round(float(v), 4) if not np.isnan(v) else "")
            writer.writerow(row)

    print(f"wrote {len(targets)} rows -> {OUT_PATH.relative_to(REPO_ROOT)}")

    # Quick summary: where do our anchor compounds land?
    anchors = ["Sulforaphane", "Phenethyl isothiocyanate", "Quercetin", "Luteolin",
               "Curcumin", "Resveratrol", "Cetirizine", "Masitinib"]
    print()
    print("anchor compounds:")
    print(f"  {'name':<30}  {'hERG':>8}  {'AMES':>8}  {'BBB':>8}")
    name_to_i = {t["name"]: i for i, t in enumerate(targets)}
    for a in anchors:
        i = name_to_i.get(a)
        if i is None:
            continue
        h = predictions["hERG"][i]
        m = predictions["AMES"][i]
        b = predictions["BBB_Martins"][i]
        print(f"  {a:<30}  {h:>8.3f}  {m:>8.3f}  {b:>8.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
