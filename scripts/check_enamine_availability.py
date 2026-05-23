"""EXP-017 — Enamine REAL Space availability check for top generated analogs.

Honest scope: there is no public, unauthenticated Enamine REAL search API
that returns commercial availability for an arbitrary SMILES. This script
does the next-best thing:

  1. Reads the unique generated analogs from `outputs/rl_generated.csv`
     (and merges `outputs/reinvent_generated.csv` for the BRICS/bioisostere
     batch).
  2. Drops the seed compounds — those are off-the-shelf (Sigma, TCI) and
     don't need REAL-Space lookups.
  3. Computes the procurement-relevant descriptors for each novel analog:
     canonical SMILES, InChI, InChIKey, MW, heavy atoms, formal charge,
     ring count, RDKit Lipinski/QED, and an RDKit SA-score proxy
     (the same proxy used in the generator).
  4. Tags each analog with a `real_space_plausible` heuristic that flags
     molecules in Enamine's typical REAL-Space envelope (MW 200–500,
     heavy atoms ≤ 35, no exotic atoms beyond C/H/N/O/S/F/Cl/Br, SA ≤ 4.5,
     ≤ 2 stereo centers).
  5. Emits a structured CSV (`outputs/exp_017/enamine_lookup.csv`) plus
     a markdown procurement packet (`outputs/exp_017/procurement_packet.md`)
     containing per-compound vendor lookup URLs (Enamine REAL search,
     MolPort, eMolecules, PubChem) that a wet-lab partner can paste into
     a CRO request.

The CRO outreach (EXP-017 follow-up) then uses the markdown packet as the
attachment for the actual quote request.

Usage:
    python scripts/check_enamine_availability.py [--top N]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import urllib.parse
from pathlib import Path

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, Crippen, Descriptors, Lipinski, QED, inchi

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "outputs" / "exp_017"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RL_CSV = REPO / "outputs" / "rl_generated.csv"
BRICS_CSV = REPO / "outputs" / "reinvent_generated.csv"

# Atoms we allow in a REAL-Space-plausible molecule.
ALLOWED_ATOMS = {"C", "H", "N", "O", "S", "F", "Cl", "Br"}

# Seeds that are off-the-shelf — they're filtered out, not lookups.
SEED_SMILES = {
    "CS(=O)CCCCN=C=S",   # Sulforaphane
    "CS(=O)CCCN=C=S",    # Iberin
    "CSCCCCN=C=S",       # Erucin
    "CS(=O)/C=C/CCN=C=S",  # Sulforaphene
    "C=CCN=C=S",         # Allyl-ITC
    "S=C=NCc1ccccc1",    # Benzyl-ITC
    "S=C=NCCc1ccccc1",   # PEITC
}


def _safe_sa(mol) -> float:
    """RDKit synthetic accessibility proxy (same as scoring in generators)."""
    try:
        from rdkit.Chem import rdMolDescriptors
        nbridge = rdMolDescriptors.CalcNumBridgeheadAtoms(mol)
        nspiro = rdMolDescriptors.CalcNumSpiroAtoms(mol)
        macrocycle = any(len(r) >= 9 for r in mol.GetRingInfo().AtomRings())
        nstereo = len(Chem.FindMolChiralCenters(mol, includeUnassigned=True))
        n_heavy = mol.GetNumHeavyAtoms()
        sa = (
            1.0
            + 0.02 * n_heavy
            + 0.5 * nbridge
            + 0.5 * nspiro
            + (2.0 if macrocycle else 0.0)
            + 0.2 * nstereo
        )
        return round(min(sa, 10.0), 2)
    except Exception:
        return 5.0


def descriptors_for(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"valid": False}
    can = Chem.MolToSmiles(mol, canonical=True)
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    hba = Lipinski.NumHAcceptors(mol)
    hbd = Lipinski.NumHDonors(mol)
    rotb = Lipinski.NumRotatableBonds(mol)
    n_heavy = mol.GetNumHeavyAtoms()
    formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
    inchi_str = inchi.MolToInchi(mol)
    inchikey = inchi.MolToInchiKey(mol)
    qed_val = QED.qed(mol)
    sa = _safe_sa(mol)
    atoms = {a.GetSymbol() for a in mol.GetAtoms()}
    exotic = atoms - ALLOWED_ATOMS
    stereo = len(Chem.FindMolChiralCenters(mol, includeUnassigned=True))
    return {
        "valid": True,
        "canonical_smiles": can,
        "molecular_formula": formula,
        "mw": round(mw, 2),
        "logp": round(logp, 2),
        "hba": hba,
        "hbd": hbd,
        "rot_bonds": rotb,
        "n_heavy_atoms": n_heavy,
        "n_stereo_centers": stereo,
        "qed": round(qed_val, 3),
        "sa_score_proxy": sa,
        "exotic_atoms": ",".join(sorted(exotic)) if exotic else "",
        "inchi": inchi_str,
        "inchikey": inchikey,
        "lipinski_pass": (mw <= 500 and logp <= 5 and hba <= 10 and hbd <= 5),
    }


def real_space_plausible(d: dict) -> tuple[bool, str]:
    """Heuristic gate for Enamine REAL Space envelope.

    REAL is mostly amide/sulfonamide/click-coupled fragments with
    drug-like profile. Reasons must be machine-parseable.
    """
    if not d.get("valid"):
        return False, "invalid_smiles"
    reasons = []
    if d["mw"] < 200 or d["mw"] > 500:
        reasons.append(f"mw_out_of_envelope({d['mw']})")
    if d["n_heavy_atoms"] > 35:
        reasons.append(f"heavy_atoms_too_many({d['n_heavy_atoms']})")
    if d["exotic_atoms"]:
        reasons.append(f"exotic_atoms({d['exotic_atoms']})")
    if d["sa_score_proxy"] > 4.5:
        reasons.append(f"sa_too_high({d['sa_score_proxy']})")
    if d["n_stereo_centers"] > 2:
        reasons.append(f"too_many_stereo({d['n_stereo_centers']})")
    return (len(reasons) == 0), ";".join(reasons) if reasons else "ok"


def vendor_urls(d: dict) -> dict:
    """Return a dict of vendor / database search URLs for manual lookup."""
    inchikey = d.get("inchikey", "")
    smiles = d.get("canonical_smiles", "")
    smiles_q = urllib.parse.quote(smiles, safe="")
    inchikey_q = urllib.parse.quote(inchikey, safe="")
    return {
        "enamine_real_search": (
            f"https://newreal.enamine.net/search?query={inchikey_q}"
            if inchikey else ""
        ),
        "molport_search": (
            f"https://www.molport.com/shop/swl-step-1?compound-smile={smiles_q}"
            if smiles else ""
        ),
        "emolecules_search": (
            f"https://search.emolecules.com/search/#?p=ssr&q={smiles_q}"
            if smiles else ""
        ),
        "pubchem_inchikey": (
            f"https://pubchem.ncbi.nlm.nih.gov/#query={inchikey_q}"
            if inchikey else ""
        ),
        "chemspider_inchikey": (
            f"https://www.chemspider.com/Search.aspx?q={inchikey_q}"
            if inchikey else ""
        ),
    }


def load_generated(top: int) -> pd.DataFrame:
    rl = pd.read_csv(RL_CSV) if RL_CSV.exists() else pd.DataFrame()
    brics = pd.read_csv(BRICS_CSV) if BRICS_CSV.exists() else pd.DataFrame()

    # Normalize columns.
    if not rl.empty:
        rl = rl.rename(columns={"smiles": "smiles"})
        rl["source"] = rl["origin"].fillna("rl")
        rl["parent_seed"] = rl["parent_seed"].fillna("")
        rl_score = rl["reward"]
    else:
        rl_score = pd.Series(dtype=float)

    if not brics.empty:
        brics["source"] = brics.get("source", "local_brics_bioisostere")
        brics["reward"] = brics.get("composite_score", 0.0)
        brics["parent_seed"] = brics.get("seed", "")
        brics["origin"] = "brics"

    keep_cols = ["smiles", "source", "parent_seed", "reward"]
    parts = []
    if not rl.empty:
        parts.append(rl[keep_cols])
    if not brics.empty:
        parts.append(brics[keep_cols])
    if not parts:
        raise SystemExit("No generated analogs found.")
    df = pd.concat(parts, ignore_index=True)

    # Drop seeds + dedup, keep highest-reward row per SMILES.
    df = df[~df["smiles"].isin(SEED_SMILES)]
    df = df.sort_values("reward", ascending=False).drop_duplicates("smiles", keep="first")
    df = df.head(top).reset_index(drop=True)
    return df


def main(top: int) -> None:
    df = load_generated(top)
    print(f"Loaded {len(df)} unique novel analogs to score.")

    rows: list[dict] = []
    for _, r in df.iterrows():
        d = descriptors_for(r["smiles"])
        plausible, reasons = real_space_plausible(d)
        urls = vendor_urls(d)
        rows.append({
            "rank": len(rows) + 1,
            "smiles": r["smiles"],
            "source": r["source"],
            "parent_seed": r["parent_seed"],
            "generator_reward": round(float(r["reward"]), 4),
            **d,
            "real_space_plausible": plausible,
            "plausibility_reasons": reasons,
            **urls,
        })

    out_df = pd.DataFrame(rows)
    out_csv = OUT_DIR / "enamine_lookup.csv"
    out_df.to_csv(out_csv, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Wrote {out_csv} — {len(out_df)} rows.")

    n_plausible = int(out_df["real_space_plausible"].sum())
    print(f"Plausible REAL-Space candidates: {n_plausible} / {len(out_df)}")

    # --- Markdown procurement packet ---
    md_path = OUT_DIR / "procurement_packet.md"
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    plausible_df = out_df[out_df["real_space_plausible"]].copy()

    lines: list[str] = []
    lines.append("# EXP-017 — Procurement packet for top generated analogs")
    lines.append("")
    lines.append(
        "**Generated:** " + timestamp + "  ·  "
        "**Pipeline commit:** see `git log` in repo  ·  "
        "**License:** MIT (data) / Apache-2.0 (code paths upstream)."
    )
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This file is a vendor-ready summary of the **top novel SFN-class analogs** "
        "from the OpenMCAS generative pipeline (EXP-013 + EXP-001). The intent is "
        "to attach this packet to a quote request to Enamine REAL Space, MolPort, "
        "and / or eMolecules to verify which structures are commercially procurable "
        "(or REAL-on-demand synthesizable) before any wet-lab β-hexosaminidase / "
        "LAD2 mast-cell assay is funded."
    )
    lines.append("")
    lines.append("## What we did vs. what we did NOT do")
    lines.append("")
    lines.append("- ✅ Computed canonical SMILES, InChI, InChIKey, MW, formula, "
                 "Lipinski compliance, QED, RDKit SA-proxy.")
    lines.append("- ✅ Filtered to compounds inside the published Enamine REAL Space "
                 "envelope (MW 200–500, ≤ 35 heavy atoms, common atoms, SA ≤ 4.5, "
                 "≤ 2 stereo centers).")
    lines.append("- ❌ **Did NOT** query the Enamine REAL Space catalog directly — "
                 "there is no public unauthenticated API. The `enamine_real_search` "
                 "URLs in the CSV are manual lookup links a CRO can click.")
    lines.append("- ❌ **Did NOT** confirm catalog presence, in-stock status, or "
                 "purity grade. Treat every link as a *probe*, not a guarantee.")
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append("Top novel analogs (seeds excluded) are sorted by the generative "
                 "model's composite reward (warhead + QED + SA + seed-similarity + "
                 "Lipinski). The seed compounds themselves (Sulforaphane, Iberin, "
                 "Erucin, Sulforaphene, Allyl-ITC, Benzyl-ITC, PEITC) are off-the-shelf "
                 "from Sigma / TCI / Cayman and are NOT included in this packet.")
    lines.append("")
    lines.append(
        f"## Top-{len(plausible_df)} REAL-Space-plausible candidates"
    )
    lines.append("")
    lines.append("| Rank | SMILES | Formula | MW | QED | SA | Lipinski | Parent seed |")
    lines.append("|------|--------|---------|----|-----|----|-----|----|")
    for _, r in plausible_df.iterrows():
        lines.append(
            f"| {int(r['rank'])} | `{r['canonical_smiles']}` | {r['molecular_formula']} | "
            f"{r['mw']:.1f} | {r['qed']:.2f} | {r['sa_score_proxy']:.1f} | "
            f"{'✅' if r['lipinski_pass'] else '❌'} | {r['parent_seed'] or '—'} |"
        )
    lines.append("")
    lines.append("## Lookup URLs per candidate")
    lines.append("")
    lines.append("Paste these into the vendor's search box. Enamine REAL Space "
                 "is searched by InChIKey for exact match (REAL-Space members do "
                 "not always have a CAS or canonical name).")
    lines.append("")
    for _, r in plausible_df.iterrows():
        lines.append(f"### #{int(r['rank'])} — `{r['canonical_smiles']}`")
        lines.append("")
        lines.append(f"- **InChIKey:** `{r['inchikey']}`")
        lines.append(f"- **Formula:** {r['molecular_formula']}, **MW** {r['mw']:.2f}, **logP** {r['logp']:.2f}")
        lines.append(f"- **Enamine REAL search:** {r['enamine_real_search']}")
        lines.append(f"- **MolPort search:** {r['molport_search']}")
        lines.append(f"- **eMolecules search:** {r['emolecules_search']}")
        lines.append(f"- **PubChem (already known?):** {r['pubchem_inchikey']}")
        lines.append("")
    lines.append("## Candidates filtered OUT (and why)")
    lines.append("")
    filtered_out = out_df[~out_df["real_space_plausible"]]
    if filtered_out.empty:
        lines.append("All scored candidates passed the REAL-Space envelope filter.")
    else:
        lines.append("| Rank | SMILES | Reason(s) filtered |")
        lines.append("|------|--------|--------------------|")
        for _, r in filtered_out.iterrows():
            lines.append(
                f"| {int(r['rank'])} | `{r.get('canonical_smiles') or r['smiles']}` | "
                f"{r['plausibility_reasons']} |"
            )
    lines.append("")
    lines.append("## Next steps after a quote comes back")
    lines.append("")
    lines.append("1. Confirm 3 procurable candidates with the most upstream-distinct "
                 "structures (don't buy 3 close analogs).")
    lines.append("2. Order 5–10 mg each, ≥ 95% purity, in DMSO-soluble form.")
    lines.append("3. Run the β-hex / LAD2 protocol referenced in "
                 "[`docs/wet_lab_protocols.md`](../docs/wet_lab_protocols.md) "
                 "alongside Sulforaphane (positive class control) + Cetirizine "
                 "(non-stabilizer negative).")
    lines.append("4. File the result as **EXP-018-real-wet-lab-pilot**, regardless "
                 "of whether the candidate moves or fails — publishable either way.")
    lines.append("")
    lines.append("## Disclaimer")
    lines.append("")
    lines.append("Not medical advice. Not a recommendation that any specific compound "
                 "is safe, effective, or appropriate for any human use. This packet "
                 "exists to surface in-silico hypotheses for in-vitro testing. See "
                 "[`docs/disclaimers.md`](../docs/disclaimers.md).")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {md_path} — {len(plausible_df)} REAL-plausible candidates surfaced.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=25, help="Top-N novel analogs to score.")
    args = ap.parse_args()
    main(args.top)
