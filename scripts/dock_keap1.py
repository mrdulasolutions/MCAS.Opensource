"""Dock the top-N remission candidates into the KEAP1 Kelch pocket with Vina.

Workflow per ligand:
  1. Pull SMILES from outputs/ranked_remission.csv (sorted by composite_score).
  2. Embed a 3D conformer via RDKit ETKDGv3 + MMFF94 minimization.
  3. Convert the ligand to PDBQT via meeko's MoleculePreparation.
  4. Run AutoDock Vina (binary at .tools/vina) against the prepared
     receptor (outputs/keap1_docking/4l7b_receptor.pdbqt) inside the box
     defined by outputs/keap1_docking/docking_box.json.
  5. Parse Vina's "Estimated Free Energy of Binding" (kcal/mol) from the
     output PDBQT — that's the score we care about (more negative = better).
  6. Write outputs/docking_KEAP1_vina.csv.

This is the physics-based supplement to the ligand-similarity score in
outputs/docking_KEAP1.csv. EXP-009 integrates the two.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCK_DIR = REPO_ROOT / "outputs" / "keap1_docking"
RECEPTOR = DOCK_DIR / "4l7b_receptor.pdbqt"
BOX_JSON = DOCK_DIR / "docking_box.json"
VINA = REPO_ROOT / ".tools" / "vina"
RANKED_REMISSION = REPO_ROOT / "outputs" / "ranked_remission.csv"
OUT_CSV = REPO_ROOT / "outputs" / "docking_KEAP1_vina.csv"

# Vina output scoring regex
SCORE_RE = re.compile(r"REMARK VINA RESULT:\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)")


def embed_ligand(smiles: str, name: str, out_pdbqt: Path) -> bool:
    """Embed a 3D conformer + write PDBQT via meeko. Returns True on success."""
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
        params.randomSeed = 0xC0FFEE
        if AllChem.EmbedMolecule(mol, params) != 0:
            # fallback: use random coords
            if AllChem.EmbedMolecule(mol, AllChem.srETKDGv3()) != 0:
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


def run_vina(ligand_pdbqt: Path, box: dict, exhaustiveness: int = 8, n_poses: int = 5) -> dict:
    """Run Vina and parse the best-pose score. Returns dict with best_score (kcal/mol)
    and per-pose scores."""
    with tempfile.NamedTemporaryFile(suffix=".pdbqt", delete=False) as tmp:
        out_pdbqt = Path(tmp.name)
    try:
        cmd = [
            str(VINA),
            "--receptor", str(RECEPTOR),
            "--ligand", str(ligand_pdbqt),
            "--center_x", str(box["center"][0]),
            "--center_y", str(box["center"][1]),
            "--center_z", str(box["center"][2]),
            "--size_x", str(box["size"][0]),
            "--size_y", str(box["size"][1]),
            "--size_z", str(box["size"][2]),
            "--out", str(out_pdbqt),
            "--exhaustiveness", str(exhaustiveness),
            "--num_modes", str(n_poses),
            "--seed", "42",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            return {"error": f"vina returned {result.returncode}: {result.stderr[-200:]}"}
        poses = []
        if out_pdbqt.exists():
            for m in SCORE_RE.finditer(out_pdbqt.read_text()):
                poses.append({
                    "kcal_per_mol": float(m.group(1)),
                    "rmsd_lb": float(m.group(2)),
                    "rmsd_ub": float(m.group(3)),
                })
        if not poses:
            return {"error": "no poses parsed"}
        return {"best_score": poses[0]["kcal_per_mol"], "n_poses": len(poses), "poses": poses}
    finally:
        out_pdbqt.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dock top-N remission candidates into KEAP1 Kelch pocket.")
    parser.add_argument("--top-n", type=int, default=50, help="How many remission candidates to dock (default 50).")
    parser.add_argument("--exhaustiveness", type=int, default=8, help="Vina exhaustiveness (default 8).")
    parser.add_argument("--n-poses", type=int, default=5, help="Number of poses per ligand.")
    args = parser.parse_args()

    if not VINA.exists():
        print(f"ERROR: Vina binary not found at {VINA}", file=sys.stderr)
        return 1
    if not RECEPTOR.exists():
        print(f"ERROR: receptor PDBQT not found; run prep_keap1_receptor.py first.", file=sys.stderr)
        return 1
    box = json.loads(BOX_JSON.read_text())

    # Load top-N remission candidates by composite_score
    with RANKED_REMISSION.open() as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: -float(r["composite_score"]))
    top = rows[: args.top_n]
    print(f"docking top {len(top)} remission candidates")
    print(f"receptor: {RECEPTOR.relative_to(REPO_ROOT)}")
    print(f"box center: {box['center']}, size: {box['size']}")
    print(f"Vina: exhaustiveness={args.exhaustiveness}, num_modes={args.n_poses}")
    print()

    results = []
    t0 = time.time()
    for i, r in enumerate(top, start=1):
        name = r["name"]
        smi = r.get("smiles") or r.get("canonical_smiles") or ""
        if not smi:
            results.append({**_keep(r), "vina_kcal_per_mol": None, "vina_status": "no_smiles"})
            print(f"[{i:3d}/{len(top)}] {name:<35}  SKIP (no SMILES)")
            continue

        with tempfile.NamedTemporaryFile(suffix=".pdbqt", delete=False) as tmp:
            lig_path = Path(tmp.name)
        try:
            ok = embed_ligand(smi, name, lig_path)
            if not ok:
                results.append({**_keep(r), "vina_kcal_per_mol": None, "vina_status": "embed_fail"})
                print(f"[{i:3d}/{len(top)}] {name:<35}  SKIP (embed fail)")
                continue
            t_l = time.time()
            res = run_vina(lig_path, box, exhaustiveness=args.exhaustiveness, n_poses=args.n_poses)
            dt = time.time() - t_l
            if "error" in res:
                results.append({**_keep(r), "vina_kcal_per_mol": None, "vina_status": res["error"][:60]})
                print(f"[{i:3d}/{len(top)}] {name:<35}  FAIL {res['error'][:50]}")
                continue
            results.append({
                **_keep(r),
                "vina_kcal_per_mol": res["best_score"],
                "vina_n_poses": res["n_poses"],
                "vina_status": "ok",
                "vina_time_s": round(dt, 1),
            })
            print(f"[{i:3d}/{len(top)}] {name:<35}  {res['best_score']:>7.2f} kcal/mol  ({dt:.1f}s)")
        finally:
            lig_path.unlink(missing_ok=True)

    total_t = time.time() - t0

    # Sort by Vina score (most negative = best binder)
    scored = [r for r in results if r.get("vina_kcal_per_mol") is not None]
    scored.sort(key=lambda r: r["vina_kcal_per_mol"])

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["name", "smiles", "category", "source", "composite_score", "score_KEAP1",
              "has_warhead", "warheads",
              "vina_kcal_per_mol", "vina_n_poses", "vina_status", "vina_time_s"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(scored + [r for r in results if r.get("vina_kcal_per_mol") is None])

    print()
    print(f"wrote {OUT_CSV.relative_to(REPO_ROOT)}  ({len(scored)} successful, {len(results) - len(scored)} failed/skipped)")
    print(f"total time: {total_t/60:.1f} min ({total_t/len(top):.1f}s per ligand)")
    print()
    print("Top 10 by Vina score (most negative = strongest predicted binder):")
    print(f"  {'rank':>4} {'kcal/mol':>10}  {'composite':>10}  {'KEAP1_sim':>10}  {'warhead':>8}  name")
    for rank, r in enumerate(scored[:10], start=1):
        wh = "yes" if r.get("has_warhead") in ("True", True) else "—"
        print(f"  {rank:>4} {r['vina_kcal_per_mol']:>10.2f}  {float(r['composite_score']):>10.3f}  {float(r['score_KEAP1']):>10.2f}  {wh:>8}  {r['name']}")
    return 0


def _keep(row):
    return {
        "name": row["name"],
        "smiles": row.get("smiles") or row.get("canonical_smiles") or "",
        "category": row.get("category", "remission"),
        "source": row.get("source", ""),
        "composite_score": row.get("composite_score", ""),
        "score_KEAP1": row.get("score_KEAP1", ""),
        "has_warhead": row.get("has_warhead", ""),
        "warheads": row.get("warheads", ""),
    }


if __name__ == "__main__":
    sys.exit(main())
