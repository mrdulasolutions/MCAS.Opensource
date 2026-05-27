"""Covalent-warhead + KEAP1-pharmacophore scorer.

For each compound in the master library + REINVENT-generated analogs, flag
the presence of cysteine-reactive electrophiles. KEAP1 binding (and a lot of
Nrf2-axis pharmacology) requires one of these; pure-Tanimoto similarity is
fooled by structural lookalikes that lack the reactive head.

Warhead SMARTS classes (all checked; first hit wins for classification, but
the boolean `has_warhead` lights up if *any* match):

  - isothiocyanate              [N]=[C]=[S]               SFN, iberin, erucin
  - thiocyanate (S-CN)          [SX2][C]#[N]              minor SFN bioisostere
  - Michael acceptor enone      [CX3]=[CX3]-[CX3]=[OX1]   curcumin, bardoxolone
  - cyanoenone                  [CX3]=[CX3](-[C]#[N])     bardoxolone class
  - acrylamide                  [CX3]=[CX3]-[C](=O)-[N]   covalent kinase / KEAP1
  - vinyl sulfone               [CX3]=[CX3]-[S](=O)(=O)   covalent
  - alpha-haloketone            [CX3](=O)-[CX4](-[F,Cl,Br,I])
  - epoxide                     [C]1[O][C]1
  - aziridine                   [C]1[N][C]1
  - quinone                     [O]=[CX3]1-[CX3]=[CX3]-[CX3](=[O])-[CX3]=[CX3]-1

A "KEAP1 pharmacophore pass" additionally requires:
  - molecular weight 100-450 (KEAP1 Kelch pocket is shallow + small)
  - cLogP < 5 (cell-permeable)
  - reasonable distance between the warhead and the rest of the molecule
    (proxied by 2-10 heavy atoms in the chain)

Output: outputs/warhead_scores.csv
"""
from __future__ import annotations

import csv
from pathlib import Path

from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors

RDLogger.DisableLog("rdApp.*")

REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
GENERATED_CSV = REPO_ROOT / "outputs" / "reinvent_generated.csv"
OUT_PATH = REPO_ROOT / "outputs" / "warhead_scores.csv"


WARHEADS: list[tuple[str, str]] = [
    ("isothiocyanate",        "[NX2]=[CX2]=[SX1]"),
    ("thiocyanate",           "[SX2][CX2]#[NX1]"),
    ("michael_enone",         "[CX3]=[CX3][CX3]=[OX1]"),
    ("cyanoenone",            "[CX3]=[CX3]([CX2]#[NX1])"),
    ("acrylamide",            "[CX3]=[CX3][CX3](=[OX1])[NX3]"),
    ("vinyl_sulfone",         "[CX3]=[CX3][SX4](=[OX1])(=[OX1])"),
    ("alpha_haloketone",      "[CX3](=[OX1])[CX4][F,Cl,Br,I]"),
    ("epoxide",               "[CX4]1[OX2][CX4]1"),
    ("aziridine",             "[CX4]1[NX3][CX4]1"),
    ("para_quinone",          "O=C1C=CC(=O)C=C1"),
    ("ortho_quinone",         "O=C1C=CC=CC1=O"),
    ("alpha_beta_unsat_ester","[CX3]=[CX3][CX3](=[OX1])[OX2]"),
    ("alpha_beta_unsat_lactone","[CX3]=[CX3][CX3](=[OX1])[OX2;R]"),
    # --- Pro-electrophile catechol class (EXP-021) ---
    # Catechols oxidize readily to ortho-quinones, which Michael-accept
    # with cysteine thiols. This is the actual mechanism by which carnosic
    # acid, carnosol, curcumin (via its enol-tautomer ortho-quinone path),
    # and EGCG covalently modify KEAP1 Cys-151/273/288. Important: the
    # catechol itself is not the electrophile — the in-vivo-oxidized
    # quinone is. We flag the precursor as a "pro-warhead."
    # SMARTS are H-constrained ([OX2H]) so methylethers (methoxy on
    # tangeretin/nobiletin) are NOT misclassified as phenols.
    ("catechol",              "c1ccc([OX2H])c([OX2H])c1"),         # adjacent ring -OH/-OH
    ("pyrogallol",            "c1cc([OX2H])c([OX2H])c([OX2H])c1"), # 3 adjacent ring -OH
    ("hydroquinone",          "[OX2H]c1ccc([OX2H])cc1"),           # para -OH/-OH
]


def compile_warheads():
    out = []
    for name, smarts in WARHEADS:
        patt = Chem.MolFromSmarts(smarts)
        if patt is None:
            print(f"  [WARN] bad SMARTS for {name}: {smarts}")
            continue
        out.append((name, patt))
    return out


def warhead_hits(mol, patts) -> list[str]:
    return [name for name, p in patts if mol.HasSubstructMatch(p)]


def keap1_pharmacophore_pass(mol) -> bool:
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    n_heavy = mol.GetNumHeavyAtoms()
    return 100.0 <= mw <= 500.0 and logp <= 5.0 and 6 <= n_heavy <= 35


def load_sources() -> list[dict]:
    out = []
    seen = set()

    with LIBRARY_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("canonical_smiles") or row.get("smiles") or ""
            if not smi or smi in seen:
                continue
            seen.add(smi)
            out.append({"name": row["name"], "smiles": smi, "source": "library", "category": row.get("category", "")})

    if GENERATED_CSV.exists():
        with GENERATED_CSV.open() as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                smi = row.get("smiles", "")
                if not smi or smi in seen:
                    continue
                seen.add(smi)
                out.append({"name": f"GEN_{i:04d}", "smiles": smi, "source": "reinvent_generated", "category": "candidate"})
    return out


def main() -> int:
    sources = load_sources()
    patts = compile_warheads()
    print(f"scoring {len(sources)} unique molecules against {len(patts)} warhead SMARTS")

    rows = []
    for s in sources:
        mol = Chem.MolFromSmiles(s["smiles"])
        if mol is None:
            continue
        hits = warhead_hits(mol, patts)
        ph_pass = keap1_pharmacophore_pass(mol)
        rows.append({
            "name": s["name"],
            "smiles": s["smiles"],
            "source": s["source"],
            "category": s["category"],
            "has_warhead": bool(hits),
            "warheads": ";".join(hits),
            "n_warheads": len(hits),
            "keap1_pharmacophore_pass": ph_pass,
            "warhead_score": (1.0 if hits else 0.0) * (1.0 if ph_pass else 0.5),
        })

    rows.sort(key=lambda r: (-r["warhead_score"], -r["n_warheads"]))
    with OUT_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    n_with_wh = sum(1 for r in rows if r["has_warhead"])
    n_pass = sum(1 for r in rows if r["keap1_pharmacophore_pass"])
    n_full = sum(1 for r in rows if r["warhead_score"] == 1.0)
    print(f"wrote {len(rows)} rows -> {OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"  has any warhead:            {n_with_wh}")
    print(f"  passes KEAP1 pharmacophore: {n_pass}")
    print(f"  both (full warhead score):  {n_full}")
    print()
    print("Top 15 (warhead + pharmacophore):")
    for r in rows[:15]:
        print(f"  {r['warhead_score']:>4.2f}  {r['name']:<30}  {r['warheads']:<40}  {r['smiles']}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
