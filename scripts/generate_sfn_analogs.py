"""Local SFN-seeded analog generator (CPU-friendly fallback for REINVENT 4).

What this does (and doesn't):
- DOES: enumerate analogs of sulforaphane (SFN) by RDKit BRICS recombination
  with the rest of the MCAS library scaffolds, plus targeted bioisosteric
  substitutions around the isothiocyanate / sulfoxide pharmacophore.
- DOES: score every analog by Tanimoto similarity to SFN, QED, synthetic
  accessibility (SA), and Lipinski pass/fail.
- DOES NOT: run reinforcement learning. The full REINVENT 4 RL loop requires
  GPU + Colab — see notebooks/03_reinvent_generation_colab.ipynb. This script
  is the local, deterministic substitute that gets you real candidates today.

Output: outputs/reinvent_generated.csv (same schema notebooks 04 and 05 expect).
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem, BRICS, Descriptors, Lipinski

RDLogger.DisableLog("rdApp.*")

REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
OUT_PATH = REPO_ROOT / "outputs" / "reinvent_generated.csv"

SEED_SMILES = "CS(=O)CCCCN=C=S"  # Sulforaphane
SEED_NAME = "Sulforaphane"


# Targeted bioisosteric replacements on the SFN scaffold.
# Each pair: (template substring, replacement).
BIOISOSTERES = [
    # Sulfoxide -> sulfone, sulfide, sulfonamide
    ("CS(=O)", "CS(=O)(=O)"),
    ("CS(=O)", "CS"),
    # Methyl sulfoxide -> ethyl sulfoxide
    ("CS(=O)", "CCS(=O)"),
    # Chain length variants (CCCC -> CCC, CCCCC)
    ("CCCCN=C=S", "CCCN=C=S"),
    ("CCCCN=C=S", "CCCCCN=C=S"),
    # Isothiocyanate -> thiocyanate, nitrile (lose covalent reactivity)
    ("N=C=S", "C#N"),
    ("N=C=S", "SC#N"),
    # Aromatic-tethered analog
    ("CS(=O)CCCCN=C=S", "CS(=O)CCc1ccc(N=C=S)cc1"),
    ("CS(=O)CCCCN=C=S", "CS(=O)Cc1ccc(N=C=S)cc1"),
]


def lipinski_pass(mol) -> bool:
    return (
        Descriptors.MolWt(mol) <= 500
        and Descriptors.MolLogP(mol) <= 5
        and Lipinski.NumHDonors(mol) <= 5
        and Lipinski.NumHAcceptors(mol) <= 10
    )


def sa_score(mol) -> float:
    """Lightweight synthetic-accessibility proxy in [1, 10]. Lower is easier.

    Uses a simple combination of ring complexity, stereo centers, and fragment
    novelty. Not the Ertl SAS — that requires the contrib script — but a usable
    relative ranker.
    """
    try:
        n_rings = Descriptors.RingCount(mol)
        n_stereo = len(Chem.FindMolChiralCenters(mol, includeUnassigned=True))
        n_aromatic = sum(1 for atom in mol.GetAtoms() if atom.GetIsAromatic())
        n_heavy = mol.GetNumHeavyAtoms()
        # cheap heuristic — 1 (easy) .. 10 (hard)
        score = 1.0 + 0.5 * n_rings + 0.7 * n_stereo + 0.02 * n_heavy + 0.05 * n_aromatic
        return max(1.0, min(10.0, score))
    except Exception:
        return 10.0


def tanimoto(mol_a, mol_b) -> float:
    fp_a = AllChem.GetMorganFingerprintAsBitVect(mol_a, 2, nBits=1024)
    fp_b = AllChem.GetMorganFingerprintAsBitVect(mol_b, 2, nBits=1024)
    return DataStructs.TanimotoSimilarity(fp_a, fp_b)


def composite(qed: float, sim: float, sa: float, lipinski: bool) -> float:
    """Multi-objective scalar used to rank.

    Mirrors notebook 03's scoring weights: QED 0.4, similarity-to-seed 0.4,
    SA bonus 0.2. Lipinski is a hard filter (zeroed out if fail).
    """
    if not lipinski:
        return 0.0
    sa_term = max(0.0, (10.0 - sa) / 9.0)  # invert + normalize
    return 0.4 * qed + 0.4 * sim + 0.2 * sa_term


def enumerate_bioisosteres(seed_smiles: str) -> set[str]:
    seen: set[str] = set()
    for template, replacement in BIOISOSTERES:
        if template in seed_smiles:
            smi = seed_smiles.replace(template, replacement)
            mol = Chem.MolFromSmiles(smi)
            if mol is not None:
                seen.add(Chem.MolToSmiles(mol, canonical=True))
    # combinatorial: apply two substitutions
    for i, (t1, r1) in enumerate(BIOISOSTERES):
        for j, (t2, r2) in enumerate(BIOISOSTERES):
            if i == j or t1 not in seed_smiles:
                continue
            interim = seed_smiles.replace(t1, r1)
            if t2 not in interim:
                continue
            smi = interim.replace(t2, r2)
            mol = Chem.MolFromSmiles(smi)
            if mol is not None:
                seen.add(Chem.MolToSmiles(mol, canonical=True))
    return seen


SFN_WARHEAD_SMARTS = "[CH3]"  # we'll graft onto an aromatic H or terminal methyl
SFN_WARHEAD_TAIL = "CS(=O)CCCCN=C=S"  # full SFN warhead as a SMILES tail


def enumerate_warhead_grafts(library_smiles: list[str], max_per_template: int = 2) -> set[str]:
    """Graft the SFN sulfoxide-isothiocyanate warhead onto library scaffolds.

    Strategy: for each library molecule, find aromatic CH or aliphatic CH3
    positions; replace one H with -CCCS(=O)C and a CCCCN=C=S tail tied to it.
    This is a crude bioisostere of the 'flavonoid-SFN hybrid' hypothesis in
    hypotheses/remission.md.
    """
    seen: set[str] = set()
    aromatic_h = Chem.MolFromSmarts("[cH]")
    tail = Chem.MolFromSmiles("CCS(=O)CCCN=C=S")
    if tail is None:
        return seen

    for smi in library_smiles:
        mol = Chem.MolFromSmiles(smi)
        if mol is None or mol.GetNumHeavyAtoms() > 35:
            continue
        matches = mol.GetSubstructMatches(aromatic_h)
        if not matches:
            continue
        for match in matches[:max_per_template]:
            # combine: link the matched aromatic carbon to the tail's first atom
            edit = Chem.RWMol(Chem.CombineMols(mol, tail))
            offset = mol.GetNumAtoms()
            edit.AddBond(match[0], offset, Chem.BondType.SINGLE)
            try:
                Chem.SanitizeMol(edit)
                seen.add(Chem.MolToSmiles(edit, canonical=True))
            except Exception:
                continue
    return seen


def enumerate_brics(seed_smiles: str, library_smiles: list[str], max_per_pair: int = 3) -> set[str]:
    """Fragment SFN + each library molecule with BRICS, recombine the fragments."""
    seed = Chem.MolFromSmiles(seed_smiles)
    if seed is None:
        return set()
    seed_frags = list(BRICS.BRICSDecompose(seed))
    seen: set[str] = set()
    for other_smi in library_smiles:
        other = Chem.MolFromSmiles(other_smi)
        if other is None:
            continue
        other_frags = list(BRICS.BRICSDecompose(other))
        all_frags = [Chem.MolFromSmiles(f) for f in (seed_frags + other_frags)]
        all_frags = [m for m in all_frags if m is not None]
        if not all_frags:
            continue
        try:
            builder = BRICS.BRICSBuild(all_frags, seeds=[seed], maxDepth=3)
            count = 0
            for prod in builder:
                if prod is None:
                    continue
                try:
                    Chem.SanitizeMol(prod)
                except Exception:
                    continue
                seen.add(Chem.MolToSmiles(prod, canonical=True))
                count += 1
                if count >= max_per_pair:
                    break
        except Exception:
            continue
    return seen


def main() -> int:
    seed_mol = Chem.MolFromSmiles(SEED_SMILES)
    assert seed_mol is not None, "Seed SFN SMILES failed to parse"

    # Pull library SMILES (excluding the seed itself)
    library_smiles: list[str] = []
    with LIBRARY_CSV.open() as fh:
        for row in csv.DictReader(fh):
            if row["name"] == SEED_NAME:
                continue
            if row["canonical_smiles"]:
                library_smiles.append(row["canonical_smiles"])

    candidates: set[str] = set()
    candidates.add(Chem.MolToSmiles(seed_mol, canonical=True))  # include seed itself for reference
    candidates.update(enumerate_bioisosteres(SEED_SMILES))
    candidates.update(enumerate_brics(SEED_SMILES, library_smiles, max_per_pair=4))
    candidates.update(enumerate_warhead_grafts(library_smiles, max_per_template=2))

    print(f"raw candidates: {len(candidates)}")

    rows = []
    for smi in candidates:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        try:
            qed = Descriptors.qed(mol)
        except Exception:
            continue
        sim = tanimoto(mol, seed_mol)
        sa = sa_score(mol)
        lip = lipinski_pass(mol)
        score = composite(qed, sim, sa, lip)
        rows.append({
            "smiles": smi,
            "tanimoto_to_SFN": round(sim, 4),
            "qed": round(qed, 4),
            "sa_score_proxy": round(sa, 4),
            "lipinski_pass": lip,
            "mw": round(Descriptors.MolWt(mol), 2),
            "logp": round(Descriptors.MolLogP(mol), 2),
            "composite_score": round(score, 4),
            "seed": SEED_NAME,
            "source": "local_brics_bioisostere",
        })

    rows.sort(key=lambda r: r["composite_score"], reverse=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "smiles",
        "tanimoto_to_SFN",
        "qed",
        "sa_score_proxy",
        "lipinski_pass",
        "mw",
        "logp",
        "composite_score",
        "seed",
        "source",
    ]
    with OUT_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} ranked analogs -> {OUT_PATH.relative_to(REPO_ROOT)}")
    print()
    print("Top 10:")
    print(f"  {'composite':>10} {'qed':>6} {'sim':>6} {'sa':>5} {'lip':>4}  smiles")
    for r in rows[:10]:
        print(f"  {r['composite_score']:>10.4f} {r['qed']:>6.3f} {r['tanimoto_to_SFN']:>6.3f} {r['sa_score_proxy']:>5.2f} {str(r['lipinski_pass'])[:4]:>4}  {r['smiles']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
