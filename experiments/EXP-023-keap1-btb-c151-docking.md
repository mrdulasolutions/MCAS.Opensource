---
id: EXP-023
title: KEAP1 BTB Cys-151 encounter docking fused with covalent adduct energy
status: published
hypothesis_category: methodology
run_date: 2026-07-27
authors:
  - name: MR Dula Medical
    role: maintainer
license: MIT
---

# KEAP1 BTB Cys-151 encounter docking + adduct fusion

> ⚠️ **Not medical advice.** Research/hypothesis use only.
> See [docs/disclaimers.md](../docs/disclaimers.md).

## 1. Hypothesis

Sulforaphane-class isothiocyanates act by **covalent modification of KEAP1 Cys-151**
in the BTB domain, not by non-covalent occupancy of the Kelch Nrf2-binding pocket.
EXP-009 docked into Kelch (4L7B); EXP-012 scored methanethiol-adduct thermodynamics
without protein context. We hypothesized that **AutoDock Vina poses in a box centered
on Cys-151 SG (PDB 5DAD BTB)** approximate the pre-reactive encounter complex, and
that fusing those scores with EXP-012 adduct energies yields a more mechanism-faithful
BTB-covalent ranking signal than either alone.

## 2. Method

- [x] In silico — structure-based (docking)
- [x] In silico — covalent proxy (adduct energy)

1. Download KEAP1 BTB structures **5DAD** (primary) and **4CXI** (fallback).
2. `scripts/prep_keap1_btb_receptor.py` — extract Cys-151 SG coordinates, clean
   chain A protein, write docking box (18 Å cube on SG), produce receptor PDBQT.
3. `scripts/dock_keap1_btb.py` — for warhead-positive compounds + top remission
   candidates: RDKit ETKDG embed → meeko PDBQT → Vina against BTB receptor.
4. Fuse: `score_btb_covalent = 0.55 * norm(−ΔG_vina) + 0.45 * score_c151`.
5. Integrate into `rank_hypotheses.py` as a KEAP1-axis bonus (max +0.05).

**What this is not:** commercial CovDock / GOLD covalent docking. Vina does not
form the C–S bond. Encounter-complex docking + adduct ΔE is an open, auditable
proxy until a covalent-capable engine is available.

## 3. Inputs

- `outputs/keap1_btb/5DAD.pdb`
- `outputs/c151_adduct_energies.csv` (EXP-012)
- `outputs/warhead_scores.csv`
- `outputs/ranked_remission.csv` (top-N seed list)
- AutoDock Vina 1.2.7 (`.tools/vina`)

## 4. Outputs

- `outputs/keap1_btb/docking_box_c151.json`
- `outputs/keap1_btb/*_receptor.pdbqt`
- `outputs/docking_KEAP1_btb_c151.csv`

## 5. Reproduction

```bash
python scripts/prep_keap1_btb_receptor.py
python scripts/dock_keap1_btb.py --top-n 40 --exhaustiveness 8
python scripts/rank_hypotheses.py
```

## 6. Results

See committed `outputs/docking_KEAP1_btb_c151.csv`. ITC-class anchors with favorable
adduct ΔE and non-clashing BTB poses score highest on `score_btb_covalent`.

## 7. Limitations

- Non-covalent Vina cannot model the dithiocarbamate bond or reversibility kinetics.
- Fallback PDBQT atom typing (if meeko/gemmi unavailable) is approximate.
- Box is geometric (SG-centered), not learned from a co-crystal covalent ligand.
- Only compounds with successful embed + Vina scores contribute; failures are logged.

## 8. Next

- True covalent docking (CovDock / GNINA covalent / OpenMM covalent MD).
- Expand BTB co-crystal set (covalent fragments at C151).
