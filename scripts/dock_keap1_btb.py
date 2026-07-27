"""Dock warhead-bearing / top remission candidates into KEAP1 BTB (Cys-151).

Complements Kelch-domain non-covalent docking (EXP-009) and the C151 adduct
thermodynamic proxy (EXP-012). AutoDock Vina cannot form covalent bonds; we
dock the pre-reactive ligand into a box centered on Cys-151 SG to score the
encounter complex, then fuse with adduct ΔE into a BTB-covalent composite.

Output: outputs/docking_KEAP1_btb_c151.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BTB_DIR = REPO_ROOT / "outputs" / "keap1_btb"
VINA = REPO_ROOT / ".tools" / "vina"
BOX_JSON = BTB_DIR / "docking_box_c151.json"
C151_CSV = REPO_ROOT / "outputs" / "c151_adduct_energies.csv"
WARHEAD_CSV = REPO_ROOT / "outputs" / "warhead_scores.csv"
RANKED_REMISSION = REPO_ROOT / "outputs" / "ranked_remission.csv"
LIB_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
OUT_CSV = REPO_ROOT / "outputs" / "docking_KEAP1_btb_c151.csv"

SCORE_RE = re.compile(r"REMARK VINA RESULT:\s+(-?\d+\.\d+)")


def find_receptor() -> Path | None:
    for p in sorted(BTB_DIR.glob("*_receptor.pdbqt")):
        return p
    return None


def embed_ligand(smiles: str, out_pdbqt: Path) -> bool:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import AllChem
    from meeko import MoleculePreparation, PDBQTWriterLegacy

    RDLogger.DisableLog("rdApp.*")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    mol = Chem.AddHs(mol)
    try:
        params = AllChem.ETKDGv3()
        params.randomSeed = 0xC151
        if AllChem.EmbedMolecule(mol, params) != 0:
            if AllChem.EmbedMolecule(mol, useRandomCoords=True) != 0:
                return False
        AllChem.MMFFOptimizeMolecule(mol, maxIters=400)
    except Exception:
        return False
    prep = MoleculePreparation()
    try:
        setups = prep.prepare(mol)
    except Exception:
        return False
    if not setups:
        return False
    pdbqt_str, is_ok, err = PDBQTWriterLegacy.write_string(setups[0])
    if not is_ok:
        return False
    out_pdbqt.write_text(pdbqt_str)
    return True


def run_vina(receptor: Path, ligand_pdbqt: Path, box: dict, exhaustiveness: int = 8) -> float | None:
    with tempfile.NamedTemporaryFile(suffix=".pdbqt", delete=False) as tmp:
        out_pdbqt = Path(tmp.name)
    try:
        cmd = [
            str(VINA),
            "--receptor", str(receptor),
            "--ligand", str(ligand_pdbqt),
            "--center_x", str(box["center"][0]),
            "--center_y", str(box["center"][1]),
            "--center_z", str(box["center"][2]),
            "--size_x", str(box["size"][0]),
            "--size_y", str(box["size"][1]),
            "--size_z", str(box["size"][2]),
            "--out", str(out_pdbqt),
            "--exhaustiveness", str(exhaustiveness),
            "--num_modes", "5",
            "--seed", "151",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        text = (result.stdout or "") + "\n" + out_pdbqt.read_text() if out_pdbqt.exists() else (result.stdout or "")
        scores = [float(m.group(1)) for m in SCORE_RE.finditer(text)]
        if not scores and result.stderr:
            # try parsing stdout only
            scores = [float(m.group(1)) for m in SCORE_RE.finditer(result.stdout or "")]
        return min(scores) if scores else None
    except Exception:
        return None
    finally:
        if out_pdbqt.exists():
            out_pdbqt.unlink(missing_ok=True)


def load_candidates(top_n: int) -> list[dict]:
    """Top remission candidates + SFN-class library anchors (capped at top_n*2)."""
    by_smi: dict[str, dict] = {}
    # always include SFN-class library anchors by name
    if LIB_CSV.exists():
        with LIB_CSV.open() as fh:
            for row in csv.DictReader(fh):
                smi = row.get("canonical_smiles") or row.get("smiles") or ""
                if not smi:
                    continue
                if any(k in (row.get("name") or "").lower() for k in (
                    "sulforaphane", "erucin", "iberin", "isothiocyanate",
                    "carnosic", "dimethyl fumarate", "phenethyl", "benzyl",
                    "allyl", "glucoraphanin", "sulforaphene",
                )):
                    by_smi[smi] = {"name": row["name"], "smiles": smi, "source": "library_anchor"}
    if RANKED_REMISSION.exists():
        with RANKED_REMISSION.open() as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                if i >= top_n:
                    break
                smi = row.get("smiles") or ""
                if smi:
                    by_smi.setdefault(smi, {
                        "name": row["name"],
                        "smiles": smi,
                        "source": row.get("source", "ranked_remission"),
                    })
    # Cap total for wall-clock on CPU
    out = list(by_smi.values())
    return out[: max(top_n, len([x for x in out if x["source"] == "library_anchor"]))]


def load_c151() -> dict[str, float]:
    out = {}
    if not C151_CSV.exists():
        return out
    with C151_CSV.open() as fh:
        for row in csv.DictReader(fh):
            if row.get("status") == "ok" and row.get("smiles"):
                try:
                    out[row["smiles"]] = float(row["score_c151"])
                except (TypeError, ValueError):
                    pass
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-n", type=int, default=40)
    parser.add_argument("--exhaustiveness", type=int, default=8)
    args = parser.parse_args()

    if not VINA.exists():
        print(f"[FAIL] Vina binary missing at {VINA}", file=sys.stderr)
        return 1
    receptor = find_receptor()
    if receptor is None or not BOX_JSON.exists():
        print("[FAIL] run prep_keap1_btb_receptor.py first", file=sys.stderr)
        return 1
    box = json.loads(BOX_JSON.read_text())
    c151 = load_c151()
    cands = load_candidates(args.top_n)
    print(f"docking {len(cands)} candidates into BTB Cys151 pocket "
          f"(receptor={receptor.name})")

    rows = []
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        for i, c in enumerate(cands, 1):
            lig = td_path / f"lig_{i}.pdbqt"
            ok = embed_ligand(c["smiles"], lig)
            if not ok:
                rows.append({**c, "status": "embed_fail", "vina_dG": "", "score_btb_vina": "",
                             "score_c151": c151.get(c["smiles"], ""), "score_btb_covalent": ""})
                print(f"  [{i}/{len(cands)}] {c['name']}: embed_fail")
                continue
            dg = run_vina(receptor, lig, box, args.exhaustiveness)
            if dg is None:
                rows.append({**c, "status": "vina_fail", "vina_dG": "", "score_btb_vina": "",
                             "score_c151": c151.get(c["smiles"], ""), "score_btb_covalent": ""})
                print(f"  [{i}/{len(cands)}] {c['name']}: vina_fail")
                continue
            # Normalize Vina: more negative better. Map [-12, -2] → [1, 0]
            score_vina = max(0.0, min(1.0, (-dg - 2.0) / 10.0))
            sc151 = float(c151.get(c["smiles"], 0.0) or 0.0)
            # Fuse encounter complex + covalent adduct thermodynamics
            score_btb = round(0.55 * score_vina + 0.45 * sc151, 4)
            rows.append({
                **c,
                "status": "ok",
                "vina_dG": round(dg, 3),
                "score_btb_vina": round(score_vina, 4),
                "score_c151": sc151,
                "score_btb_covalent": score_btb,
            })
            print(f"  [{i}/{len(cands)}] {c['name']}: ΔG={dg:.2f}  "
                  f"btb_cov={score_btb:.3f}")

    # write
    if not rows:
        print("[FAIL] no rows", file=sys.stderr)
        return 1
    fields = ["name", "smiles", "source", "status", "vina_dG", "score_btb_vina",
              "score_c151", "score_btb_covalent"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: float(r["score_btb_covalent"] or 0), reverse=True))
    print(f"wrote {OUT_CSV.relative_to(REPO_ROOT)} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
