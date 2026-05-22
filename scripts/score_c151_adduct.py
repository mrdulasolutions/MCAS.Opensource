"""KEAP1-C151 dithiocarbamate adduct energy proxy (EXP-012).

SFN's actual mechanism is covalent: its terminal isothiocyanate carbon
attacks KEAP1's Cys-151 thiol → forms a dithiocarbamate adduct:

    R-N=C=S  +  HS-Cys151  →  R-NH-C(=S)-S-Cys151

Vanilla Vina cannot model this (it's a covalent bond change, not a
non-covalent pose). Without commercial covalent-docking software, we
build an honest CPU-friendly proxy:

  1. For each ITC-class candidate, construct the methanethiol-adduct
     (R-NH-C(=S)-S-CH3) as a small-molecule model for the Cys-151 attack.
     CH3SH is the chemist's standard one-amino-acid cysteine mimic.
  2. Embed parent ITC, free methanethiol, and the adduct via RDKit ETKDGv3
     + MMFF94 minimize.
  3. Reaction energy proxy:
         ΔE_proxy  =  E(adduct)  −  [E(ITC) + E(CH3SH)]
     More-negative = more thermodynamically favorable adduct formation.

What this captures:
  - The chemistry SFN/Erucin actually does at C151.
  - Steric / electronic differences between ITCs (chain length, sulfoxide
    vs sulfide, aromatic vs aliphatic) that affect adduct stability.

What it does NOT capture:
  - Protein context: the actual Cys-151 sits in the BTB domain pocket
    with specific neighbors; we model only the thiol.
  - Reaction kinetics: ΔE_proxy is thermodynamic, not kinetic.
  - Reversibility: dithiocarbamate adducts ARE reversible, but the proxy
    treats them as point states.

Output: outputs/c151_adduct_energies.csv with columns:
    name, smiles, parent_E, adduct_E, methanethiol_E, dE_kcal_per_mol,
    score_c151
where `score_c151` is a [0, 1] normalized score for use in the composite
ranking — most-negative ΔE in the population maps to 1.0.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
GEN_CSV = REPO_ROOT / "outputs" / "reinvent_generated.csv"
OUT_CSV = REPO_ROOT / "outputs" / "c151_adduct_energies.csv"


def is_itc(smiles: str) -> bool:
    """True if the molecule contains an isothiocyanate group.

    Uses RDKit SMARTS so direction-agnostic — catches both `N=C=S` and
    `S=C=N` canonical writings.
    """
    from rdkit import Chem
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    patt = Chem.MolFromSmarts("[NX2]=[CX2]=[SX1]")
    return mol.HasSubstructMatch(patt)


def make_adduct(smiles: str) -> str | None:
    """Convert R-N=C=S → R-N(H)-C(=S)-S-C (methanethiol-adduct model).

    Direction-agnostic via RDKit substructure replacement.
    """
    from rdkit import Chem
    from rdkit.Chem import AllChem
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    patt = Chem.MolFromSmarts("[NX2]=[CX2]=[SX1]")
    if not mol.HasSubstructMatch(patt):
        return None
    # Use RDKit's replace_substructs: replace `N=C=S` with `N-C(=S)-S-C`.
    repl = Chem.MolFromSmiles("NC(=S)SC")
    new_mols = AllChem.ReplaceSubstructs(mol, patt, repl, replaceAll=True)
    if not new_mols:
        return None
    try:
        Chem.SanitizeMol(new_mols[0])
    except Exception:
        return None
    return Chem.MolToSmiles(new_mols[0], canonical=True)


def mmff_energy(mol):
    """Embed + MMFF94 minimize + return final energy (kcal/mol). None on fail."""
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 0xC0FFEE
    try:
        if AllChem.EmbedMolecule(mol, params) != 0:
            # try fallback
            if AllChem.EmbedMolecule(mol, AllChem.srETKDGv3()) != 0:
                return None
    except Exception:
        return None
    props = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant="MMFF94")
    if props is None:
        return None
    ff = AllChem.MMFFGetMoleculeForceField(mol, props)
    if ff is None:
        return None
    ff.Minimize(maxIts=400)
    return float(ff.CalcEnergy())


def load_candidates():
    """All ITC-class molecules from library + generated."""
    from rdkit import Chem
    out = []
    with LIB_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("canonical_smiles") or row.get("smiles") or ""
            if is_itc(smi):
                mol = Chem.MolFromSmiles(smi)
                if mol is not None:
                    out.append({"name": row["name"], "smiles": smi, "source": "library"})
    if GEN_CSV.exists():
        with GEN_CSV.open() as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                smi = row.get("smiles", "")
                if is_itc(smi):
                    mol = Chem.MolFromSmiles(smi)
                    if mol is not None:
                        out.append({"name": f"GEN_{i:04d}", "smiles": smi, "source": "reinvent_generated"})
    return out


def main() -> int:
    try:
        from rdkit import Chem, RDLogger
    except ImportError:
        print("ERROR: rdkit required", file=sys.stderr)
        return 1
    RDLogger.DisableLog("rdApp.*")

    candidates = load_candidates()
    print(f"scoring {len(candidates)} ITC-class candidates")

    # Reference: methanethiol energy
    ch3sh_mol = Chem.MolFromSmiles("CS")
    e_ch3sh = mmff_energy(ch3sh_mol)
    print(f"  methanethiol MMFF energy: {e_ch3sh:.3f} kcal/mol")
    print()

    rows = []
    for cand in candidates:
        smi = cand["smiles"]
        adduct_smi = make_adduct(smi)
        if not adduct_smi:
            continue

        parent_mol = Chem.MolFromSmiles(smi)
        adduct_mol = Chem.MolFromSmiles(adduct_smi)
        if parent_mol is None or adduct_mol is None:
            continue

        e_parent = mmff_energy(parent_mol)
        e_adduct = mmff_energy(adduct_mol)
        if e_parent is None or e_adduct is None:
            rows.append({
                **cand,
                "adduct_smiles": adduct_smi,
                "parent_E": "",
                "methanethiol_E": "",
                "adduct_E": "",
                "dE_kcal_per_mol": "",
                "status": "energy_calc_failed",
            })
            continue

        dE = e_adduct - (e_parent + e_ch3sh)
        rows.append({
            **cand,
            "adduct_smiles": adduct_smi,
            "parent_E": round(e_parent, 3),
            "methanethiol_E": round(e_ch3sh, 3),
            "adduct_E": round(e_adduct, 3),
            "dE_kcal_per_mol": round(dE, 3),
            "status": "ok",
        })

    # Score normalization: map ΔE to [0, 1] where most-negative ΔE → 1
    valid = [r for r in rows if r["status"] == "ok"]
    if valid:
        des = [r["dE_kcal_per_mol"] for r in valid]
        min_de = min(des)  # most negative
        max_de = max(des)  # least negative / least favorable
        rng = max_de - min_de if max_de != min_de else 1.0
        for r in valid:
            r["score_c151"] = round((max_de - r["dE_kcal_per_mol"]) / rng, 3)
    for r in rows:
        r.setdefault("score_c151", "")

    # Sort by score_c151 desc, then by ΔE asc
    rows_sorted = sorted(
        rows,
        key=lambda r: (-(r["score_c151"] if isinstance(r["score_c151"], float) else -1),
                       r["dE_kcal_per_mol"] if isinstance(r["dE_kcal_per_mol"], float) else 0),
    )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["name", "smiles", "adduct_smiles", "source", "parent_E", "methanethiol_E",
              "adduct_E", "dE_kcal_per_mol", "score_c151", "status"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows_sorted)

    print(f"wrote {OUT_CSV.relative_to(REPO_ROOT)}  ({len(rows_sorted)} candidates)")
    print()
    print(f"Top 15 by C151 adduct thermodynamic favorability (more negative ΔE = better):")
    print(f"  {'rank':>4} {'ΔE':>8}  {'score':>5}  name")
    valid_sorted = sorted(valid, key=lambda r: r["dE_kcal_per_mol"])
    for i, r in enumerate(valid_sorted[:15], 1):
        print(f"  {i:>4} {r['dE_kcal_per_mol']:>8.2f}  {r['score_c151']:>5.2f}  {r['name']}  ({r['source']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
