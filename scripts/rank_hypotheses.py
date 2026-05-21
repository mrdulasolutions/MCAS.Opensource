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
OUT_DIR = REPO_ROOT / "outputs"
HYP_DIR = REPO_ROOT / "hypotheses"


# Per-category target weights for docking-style score aggregation.
# Pick targets that matter for what the category is trying to do.
CATEGORY_TARGETS: dict[str, dict[str, float]] = {
    "rescue":      {"HRH1": 0.4, "HRH2": 0.2, "CYSLTR1": 0.2, "MRGPRX2": 0.2},
    "maintenance": {"CYSLTR1": 0.3, "HRH1": 0.15, "BTK": 0.15, "MRGPRX2": 0.2, "NFE2L2": 0.2},
    "remission":   {"MRGPRX2": 0.3, "KIT": 0.3, "NFE2L2": 0.3, "GLP1R": 0.1},
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


def composite(record: dict, target_scores: dict) -> float:
    """Weighted composite per record."""
    s = 0.0
    cat = record.get("category", "")
    s += EVIDENCE_WEIGHT.get(record.get("evidence_level", ""), 0.0) * 0.4

    weights = CATEGORY_TARGETS.get(cat, {})
    dock_total = 0.0
    weight_total = 0.0
    for tgt, w in weights.items():
        tgt_record = target_scores.get(tgt, {})
        if tgt_record:
            dock_total += tgt_record["score"] * w
            weight_total += w
    if weight_total > 0:
        s += (dock_total / weight_total) * 0.5

    # small drug-likeness bonus for generated analogs (we already have evidence
    # weights for library compounds)
    if record.get("source") == "reinvent_generated":
        try:
            s += float(record.get("qed") or 0.0) * 0.1
        except ValueError:
            pass
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


def update_hypothesis_doc(category: str, top: list[dict]) -> None:
    """Replace the 'Top AI-ranked candidates' section with the latest top-10."""
    md = HYP_DIR / f"{category}.md"
    if not md.exists():
        return
    text = md.read_text()
    marker = "## Top AI-ranked candidates"
    if marker not in text:
        return

    rows_md = ["", "| # | Name | Composite | MRGPRX2 | KIT | NFE2L2 | HRH1 | Source |",
               "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(top[:10], start=1):
        rows_md.append(
            f"| {i} | "
            f"{r['name']} | "
            f"{r['composite_score']:.3f} | "
            f"{r.get('score_MRGPRX2', 0):.2f} | "
            f"{r.get('score_KIT', 0):.2f} | "
            f"{r.get('score_NFE2L2', 0):.2f} | "
            f"{r.get('score_HRH1', 0):.2f} | "
            f"{r['source']} |"
        )
    block = (
        marker
        + "\n\n_Auto-generated by `scripts/rank_hypotheses.py` from the current "
          "library + generated analogs + ligand-based target scores. Higher "
          "composite = better hypothesis._\n"
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
    print(f"library: {len(library)}, generated: {len(generated)}, scored smiles: {len(target_scores)}")

    by_category: dict[str, list[dict]] = {"rescue": [], "maintenance": [], "remission": []}

    for rec in library + generated:
        smi = rec.get("smiles", "")
        ts = target_scores.get(smi, {})
        for tgt in CATEGORY_TARGETS["rescue"] | CATEGORY_TARGETS["maintenance"] | CATEGORY_TARGETS["remission"]:
            rec[f"score_{tgt}"] = ts.get(tgt, {}).get("score", 0.0)
            rec[f"ref_{tgt}"] = ts.get(tgt, {}).get("best_ref", "")
        rec["composite_score"] = composite(rec, ts)

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
