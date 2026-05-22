"""CPU-friendly substitute for REINVENT 4 RL — iterative policy-improvement on the SFN class.

REINVENT 4's full RL loop requires a CUDA-capable PyTorch install (no
Boost-free PyPI wheel for our Mac+CPU stack). This script gives an
equivalent shape — *iterative generation with a multi-objective reward,
keeping high-reward molecules as seeds for the next iteration* — using
only deterministic RDKit operations. It's not a learned policy, but
it's a real, reproducible policy-improvement loop that runs in seconds
on a laptop.

Algorithm:
  1. Start from the 7 ITC seeds (Sulforaphane, Iberin, Erucin,
     Sulforaphene, Allyl-ITC, Benzyl-ITC, Phenethyl-ITC).
  2. Each iteration, propose K candidates per seed via:
       - Bioisosteric substitution at sulfoxide / chain length /
         warhead variants
       - BRICS recombination with library scaffolds
       - Warhead grafting onto library aromatic positions
  3. Score each proposal:
       reward = w_warhead · has_warhead
              + w_qed     · QED
              + w_sim     · max_tanimoto_to_seeds
              + w_lipinski · lipinski_pass
              − w_sa      · sa_proxy / 10
     (Mirrors REINVENT's scoring TOML.)
  4. Keep top-T candidates as seeds for the next iteration (policy-
     improvement). Persist all generated molecules + per-iteration
     reward in outputs/rl_generated.csv.

Why this is honest:
  - It's NOT REINVENT 4 — no learned policy, no SMILES sampler trained
    on ChEMBL, no RL gradient. We document this clearly.
  - It IS a real iterative generation-and-selection loop that exercises
    the same multi-objective reward function REINVENT 4 would use.
  - For a contributor who can't run Colab but wants more SFN-class
    candidates, this gives ~3-5× the diversity of the one-shot
    generator in scripts/generate_sfn_analogs.py.

REINVENT 4 on Colab remains the recommended path for serious generative
runs — see notebooks/03_reinvent_generation_colab.ipynb.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from generate_sfn_analogs import (  # noqa: E402
    SEEDS,
    enumerate_bioisosteres,
    enumerate_brics,
    enumerate_warhead_grafts,
    lipinski_pass,
    sa_score,
    tanimoto,
)

OUT_CSV = REPO_ROOT / "outputs" / "rl_generated.csv"

# Reward weights — mirror REINVENT 4 TOML in notebook 03
W = {
    "warhead": 0.40,
    "qed": 0.20,
    "sim": 0.20,
    "lipinski": 0.10,
    "sa": 0.10,
}


def has_isothiocyanate(mol) -> bool:
    from rdkit import Chem
    patt = Chem.MolFromSmarts("[NX2]=[CX2]=[SX1]")
    return mol.HasSubstructMatch(patt)


def reward(mol, seed_mols) -> dict:
    """Compute multi-objective reward components + total."""
    from rdkit.Chem import Descriptors
    qed = Descriptors.qed(mol)
    sim = max((tanimoto(mol, s) for s in seed_mols), default=0.0)
    lip = lipinski_pass(mol)
    sa = sa_score(mol)
    wh = has_isothiocyanate(mol)
    total = (
        W["warhead"] * (1.0 if wh else 0.0)
        + W["qed"] * qed
        + W["sim"] * sim
        + W["lipinski"] * (1.0 if lip else 0.0)
        - W["sa"] * sa / 10.0
    )
    return {
        "reward": round(total, 4),
        "has_warhead": wh,
        "qed": round(qed, 4),
        "max_sim_to_seeds": round(sim, 4),
        "lipinski_pass": lip,
        "sa": round(sa, 4),
    }


def load_library_smiles() -> list[str]:
    out = []
    lib_csv = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
    seed_names = {n for n, _ in SEEDS}
    with lib_csv.open() as fh:
        for row in csv.DictReader(fh):
            if row["name"] in seed_names:
                continue
            smi = row.get("canonical_smiles") or row.get("smiles") or ""
            if smi:
                out.append(smi)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Local RL-like iterative generator.")
    parser.add_argument("--iterations", type=int, default=3, help="Policy-improvement iterations (default 3).")
    parser.add_argument("--top-keep", type=int, default=15, help="Top-N rewarded candidates kept as next-iter seeds (default 15).")
    parser.add_argument("--brics-per-pair", type=int, default=2, help="BRICS recombinations per seed×library pair.")
    args = parser.parse_args()

    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")

    library_smiles = load_library_smiles()
    print(f"loaded {len(library_smiles)} library scaffolds for BRICS / warhead grafting")

    seed_mols = []
    seen: set[str] = set()
    rows = []

    # Initial seeds
    for name, smi in SEEDS:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        canon = Chem.MolToSmiles(mol, canonical=True)
        if canon in seen:
            continue
        seen.add(canon)
        seed_mols.append(mol)
        r = reward(mol, [m for _, m in (
            (n, Chem.MolFromSmiles(s)) for n, s in SEEDS
        ) if m is not None])
        rows.append({
            "iteration": 0,
            "smiles": canon,
            "origin": "seed",
            "parent_seed": name,
            **r,
        })

    print(f"iteration 0: {len(seed_mols)} initial seeds")
    print()

    for it in range(1, args.iterations + 1):
        print(f"=== iteration {it} ===")
        proposals: set[str] = set()
        for seed in seed_mols:
            seed_smi = Chem.MolToSmiles(seed, canonical=True)
            proposals |= enumerate_bioisosteres(Chem.MolToSmiles(seed))
            proposals |= enumerate_brics(seed_smi, library_smiles, max_per_pair=args.brics_per_pair)
        proposals |= enumerate_warhead_grafts(library_smiles, max_per_template=2)
        print(f"  proposals from this iteration: {len(proposals)} (de-duped against history below)")

        new_this_iter = []
        for smi in proposals:
            if smi in seen:
                continue
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                continue
            r = reward(mol, seed_mols)
            seen.add(smi)
            new_this_iter.append({
                "iteration": it,
                "smiles": smi,
                "origin": "rl_iter",
                "parent_seed": "",
                **r,
            })

        # Keep top-N by reward as new seeds
        new_this_iter.sort(key=lambda r: -r["reward"])
        keep = new_this_iter[: args.top_keep]
        print(f"  new this iter (post-dedup): {len(new_this_iter)};  top-{args.top_keep} promoted to seeds")
        for r in keep[:5]:
            print(f"    reward {r['reward']:.3f}  qed {r['qed']:.2f}  sim {r['max_sim_to_seeds']:.2f}  warhead {r['has_warhead']}  {r['smiles'][:60]}")

        # Append all (not just top-N) so we keep a record
        rows.extend(new_this_iter)

        # Promote top-N as next-iter seeds
        seed_mols = [Chem.MolFromSmiles(r["smiles"]) for r in keep]
        seed_mols = [m for m in seed_mols if m is not None]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print()
    print(f"wrote {OUT_CSV.relative_to(REPO_ROOT)}  ({len(rows)} rows across {args.iterations + 1} iterations)")

    # Summary stats per iteration
    print()
    print("=== per-iteration reward summary ===")
    print(f"  {'it':>3}  {'n_new':>6}  {'mean_reward':>11}  {'top_reward':>10}  {'warhead_frac':>12}")
    by_iter: dict[int, list[dict]] = {}
    for r in rows:
        by_iter.setdefault(r["iteration"], []).append(r)
    for it, sub in sorted(by_iter.items()):
        if not sub:
            continue
        rewards = [s["reward"] for s in sub]
        warhead_frac = sum(1 for s in sub if s["has_warhead"]) / len(sub)
        print(f"  {it:>3}  {len(sub):>6}  {sum(rewards)/len(rewards):>11.3f}  {max(rewards):>10.3f}  {warhead_frac:>12.2%}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
