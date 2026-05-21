"""Final multi-objective ranking (script version of notebook 05).

Joins:
- data/compounds/MCAS_Compound_Library_v1.csv  (library compounds + metadata)
- outputs/reinvent_generated.csv               (locally-generated SFN analogs)
- outputs/docking_<target>.csv                 (ligand-based binding-class scores)

Produces:
- outputs/ranked_rescue.csv
- outputs/ranked_maintenance.csv
- outputs/ranked_remission.csv
- outputs/ranked_all.csv

Also writes a "Top AI-ranked candidates" table to each hypotheses/<category>.md
so the hypothesis docs reflect the current ranking.
"""
from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
GEN_CSV = REPO_ROOT / "outputs" / "reinvent_generated.csv"
WARHEAD_CSV = REPO_ROOT / "outputs" / "warhead_scores.csv"
QSAR_CSV = REPO_ROOT / "outputs" / "qsar_predictions.csv"
OUT_DIR = REPO_ROOT / "outputs"
HYP_DIR = REPO_ROOT / "hypotheses"


# Per-category target weights for docking-style score aggregation.
# Pick targets that matter for what the category is trying to do.
CATEGORY_TARGETS: dict[str, dict[str, float]] = {
    "rescue":      {"HRH1": 0.4, "HRH2": 0.2, "CYSLTR1": 0.2, "MRGPRX2": 0.2},
    "maintenance": {"CYSLTR1": 0.3, "HRH1": 0.15, "BTK": 0.15, "MRGPRX2": 0.2, "KEAP1": 0.2},
    "remission":   {"MRGPRX2": 0.3, "KIT": 0.3, "KEAP1": 0.3, "GLP1R": 0.1},
}

EVIDENCE_WEIGHT = {"high": 1.0, "medium": 0.6, "low": 0.3, "": 0.0}


def load_library() -> list[dict]:
    out = []
    with LIB_CSV.open() as fh:
        for row in csv.DictReader(fh):
            out.append({
                "name": row["name"],
                "smiles": row.get("canonical_smiles") or row.get("smiles") or "",
                "category": row["category"],
                "subcategory": row.get("subcategory", ""),
                "mechanism": row.get("mechanism", ""),
                "target": row.get("target", ""),
                "evidence_level": row.get("evidence_level", ""),
                "source": "library",
                "biologic_flag": row.get("biologic_flag", ""),
            })
    return out


def load_generated() -> list[dict]:
    if not GEN_CSV.exists():
        return []
    out = []
    with GEN_CSV.open() as fh:
        for i, row in enumerate(csv.DictReader(fh)):
            # Cross-categorize generated analogs by seed: SFN seed → remission
            seed = row.get("seed", "")
            cat = "remission" if seed == "Sulforaphane" else "candidate"
            out.append({
                "name": f"GEN_{i:04d}",
                "smiles": row.get("smiles", ""),
                "category": cat,
                "subcategory": f"generated_{seed.lower()}_analog",
                "mechanism": f"{seed}-class hypothesis (SFN warhead / bioisostere)",
                "target": "",
                "evidence_level": "low",                  # AI-generated; not validated
                "source": "reinvent_generated",
                "qed": row.get("qed"),
                "sa_proxy": row.get("sa_score_proxy"),
                "tanimoto_to_SFN": row.get("tanimoto_to_SFN"),
                "lipinski_pass": row.get("lipinski_pass"),
            })
    return out


def load_qsar() -> dict[str, dict]:
    """Return {smiles: {hERG_score, AMES_score, BBB_score}} from outputs/qsar_predictions.csv."""
    out: dict[str, dict] = {}
    if not QSAR_CSV.exists():
        return out
    with QSAR_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("smiles", "")
            if not smi:
                continue
            out[smi] = {
                "hERG_score": float(row.get("hERG_score") or 0.5),
                "AMES_score": float(row.get("AMES_score") or 0.5),
                "BBB_score":  float(row.get("BBB_Martins_score") or 0.5),
            }
    return out


def load_warhead_scores() -> dict[str, dict]:
    """Return {smiles: {has_warhead, warheads, keap1_pharmacophore_pass, warhead_score}}."""
    out: dict[str, dict] = {}
    if not WARHEAD_CSV.exists():
        return out
    with WARHEAD_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("smiles", "")
            if not smi:
                continue
            out[smi] = {
                "has_warhead": row.get("has_warhead") == "True",
                "warheads": row.get("warheads", ""),
                "keap1_pharmacophore_pass": row.get("keap1_pharmacophore_pass") == "True",
                "warhead_score": float(row.get("warhead_score") or 0.0),
            }
    return out


def load_target_scores() -> dict[str, dict[str, dict]]:
    """Return {smiles: {target: {score, best_ref}, ...}, ...}."""
    by_smiles: dict[str, dict] = {}
    for path in OUT_DIR.glob("docking_*.csv"):
        target = path.stem.replace("docking_", "")
        with path.open() as fh:
            for row in csv.DictReader(fh):
                smi = row.get("smiles", "")
                if not smi:
                    continue
                by_smiles.setdefault(smi, {})[target] = {
                    "score": float(row.get("score") or 0.0),
                    "best_ref": row.get("best_ref", ""),
                }
    return by_smiles


def composite(record: dict, target_scores: dict, warhead: dict, qsar: dict) -> float:
    """Weighted composite per record.

    Components:
      - 0.30 * evidence_level
      - 0.35 * weighted target similarity (per-category target mix)
      - 0.10 * QED (generated analogs only — library evidence already covers it)
      - 0.10 * warhead score (KEAP1 axis only)
      - 0.15 * safety bonus = 0.5*(1 - hERG) + 0.5*(1 - AMES)
              + small contextual BBB bonus (high BBB for maintenance/remission
                with neuro/mast-cell-stabilizer story; low BBB tolerated for
                rescue if HRH1 score is high).
      - explicit penalty: KEAP1-targeting Tanimoto >0.4 without a warhead = -0.08
    """
    s = 0.0
    cat = record.get("category", "")
    weights = CATEGORY_TARGETS.get(cat, {})

    s += EVIDENCE_WEIGHT.get(record.get("evidence_level", ""), 0.0) * 0.30

    dock_total = 0.0
    weight_total = 0.0
    for tgt, w in weights.items():
        tgt_record = target_scores.get(tgt, {})
        if tgt_record:
            dock_total += tgt_record["score"] * w
            weight_total += w
    if weight_total > 0:
        s += (dock_total / weight_total) * 0.35

    if record.get("source") == "reinvent_generated":
        try:
            s += float(record.get("qed") or 0.0) * 0.10
        except ValueError:
            pass

    # KEAP1-axis warhead boost / penalty
    if "KEAP1" in weights:
        wh_score = warhead.get("warhead_score", 0.0) if warhead else 0.0
        s += wh_score * 0.10
        keap1_sim = target_scores.get("KEAP1", {}).get("score", 0.0)
        if keap1_sim > 0.4 and not (warhead and warhead.get("has_warhead")):
            s -= 0.08

    # Safety bonus from QSAR (low hERG / low AMES = good)
    if qsar:
        herg = qsar.get("hERG_score", 0.5)
        ames = qsar.get("AMES_score", 0.5)
        bbb  = qsar.get("BBB_score", 0.5)
        safety = 0.5 * (1.0 - herg) + 0.5 * (1.0 - ames)
        s += safety * 0.15

        # contextual BBB bonus
        if cat in ("maintenance", "remission"):
            s += (bbb - 0.5) * 0.05    # neuro / systemic candidates: high BBB good
        elif cat == "rescue":
            # rescue prefers peripheral unless HRH1 is hit (then BBB is ok)
            hrh1_sim = target_scores.get("HRH1", {}).get("score", 0.0)
            if hrh1_sim < 0.5:
                s -= (bbb - 0.5) * 0.03

    return round(s, 4)


def write_ranked(name: str, rows: list[dict]) -> Path:
    rows = sorted(rows, key=lambda r: r["composite_score"], reverse=True)
    out = OUT_DIR / f"ranked_{name}.csv"
    if not rows:
        return out
    fields: list[str] = []
    seen = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                fields.append(k)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return out


def _git_commit() -> str:
    """Return short commit hash, or 'uncommitted' if not in a git repo / dirty."""
    import subprocess
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return out or "uncommitted"
    except Exception:
        return "uncommitted"


def update_hypothesis_doc(category: str, top: list[dict]) -> None:
    """Replace the 'Top AI-ranked candidates' section with the latest top-10."""
    md = HYP_DIR / f"{category}.md"
    if not md.exists():
        return
    text = md.read_text()
    marker = "## Top AI-ranked candidates"
    if marker not in text:
        return

    rows_md = ["", "| # | Name | Composite | KEAP1 | MRGPRX2 | KIT | HRH1 | Warhead | hERG | AMES | BBB | Source |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    def _fmt(v):
        try: return f"{float(v):.2f}"
        except (TypeError, ValueError): return "—"
    for i, r in enumerate(top[:10], start=1):
        wh_mark = "yes" if r.get("has_warhead") else "—"
        rows_md.append(
            f"| {i} | "
            f"{r['name']} | "
            f"{r['composite_score']:.3f} | "
            f"{r.get('score_KEAP1', 0):.2f} | "
            f"{r.get('score_MRGPRX2', 0):.2f} | "
            f"{r.get('score_KIT', 0):.2f} | "
            f"{r.get('score_HRH1', 0):.2f} | "
            f"{wh_mark} | "
            f"{_fmt(r.get('hERG_score'))} | "
            f"{_fmt(r.get('AMES_score'))} | "
            f"{_fmt(r.get('BBB_score'))} | "
            f"{r['source']} |"
        )
    from datetime import datetime, timezone
    provenance = (
        f"\n\n> 🤖 **Auto-generated artifact.** Produced by "
        f"`scripts/rank_hypotheses.py` on "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} "
        f"from commit `{_git_commit()}`. "
        f"Inputs: `data/compounds/MCAS_Compound_Library_v1.csv`, "
        f"`outputs/reinvent_generated.csv`, `outputs/docking_*.csv`, "
        f"`outputs/warhead_scores.csv`, `outputs/qsar_predictions.csv`. "
        f"Composite formula and weights documented in "
        f"[EXP-005](../experiments/EXP-005-multi-objective-ranking.md). "
        f"Recovery benchmark: [EXP-006](../experiments/EXP-006-known-actives-recovery.md).\n"
    )
    block = (
        marker
        + provenance
        + "\n_Higher composite = better hypothesis. Edit `scripts/rank_hypotheses.py` "
          "to change weights or category target mix; the next run will overwrite this table._\n"
        + "\n".join(rows_md)
        + "\n"
    )

    # Replace from marker to the next H2 header, preserving the rest
    after_marker = text.split(marker, 1)[1]
    if "\n## " in after_marker:
        next_h2 = "\n## " + after_marker.split("\n## ", 1)[1]
        new_text = text.split(marker, 1)[0] + block + "\n" + next_h2
    else:
        new_text = text.split(marker, 1)[0] + block

    md.write_text(new_text)


def main() -> int:
    library = load_library()
    generated = load_generated()
    target_scores = load_target_scores()
    warhead_scores = load_warhead_scores()
    qsar_scores = load_qsar()
    print(f"library: {len(library)}, generated: {len(generated)}, target-scored: {len(target_scores)}, warhead: {len(warhead_scores)}, qsar: {len(qsar_scores)}")

    by_category: dict[str, list[dict]] = {"rescue": [], "maintenance": [], "remission": []}

    for rec in library + generated:
        smi = rec.get("smiles", "")
        ts = target_scores.get(smi, {})
        wh = warhead_scores.get(smi, {})
        qs = qsar_scores.get(smi, {})
        for tgt in CATEGORY_TARGETS["rescue"] | CATEGORY_TARGETS["maintenance"] | CATEGORY_TARGETS["remission"]:
            rec[f"score_{tgt}"] = ts.get(tgt, {}).get("score", 0.0)
            rec[f"ref_{tgt}"] = ts.get(tgt, {}).get("best_ref", "")
        rec["has_warhead"] = wh.get("has_warhead", False)
        rec["warheads"] = wh.get("warheads", "")
        rec["keap1_pharm_pass"] = wh.get("keap1_pharmacophore_pass", False)
        rec["hERG_score"] = qs.get("hERG_score", "")
        rec["AMES_score"] = qs.get("AMES_score", "")
        rec["BBB_score"] = qs.get("BBB_score", "")
        rec["composite_score"] = composite(rec, ts, wh, qs)

        if rec["category"] in by_category:
            by_category[rec["category"]].append(rec)

    all_rows = []
    for cat, rows in by_category.items():
        path = write_ranked(cat, rows)
        all_rows.extend(rows)
        print(f"  {cat}: {len(rows)} ranked -> {path.relative_to(REPO_ROOT)}")
        if rows:
            top = sorted(rows, key=lambda r: r["composite_score"], reverse=True)
            update_hypothesis_doc(cat, top)
            print(f"    updated hypotheses/{cat}.md with top 10")

    write_ranked("all", all_rows)
    print(f"  all: {len(all_rows)} ranked -> outputs/ranked_all.csv")

    # Print top 5 per category for the operator
    print()
    for cat in ("rescue", "maintenance", "remission"):
        print(f"--- top 5 {cat} ---")
        rows = sorted(by_category[cat], key=lambda r: r["composite_score"], reverse=True)
        for r in rows[:5]:
            print(f"  {r['composite_score']:>6.3f}  {r['name']:<30}  src={r['source']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
