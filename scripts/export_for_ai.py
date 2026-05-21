"""Export the master compound library for downstream AI tooling.

Outputs:
- outputs/library.smi   one canonical SMILES per line + name (REINVENT 4 input)
- outputs/library.sdf   3D-embedded SDF (DiffDock / docking)
- outputs/seeds_for_reinvent.smi   3 high-priority seeds (quercetin, luteolin, sulforaphane)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
OUT_DIR = REPO_ROOT / "outputs"

SEED_NAMES = {"Quercetin", "Luteolin", "Sulforaphane"}


def main() -> int:
    if not CSV_PATH.exists():
        print(f"[FAIL] missing {CSV_PATH}. Run build_compound_library.py first.", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    smi_path = OUT_DIR / "library.smi"
    sdf_path = OUT_DIR / "library.sdf"
    seeds_path = OUT_DIR / "seeds_for_reinvent.smi"

    smi_lines: list[str] = []
    seed_lines: list[str] = []
    sdf_blocks: list[str] = []

    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError:
        print("[WARN] rdkit not installed, .sdf will be skipped.")
        Chem = None  # type: ignore
        AllChem = None  # type: ignore

    with CSV_PATH.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = row["name"]
            smiles = row["canonical_smiles"] or row["smiles"]
            if not smiles:
                continue
            smi_lines.append(f"{smiles}\t{name}")
            if name in SEED_NAMES:
                seed_lines.append(f"{smiles}\t{name}")

            if Chem is not None:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    continue
                mol.SetProp("_Name", name)
                mol_3d = Chem.AddHs(mol)
                try:
                    AllChem.EmbedMolecule(mol_3d, AllChem.ETKDGv3())
                    AllChem.MMFFOptimizeMolecule(mol_3d, maxIters=200)
                except Exception:
                    pass
                sdf_blocks.append(Chem.MolToMolBlock(mol_3d) + "$$$$\n")

    smi_path.write_text("\n".join(smi_lines) + "\n")
    seeds_path.write_text("\n".join(seed_lines) + "\n")
    if sdf_blocks:
        sdf_path.write_text("".join(sdf_blocks))

    print(f"Wrote {len(smi_lines)} SMILES -> {smi_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {len(seed_lines)} seeds -> {seeds_path.relative_to(REPO_ROOT)}")
    if sdf_blocks:
        print(f"Wrote {len(sdf_blocks)} 3D molecules -> {sdf_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
