---
id: EXP-001
title: SFN-class analog generation across 7 natural isothiocyanate seeds
status: published
hypothesis_category: remission
run_date: 2026-05-21
authors:
  - name: MR Dula Medical
    role: provider
    affiliation: "DBA of MR Dula Enterprise, LLC; Raleigh, NC, USA"
  - name: OpenMCAS contributors
    role: maintainer
license: MIT
---

# SFN-class analog generation across 7 natural isothiocyanate seeds

> ⚠️ **Not medical advice.** Research/hypothesis use only.
> See [docs/disclaimers.md](../docs/disclaimers.md).

## 1. Hypothesis

The sulforaphane (SFN) scaffold is the strongest natural candidate for **upstream
remission** of MCAS via covalent KEAP1 modification → Nrf2 activation. SFN itself
is one of many natural isothiocyanates (ITCs) with the same warhead; the chemical
space immediately around these 7 seeds should contain analogs with:
- the same covalent KEAP1-binding head,
- better drug-likeness (QED), and
- improved metabolic stability vs. SFN (which is rapidly conjugated by GST).

Falsifiable claim: at least some bioisosteric or hybrid analogs of the 7 ITC seeds
should pass Lipinski + carry a confirmed cysteine-reactive warhead.

## 2. Method

In silico — generative.

Three operators applied to each seed:
1. **Bioisosteric enumeration** — sulfoxide ↔ sulfone ↔ sulfide, methyl ↔ ethyl,
   chain-length ±1 CH₂, isothiocyanate ↔ nitrile ↔ thiocyanate, phenyl tethers.
2. **BRICS recombination** — fragment each seed via RDKit BRICS, recombine with
   fragments from every other small molecule in the master library.
3. **Warhead grafting** — append the SFN sulfoxide-isothiocyanate tail onto
   aromatic positions of library scaffolds.

Scoring per candidate:
- Tanimoto similarity to the nearest ITC seed (Morgan r=2, 1024 bits)
- QED (drug-likeness)
- Lipinski (hard filter)
- SA proxy

Composite: `0.4·QED + 0.4·max_similarity + 0.2·(1 − SA/10)`, gated by Lipinski.

## 3. Inputs

| Input | File / version |
|-------|----------------|
| Seeds | `scripts/generate_sfn_analogs.py` (in-code: SFN, iberin, erucin, sulforaphene, allyl-ITC, benzyl-ITC, phenethyl-ITC) |
| Library scaffolds | `data/compounds/MCAS_Compound_Library_v1.csv` @ commit `01b81de` |

## 4. Parameters

```bash
python scripts/generate_sfn_analogs.py
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
| `outputs/reinvent_generated.csv` | 113 ranked candidate analogs |

Schema: `smiles, tanimoto_to_SFN, best_seed_match, qed, sa_score_proxy,
lipinski_pass, mw, logp, composite_score, seed, source`.

## 7. Interpretation

- **113 unique candidates** across 7 seeds (vs. 80 from SFN-only in an earlier
  iteration), confirming that seeding with the full ITC family materially
  broadens the explored chemical space.
- Top-ranked novel scaffolds include phenyl-tethered sulfoxide-ITCs
  (`CS(=O)CCc1ccc(N=C=S)cc1`), the C2=C3-unsaturated sulforaphene homolog
  family, and an **aspirin + SFN warhead hybrid** (`CC(=O)Oc1cc(CCS(=O)CCCN=C=S)ccc1C(=O)O`)
  that is a real cross-axis hypothesis (COX + KEAP1).
- The seeds themselves (Tanimoto = 1.0 to themselves) are correctly retained
  for downstream scoring continuity.

## 8. Reproduction

```bash
git clone https://github.com/mrdulasolutions/MCAS.Opensource.git
cd MCAS.Opensource
git checkout 01b81de
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python scripts/build_compound_library.py
.venv/bin/python scripts/generate_sfn_analogs.py
```

Wall-clock: <30 seconds. Memory: <500 MB.

## 9. Limitations

- This is **not** REINVENT 4 RL — it's deterministic BRICS + bioisostere
  enumeration. REINVENT's policy gradient would explore more diverse space.
- The SA proxy is a crude heuristic, not the published Ertl SAS.
- No prediction of actual KEAP1 binding affinity — that comes in EXP-002 +
  EXP-003.

## 10. Next experiments suggested

1. EXP-002 — score every candidate vs. KEAP1 reference ligands.
2. EXP-003 — flag candidates with cysteine-reactive warheads.
3. Future — REINVENT 4 on Colab GPU seeded on top-10 of this run.
4. Future — Vina/smina docking of top-50 into KEAP1 Kelch domain (PDB 4L7B).

## 11. References

- Fahey JW, Wade KL, et al. *Stabilized sulforaphane for clinical use.* 2015.
- Houghton CA. *Sulforaphane and other nutrigenomic Nrf2 activators.* 2013.
- Yang G et al. *Sulforaphane inhibits mast cell activation.* 2017.
