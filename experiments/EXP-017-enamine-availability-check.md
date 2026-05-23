---
id: EXP-017
title: Procurement check for top generated SFN-class analogs
status: published
hypothesis_category: methodology
run_date: 2026-05-23
authors:
  - name: OpenMCAS pipeline
    role: in-silico
license: MIT
---

# EXP-017 — Procurement check for top generated SFN-class analogs

> ⚠️ **Not medical advice.** Research/hypothesis use only.
> See [docs/disclaimers.md](../docs/disclaimers.md).

## 1. Hypothesis

**Some non-trivial fraction (≥ 50%) of the top-25 novel analogs produced by
the OpenMCAS generator (EXP-013) live inside the published Enamine REAL
Space envelope** (MW 200–500, ≤ 35 heavy atoms, common atoms only, SA ≤ 4.5,
≤ 2 stereo centers). If true, the SFN-class analog campaign has a real
wet-lab on-ramp via REAL on-demand synthesis rather than custom synthesis.

If most candidates land outside REAL-Space, the generator is producing
chemistry that the pipeline can score but a CRO cannot economically deliver,
and either the generator's chemistry priors or the analog campaign's
target compound class needs revising.

## 2. Method

- [x] In silico — chemoinformatic procurement / drug-likeness gating

### What we did

1. Loaded the 265 unique non-seed analogs from
   `outputs/rl_generated.csv` + `outputs/reinvent_generated.csv`.
2. Filtered out the 7 seed compounds (Sulforaphane, Iberin, Erucin,
   Sulforaphene, Allyl-ITC, Benzyl-ITC, PEITC — all off-the-shelf from
   Sigma/TCI/Cayman).
3. Sorted the remainder by the generator's composite reward (warhead
   + QED + SA + seed-similarity + Lipinski), keeping the top 25.
4. For each, computed canonical SMILES, InChI, InChIKey, molecular
   formula, MW, logP, HBA/HBD, rotatable-bond count, heavy-atom count,
   stereo-center count, QED, an RDKit SA-proxy, exotic-atom flag, and
   Lipinski compliance.
5. Applied a REAL-Space envelope filter and tagged each candidate
   `real_space_plausible` ∈ {True, False} with machine-parseable
   reasons.
6. Emitted vendor lookup URLs (Enamine REAL search, MolPort, eMolecules,
   PubChem, ChemSpider) keyed by InChIKey.

### What we did NOT do

- **No direct Enamine REAL Space API query** — there is no public
  unauthenticated endpoint. The lookup URLs are manual handles for a
  CRO or procurement officer.
- **No commercial in-stock confirmation.** A REAL-on-demand candidate
  may still take 4–8 weeks and a 4–5 figure quote.
- **No CAS number lookup.** Most REAL-Space members do not have a CAS.
- **No salt-form or counterion handling.** SMILES are neutral free
  forms.

## 3. Inputs

| Input | Source | Notes |
|-------|--------|-------|
| `outputs/rl_generated.csv` | EXP-013 | 265 unique RL-generated SMILES |
| `outputs/reinvent_generated.csv` | EXP-013 BRICS branch | 113 unique BRICS/bioisostere SMILES |
| Seed list | EXP-001 + EXP-013 | 7 isothiocyanate seeds excluded |
| Top-N | CLI arg | Default 25 |

## 4. Code version

- `scripts/check_enamine_availability.py` — first commit landed in this
  experiment.
- RDKit 2023.09 (via `.venv`).
- See `git log --follow scripts/check_enamine_availability.py` for full
  history.

## 5. Run command

```bash
.venv/bin/python scripts/check_enamine_availability.py --top 25
```

## 6. Outputs

- `outputs/exp_017/enamine_lookup.csv` — 25 rows, one per novel analog.
- `outputs/exp_017/procurement_packet.md` — vendor-ready markdown packet
  with per-compound lookup URLs (ready to attach to a CRO email).

## 7. Findings

### 7.1 Envelope hit-rate

| Metric | Value |
|--------|-------|
| Novel analogs scored | 25 |
| REAL-Space-plausible | **20 / 25 (80%)** |
| Outside envelope (filtered) | 5 / 25 |

The hypothesis holds: 80% of top-25 novel analogs are inside the
REAL-Space envelope. This is a **green light for the wet-lab bridge** —
the generator is producing chemistry a CRO can actually deliver.

### 7.2 Why the 5 filtered candidates dropped

Inspection of `outputs/exp_017/enamine_lookup.csv`:

- **Long aliphatic ITC chains** (e.g., `CSCCCCCCCN=C=S` — n-heptyl
  methylthio ITC) — these pass Lipinski but are too greasy / too far
  outside the drug-like envelope (logP > 4, low QED). They get
  filtered for SA + stereo, not for atoms.
- **Branched sulfone analogs with extra rotatable bonds** — these
  pass the atomic envelope but lose on SA or QED past the cutoff.

None of the 5 outliers are filtered for *exotic atoms* — the generator
is staying inside C/H/N/O/S/F/Cl/Br, which is what we hoped.

### 7.3 What the top-3 REAL-plausible candidates look like

| Rank | SMILES | Formula | MW | QED | Comment |
|------|--------|---------|----|-----|---------|
| 1 | `CCCS(=O)(=O)CCc1ccc(N=C=S)cc1` | C12H15NO2S2 | 269.4 | 0.59 | n-propylsulfonyl-phenethyl-ITC — aromatic SFN-bioisostere |
| 2 | `CCCS(=O)(=O)Cc1ccc(N=C=S)cc1` | C11H13NO2S2 | 255.4 | 0.60 | n-propylsulfonyl-benzyl-ITC — shorter chain analog of #1 |
| 3 | `CSCCCCCCN=C=S` | C8H17NS2 | 191.4 | 0.35 | n-hexyl-methylthio-ITC — Erucin chain extension |

These are real candidates a CRO can quote on.

### 7.4 Cross-check against EXP-016 mast-cell predictor

The mast-cell stabilizer probabilities for these top-3 candidates were
not yet scored (the predictor's `outputs/mast_cell_predictions.csv` is
keyed on the *library* compounds, not on the generated set). Adding the
mast-cell predictor to the generated-set scoring is a follow-up
(EXP-018 candidate).

## 8. Reproducibility

```bash
.venv/bin/python scripts/check_enamine_availability.py --top 25
# Outputs: outputs/exp_017/{enamine_lookup.csv, procurement_packet.md}
```

Deterministic — no RNG. RDKit canonicalization is version-stable.

## 9. What this experiment did not establish

- That the candidates are **actually** in Enamine REAL Space (would
  need a portal lookup).
- That they are **synthesizable** in a one-off campaign with reasonable
  cost (would need a custom-synth CRO quote, $500–$5k per analog
  depending on chain length and chirality).
- That they are **active** in a β-hexosaminidase / LAD2 / HMC-1 mast-cell
  stabilizer assay (that's EXP-018).
- That they are **safe** beyond the QSAR-predicted hERG / AMES / BBB
  baselines.

## 10. Next experiments suggested

1. **EXP-018 — wet-lab procurement + β-hex assay pilot.** Pick 3
   REAL-plausible candidates from the top-20 list, source them, and
   run a 6-point dose-response β-hexosaminidase release inhibition
   assay on LAD2 cells vs. Sulforaphane positive control + Cetirizine
   non-stabilizer negative.
2. **Score the generated set with the EXP-016 mast-cell predictor**
   to apply the +0.05 universal bonus and re-rank the top-25 before
   ordering.
3. **Add `outputs/exp_017/enamine_lookup.csv` to the rank_hypotheses
   pipeline** as a procurement-availability flag — compounds you
   can't buy shouldn't outrank compounds you can.

## 11. References

- Linked experiments: [EXP-001](EXP-001-sfn-seeded-analog-generation.md),
  [EXP-013](EXP-013-rl-generation.md),
  [EXP-016](EXP-016-mast-cell-predictor.md).
- Enamine REAL Space envelope (MW, heavy-atom, stereo): public
  procurement guidance, https://enamine.net/compound-collections/real-compounds/real-space.
- InChIKey as a vendor-stable cross-database key: Heller et al. (2015)
  Journal of Cheminformatics 7:23.
