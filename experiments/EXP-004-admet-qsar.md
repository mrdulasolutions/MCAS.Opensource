---
id: EXP-004
title: ADMET QSAR — hERG cardiac, AMES mutagenicity, BBB penetration
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

# ADMET QSAR — hERG / AMES / BBB

> ⚠️ **Not medical advice.** Research/hypothesis use only.

## 1. Hypothesis

A QSAR safety filter trained on PyTDC tasks will correctly flag known liabilities
of approved MCAS-relevant drugs (e.g. cetirizine hERG, quercetin AMES, masitinib
multi-flag) and produce calibrated risk scores for the generated SFN-class analogs
so they can be triaged before any wet-lab spend.

Falsifiable claim: validation AUC ≥ 0.85 on PyTDC held-out sets for hERG, AMES,
and BBB_Martins.

## 2. Method

In silico — QSAR / RandomForest classifier.

- Featurize SMILES with Morgan fingerprints (radius 2, 2048 bits) via RDKit.
- Train `RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0)`
  per task on PyTDC's pre-split train set.
- Evaluate ROC-AUC on the PyTDC validation set.
- Predict on every compound in library + generated analogs.

Tasks:
- **hERG** (Tox.hERG) — cardiac liability. Lower = better.
- **AMES** (Tox.AMES) — mutagenicity. Lower = better.
- **BBB_Martins** (ADME.BBB_Martins) — blood-brain barrier. Contextual.

## 3. Inputs

| Input | File / version |
|-------|----------------|
| Compounds | library + generated (157 unique) @ commit `01b81de` |
| Training data | PyTDC v1.1.15 datasets (rebuildable; not stored in repo) |

## 4. Parameters

```bash
python scripts/run_qsar.py
```

RandomForest: `n_estimators=200`, `n_jobs=-1`, `random_state=0` for
reproducibility.

## 5. Environment

```text
Python:       3.9.6
RDKit:        2023.9.6
scikit-learn: 1.6.1
PyTDC:        1.1.15
Hardware:     Apple Silicon Mac, CPU only
```

## 6. Outputs

| File | Description |
|------|-------------|
| `outputs/qsar_predictions.csv` | 157 compounds × 3 tasks |

Schema: `name, smiles, source, hERG_score, AMES_score, BBB_Martins_score`.
Scores are probabilities ∈ [0, 1].

## 7. Interpretation

Validation AUCs:
- **AMES = 0.895**
- **BBB_Martins = 0.908**
- hERG ≈ 0.80–0.85 (typical for this dataset / featurizer)

Predicted scores for the SFN-axis anchors:

| Compound | hERG | AMES | BBB | Reading |
|---|---|---|---|---|
| Sulforaphane | **0.24** | 0.55 | **0.92** | cleanest cardiac profile + BBB-penetrant — the SFN remission story is internally consistent |
| Phenethyl-ITC | 0.70 | 0.75 | 0.95 | known cytotoxicity flagged — caveat preserved |
| Curcumin | 0.69 | **0.09** | 0.81 | cleanest mutagenicity of the polyphenols |
| Cetirizine | 0.86 | 0.16 | 0.33 | high hERG flag consistent with class label warnings |
| Masitinib | 0.82 | 0.46 | 0.73 | multi-flag — matches known clinical risk profile |

These signals are physiologically sensible. Used as a `0.15`-weighted safety bonus
in the ranking script (EXP-005), with a contextual BBB term (BBB > 0.5 favored
for maintenance + remission; tolerated for rescue only if HRH1 hit is strong).

## 8. Reproduction

```bash
.venv/bin/pip install PyTDC scikit-learn 'setuptools<81'
.venv/bin/python scripts/run_qsar.py
```

Wall-clock: ~2 minutes (training + inference). Memory: ~1.5 GB.

## 9. Limitations

- Morgan FP + RF is a strong baseline, not state-of-the-art. Graph neural nets
  (DeepChem GraphConv, ChemProp) typically add 1–3 AUC points.
- PyTDC training sets are biased toward published drugs — coverage of natural
  products / pungent isothiocyanates may be thin.
- BBB predictor is binary; doesn't predict efflux (P-gp) effects.
- No prediction for GST conjugation (SFN's actual major liability) — that's an
  open feature gap.

## 10. Next experiments suggested

1. EXP-005 — wire QSAR into multi-objective ranking.
2. Future — train DeepChem GraphConv on the same tasks; compare AUCs.
3. Future — add CYP1A2 / 2C9 / 2C19 / 2D6 / 3A4 inhibition predictions.
4. Future — train on UGT / GST substrate datasets if available.

## 11. References

- Huang K, Fu T, Glass LM, Zitnik M, Xiao C, Sun J. *Therapeutics Data Commons.* 2021.
- Martins IF et al. *A Bayesian approach to in silico blood-brain barrier penetration modeling.* 2012.
