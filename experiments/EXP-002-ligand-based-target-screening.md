---
id: EXP-002
title: Ligand-based virtual screening across 8 MCAS targets
status: published
hypothesis_category: methodology
run_date: 2026-05-21
authors:
  - name: MR Dula Medical
    role: provider
    affiliation: "DBA of MR Dula Enterprise, LLC; Raleigh, NC, USA"
  - name: OpenMCAS contributors
    role: maintainer
license: MIT
---

# Ligand-based virtual screening across 8 MCAS targets

> ⚠️ **Not medical advice.** Research/hypothesis use only.

## 1. Hypothesis

For an early-triage MCAS hypothesis pipeline running on commodity laptops (no
GPU), **maximum Tanimoto similarity to a curated set of known reference ligands
per target** is a defensible proxy for "this compound is plausibly in the same
pharmacological class." It is not a substitute for physics-based docking — but
when a target structure is uncertain (MRGPRX2's shallow pocket, KEAP1's covalent
site) or no GPU is available, it gives reproducible, audit-able rankings.

Falsifiable claim: well-known reference compounds should score ≥0.5 (Tanimoto)
against their known targets and ≤0.3 against unrelated targets.

## 2. Method

In silico — ligand-based.

For each of 8 targets, define a curated reference set of 4–13 known
binders/inhibitors/activators (SMILES-validated against PubChem CID).

For every compound in the library + every generated analog:
1. Compute Morgan fingerprint (radius 2, 2048 bits).
2. For each target: max Tanimoto over the target's reference fingerprints.
3. Record best matching reference + score.

Targets covered: MRGPRX2, KIT, **KEAP1** (replaces an earlier NFE2L2 misnaming —
SFN binds KEAP1, not the Nrf2 TF), HRH1, HRH2, CYSLTR1, BTK, GLP1R.

## 3. Inputs

| Input | File / version |
|-------|----------------|
| Compound sources | `data/compounds/MCAS_Compound_Library_v1.csv` + `outputs/reinvent_generated.csv` @ commit `01b81de` |
| Reference ligand sets | in-code in `scripts/score_against_targets.py` |
| Target index | `data/targets/MCAS_Targets.csv` |

## 4. Parameters

```bash
python scripts/score_against_targets.py
```

## 5. Environment

```text
Python: 3.9.6
RDKit:  2023.9.6
Hardware: Apple Silicon Mac, CPU only
```

## 6. Outputs

| File | Description |
|------|-------------|
| `outputs/docking_MRGPRX2.csv` | 157 compounds × 1 target |
| `outputs/docking_KIT.csv` | 157 × 1 |
| `outputs/docking_KEAP1.csv` | 157 × 1 |
| `outputs/docking_HRH1.csv`, `_HRH2.csv`, `_CYSLTR1.csv`, `_BTK.csv`, `_GLP1R.csv` | per-target |

Schema (each file): `name, smiles, category, source, target, score, best_ref, method`.
The `method` column is always `ligand_based_similarity_tanimoto_morgan2_2048`,
so downstream consumers can never mistake this for physics-based docking.

## 7. Interpretation

Sanity checks passed: known anchors top their own targets cleanly.

- KEAP1 top: Curcumin / Sulforaphane (1.00) — both in reference set
- KIT top: Masitinib (0.75 vs. imatinib) — class match without self-match
- HRH1 top: Cetirizine (1.00) — in reference
- HRH2 top: Famotidine (1.00) — in reference
- CYSLTR1 top: Montelukast (0.51) — class match

For the SFN-axis specifically (KEAP1 target), 13 reference ligands span both
covalent electrophiles (SFN, iberin, erucin, DMF, bardoxolone, oltipraz,
omaveloxolone, dimethyl itaconate) and non-covalent Kelch-PPI binders.

## 8. Reproduction

```bash
git clone https://github.com/mrdulasolutions/MCAS.Opensource.git
cd MCAS.Opensource && git checkout 01b81de
.venv/bin/python scripts/score_against_targets.py
```

Wall-clock: ~5 seconds for 157 × 8 targets. Memory: <500 MB.

## 9. Limitations

- Tanimoto-only — no docking pose, no scoring function, no free-energy estimate.
- Reference ligands are hand-curated; not exhaustive. Bias toward well-known
  drugs may miss novel chemotypes.
- Self-matches inflate the top of each list (e.g. Quercetin = 1.00 vs. itself);
  the ranking script (`rank_hypotheses.py`) accounts for this.

## 10. Next experiments suggested

1. EXP-003 — covalent-warhead SMARTS filter to penalize KEAP1 lookalikes that
   lack the cysteine-reactive head.
2. Future — Vina/smina docking on KEAP1 Kelch domain (PDB 4L7B) for top-30.
3. Future — pull ChEMBL bioassays tagged "mast cell" or "degranulation" and
   train an actual mast-cell-stabilizer predictor.

## 11. References

- Maggiora G et al. *Molecular similarity in medicinal chemistry.* J Med Chem 2014.
- Cereto-Massagué A et al. *Molecular fingerprint similarity search in virtual screening.* Methods 2015.
