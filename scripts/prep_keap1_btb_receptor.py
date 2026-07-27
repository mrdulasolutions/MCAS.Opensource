"""Prepare KEAP1 BTB-domain receptor (Cys-151 pocket) for Vina.

Uses PDB 5DAD (human KEAP1 BTB + small-molecule complex) as the primary
structure, with 4CXI as a fallback. Centers the docking box on Cys-151 SG
— the covalent attachment site for sulforaphane-class isothiocyanates.

This is the structure-based counterpart to EXP-012's small-molecule adduct
energy proxy: non-covalent Vina poses in the BTB pocket approximate the
pre-reactive encounter complex.

Outputs under outputs/keap1_btb/:
  - 5dad_clean.pdb / 5dad_receptor.pdbqt
  - docking_box_c151.json
  - c151_sg.json  (SG coordinates for documentation)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BTB_DIR = REPO_ROOT / "outputs" / "keap1_btb"
PDB_CANDIDATES = [BTB_DIR / "5DAD.pdb", BTB_DIR / "4CXI.pdb"]


def parse_atom(line: str) -> dict:
    return {
        "record": line[0:6].strip(),
        "atom_name": line[12:16].strip(),
        "res_name": line[17:20].strip(),
        "chain": line[21],
        "res_no": int(line[22:26]),
        "x": float(line[30:38]),
        "y": float(line[38:46]),
        "z": float(line[46:54]),
        "raw": line,
    }


def find_c151_sg(path: Path) -> tuple[dict, str] | tuple[None, None]:
    for line in path.read_text().splitlines():
        if not line.startswith("ATOM"):
            continue
        rec = parse_atom(line)
        if rec["res_name"] == "CYS" and rec["res_no"] == 151 and rec["atom_name"] in ("SG", "S"):
            return rec, rec["chain"]
    return None, None


def main() -> int:
    BTB_DIR.mkdir(parents=True, exist_ok=True)
    pdb_path = next((p for p in PDB_CANDIDATES if p.exists()), None)
    if pdb_path is None:
        print("[FAIL] missing 5DAD.pdb / 4CXI.pdb — download first.", file=sys.stderr)
        return 1

    sg, chain = find_c151_sg(pdb_path)
    if sg is None:
        print(f"[FAIL] Cys151 SG not found in {pdb_path.name}", file=sys.stderr)
        return 1

    print(f"using {pdb_path.name} chain {chain} Cys151 SG "
          f"@ ({sg['x']:.2f}, {sg['y']:.2f}, {sg['z']:.2f})")

    protein_lines = []
    with pdb_path.open() as fh:
        for line in fh:
            if line.startswith("ATOM"):
                rec = parse_atom(line)
                if rec["chain"] != chain:
                    continue
                if rec["res_name"] in ("HOH", "WAT", "NA", "CL", "SO4", "GOL", "EDO"):
                    continue
                protein_lines.append(line)
            elif line.startswith("TER"):
                protein_lines.append(line)

    stem = pdb_path.stem.lower()
    clean = BTB_DIR / f"{stem}_clean.pdb"
    clean.write_text("".join(protein_lines) + "END\n")
    box = {
        "center": [round(sg["x"], 3), round(sg["y"], 3), round(sg["z"], 3)],
        "size": [18.0, 18.0, 18.0],
        "pdb": pdb_path.name,
        "chain": chain,
        "residue": "CYS151",
        "note": "Box centered on Cys-151 SG (covalent warhead attack site).",
    }
    box_path = BTB_DIR / "docking_box_c151.json"
    box_path.write_text(json.dumps(box, indent=2))
    (BTB_DIR / "c151_sg.json").write_text(json.dumps({
        "pdb": pdb_path.name,
        "chain": chain,
        "res_no": 151,
        "atom": sg["atom_name"],
        "xyz": [sg["x"], sg["y"], sg["z"]],
    }, indent=2))
    print(f"wrote {clean.relative_to(REPO_ROOT)} ({len(protein_lines)} atoms)")
    print(f"wrote {box_path.relative_to(REPO_ROOT)}")

    receptor_out = BTB_DIR / f"{stem}_receptor.pdbqt"
    try:
        from meeko import PDBQTReceptor  # type: ignore
        rec = PDBQTReceptor(str(clean))
        if hasattr(rec, "write_pdbqt_string"):
            receptor_out.write_text(rec.write_pdbqt_string())
        elif hasattr(rec, "write_pdbqt_file"):
            rec.write_pdbqt_file(str(receptor_out))
        else:
            raise AttributeError("no write method on PDBQTReceptor")
        print(f"wrote {receptor_out.relative_to(REPO_ROOT)} via PDBQTReceptor")
        return 0
    except Exception as e1:
        print(f"[warn] meeko receptor prep failed ({e1}); using minimal PDBQT fallback")

    # Fallback: openbabel-free minimal PDBQT for protein (atom types crude).
    # AutoDock Vina rigid-receptor lines: partial charge in a 6-char field,
    # then atom type. No ROOT/BRANCH/TORSDOF tags on receptors.
    fixed = []
    serial = 0
    for line in protein_lines:
        if not line.startswith("ATOM"):
            continue
        rec = parse_atom(line)
        element = (line[76:78].strip() or rec["atom_name"][0]).upper()
        if element.startswith("H"):
            continue
        serial += 1
        name = rec["atom_name"][:4]
        # PDB atom name field is 4 chars, right/left justified by convention
        name_field = f"{name:>4s}" if len(name) < 4 else name[:4]
        x, y, z = rec["x"], rec["y"], rec["z"]
        atype = {"C": "C", "N": "N", "O": "OA", "S": "SA", "P": "P"}.get(element[:1], "C")
        # Match classic ADT layout (charge then type).
        fixed.append(
            f"ATOM  {serial:5d} {name_field} {rec['res_name']:3s} {rec['chain']}"
            f"{rec['res_no']:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00     "
            f"{0.0:5.3f} {atype}\n"
        )
    receptor_out.write_text("".join(fixed))
    print(f"wrote {receptor_out.relative_to(REPO_ROOT)} via minimal PDBQT fallback "
          f"({len(fixed)} heavy atoms)")
    print("NOTE: fallback PDBQT atom typing is approximate; prefer meeko+gemmi when available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
