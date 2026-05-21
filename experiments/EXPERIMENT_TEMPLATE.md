---
id: EXP-NNN
title: Short imperative title
status: draft | running | published | retracted
hypothesis_category: rescue | maintenance | remission | injury_mechanism | trigger | methodology
run_date: YYYY-MM-DD
authors:
  - name: Your name or handle
    role: e.g. contributor, academic-collaborator, patient-reporter
license: MIT
---

# {{ Title }}

> ⚠️ **Not medical advice.** Research/hypothesis use only.
> See [docs/disclaimers.md](../docs/disclaimers.md).

## 1. Hypothesis

One paragraph. State plainly what you believed before running the experiment.
What MCAS / MCAD subgroup, what compound or compound class, what biological
effect, what direction.

A good hypothesis is *falsifiable*: it should be possible to describe a result
that would refute it.

## 2. Method

What kind of test? Pick one (or list both if combined):
- [ ] In silico — ligand-based (similarity, pharmacophore)
- [ ] In silico — structure-based (docking, MD, FEP)
- [ ] In silico — generative (REINVENT, BRICS, fragment, transformer)
- [ ] In silico — QSAR / ADMET prediction
- [ ] Wet-lab — cell line (LAD2, HMC-1, primary, iPSC-derived)
- [ ] Wet-lab — animal model
- [ ] Clinical — case report / case series
- [ ] Observational — patient-reported

Describe the actual procedure in enough detail that someone else can repeat it.

## 3. Inputs

| Input | File / version |
|-------|----------------|
| Source library | `data/compounds/MCAS_Compound_Library_v1.csv` @ commit `<hash>` |
| Generated set  | `outputs/reinvent_generated.csv` @ commit `<hash>` |
| Reference set  | (e.g. KEAP1 reference ligands defined in `scripts/score_against_targets.py`) |
| External data  | (PyTDC tasks, UniProt IDs, ChEMBL assays — name + version) |

## 4. Parameters

All command-line flags / config values used. Quote the actual command:

```bash
python scripts/<name>.py --flag value
```

If you used a notebook, name the notebook and which kernel / Python version.

## 5. Environment

```text
Python: 3.x.x
RDKit:  yyyy.mm.x
Hardware: e.g. Apple Silicon M1, 8 GB RAM, no GPU
OS:     macOS 14.x
```

## 6. Outputs

| File | Description |
|------|-------------|
| `outputs/<file>.csv` | what it contains |

For each output, state the schema (column names + meaning).

## 7. Interpretation

What did the result actually tell you?
- Effect size? Direction? Magnitude?
- Did the hypothesis survive or get refuted?
- What surprised you?
- What's the most important caveat?

Be honest. Null results are publishable here.

## 8. Reproduction

```bash
git clone https://github.com/mrdulasolutions/MCAS.Opensource.git
cd MCAS.Opensource
git checkout <commit-hash>
# follow Method section
```

Expected wall-clock time + memory.

## 9. Limitations

What this experiment **cannot** answer. Honest.

## 10. Next experiments suggested

Numbered list. Each should link to a follow-up `EXP-` doc when it's written.

## 11. References

- Citations (author / year + URL or DOI).
- Linked compounds in `data/compounds/seeds.json` (by name).
- Linked injury mechanisms or triggers (by row).
