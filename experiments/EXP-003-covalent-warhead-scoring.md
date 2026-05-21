---
id: EXP-003
title: Covalent-warhead SMARTS scoring + KEAP1 pharmacophore filter
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

# Covalent-warhead SMARTS scoring + KEAP1 pharmacophore filter

> ⚠️ **Not medical advice.** Research/hypothesis use only.

## 1. Hypothesis

Pure Tanimoto similarity to known KEAP1 binders is *insufficient* — KEAP1
activation is mechanistically driven by **cysteine-reactive warheads** (the
SFN isothiocyanate, the bardoxolone cyanoenone, the curcumin Michael acceptor).
A compound that looks like SFN in fingerprint space but lacks the warhead
cannot covalently modify KEAP1.

Falsifiable claim: a SMARTS-based warhead detector should flag SFN, curcumin,
bardoxolone, all natural ITCs, and quinones — and should *not* flag the
generated `C#N` nitrile bioisosteres of SFN (which lose the warhead).

## 2. Method

In silico — pharmacophore / SMARTS pattern matching.

Define 13 SMARTS patterns covering the major cysteine-reactive warhead classes:

| Class | SMARTS |
|---|---|
| Isothiocyanate | `[NX2]=[CX2]=[SX1]` |
| Thiocyanate | `[SX2][CX2]#[NX1]` |
| Michael acceptor enone | `[CX3]=[CX3][CX3]=[OX1]` |
| Cyanoenone | `[CX3]=[CX3]([CX2]#[NX1])` |
| Acrylamide | `[CX3]=[CX3][CX3](=[OX1])[NX3]` |
| Vinyl sulfone | `[CX3]=[CX3][SX4](=[OX1])(=[OX1])` |
| α-haloketone | `[CX3](=[OX1])[CX4][F,Cl,Br,I]` |
| Epoxide / aziridine | `[CX4]1[OX2]1` / `[CX4]1[NX3]1` |
| Para / ortho quinone | `O=C1C=CC(=O)C=C1` / `O=C1C=CC=CC1=O` |
| α,β-unsat ester / lactone | various |

Plus a KEAP1 pharmacophore filter:
- MW 100–500
- cLogP ≤ 5
- 6 ≤ heavy atoms ≤ 35

Per compound: `warhead_score = (1.0 if any_warhead else 0.0) × (1.0 if
pharmacophore_pass else 0.5)`.

## 3. Inputs

| Input | File / version |
|-------|----------------|
| Compounds | library + generated (157 unique SMILES) @ commit `01b81de` |

## 4. Parameters

```bash
python scripts/score_warheads.py
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
| `outputs/warhead_scores.csv` | 157 rows |

Schema: `name, smiles, source, category, has_warhead, warheads, n_warheads,
keap1_pharmacophore_pass, warhead_score`.

## 7. Interpretation

- **101 of 157 compounds** carry at least one warhead.
- **121 pass** the KEAP1 pharmacophore filter.
- **79 do both** (the actually viable KEAP1-class candidates).

Sanity checks all pass:
- SFN → isothiocyanate ✓
- Curcumin → michael_enone ✓
- Thymoquinone → michael_enone + para_quinone ✓
- Ascorbic acid → michael_enone + α,β-unsat ester + lactone ✓
- Bardoxolone (in reference set) → cyanoenone ✓

The ranking script in EXP-005 applies a **penalty of −0.08** when KEAP1
Tanimoto > 0.4 but no warhead is present, correctly demoting structural
lookalikes that can't covalently bind.

## 8. Reproduction

```bash
.venv/bin/python scripts/score_warheads.py
```

Wall-clock: <2 seconds. Memory: <300 MB.

## 9. Limitations

- SMARTS patterns are pattern-only — they don't model the actual reactivity
  rate (an acrylamide on a soft Michael acceptor reacts faster than a
  hindered one).
- The KEAP1 pharmacophore is a generic Lipinski-like filter, not a true
  pocket-shape match.
- A compound can have a warhead and still not reach Cys-151 of KEAP1 in vivo
  (PK / binding orientation). Wet-lab validation required.

## 10. Next experiments suggested

1. EXP-005 — integrate into the multi-objective ranking.
2. Future — reactivity ranking via Pearson hardness / electrophilicity
   indices computed from xTB or DFT.
3. Future — covalent docking with CovDock or GOLD-Covalent (KEAP1 Cys-151).

## 11. References

- Singh AK et al. *Identification of KEAP1-Nrf2 PPI inhibitors.* 2019.
- Hu L et al. *Discovery of covalent inhibitors of KEAP1 via warhead screening.* 2016.
