"""Prepare KEAP1 Kelch-domain receptor for Vina docking.

Workflow:
  1. Read outputs/keap1_docking/4l7b.pdb (downloaded from RCSB).
  2. Compute the centroid of the bound ligand 1VV — gives the Kelch
     pocket center (where Nrf2-PPI inhibitors / SFN-class binders are
     expected to land).
  3. Extract just the protein (chain A, drop waters / co-solvents / ions /
     bound ligand) → outputs/keap1_docking/4l7b_clean.pdb.
  4. Convert clean PDB → PDBQT via meeko's prep_receptor utilities.
  5. Persist the docking box (center + size) for the docking script.

No external binaries required — pure RDKit + meeko + stdlib.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCK_DIR = REPO_ROOT / "outputs" / "keap1_docking"
PDB_RAW = DOCK_DIR / "4l7b.pdb"
PDB_CLEAN = DOCK_DIR / "4l7b_clean.pdb"
RECEPTOR_PDBQT = DOCK_DIR / "4l7b_receptor.pdbqt"
LIGAND_REF_PDB = DOCK_DIR / "4l7b_1vv.pdb"
BOX_JSON = DOCK_DIR / "docking_box.json"


def parse_atom(line):
    """Parse a single ATOM/HETATM line."""
    return {
        "record": line[0:6].strip(),
        "atom_no": int(line[6:11]),
        "atom_name": line[12:16].strip(),
        "alt_loc": line[16],
        "res_name": line[17:20].strip(),
        "chain": line[21],
        "res_no": int(line[22:26]),
        "x": float(line[30:38]),
        "y": float(line[38:46]),
        "z": float(line[46:54]),
        "element": line[76:78].strip(),
        "raw": line,
    }


def main() -> int:
    assert PDB_RAW.exists(), f"missing {PDB_RAW}; download it first."

    protein_lines = []
    ligand_lines = []
    ligand_xyz = []

    with PDB_RAW.open() as fh:
        for line in fh:
            if not line.startswith(("ATOM", "HETATM", "TER", "END")):
                continue
            if line.startswith(("ATOM", "HETATM")):
                rec = parse_atom(line)
                # Drop waters, co-solvents (ACT = acetate), counter-ions
                if rec["res_name"] in ("HOH", "ACT", "NA", "CL"):
                    continue
                # Keep chain B protein (the monomer with the bound 1VV ligand)
                if line.startswith("ATOM") and rec["chain"] == "B":
                    protein_lines.append(line)
                # Capture the bound 1VV ligand for pocket centering
                if rec["res_name"] == "1VV":
                    ligand_lines.append(line)
                    ligand_xyz.append((rec["x"], rec["y"], rec["z"]))
            elif line.startswith("TER"):
                protein_lines.append(line)

    if not ligand_xyz:
        print("[FAIL] no 1VV ligand atoms found.", file=sys.stderr)
        return 1

    # Box center = ligand centroid; box size = 22 Å on each side
    cx = sum(x for x, _, _ in ligand_xyz) / len(ligand_xyz)
    cy = sum(y for _, y, _ in ligand_xyz) / len(ligand_xyz)
    cz = sum(z for _, _, z in ligand_xyz) / len(ligand_xyz)
    box = {"center": [round(cx, 3), round(cy, 3), round(cz, 3)], "size": [22.0, 22.0, 22.0]}
    print(f"docking box center: ({cx:.2f}, {cy:.2f}, {cz:.2f}) Å")
    print(f"box size: 22 x 22 x 22 Å")

    PDB_CLEAN.write_text("".join(protein_lines))
    LIGAND_REF_PDB.write_text("".join(ligand_lines))
    BOX_JSON.write_text(json.dumps(box, indent=2))
    print(f"wrote {PDB_CLEAN.relative_to(REPO_ROOT)} ({len(protein_lines)} lines)")
    print(f"wrote {LIGAND_REF_PDB.relative_to(REPO_ROOT)} (bound 1VV reference)")
    print(f"wrote {BOX_JSON.relative_to(REPO_ROOT)}")

    # Convert receptor PDB -> PDBQT via meeko.
    # meeko 0.7.x exposes PDBQTReceptor; older versions use prep_receptor4.py.
    try:
        from meeko import PDBQTWriterLegacy
    except ImportError:
        PDBQTWriterLegacy = None
    try:
        from meeko import MoleculePreparation
    except ImportError:
        MoleculePreparation = None

    # The most reliable Mac-friendly approach: use meeko's prep_receptor CLI
    # which is bundled with meeko ≥0.5.
    import subprocess
    venv_bin = REPO_ROOT / ".venv" / "bin"
    for tool in ("mk_prepare_receptor.py", "mk_prepare_receptor"):
        if (venv_bin / tool).exists():
            cmd = [
                str(venv_bin / tool),
                "--read_pdb", str(PDB_CLEAN),
                "-o", str(RECEPTOR_PDBQT.with_suffix("")),
                "-p",
                # box from JSON
                "--box_center", str(box["center"][0]), str(box["center"][1]), str(box["center"][2]),
                "--box_size", str(box["size"][0]), str(box["size"][1]), str(box["size"][2]),
            ]
            print("running:", " ".join(cmd))
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                print(result.stderr, file=sys.stderr)
                return 2
            break
    else:
        print("[WARN] meeko CLI mk_prepare_receptor not found; will try direct PDBQT writer.", file=sys.stderr)

    if RECEPTOR_PDBQT.exists() or (RECEPTOR_PDBQT.with_suffix(".pdbqt")).exists():
        print(f"OK: receptor PDBQT prepared at {RECEPTOR_PDBQT.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
