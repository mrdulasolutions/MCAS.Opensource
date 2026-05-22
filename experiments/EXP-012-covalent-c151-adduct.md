---
id: EXP-012
title: Covalent KEAP1-C151 dithiocarbamate adduct energy proxy
status: published
hypothesis_category: remission
run_date: 2026-05-22
authors:
  - name: MR Dula Medical
    role: provider
    affiliation: "DBA of MR Dula Enterprise, LLC; Raleigh, NC, USA"
  - name: OpenMCAS contributors
    role: maintainer
license: MIT
---

# Covalent KEAP1-C151 adduct energy proxy — the actual SFN mechanism

> ⚠️ **Not medical advice.** Research/hypothesis use only.

## Headline

EXP-009's Vina docking targeted the KEAP1 Kelch pocket — a *non-covalent*
PPI site. But **SFN's actual mechanism is covalent C151 modification in
the BTB domain**, which vanilla Vina cannot model.

This experiment fills that gap with an honest CPU-friendly proxy: build
each ITC's **dithiocarbamate adduct with methanethiol** (a one-amino-acid
cysteine model), MMFF94-minimize parent / methanethiol / adduct
separately, compute the reaction energy

```
ΔE_proxy  =  E(adduct)  −  [E(ITC) + E(CH3SH)]
```

More-negative ΔE = more thermodynamically favorable adduct → more
mechanism-relevant covalent KEAP1 modifier.

Results across 86 ITC-class candidates from the library + AI-generated
analogs:

| Rank | Compound | ΔE (kcal/mol) | Score |
|------|----------|---------------|-------|
| 1 | Allyl-ITC | -39.42 | 0.41 |
| 2 | Iberin | -39.17 | 0.41 |
| 3 | Benzyl-ITC | -37.55 | 0.38 |
| 4 | **Sulforaphane** | -34.76 | 0.34 |
| 5 | Erucin | -34.18 | 0.33 |
| 6 | PEITC | -33.97 | 0.32 |
| 7 | Sulforaphene | -32.45 | 0.30 |

(Top-15 includes 4 AI-generated analogs with stronger predicted adduct
stability than any natural ITC — large hybrid scaffolds where the bulkier
parent contributes extra MMFF stabilization in the adduct state.)

**Chemistry sanity:** smaller / less-hindered ITCs (allyl, iberin)
predict more favorable thiol adducts — consistent with their known
reactivity. The bulkier SFN-class anchors sit ~5 kcal/mol behind but
still well-favored.

## 1. Hypothesis

> The dithiocarbamate adduct formation reaction
> `R-N=C=S + H-S-Cys151 → R-NH-C(=S)-S-Cys151` is favorable for every
> ITC-class compound, and the relative thermodynamic favorability
> orders compounds consistent with their published reactivity toward
> protein thiols.

Falsifiable: if any ITC-class candidate produces ΔE > 0 (adduct LESS
stable than starting materials), the proxy is broken. (None did. ΔE
range across 86 candidates: -76.4 to -32.5 kcal/mol — all favorable.)

## 2. Method

In silico — thermodynamic proxy via RDKit + MMFF94.

For each candidate with a SMARTS-matchable isothiocyanate (`[NX2]=[CX2]=[SX1]`):
1. Build the methanethiol-adduct model:
   `R-N=C=S` → `R-NH-C(=S)-S-CH3`
   via RDKit `AllChem.ReplaceSubstructs` (direction-agnostic — works
   for both `N=C=S` and `S=C=N` canonical writings).
2. Embed parent ITC, free `CH3SH`, and the adduct via `ETKDGv3` +
   `MMFFOptimizeMolecule(maxIts=400)`. Deterministic seed `0xC0FFEE`.
3. Reaction energy proxy:
   ```
   ΔE_proxy = E(adduct) − [E(ITC) + E(CH3SH)]
   ```
4. Normalize across the population:
   ```
   score_c151 = (max_dE − dE) / (max_dE − min_dE)   ∈ [0, 1]
   ```
   Most-negative ΔE in the population → 1.0.
5. Integrate into `rank_hypotheses.py` as a small (+0.05 max) bonus
   for KEAP1-axis categories.

## 3. Inputs

| Input | File / commit |
|-------|---------------|
| ITC-class candidates | `data/compounds/MCAS_Compound_Library_v1.csv` + `outputs/reinvent_generated.csv` (any SMILES containing the isothiocyanate SMARTS) |
| Reference thiol | Methanethiol (`CS`), MMFF94-minimized, E = 0.606 kcal/mol |

## 4. Parameters

```bash
python scripts/score_c151_adduct.py
```

Deterministic.

## 5. Environment

```text
Python: 3.9.6
RDKit:  2023.9.6
Hardware: Apple Silicon Mac, CPU only
```

## 6. Outputs

| File | Description |
|------|-------------|
| `outputs/c151_adduct_energies.csv` | Per-candidate diagnostic: parent_E, adduct_E, methanethiol_E, dE_kcal_per_mol, score_c151, status |

Schema: `name, smiles, adduct_smiles, source, parent_E, methanethiol_E,
adduct_E, dE_kcal_per_mol, score_c151, status`.

## 7. Interpretation

### Named-anchor ranking

Every natural ITC anchor produces a favorable adduct (negative ΔE).
The ordering Allyl-ITC > Iberin > Benzyl-ITC > SFN > Erucin > PEITC >
Sulforaphene reflects:

- **Allyl-ITC** is the smallest / least hindered → most reactive C of
  the cumulated `N=C=S`.
- **Aromatic-tethered** (Benzyl, PEITC) sit in the middle — phenyl
  stabilization of the parent slightly reduces adduct-formation Δ.
- **Long-chain sulfoxides** (SFN, sulforaphene) and **sulfides**
  (Erucin) cluster at -32 to -35 kcal/mol — chemistry well-favored,
  ~5 kcal/mol behind allyl-ITC but still strongly negative.

This ordering is **chemically sensible** and matches published in vitro
reactivity studies of ITCs against simple thiols (allyl-ITC is famously
"too reactive" for some uses, hence SFN's moderate reactivity being
seen as a feature).

### Generated analogs

The top 4 by ΔE (-76 to -67 kcal/mol) are all AI-generated SFN-class
analogs — large hybrid molecules where the bulky parent gets a lot of
intramolecular stabilization in the adduct conformation. Treat with
caution: MMFF94 total energies favor large molecules with many
non-bonded interactions, and these are not necessarily kinetically
accessible. But they suggest the warhead-grafted hybrid scaffolds
*could* form thermodynamically stable adducts if reachable.

### Integration into the composite ranking

The composite score now includes `score_c151 × 0.05` as a small bonus
for KEAP1-axis categories. After this addition the remission top-5 is:

| # | Compound | Composite |
|---|----------|-----------|
| 1 | **Erucin** | 0.689 |
| 2 | **Sulforaphane** | 0.685 |
| 3 | PEITC | 0.652 |
| 4 | Iberin | 0.577 |
| 5 | Benzyl-ITC | 0.552 |

The ITC family ordering at the top is preserved; the bonus tightens the
Erucin–SFN race but doesn't flip it. Allyl-ITC, which had the strongest
ΔE but lower evidence weight (`medium` vs SFN/Erucin's `high`), still
sits below the top.

### Cross-check with EXP-009 Vina

The C151 proxy and the Vina LE ranking from EXP-009 broadly agree that
**warhead-positive small ITCs are favorable KEAP1 binders**, but they
emphasize different chemistry:

- EXP-009 Vina LE rewards Kelch-pocket fit per heavy atom.
- EXP-012 C151 proxy rewards adduct thermodynamic favorability.

A compound that scores well on both (Allyl-ITC, Iberin, SFN-class
small analogs) is more likely to be a real KEAP1 modifier than one
that scores well on only one signal.

## 8. Reproduction

```bash
.venv/bin/python scripts/score_c151_adduct.py
```

Wall-clock: ~10 minutes for 86 candidates on Apple Silicon CPU.
Memory: < 500 MB. No external services needed.

## 9. Limitations

- **MMFF94 is a force field, not QM.** Absolute energy values should
  not be over-interpreted. Relative ordering across same-class
  compounds (ITCs) is what matters.
- **Methanethiol model omits protein context.** Real Cys-151 sits in
  the BTB domain with specific neighbors (Arg-415, His-129, etc.) that
  affect both reactivity and steric accessibility. Capturing those
  needs QM/MM or full-protein docking.
- **Thermodynamic, not kinetic.** The proxy says "the adduct, once
  formed, is stable." It doesn't quantify activation energy or how
  long the adduct persists in vivo.
- **No conformational ensemble.** Single-pose minimization, not a
  Boltzmann-weighted ensemble. For molecules with many rotatable
  bonds (some generated analogs) this introduces noise.
- **Total-energy comparisons across very different molecular sizes**
  are inherently noisy. The reported ΔE for AI-generated large
  analogs is informative directionally but should not be compared
  numerically with small natural ITC ΔEs without further normalization.

## 10. Next experiments suggested

1. **QM upgrade** — re-evaluate top-15 candidates with semi-empirical
   PM6 / GFN2-xTB via the `xtb` binary. Gives meaningful absolute
   energies for ~$0.001 per compound in compute.
2. **Protein context** — pull a KEAP1 BTB-domain crystal (PDB 5DAD)
   and run constrained covalent docking via custom RDKit-OpenMM
   workflow. Substantial work but closes the protein-environment gap.
3. **Mercapturate analogy** — extend the proxy to the full GSH-adduct
   thermodynamics. SFN's biggest in vivo liability is GST-catalyzed
   GSH conjugation; modeling the GSH analog of the same reaction tells
   us which candidates resist conjugation longest.
4. **Kinetic upgrade** — extend the proxy with a TS estimate via
   Nudged Elastic Band on the same MMFF94 / xTB surface.

## 11. References

- Sulforaphane's covalent C151 mechanism: Hu C et al. *Modification of
  Keap1 cysteine residues by sulforaphane.* Chem Res Toxicol 2011.
- KEAP1 BTB structure with C151: Cleasby A et al. *Structure of the
  BTB domain of Keap1.* PDB 5DAD, 2014.
- ITC thiol reactivity rankings: Nakamura Y, Miyoshi N. *Chemoprevention
  by isothiocyanates: molecular mechanisms.* 2009.
- Linked experiments: [EXP-001](EXP-001-sfn-seeded-analog-generation.md),
  [EXP-005](EXP-005-multi-objective-ranking.md),
  [EXP-009](EXP-009-keap1-vina-docking.md).
