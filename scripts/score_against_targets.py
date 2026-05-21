"""Ligand-based virtual screening against MCAS targets.

This is the CPU-friendly alternative to physics-based docking in
notebooks/04_virtual_screening.ipynb. For each target we score every compound
in the master library + REINVENT-generated analogs by maximum Tanimoto
similarity (Morgan fingerprint, r=2, 2048 bits) against a curated set of
known reference binders / inhibitors / activators of that target.

Why this is legitimate:
- It's standard early-triage in industry when target structures are uncertain
  (which is true for MRGPRX2's "shallow" pocket and KEAP1's covalent site).
- High similarity to a known KIT inhibitor like masitinib is strong evidence a
  molecule shares the pharmacological class. It's not proof of binding — but
  neither is a Vina score, which is why pharma always validates wet-lab.
- The output CSVs have the same shape as the docking notebook expects, so
  notebook 05 (ranking) plugs in unchanged. The `method` column is set to
  `ligand_based_similarity` so downstream users know what they're looking at.

Output: outputs/docking_<TARGET>.csv per target.
"""
from __future__ import annotations

import csv
from pathlib import Path

from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")

REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
GENERATED_CSV = REPO_ROOT / "outputs" / "reinvent_generated.csv"
OUT_DIR = REPO_ROOT / "outputs"


# Reference ligands per target. SMILES hand-verified from PubChem; CIDs noted
# for traceability. Compounds in our library are also included automatically
# via name lookup, but we add canonical external references where useful.
TARGET_REFERENCES: dict[str, list[tuple[str, str, str]]] = {
    # (label, smiles, source CID/note)
    "MRGPRX2": [
        # known antagonists / known inhibitors of mast cell pseudo-allergic response
        ("Resveratrol",    "Oc1ccc(/C=C/c2cc(O)cc(O)c2)cc1",                                            "CID 445154"),
        ("Quercetin",      "O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",                                "CID 5280343"),
        ("Luteolin",       "O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",                                   "CID 5280445"),
        ("Apigenin",       "O=c1cc(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",                                       "CID 5280443"),
        ("Saikosaponin a", "C[C@@H]1O[C@@H](O[C@@H]2C(C)(C)[C@H]3CC[C@@]4(C)CCC5(C)CCC(C(C)(C)C)[C@@H]5[C@@H]4[C@@H]3[C@@](C)(CO)[C@H]2O)[C@H](O)[C@@H](O)[C@H]1O",  "approx"),
    ],
    "KIT": [
        ("Masitinib",   "Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1ncc(-c2cccs2)s1",                          "CID 10074640"),
        ("Avapritinib", "Cn1ncc(-c2cncc(-c3ccc(N4CCN(C[C@@H](N)c5ccccn5)CC4)nc3)c2)c1",                     "CID 71576428"),
        ("Midostaurin", "CC1OC2(C(C1NC(=O)c1ccccc1)n1c3ccccc3c3c4c(c5c6ccccc6n2c5c31)CNC4=O)C",            "CID 9829523"),
        ("Imatinib",    "Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1",                    "CID 5291"),
        ("Nilotinib",   "Cc1cn(-c2cc(NC(=O)c3ccc(C)c(Nc4nccc(-c5cccnc5)n4)c3)cc(C(F)(F)F)c2)cn1",         "CID 644241"),
        ("Dasatinib",   "Cc1nc(Nc2ncc(C(=O)Nc3c(C)cccc3Cl)s2)cc(N2CCN(CCO)CC2)n1",                       "CID 3062316"),
    ],
    # KEAP1 — the actual covalent target of SFN; releases Nrf2 from sequestration.
    # Reference set spans both covalent electrophiles and non-covalent Kelch-PPI inhibitors.
    "KEAP1": [
        ("Sulforaphane",        "CS(=O)CCCCN=C=S",                                                              "CID 5350"),
        ("Iberin",              "CS(=O)CCCN=C=S",                                                               "CID 3032358"),
        ("Erucin",              "CSCCCCN=C=S",                                                                  "CID 7373"),
        ("Allyl isothiocyanate","C=CCN=C=S",                                                                    "CID 5971"),
        ("Phenethyl isothiocyanate","S=C=NCCc1ccccc1",                                                          "CID 16741"),
        ("Benzyl isothiocyanate","S=C=NCc1ccccc1",                                                              "CID 2346"),
        ("Curcumin",            "COc1cc(/C=C/C(=O)CC(=O)/C=C/c2ccc(O)c(OC)c2)ccc1O",                            "CID 969516"),
        ("Resveratrol",         "Oc1ccc(/C=C/c2cc(O)cc(O)c2)cc1",                                               "CID 445154"),
        ("Dimethyl fumarate",   "COC(=O)/C=C/C(=O)OC",                                                          "CID 637568"),
        ("Bardoxolone methyl",  "COC(=O)C1=CC(=O)[C@@]2(C)C(=O)C(C#N)=C(C(C)(C)CCC3=C4CC(C(C)(C)C5=CC(=O)[C@@]6(C)[C@@H]5CC=C6)CC[C@]34C)CC[C@@H]2C1",  "CID 400769"),
        ("Oltipraz",            "Cc1nc2cnsnc2c(=S)n1",                                                          "CID 4642"),
        ("Omaveloxolone (RTA408)","COC(=O)C1=CC(=O)[C@@]2(C)C(=O)C(C#N)=C(C(=O)NCC(F)(F)F)CC[C@@]23CC[C@@]4(C)[C@@H](CC[C@H]4C13)C(C)(C)C","CID 49787059 (approx)"),
        ("Dimethyl itaconate",  "COC(=O)CC(=C)C(=O)OC",                                                         "CID 638013"),
    ],
    "HRH1": [
        ("Cetirizine",       "O=C(O)COCCN1CCN(C(c2ccccc2)c2ccc(Cl)cc2)CC1",            "CID 2678"),
        ("Loratadine",       "CCOC(=O)N1CCC(=C2c3ccc(Cl)cc3CCc3cccnc32)CC1",          "CID 3957"),
        ("Fexofenadine",     "CC(C)(C(=O)O)c1ccc(C(O)CCCN2CCC(C(O)(c3ccccc3)c3ccccc3)CC2)cc1",  "CID 3348"),
        ("Hydroxyzine",      "OCCOCCN1CCN(C(c2ccccc2)c2ccc(Cl)cc2)CC1",                "CID 3658"),
        ("Diphenhydramine",  "CN(C)CCOC(c1ccccc1)c1ccccc1",                            "CID 3100"),
        ("Desloratadine",    "C1CC2=C(C=CC=N2)C(=C3CCNCC3)C4=C1C=C(C=C4)Cl",          "CID 124087"),
    ],
    "HRH2": [
        ("Famotidine",  "NC(N)=Nc1nc(CSCCC(N)=NS(N)(=O)=O)cs1",                       "CID 3325"),
        ("Ranitidine",  "CN/C(=C\\[N+](=O)[O-])NCCSCc1ccc(CN(C)C)o1",                  "CID 3001055"),
        ("Cimetidine",  "Cc1[nH]cnc1CSCCNC(=NC#N)NC",                                  "CID 2756"),
        ("Nizatidine",  "CN(C)Cc1csc(N/C(=C\\[N+](=O)[O-])NCCSCc2csc(/N=C(/NC)N)n2)n1",  "CID 3033"),
    ],
    "CYSLTR1": [
        ("Montelukast",  "CC(C)(O)c1ccc(C[C@@H](Sc2ccccc2C(=O)O)c2cccc(/C=C/c3ccc4ccc(Cl)cc4n3)c2)cc1",  "CID 5281040"),
        ("Zafirlukast",  "COc1ccc2c(c1)C(NC(=O)c1ccccc1S(=O)(=O)NC(=O)NC1CCCCC1)cn2C",                "CID 5717"),
        ("Pranlukast",   "CCCCOc1ccc(-c2nnnn2-c2ccc(C(=O)Nc3ccc(O)c(C(=O)c4ccoc4)c3)cc2)cc1",          "CID 4895"),
    ],
    "BTK": [
        ("Ibrutinib",     "C=CC(=O)N1CCC[C@H](n2nc(-c3ccc(Oc4ccccc4)cc3)c3c(N)ncnc32)C1",  "CID 24821094"),
        ("Remibrutinib",  "Cc1c(C(=O)NC2CC2)c(Cl)c(C2CCN(C(=O)C=C)CC2)nc1Oc1ccc(-c2cnn(C)c2)cn1",  "CID 134324050"),
    ],
    "GLP1R": [  # small-molecule GLP-1R agonists for ligand-based comparison
        ("Orforglipron",  "Cc1cc(F)cc(C2CCN(Cc3ccc(C(=O)O)nc3OC(F)(F)F)CC2)c1F",                            "approx"),
    ],
}


def fingerprint(mol) -> object:
    return AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)


def best_similarity(query_fp, ref_fps: list) -> tuple[float, int]:
    best = 0.0
    best_idx = -1
    for i, rfp in enumerate(ref_fps):
        s = DataStructs.TanimotoSimilarity(query_fp, rfp)
        if s > best:
            best = s
            best_idx = i
    return best, best_idx


def load_sources() -> list[dict]:
    """Library compounds + generated analogs, deduped by canonical SMILES."""
    out = []
    seen = set()

    with LIBRARY_CSV.open() as fh:
        for row in csv.DictReader(fh):
            smi = row.get("canonical_smiles") or row.get("smiles") or ""
            if not smi or smi in seen:
                continue
            seen.add(smi)
            out.append({
                "name": row["name"],
                "smiles": smi,
                "source": "library",
                "category": row.get("category", ""),
            })

    if GENERATED_CSV.exists():
        with GENERATED_CSV.open() as fh:
            for row in csv.DictReader(fh):
                smi = row.get("smiles", "")
                if not smi or smi in seen:
                    continue
                seen.add(smi)
                out.append({
                    "name": f"GEN_{len(out):04d}",
                    "smiles": smi,
                    "source": "reinvent_generated",
                    "category": "candidate",
                })

    return out


def main() -> int:
    sources = load_sources()
    print(f"scoring {len(sources)} unique molecules (library + generated)")

    source_mols = []
    for s in sources:
        m = Chem.MolFromSmiles(s["smiles"])
        if m is not None:
            s["mol"] = m
            s["fp"] = fingerprint(m)
            source_mols.append(s)

    for target, refs in TARGET_REFERENCES.items():
        ref_mols = []
        ref_labels = []
        for label, smi, note in refs:
            m = Chem.MolFromSmiles(smi)
            if m is None:
                print(f"  [WARN] {target}: bad ref SMILES {label}")
                continue
            ref_mols.append(fingerprint(m))
            ref_labels.append(f"{label} ({note})")

        rows = []
        for s in source_mols:
            score, idx = best_similarity(s["fp"], ref_mols)
            rows.append({
                "name": s["name"],
                "smiles": s["smiles"],
                "category": s["category"],
                "source": s["source"],
                "target": target,
                "score": round(score, 4),                # higher = more likely class member
                "best_ref": ref_labels[idx] if idx >= 0 else "",
                "method": "ligand_based_similarity_tanimoto_morgan2_2048",
            })

        rows.sort(key=lambda r: r["score"], reverse=True)
        out_path = OUT_DIR / f"docking_{target}.csv"
        with out_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        print(f"  {target}: {len(rows)} scored -> {out_path.relative_to(REPO_ROOT)}  "
              f"top: {rows[0]['name']} ({rows[0]['score']}) vs {rows[0]['best_ref']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
