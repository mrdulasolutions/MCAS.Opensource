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
VINA_CSV = REPO_ROOT / "outputs" / "docking_KEAP1_vina.csv"
BTB_CSV = REPO_ROOT / "outputs" / "docking_KEAP1_btb_c151.csv"
C151_CSV = REPO_ROOT / "outputs" / "c151_adduct_energies.csv"
CHEMBL_PRED_CSV = REPO_ROOT / "outputs" / "chembl_predictions.csv"
MAST_CELL_PRED_CSV = REPO_ROOT / "outputs" / "mast_cell_predictions.csv"
ENAMINE_CSV = REPO_ROOT / "outputs" / "exp_017" / "enamine_lookup.csv"
OUT_DIR = REPO_ROOT / "outputs"
HYP_DIR = REPO_ROOT / "hypotheses"

# SFN-class seed SMILES for novelty tagging (canonical forms used in generation).
SFN_CLASS_SEEDS = {
    "CS(=O)CCCCN=C=S",   # Sulforaphane
    "CS(=O)CCCN=C=S",    # Iberin
    "CSCCCCN=C=S",       # Erucin
    "CS(=O)/C=C/CCN=C=S",  # Sulforaphene
    "C=CCN=C=S",         # AITC
    "S=C=NCc1ccccc1",    # BITC
    "S=C=NCCc1ccccc1",   # PEITC
}


# Per-category target weights for docking-style score aggregation.
# Pick targets that matter for what the category is trying to do.
CATEGORY_TARGETS: dict[str, dict[str, float]] = {
    "rescue":      {"HRH1": 0.40, "HRH2": 0.20, "CYSLTR1": 0.20, "MRGPRX2": 0.20},
    # Maintenance — SYK (FcεRI proximal) + PTGS2 (COX-2) added in EXP-021.
    "maintenance": {"CYSLTR1": 0.20, "HRH1": 0.12, "BTK": 0.12, "MRGPRX2": 0.12,
                    "KEAP1": 0.12, "CNR2": 0.12, "SYK": 0.10, "PTGS2": 0.10},
    # Remission — SYK gets a small weight too (proximal FcεRI is upstream
    # enough to count). PTGS2 stays out — COX-2 is symptomatic, not remission.
    "remission":   {"MRGPRX2": 0.22, "KIT": 0.22, "KEAP1": 0.28,
                    "GLP1R": 0.08, "CNR2": 0.10, "SYK": 0.10},
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


def load_mast_cell_predictions() -> dict[str, float]:
    """Return {smiles: mast_cell_stabilizer_prob ∈ [0, 1]} from EXP-016."""
    out: dict[str, float] = {}
    if not MAST_CELL_PRED_CSV.exists():
        return out
    with MAST_CELL_PRED_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("smiles", "")
            p = row.get("mast_cell_stabilizer_prob", "")
            if smi and p:
                try:
                    out[smi] = float(p)
                except ValueError:
                    pass
    return out


def load_chembl_predictions() -> dict[str, dict[str, float]]:
    """Return {smiles: {target: predicted_pIC50}} from outputs/chembl_predictions.csv (EXP-011).

    Predictions are continuous pIC50 values. Higher = more potent.
    Range typically 4-9 (10 µM to 1 nM). The composite normalizes to
    [0, 1] via a logistic centered at pIC50=6 (=1 µM).
    """
    out: dict[str, dict[str, float]] = {}
    if not CHEMBL_PRED_CSV.exists():
        return out
    with CHEMBL_PRED_CSV.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            smi = row.get("smiles", "")
            if not smi:
                continue
            preds = {}
            for col, val in row.items():
                if col.startswith("chembl_pIC50_") and val:
                    try:
                        preds[col.replace("chembl_pIC50_", "")] = float(val)
                    except ValueError:
                        continue
            if preds:
                out[smi] = preds
    return out


def load_c151_adducts() -> dict[str, dict]:
    """Return {smiles: {score_c151, dE_kcal_per_mol}}.

    Covalent C151 adduct thermodynamic proxy (EXP-012). Higher score_c151
    (closer to 1.0) = more favorable adduct formation.
    """
    out: dict[str, dict] = {}
    if not C151_CSV.exists():
        return out
    with C151_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("smiles", "")
            if not smi or row.get("status") != "ok":
                continue
            try:
                out[smi] = {
                    "score_c151": float(row.get("score_c151") or 0.0),
                    "dE_kcal_per_mol": float(row.get("dE_kcal_per_mol") or 0.0),
                }
            except (ValueError, TypeError):
                continue
    return out


def load_btb_covalent() -> dict[str, dict]:
    """BTB Cys-151 encounter docking fused with adduct energy (EXP-023)."""
    out: dict[str, dict] = {}
    if not BTB_CSV.exists():
        return out
    with BTB_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("smiles", "")
            if not smi or row.get("status") != "ok":
                continue
            try:
                out[smi] = {
                    "score_btb_covalent": float(row.get("score_btb_covalent") or 0.0),
                    "vina_dG_btb": float(row.get("vina_dG") or 0.0),
                }
            except (ValueError, TypeError):
                continue
    return out


def load_enamine() -> dict[str, dict]:
    """Map SMILES / InChIKey → REAL-space flags from EXP-017 lookup."""
    out: dict[str, dict] = {}
    if not ENAMINE_CSV.exists():
        return out
    with ENAMINE_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("canonical_smiles") or row.get("smiles") or ""
            info = {
                "real_space_plausible": str(row.get("real_space_plausible", "")).lower() in ("true", "1", "yes"),
                "enamine_real_search": row.get("enamine_real_search", ""),
                "inchikey": row.get("inchikey", ""),
            }
            if smi:
                out[smi] = info
            if row.get("inchikey"):
                out[row["inchikey"]] = info
    return out


def novelty_features(smiles: str, library_fps: list, seed_fps: list) -> dict:
    """Tanimoto-to-library / to-SFN-class novelty tags (EXP-025). No RDKit required if fps prebuilt."""
    from rdkit import Chem, DataStructs
    from rdkit.Chem import AllChem

    mol = Chem.MolFromSmiles(smiles) if smiles else None
    if mol is None:
        return {
            "max_tanimoto_to_library": "",
            "tanimoto_to_sfn_class": "",
            "novelty_score": "",
            "near_duplicate_of_seed": False,
            "near_duplicate_of_library": False,
        }
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    max_lib = 0.0
    for rfp in library_fps:
        max_lib = max(max_lib, float(DataStructs.TanimotoSimilarity(fp, rfp)))
    max_seed = 0.0
    for rfp in seed_fps:
        max_seed = max(max_seed, float(DataStructs.TanimotoSimilarity(fp, rfp)))
    # Identity to self in library: treat as library member, not generated novelty issue
    novelty = round(1.0 - max(max_lib, max_seed), 4)
    return {
        "max_tanimoto_to_library": round(max_lib, 4),
        "tanimoto_to_sfn_class": round(max_seed, 4),
        "novelty_score": novelty,
        "near_duplicate_of_seed": max_seed >= 0.90,
        "near_duplicate_of_library": max_lib >= 0.90,
    }


def load_vina_keap1() -> dict[str, dict]:
    """Return {smiles: {vina_kcal_per_mol, vina_ligand_efficiency, heavy_atoms}}
    from outputs/docking_KEAP1_vina.csv. Empty dict if missing.

    Vina ligand efficiency = kcal/mol divided by heavy_atom count — removes
    Vina's well-documented size bias toward large drug-like compounds.
    Most negative LE = strongest per-atom binder.
    """
    out: dict[str, dict] = {}
    if not VINA_CSV.exists():
        return out
    with VINA_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("smiles", "")
            if not smi:
                continue
            try:
                kcal = float(row.get("vina_kcal_per_mol") or "")
                le = float(row.get("vina_ligand_efficiency") or "")
                out[smi] = {
                    "vina_kcal_per_mol": kcal,
                    "vina_ligand_efficiency": le,
                    "heavy_atoms": int(row.get("heavy_atoms") or 0),
                }
            except (ValueError, TypeError):
                continue
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


def pic50_potency_norm(pic50: float) -> float:
    """Normalize a pIC50 prediction to [0, 1] via a logistic centered at 6 (1 µM).

    pIC50  4 → 0.12  (10 µM, baseline / not potent)
    pIC50  5 → 0.27  (1 µM, weak)
    pIC50  6 → 0.50  (100 nM, modest)
    pIC50  7 → 0.73  (10 nM, potent)
    pIC50  8 → 0.88  (1 nM, very potent)
    pIC50  9 → 0.95
    """
    import math
    return 1.0 / (1.0 + math.exp(-(pic50 - 6.0)))


def composite(
    record: dict,
    target_scores: dict,
    warhead: dict,
    qsar: dict,
    vina: dict | None = None,
    c151: dict | None = None,
    chembl: dict | None = None,
    mast_cell: float | None = None,
    btb: dict | None = None,
) -> float:
    """Weighted composite per record.

    Components:
      - 0.30 * evidence_level
      - 0.35 * weighted target similarity (per-category target mix; self-debiased)
      - 0.10 * QED (generated analogs only — library evidence already covers it)
      - 0.10 * warhead score (KEAP1 axis only)
      - 0.15 * safety bonus = 0.5*(1 - hERG) + 0.5*(1 - AMES)
              + small contextual BBB bonus
      - explicit penalty: KEAP1-targeting Tanimoto >0.4 without a warhead = -0.08
      - BTB covalent encounter score (EXP-023) up to +0.05 on KEAP1 axis
      - near-duplicate generated penalty (EXP-025): -0.04 if tanimoto_to_sfn_class ≥ 0.90
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
        # Novelty: penalize near-exact SFN-class copies so GEN_* doesn't
        # dominate remission purely by warhead + self-similarity (EXP-025).
        try:
            t_seed = float(record.get("tanimoto_to_sfn_class") or 0.0)
            if t_seed >= 0.95:
                s -= 0.06
            elif t_seed >= 0.90:
                s -= 0.04
        except (TypeError, ValueError):
            pass

    # KEAP1-axis warhead boost / penalty
    if "KEAP1" in weights:
        wh_score = warhead.get("warhead_score", 0.0) if warhead else 0.0
        s += wh_score * 0.10
        keap1_sim = target_scores.get("KEAP1", {}).get("score", 0.0)
        if keap1_sim > 0.4 and not (warhead and warhead.get("has_warhead")):
            s -= 0.08
        # Vina ligand efficiency contribution (EXP-009).
        if vina:
            le = vina.get("vina_ligand_efficiency", 0.0)
            if le < 0:
                s += min(-le, 0.5) * 0.10  # max bonus 0.05 at LE = -0.5
        # Covalent C151 adduct thermodynamic proxy (EXP-012).
        if c151:
            s += c151.get("score_c151", 0.0) * 0.05
        # BTB Cys-151 encounter + adduct fusion (EXP-023).
        if btb:
            s += btb.get("score_btb_covalent", 0.0) * 0.05

    # Mast-cell-stabilizer-class predictor (EXP-016).
    if mast_cell is not None:
        s += min(max(mast_cell, 0.0), 1.0) * 0.05

    # ChEMBL-trained predicted potency bonus (EXP-011).
    if chembl:
        chembl_total = 0.0
        weight_total = 0.0
        for tgt, w in weights.items():
            pic50 = chembl.get(tgt)
            if pic50 is not None:
                chembl_total += pic50_potency_norm(pic50) * w
                weight_total += w
        if weight_total > 0:
            s += min((chembl_total / weight_total), 1.0) * 0.10

    # Safety bonus from QSAR (low hERG / low AMES = good)
    if qsar:
        herg = qsar.get("hERG_score", 0.5)
        ames = qsar.get("AMES_score", 0.5)
        bbb  = qsar.get("BBB_score", 0.5)
        safety = 0.5 * (1.0 - herg) + 0.5 * (1.0 - ames)
        s += safety * 0.15

        if cat in ("maintenance", "remission"):
            s += (bbb - 0.5) * 0.05
        elif cat == "rescue":
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
    from rdkit import Chem
    from rdkit.Chem import AllChem

    library = load_library()
    generated = load_generated()
    target_scores = load_target_scores()
    warhead_scores = load_warhead_scores()
    qsar_scores = load_qsar()
    vina_scores = load_vina_keap1()
    c151_scores = load_c151_adducts()
    btb_scores = load_btb_covalent()
    chembl_preds = load_chembl_predictions()
    mast_cell_preds = load_mast_cell_predictions()
    enamine = load_enamine()

    # Fingerprints for novelty (library + SFN-class seeds)
    lib_fps = []
    for rec in library:
        m = Chem.MolFromSmiles(rec.get("smiles") or "")
        if m is not None:
            lib_fps.append(AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048))
    seed_fps = []
    for smi in SFN_CLASS_SEEDS:
        m = Chem.MolFromSmiles(smi)
        if m is not None:
            seed_fps.append(AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048))

    print(
        f"library: {len(library)}, generated: {len(generated)}, "
        f"target-scored: {len(target_scores)}, warhead: {len(warhead_scores)}, "
        f"qsar: {len(qsar_scores)}, vina_keap1: {len(vina_scores)}, "
        f"c151_adduct: {len(c151_scores)}, btb_covalent: {len(btb_scores)}, "
        f"chembl: {len(chembl_preds)}, mast_cell: {len(mast_cell_preds)}, "
        f"enamine: {len(enamine)}"
    )

    by_category: dict[str, list[dict]] = {"rescue": [], "maintenance": [], "remission": []}

    for rec in library + generated:
        smi = rec.get("smiles", "")
        ts = target_scores.get(smi, {})
        wh = warhead_scores.get(smi, {})
        qs = qsar_scores.get(smi, {})
        vn = vina_scores.get(smi, {})
        for tgt in CATEGORY_TARGETS["rescue"] | CATEGORY_TARGETS["maintenance"] | CATEGORY_TARGETS["remission"]:
            rec[f"score_{tgt}"] = ts.get(tgt, {}).get("score", 0.0)
            rec[f"ref_{tgt}"] = ts.get(tgt, {}).get("best_ref", "")
        rec["has_warhead"] = wh.get("has_warhead", False)
        rec["warheads"] = wh.get("warheads", "")
        rec["keap1_pharm_pass"] = wh.get("keap1_pharmacophore_pass", False)
        rec["hERG_score"] = qs.get("hERG_score", "")
        rec["AMES_score"] = qs.get("AMES_score", "")
        rec["BBB_score"] = qs.get("BBB_score", "")
        rec["vina_kcal_per_mol"] = vn.get("vina_kcal_per_mol", "")
        rec["vina_ligand_efficiency"] = vn.get("vina_ligand_efficiency", "")
        c151 = c151_scores.get(smi, {})
        rec["c151_dE_kcal_per_mol"] = c151.get("dE_kcal_per_mol", "")
        rec["c151_score"] = c151.get("score_c151", "")
        btb = btb_scores.get(smi, {})
        rec["vina_dG_btb"] = btb.get("vina_dG_btb", "")
        rec["score_btb_covalent"] = btb.get("score_btb_covalent", "")
        cb = chembl_preds.get(smi, {})
        for tgt_name, val in cb.items():
            rec[f"chembl_pIC50_{tgt_name}"] = round(val, 3)
        mc = mast_cell_preds.get(smi)
        rec["mast_cell_stabilizer_prob"] = round(mc, 3) if mc is not None else ""

        # Novelty + Enamine (EXP-025 / EXP-017)
        nov = novelty_features(smi, lib_fps, seed_fps)
        rec.update(nov)
        en = enamine.get(smi, {})
        rec["real_space_plausible"] = en.get("real_space_plausible", "")
        rec["enamine_real_search"] = en.get("enamine_real_search", "")

        rec["composite_score"] = composite(rec, ts, wh, qs, vn, c151, cb, mc, btb)

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
