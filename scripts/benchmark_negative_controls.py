"""Negative-control benchmark.

Scores 20 widely-used drugs from therapeutic areas with no plausible MCAS
mechanism (statins, antihypertensives, anticonvulsants, etc.) through the
exact same pipeline as EXP-006. For each negative control we compute its
composite score for ALL THREE categories (rescue, maintenance, remission)
and report:

  precision@N (per category)  = fraction of negative controls correctly
                                ranked OUTSIDE the top-N of that category
  precision@N (overall)       = fraction of negative controls ranked
                                outside the top-N of EVERY category

A clean negative-control result complements EXP-006: we both recover
known actives AND reject unrelated drugs. Together they say the composite
isn't just a generic drug-likeness reward.

Output: outputs/benchmark_negative_controls.csv + console summary.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from fetch_smiles import fetch_by_cid  # noqa: E402
from score_against_targets import TARGET_REFERENCES, fingerprint, best_similarity  # noqa: E402
from score_warheads import compile_warheads, warhead_hits, keap1_pharmacophore_pass  # noqa: E402

BENCHMARK_PATH = REPO_ROOT / "data" / "benchmarks" / "negative_controls.json"
OUT_PATH = REPO_ROOT / "outputs" / "benchmark_negative_controls.csv"

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


def load_qsar_models():
    """Train the same three RF models as scripts/run_qsar.py (used for safety bonus)."""
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
        Xtr, mtr = featurize_df(train_df["Drug"].tolist())
        ytr = np.array(train_df["Y"].tolist())[mtr]
        Xtr = Xtr[mtr]
        model = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0)
        model.fit(Xtr, ytr.astype(int))
        valid_df = split["valid"]
        Xva, mva = featurize_df(valid_df["Drug"].tolist())
        yva = np.array(valid_df["Y"].tolist())[mva]
        Xva = Xva[mva]
        auc = roc_auc_score(yva, model.predict_proba(Xva)[:, 1])
        models[name] = model
        print(f" AUC {auc:.3f}")
    return models


def composite_for_category(target_scores, warhead, qsar, category, evidence_weight=0.0):
    """Replicate rank_hypotheses.py composite for an arbitrary category.

    `evidence_weight` controls how we treat the negative control:
      0.0 — production-realistic: unknown compound, no curated evidence.
      0.3 — equivalent to evidence_level='low'.
      0.6 — equivalent to evidence_level='medium'.
      1.0 — equivalent to evidence_level='high' (most generous to control).

    The primary metric uses 0.0 since that matches what happens in real
    deployment for any new compound the pipeline has never seen.
    """
    weights = CATEGORY_TARGETS[category]

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
        wh_score = warhead.get("warhead_score", 0.0) if warhead else 0.0
        s += wh_score * 0.10
        if target_scores.get("KEAP1", 0) > 0.4 and not warhead.get("has_warhead", False):
            s -= 0.08

    herg = qsar.get("hERG", 0.5)
    ames = qsar.get("AMES", 0.5)
    bbb = qsar.get("BBB_Martins", 0.5)
    safety = 0.5 * (1 - herg) + 0.5 * (1 - ames)
    s += safety * 0.15
    if category in ("maintenance", "remission"):
        s += (bbb - 0.5) * 0.05
    elif category == "rescue":
        if target_scores.get("HRH1", 0) < 0.5:
            s -= (bbb - 0.5) * 0.03
    return round(s, 4)


def rank_against_csv(composite, ranked_csv_path):
    """How many existing rows beat this composite score? Returns rank (1 = top)."""
    rank = 1
    with ranked_csv_path.open() as fh:
        for row in csv.DictReader(fh):
            try:
                if float(row["composite_score"]) > composite:
                    rank += 1
            except (ValueError, KeyError):
                continue
    return rank


def main() -> int:
    with BENCHMARK_PATH.open() as fh:
        bench = json.load(fh)
    controls = bench["controls"]
    print(f"benchmark: {len(controls)} negative controls")

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

    print("  training QSAR models...")
    qsar_models = load_qsar_models()

    ranked_csvs = {c: REPO_ROOT / "outputs" / f"ranked_{c}.csv" for c in ("rescue", "maintenance", "remission")}

    print()
    print("Scoring each negative control...")
    rows = []
    for c in controls:
        cid = c["pubchem_cid"]
        s = fetch_by_cid(cid)
        smi = s.get("canonical_smiles") or s.get("isomeric_smiles") or ""
        if not smi:
            rows.append({**c, "error": "no_smiles"})
            print(f"  [ERR] {c['name']:<22}: no SMILES")
            continue
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            rows.append({**c, "error": "unparseable", "smiles": smi})
            continue
        fp = fingerprint(mol)

        target_scores = {tgt: best_similarity(fp, ref_fps)[0] for tgt, ref_fps in target_fps.items()}

        hits = warhead_hits(mol, warhead_patts)
        ph_pass = keap1_pharmacophore_pass(mol)
        warhead_score = (1.0 if hits else 0.0) * (1.0 if ph_pass else 0.5)

        fp_arr = fp_array(mol).reshape(1, -1)
        qsar = {
            "hERG": float(qsar_models["hERG"].predict_proba(fp_arr)[0, 1]),
            "AMES": float(qsar_models["AMES"].predict_proba(fp_arr)[0, 1]),
            "BBB_Martins": float(qsar_models["BBB_Martins"].predict_proba(fp_arr)[0, 1]),
        }

        row = {
            **c,
            "smiles": Chem.MolToSmiles(mol, canonical=True),
            "has_warhead": bool(hits),
            "warheads": ";".join(hits),
            "hERG_score": round(qsar["hERG"], 3),
            "AMES_score": round(qsar["AMES"], 3),
            "BBB_score": round(qsar["BBB_Martins"], 3),
        }
        for tgt, score in target_scores.items():
            row[f"score_{tgt}"] = round(score, 3)

        wh_pack = {"warhead_score": warhead_score, "has_warhead": bool(hits)}
        for cat, ranked_csv in ranked_csvs.items():
            # Production-realistic: no curated evidence for an unknown compound
            comp = composite_for_category(target_scores, wh_pack, qsar, cat, evidence_weight=0.0)
            rank = rank_against_csv(comp, ranked_csv)
            with ranked_csv.open() as fh:
                size = sum(1 for _ in csv.DictReader(fh))
            row[f"composite_{cat}"] = comp
            row[f"rank_{cat}"] = rank
            row[f"size_{cat}"] = size
            # Sanity column: what if we had generously credited evidence=high?
            row[f"composite_{cat}_with_high_evidence"] = composite_for_category(
                target_scores, wh_pack, qsar, cat, evidence_weight=1.0
            )

        rows.append(row)
        ranks = " ".join(f"{cat}={row[f'rank_{cat}']}/{row[f'size_{cat}']}" for cat in ranked_csvs)
        print(f"  {c['name']:<22}  {ranks}  wh={row['has_warhead']}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with OUT_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"wrote {OUT_PATH.relative_to(REPO_ROOT)}")
    print()
    print("=== Precision summary (fraction of negative controls correctly OUTSIDE top-N) ===")
    valid = [r for r in rows if "rank_rescue" in r]
    for cat in ("rescue", "maintenance", "remission"):
        for N in (5, 10, 20):
            ok = sum(1 for r in valid if r[f"rank_{cat}"] > N)
            pct = 100 * ok / len(valid)
            print(f"  {cat:<11}  precision@{N:<2}  {ok}/{len(valid)} = {pct:.1f}%")
    print()
    print("Overall (excluded from top-N of EVERY category):")
    for N in (5, 10, 20):
        ok = sum(1 for r in valid if all(r[f"rank_{cat}"] > N for cat in ("rescue", "maintenance", "remission")))
        print(f"  precision@{N:<2}  {ok}/{len(valid)} = {100*ok/len(valid):.1f}%")

    # Flag any leaks
    print()
    leaks = []
    for r in valid:
        for cat in ("rescue", "maintenance", "remission"):
            if r[f"rank_{cat}"] <= 10:
                leaks.append((r["name"], cat, r[f"rank_{cat}"], r[f"size_{cat}"], r[f"composite_{cat}"]))
    if leaks:
        print(f"⚠️  Leaks into top-10 ({len(leaks)}):")
        for name, cat, rank, size, comp in leaks:
            print(f"    {name:<22} {cat:<11} rank {rank}/{size}  composite={comp}")
    else:
        print("✅ No leaks into any top-10.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
