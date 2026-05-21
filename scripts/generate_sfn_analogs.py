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

SEEDS = [
    ("Sulforaphane",            "CS(=O)CCCCN=C=S"),     # CID 5350    — broccoli (4-(methylsulfinyl)butyl ITC)
    ("Iberin",                  "CS(=O)CCCN=C=S"),       # CID 3032358 — cabbage (3-(methylsulfinyl)propyl ITC)
    ("Erucin",                  "CSCCCCN=C=S"),          # CID 7373    — arugula (sulfide form of SFN)
    ("Sulforaphene",            "CS(=O)/C=C/CCN=C=S"),   # CID 6433469 — radish (C2=C3 unsaturated SFN)
    ("Allyl_isothiocyanate",    "C=CCN=C=S"),            # CID 5971    — mustard / wasabi
    ("Benzyl_isothiocyanate",   "S=C=NCc1ccccc1"),       # CID 2346    — papaya / garden cress
    ("Phenethyl_isothiocyanate","S=C=NCCc1ccccc1"),      # CID 16741   — watercress (PEITC)
]
SEED_NAMES = {n for n, _ in SEEDS}


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
    # Pull library SMILES (excluding the seeds themselves)
    library_smiles: list[str] = []
    with LIBRARY_CSV.open() as fh:
        for row in csv.DictReader(fh):
            if row["name"] in SEED_NAMES:
                continue
            if row["canonical_smiles"]:
                library_smiles.append(row["canonical_smiles"])

    # Best-of similarity to ANY seed (so erucin-like analogs aren't penalized
    # just because they're far from SFN-canonical).
    seed_mols = [(name, Chem.MolFromSmiles(smi)) for name, smi in SEEDS]
    seed_mols = [(n, m) for n, m in seed_mols if m is not None]
    if not seed_mols:
        print("[ERR] no seeds parsed")
        return 1

    candidates: set[str] = set()
    seed_provenance: dict[str, str] = {}  # smi -> primary seed name

    for seed_name, seed_mol in seed_mols:
        seed_smi = Chem.MolToSmiles(seed_mol, canonical=True)
        if seed_smi not in candidates:
            candidates.add(seed_smi)
            seed_provenance[seed_smi] = seed_name
        for new_smi in enumerate_bioisosteres(Chem.MolToSmiles(seed_mol)):
            if new_smi not in candidates:
                candidates.add(new_smi)
                seed_provenance[new_smi] = seed_name
        for new_smi in enumerate_brics(Chem.MolToSmiles(seed_mol), library_smiles, max_per_pair=3):
            if new_smi not in candidates:
                candidates.add(new_smi)
                seed_provenance[new_smi] = seed_name

    # Warhead grafting is seed-independent: graft generic SFN-class tail onto library scaffolds.
    for new_smi in enumerate_warhead_grafts(library_smiles, max_per_template=2):
        if new_smi not in candidates:
            candidates.add(new_smi)
            seed_provenance[new_smi] = "Sulforaphane"

    print(f"raw candidates: {len(candidates)} across {len(seed_mols)} ITC seeds")

    rows = []
    for smi in candidates:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        try:
            qed = Descriptors.qed(mol)
        except Exception:
            continue
        # max similarity to any seed
        best_sim = 0.0
        best_seed = ""
        for name, sm in seed_mols:
            t = tanimoto(mol, sm)
            if t > best_sim:
                best_sim = t
                best_seed = name
        sa = sa_score(mol)
        lip = lipinski_pass(mol)
        score = composite(qed, best_sim, sa, lip)
        rows.append({
            "smiles": smi,
            "tanimoto_to_SFN": round(best_sim, 4),     # column kept for back-compat; now = max-to-any-ITC-seed
            "best_seed_match": best_seed,
            "qed": round(qed, 4),
            "sa_score_proxy": round(sa, 4),
            "lipinski_pass": lip,
            "mw": round(Descriptors.MolWt(mol), 2),
            "logp": round(Descriptors.MolLogP(mol), 2),
            "composite_score": round(score, 4),
            "seed": seed_provenance.get(smi, "Sulforaphane"),
            "source": "local_brics_bioisostere",
        })

    rows.sort(key=lambda r: r["composite_score"], reverse=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "smiles",
        "tanimoto_to_SFN",
        "best_seed_match",
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
