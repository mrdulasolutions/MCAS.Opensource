"""Known Actives Recovery benchmark.

For each held-out known active in data/benchmarks/known_actives.json:
  1. Fetch SMILES from PubChem.
  2. Run target-similarity, warhead, and QSAR scoring blind (same code paths
     as the main pipeline; the actives are NOT added to the seeds).
  3. Compute the per-category composite score using the same formula as
     rank_hypotheses.py.
  4. Insert the active into the existing ranked CSV for its expected
     category and report where it lands.

Reports:
  - recovery@20: fraction of known actives that land in top-20 of expected category
  - recovery@50: fraction in top-50
  - per-compound diagnostic with composite score, target hits, warhead, ADMET

Output: outputs/benchmark_known_actives.csv + console summary.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem, Descriptors, Lipinski

RDLogger.DisableLog("rdApp.*")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from fetch_smiles import fetch_by_cid  # noqa: E402
from score_against_targets import TARGET_REFERENCES, fingerprint, best_similarity  # noqa: E402
from score_warheads import WARHEADS, compile_warheads, warhead_hits, keap1_pharmacophore_pass  # noqa: E402

BENCHMARK_PATH = REPO_ROOT / "data" / "benchmarks" / "known_actives.json"
OUT_PATH = REPO_ROOT / "outputs" / "benchmark_known_actives.csv"

# Mirror the per-category target weights from rank_hypotheses.py
CATEGORY_TARGETS = {
    "rescue":      {"HRH1": 0.4, "HRH2": 0.2, "CYSLTR1": 0.2, "MRGPRX2": 0.2},
    "maintenance": {"CYSLTR1": 0.3, "HRH1": 0.15, "BTK": 0.15, "MRGPRX2": 0.2, "KEAP1": 0.2},
    "remission":   {"MRGPRX2": 0.3, "KIT": 0.3, "KEAP1": 0.3, "GLP1R": 0.1},
}


def fp_array(mol) -> np.ndarray:
    arr = np.zeros(2048, dtype=np.int8)
    bv = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    DataStructs.ConvertToNumpyArray(bv, arr)
    return arr


def load_qsar_models():
    """Train the same three RF models as scripts/run_qsar.py.

    Trained once per invocation; reused across all benchmark compounds.
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score
    from tdc.single_pred import Tox, ADME

    tasks = {
        "hERG":        (Tox,  "hERG"),
        "AMES":        (Tox,  "AMES"),
        "BBB_Martins": (ADME, "BBB_Martins"),
    }

    models = {}
    for name, (cls, ds_name) in tasks.items():
        print(f"  training {name} ...", end="", flush=True)
        task = cls(name=ds_name)
        split = task.get_split()
        train_df = split["train"]
        valid_df = split["valid"]
        Xtr, mtr = featurize_df(train_df["Drug"].tolist())
        ytr = np.array(train_df["Y"].tolist())[mtr]
        Xtr = Xtr[mtr]
        Xva, mva = featurize_df(valid_df["Drug"].tolist())
        yva = np.array(valid_df["Y"].tolist())[mva]
        Xva = Xva[mva]
        model = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0)
        model.fit(Xtr, ytr.astype(int))
        auc = roc_auc_score(yva, model.predict_proba(Xva)[:, 1])
        models[name] = model
        print(f" AUC {auc:.3f}")
    return models


def featurize_df(smiles_list):
    mask = np.zeros(len(smiles_list), dtype=bool)
    X = np.zeros((len(smiles_list), 2048), dtype=np.float32)
    for i, smi in enumerate(smiles_list):
        if not smi:
            continue
        m = Chem.MolFromSmiles(smi)
        if m is None:
            continue
        X[i] = fp_array(m)
        mask[i] = True
    return X, mask


def score_active(active: dict, target_fps: dict, warhead_patts, qsar_models, ranked_csv):
    """Score a single known active and find its rank in the expected category."""
    cid = active["pubchem_cid"]
    expected = active["expected_category"]
    weights = CATEGORY_TARGETS[expected]

    smiles_data = fetch_by_cid(cid)
    smiles = smiles_data.get("canonical_smiles") or smiles_data.get("isomeric_smiles") or ""
    if not smiles:
        return {**active, "error": "no_smiles", "rank": None, "composite_score": None}

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {**active, "error": "unparseable_smiles", "smiles": smiles, "rank": None, "composite_score": None}

    canonical_smiles = Chem.MolToSmiles(mol, canonical=True)

    # 1. Per-target similarity
    fp = fingerprint(mol)
    target_scores = {}
    for tgt, ref_fps in target_fps.items():
        score, idx = best_similarity(fp, ref_fps)
        target_scores[tgt] = score

    # 2. Warhead detection
    hits = warhead_hits(mol, warhead_patts)
    has_warhead = bool(hits)
    ph_pass = keap1_pharmacophore_pass(mol)
    warhead_score = (1.0 if has_warhead else 0.0) * (1.0 if ph_pass else 0.5)

    # 3. QSAR
    fp_arr = fp_array(mol).reshape(1, -1)
    herg = float(qsar_models["hERG"].predict_proba(fp_arr)[0, 1])
    ames = float(qsar_models["AMES"].predict_proba(fp_arr)[0, 1])
    bbb = float(qsar_models["BBB_Martins"].predict_proba(fp_arr)[0, 1])

    # 4. Composite — same formula as rank_hypotheses.py
    # evidence_level is "known clinical" → treat as "high"
    evidence_weight = 1.0
    s = 0.30 * evidence_weight

    dock_total = 0.0
    weight_total = 0.0
    for tgt, w in weights.items():
        if tgt in target_scores:
            dock_total += target_scores[tgt] * w
            weight_total += w
    if weight_total > 0:
        s += (dock_total / weight_total) * 0.35

    if "KEAP1" in weights:
        s += warhead_score * 0.10
        if target_scores.get("KEAP1", 0) > 0.4 and not has_warhead:
            s -= 0.08

    safety = 0.5 * (1 - herg) + 0.5 * (1 - ames)
    s += safety * 0.15
    if expected in ("maintenance", "remission"):
        s += (bbb - 0.5) * 0.05
    elif expected == "rescue":
        if target_scores.get("HRH1", 0) < 0.5:
            s -= (bbb - 0.5) * 0.03

    composite_score = round(s, 4)

    # 5. Find rank in current ranked CSV
    rank = None
    with ranked_csv.open() as fh:
        rows = list(csv.DictReader(fh))
        # ranked rows are sorted desc by composite; find where our composite slots in
        rank = 1 + sum(1 for r in rows if float(r["composite_score"]) > composite_score)

    return {
        **active,
        "smiles": canonical_smiles,
        "composite_score": composite_score,
        "rank_in_expected_category": rank,
        "expected_category_size": len(rows),
        "score_KEAP1": round(target_scores.get("KEAP1", 0), 3),
        "score_MRGPRX2": round(target_scores.get("MRGPRX2", 0), 3),
        "score_KIT": round(target_scores.get("KIT", 0), 3),
        "score_HRH1": round(target_scores.get("HRH1", 0), 3),
        "score_HRH2": round(target_scores.get("HRH2", 0), 3),
        "score_CYSLTR1": round(target_scores.get("CYSLTR1", 0), 3),
        "score_BTK": round(target_scores.get("BTK", 0), 3),
        "has_warhead": has_warhead,
        "warheads": ";".join(hits),
        "hERG_score": round(herg, 3),
        "AMES_score": round(ames, 3),
        "BBB_score": round(bbb, 3),
        "error": "",
    }


def main() -> int:
    with BENCHMARK_PATH.open() as fh:
        benchmark = json.load(fh)
    actives = benchmark["actives"]

    print(f"benchmark: {len(actives)} known actives")
    print("  precomputing reference fingerprints...")
    target_fps = {}
    for tgt, refs in TARGET_REFERENCES.items():
        fps = []
        for label, smi, note in refs:
            m = Chem.MolFromSmiles(smi)
            if m is not None:
                fps.append(fingerprint(m))
        target_fps[tgt] = fps

    print("  compiling warhead SMARTS...")
    warhead_patts = compile_warheads()

    print("  training QSAR models on PyTDC tasks...")
    qsar_models = load_qsar_models()

    print()
    print("Scoring each known active blind...")
    results = []
    ranked_csvs = {
        "rescue": REPO_ROOT / "outputs" / "ranked_rescue.csv",
        "maintenance": REPO_ROOT / "outputs" / "ranked_maintenance.csv",
        "remission": REPO_ROOT / "outputs" / "ranked_remission.csv",
    }
    for a in actives:
        ranked_csv = ranked_csvs[a["expected_category"]]
        r = score_active(a, target_fps, warhead_patts, qsar_models, ranked_csv)
        results.append(r)
        rank = r.get("rank_in_expected_category")
        size = r.get("expected_category_size")
        err = r.get("error", "")
        cs = r.get("composite_score")
        cs_str = f"{cs:.3f}" if cs is not None else "n/a"
        if err:
            print(f"  [ERR] {a['name']:<28}  {err}")
        else:
            print(f"  {a['name']:<28}  cat={a['expected_category']:<11}  rank={rank}/{size}  composite={cs_str}")

    # Aggregate metrics per category + overall
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(results[0].keys())
    with OUT_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"\nwrote {OUT_PATH.relative_to(REPO_ROOT)}")

    print()
    print("=== Recovery summary ===")
    valid = [r for r in results if r.get("rank_in_expected_category") is not None]
    for cat in ("rescue", "maintenance", "remission"):
        sub = [r for r in valid if r["expected_category"] == cat]
        if not sub:
            continue
        for N in (10, 20, 50):
            hit = sum(1 for r in sub if r["rank_in_expected_category"] <= N)
            print(f"  {cat:<11} recovery@{N:<2}: {hit}/{len(sub)} = {100*hit/len(sub):.1f}%")
    print()
    print("Overall:")
    for N in (10, 20, 50):
        hit = sum(1 for r in valid if r["rank_in_expected_category"] <= N)
        print(f"  recovery@{N:<2}: {hit}/{len(valid)} = {100*hit/len(valid):.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
