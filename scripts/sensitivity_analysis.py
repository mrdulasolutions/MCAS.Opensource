"""Sensitivity analysis on the composite ranking weights.

The composite formula in rank_hypotheses.py has six tunable weights:

  w_evidence      0.30   weight on curated evidence_level
  w_target        0.35   weight on per-category target-similarity mix
  w_qed           0.10   weight on QED (generated analogs only)
  w_warhead       0.10   weight on covalent-warhead score (KEAP1 axis only)
  w_safety        0.15   weight on QSAR (1-hERG)*0.5 + (1-AMES)*0.5
  w_bbb_context   0.05   weight on BBB_score (sign depends on category)

This script sweeps each weight in turn at {0.5x, 1.5x} of its nominal value,
re-ranks all three categories, and reports:

  - Spearman ρ between perturbed and baseline composite scores
  - Top-10 Jaccard overlap (perturbed top-10 ∩ baseline top-10) / 10
  - Top-1 stability (does #1 change?)
  - Compounds that entered / left each top-10

Output: outputs/sensitivity_analysis.csv + console summary.

Used as the methodology check in EXP-008.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

LIB_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
GEN_CSV = REPO_ROOT / "outputs" / "reinvent_generated.csv"
WARHEAD_CSV = REPO_ROOT / "outputs" / "warhead_scores.csv"
QSAR_CSV = REPO_ROOT / "outputs" / "qsar_predictions.csv"
OUT_CSV = REPO_ROOT / "outputs" / "sensitivity_analysis.csv"
TOP_CHANGES_CSV = REPO_ROOT / "outputs" / "sensitivity_top10_changes.csv"

CATEGORY_TARGETS = {
    "rescue":      {"HRH1": 0.40, "HRH2": 0.20, "CYSLTR1": 0.20, "MRGPRX2": 0.20},
    # Maintenance — 8 weighted targets after EXP-021 (added SYK + PTGS2; CNR2 was added in EXP-019).
    "maintenance": {"CYSLTR1": 0.20, "HRH1": 0.12, "BTK": 0.12, "MRGPRX2": 0.12,
                    "KEAP1": 0.12, "CNR2": 0.12, "SYK": 0.10, "PTGS2": 0.10},
    # Remission — 6 weighted targets after EXP-021 (added SYK; CNR2 added in EXP-019).
    "remission":   {"MRGPRX2": 0.22, "KIT": 0.22, "KEAP1": 0.28,
                    "GLP1R": 0.08, "CNR2": 0.10, "SYK": 0.10},
}

BASELINE_WEIGHTS = {
    "w_evidence":     0.30,
    "w_target":       0.35,
    "w_qed":          0.10,
    "w_warhead":      0.10,
    "w_safety":       0.15,
    "w_bbb_context":  0.05,
}

EVIDENCE_LEVEL_MAP = {"high": 1.0, "medium": 0.6, "low": 0.3, "": 0.0}


def _load_c151_table():
    out = {}
    p = REPO_ROOT / "outputs" / "c151_adduct_energies.csv"
    if not p.exists():
        return out
    with p.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("smiles", "")
            if smi and row.get("status") == "ok":
                try:
                    out[smi] = float(row.get("score_c151") or 0)
                except ValueError:
                    pass
    return out


def _load_chembl_table():
    out = {}
    p = REPO_ROOT / "outputs" / "chembl_predictions.csv"
    if not p.exists():
        return out
    with p.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("smiles", "")
            if not smi:
                continue
            preds = {}
            for col, val in row.items():
                if col.startswith("chembl_pIC50_") and val:
                    try:
                        preds[col.replace("chembl_pIC50_", "")] = float(val)
                    except ValueError:
                        pass
            if preds:
                out[smi] = preds
    return out


def load_records():
    """Return list of records ready for composite scoring."""
    target_scores = {}
    for path in (REPO_ROOT / "outputs").glob("docking_*.csv"):
        target = path.stem.replace("docking_", "")
        with path.open() as fh:
            for row in csv.DictReader(fh):
                smi = row.get("smiles", "")
                if not smi:
                    continue
                target_scores.setdefault(smi, {})[target] = float(row.get("score") or 0)

    warhead = {}
    if WARHEAD_CSV.exists():
        with WARHEAD_CSV.open() as fh:
            for row in csv.DictReader(fh):
                smi = row.get("smiles", "")
                if smi:
                    warhead[smi] = {
                        "has_warhead": row.get("has_warhead") == "True",
                        "warhead_score": float(row.get("warhead_score") or 0),
                    }

    qsar = {}
    if QSAR_CSV.exists():
        with QSAR_CSV.open() as fh:
            for row in csv.DictReader(fh):
                smi = row.get("smiles", "")
                if smi:
                    qsar[smi] = {
                        "hERG": float(row.get("hERG_score") or 0.5),
                        "AMES": float(row.get("AMES_score") or 0.5),
                        "BBB":  float(row.get("BBB_Martins_score") or 0.5),
                    }

    records = []
    with LIB_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("canonical_smiles") or row.get("smiles") or ""
            if not smi:
                continue
            records.append({
                "name": row["name"],
                "smiles": smi,
                "category": row["category"],
                "source": "library",
                "evidence_level": row.get("evidence_level", ""),
                "qed": None,
            })

    if GEN_CSV.exists():
        with GEN_CSV.open() as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                smi = row.get("smiles", "")
                if not smi:
                    continue
                seed = row.get("seed", "")
                category = "remission" if seed == "Sulforaphane" else "candidate"
                records.append({
                    "name": f"GEN_{i:04d}",
                    "smiles": smi,
                    "category": category,
                    "source": "reinvent_generated",
                    "evidence_level": "",
                    "qed": float(row.get("qed") or 0.0),
                })

    # Attach scores
    c151_table = _load_c151_table()
    chembl_table = _load_chembl_table()
    for r in records:
        r["target_scores"] = target_scores.get(r["smiles"], {})
        r["warhead"] = warhead.get(r["smiles"], {"has_warhead": False, "warhead_score": 0.0})
        r["qsar"] = qsar.get(r["smiles"], {"hERG": 0.5, "AMES": 0.5, "BBB": 0.5})
        r["c151_score"] = c151_table.get(r["smiles"], 0.0)
        r["chembl_preds"] = chembl_table.get(r["smiles"], {})

    return records


def composite(record, weights):
    """Compute composite under arbitrary weights dict."""
    cat = record["category"]
    cat_for_weights = cat if cat in CATEGORY_TARGETS else "remission"
    target_mix = CATEGORY_TARGETS[cat_for_weights]

    s = 0.0
    s += weights["w_evidence"] * EVIDENCE_LEVEL_MAP.get(record["evidence_level"], 0.0)

    dock_total = 0.0
    weight_total = 0.0
    for tgt, w in target_mix.items():
        score = record["target_scores"].get(tgt, 0.0)
        dock_total += score * w
        weight_total += w
    if weight_total > 0:
        s += weights["w_target"] * (dock_total / weight_total)

    if record["source"] == "reinvent_generated" and record["qed"] is not None:
        s += weights["w_qed"] * record["qed"]

    if "KEAP1" in target_mix:
        s += weights["w_warhead"] * record["warhead"]["warhead_score"]
        keap1_sim = record["target_scores"].get("KEAP1", 0.0)
        if keap1_sim > 0.4 and not record["warhead"]["has_warhead"]:
            s -= 0.08
        # C151 covalent adduct (EXP-012) — small fixed bonus, not weight-perturbed
        s += record.get("c151_score", 0.0) * 0.05

    herg = record["qsar"]["hERG"]
    ames = record["qsar"]["AMES"]
    bbb = record["qsar"]["BBB"]
    safety = 0.5 * (1 - herg) + 0.5 * (1 - ames)
    s += weights["w_safety"] * safety

    if cat_for_weights in ("maintenance", "remission"):
        s += weights["w_bbb_context"] * (bbb - 0.5)
    elif cat_for_weights == "rescue":
        hrh1 = record["target_scores"].get("HRH1", 0.0)
        if hrh1 < 0.5:
            s -= weights["w_bbb_context"] * 0.6 * (bbb - 0.5)

    # ChEMBL-trained potency bonus (EXP-011) — fixed +0.10 max, not weight-perturbed
    chembl_preds = record.get("chembl_preds", {})
    if chembl_preds:
        import math
        chembl_total = 0.0
        chembl_weight_total = 0.0
        for tgt, w in target_mix.items():
            pic50 = chembl_preds.get(tgt)
            if pic50 is not None:
                chembl_total += (1.0 / (1.0 + math.exp(-(pic50 - 6.0)))) * w
                chembl_weight_total += w
        if chembl_weight_total > 0:
            s += min(chembl_total / chembl_weight_total, 1.0) * 0.10

    return s


def rank_by_category(records, weights, category):
    sub = [r for r in records if r["category"] == category]
    scored = [(r["name"], composite(r, weights)) for r in sub]
    scored.sort(key=lambda x: -x[1])
    return [name for name, _ in scored], dict(scored)


def spearman(xs: Iterable[float], ys: Iterable[float]) -> float:
    import math
    xs, ys = list(xs), list(ys)
    n = len(xs)
    if n < 2:
        return float("nan")
    def rank(values):
        idx = sorted(range(n), key=lambda i: values[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and values[idx[j + 1]] == values[idx[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                ranks[idx[k]] = avg
            i = j + 1
        return ranks
    rx, ry = rank(xs), rank(ys)
    mean_x = sum(rx) / n
    mean_y = sum(ry) / n
    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(rx, ry))
    den = math.sqrt(
        sum((a - mean_x) ** 2 for a in rx) * sum((b - mean_y) ** 2 for b in ry)
    )
    return num / den if den else float("nan")


def main() -> int:
    records = load_records()
    print(f"loaded {len(records)} records")

    # Baseline rankings
    baseline = {}
    for cat in ("rescue", "maintenance", "remission"):
        order, scores = rank_by_category(records, BASELINE_WEIGHTS, cat)
        baseline[cat] = {"order": order, "scores": scores}
        print(f"  baseline {cat:<11}  {len(order)} candidates  top1={order[0]}")

    # Sweep
    print()
    rows = []
    top10_changes = []
    for weight_name in BASELINE_WEIGHTS:
        for scale in (0.5, 1.5):
            perturbed_weights = dict(BASELINE_WEIGHTS)
            perturbed_weights[weight_name] = BASELINE_WEIGHTS[weight_name] * scale
            label = f"{weight_name} × {scale:.1f}"
            for cat in ("rescue", "maintenance", "remission"):
                order_p, scores_p = rank_by_category(records, perturbed_weights, cat)
                names = baseline[cat]["order"]
                base_scores = [baseline[cat]["scores"][n] for n in names]
                p_scores = [scores_p[n] for n in names]
                rho = spearman(base_scores, p_scores)

                base_top10 = set(baseline[cat]["order"][:10])
                p_top10 = set(order_p[:10])
                jaccard = len(base_top10 & p_top10) / max(len(base_top10 | p_top10), 1)
                entered = sorted(p_top10 - base_top10)
                left = sorted(base_top10 - p_top10)
                top1_same = order_p[0] == baseline[cat]["order"][0]

                rows.append({
                    "weight": weight_name,
                    "scale": scale,
                    "category": cat,
                    "spearman_rho_vs_baseline": round(rho, 4),
                    "top10_jaccard": round(jaccard, 3),
                    "top1_baseline": baseline[cat]["order"][0],
                    "top1_perturbed": order_p[0],
                    "top1_same": top1_same,
                    "entered_top10": ";".join(entered),
                    "left_top10": ";".join(left),
                    "n_compounds": len(order_p),
                })
                for n in entered:
                    top10_changes.append({"weight": weight_name, "scale": scale, "category": cat,
                                          "compound": n, "change": "entered",
                                          "baseline_rank": baseline[cat]["order"].index(n) + 1,
                                          "perturbed_rank": order_p.index(n) + 1})
                for n in left:
                    top10_changes.append({"weight": weight_name, "scale": scale, "category": cat,
                                          "compound": n, "change": "left",
                                          "baseline_rank": baseline[cat]["order"].index(n) + 1,
                                          "perturbed_rank": order_p.index(n) + 1})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT_CSV.relative_to(REPO_ROOT)}")

    if top10_changes:
        with TOP_CHANGES_CSV.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(top10_changes[0].keys()))
            writer.writeheader()
            writer.writerows(top10_changes)
        print(f"wrote {TOP_CHANGES_CSV.relative_to(REPO_ROOT)}  ({len(top10_changes)} top-10 movements)")

    # Print summary tables
    print()
    print("=== Per-weight robustness (mean across scales + categories) ===")
    weight_rho = {w: [] for w in BASELINE_WEIGHTS}
    weight_jacc = {w: [] for w in BASELINE_WEIGHTS}
    weight_top1 = {w: [] for w in BASELINE_WEIGHTS}
    for r in rows:
        weight_rho[r["weight"]].append(r["spearman_rho_vs_baseline"])
        weight_jacc[r["weight"]].append(r["top10_jaccard"])
        weight_top1[r["weight"]].append(1.0 if r["top1_same"] else 0.0)
    print(f"  {'weight':<16}  {'mean ρ':>8}  {'min ρ':>8}  {'mean top10 J':>14}  {'top1 same %':>12}")
    for w in BASELINE_WEIGHTS:
        rs = weight_rho[w]
        js = weight_jacc[w]
        t1 = weight_top1[w]
        print(f"  {w:<16}  {sum(rs)/len(rs):>8.3f}  {min(rs):>8.3f}  {sum(js)/len(js):>14.3f}  {100*sum(t1)/len(t1):>11.1f}%")

    print()
    print("=== Highest-leverage weight changes ===")
    sorted_rows = sorted(rows, key=lambda r: r["spearman_rho_vs_baseline"])
    for r in sorted_rows[:6]:
        print(f"  {r['weight']:<16} × {r['scale']:.1f}  {r['category']:<11}  ρ={r['spearman_rho_vs_baseline']:.3f}  J={r['top10_jaccard']:.2f}  top1={r['top1_perturbed']} (was {r['top1_baseline']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
