---
id: EXP-005
title: Multi-objective ranking → rescue / maintenance / remission top-10s
status: published
hypothesis_category: methodology
run_date: 2026-05-21
authors:
  - name: OpenMCAS contributors
    role: maintainer
license: MIT
---

# Multi-objective ranking → rescue / maintenance / remission top-10s

> ⚠️ **Not medical advice.** Research/hypothesis use only.

## 1. Hypothesis

A composite ranking that combines (a) human evidence weight, (b) per-category
target similarity from EXP-002, (c) covalent-warhead score from EXP-003, (d)
QSAR safety from EXP-004, and (e) drug-likeness for generated analogs will
reproduce known MCAS first-line therapy at the top of the **rescue** list and
surface upstream Nrf2/KEAP1 candidates at the top of the **remission** list —
without manual cherry-picking.

Falsifiable: if the ranking puts ranitidine above cetirizine for rescue, or
omalizumab above sulforaphane for remission, the weighting is wrong.

## 2. Method

In silico — composite scoring.

For each compound:

```
composite =
  0.30 · evidence_level             # high=1.0, medium=0.6, low=0.3
+ 0.35 · weighted_target_similarity # per-category target mix from EXP-002
+ 0.10 · QED                        # generated analogs only
+ 0.10 · warhead_score              # KEAP1 axis only (EXP-003)
+ 0.15 · safety_bonus               # 0.5·(1-hERG) + 0.5·(1-AMES) from EXP-004
+  ε · BBB_context                  # +/- based on category needs
−  ε · keap1_lookalike_no_warhead   # explicit penalty
```

Per-category target weights:

| Category | Target weights |
|---|---|
| rescue | HRH1 0.40, HRH2 0.20, CYSLTR1 0.20, MRGPRX2 0.20 |
| maintenance | CYSLTR1 0.30, HRH1 0.15, BTK 0.15, MRGPRX2 0.20, KEAP1 0.20 |
| remission | MRGPRX2 0.30, KIT 0.30, KEAP1 0.30, GLP1R 0.10 |

## 3. Inputs

| Input | File / commit |
|-------|--------------|
| Library | `data/compounds/MCAS_Compound_Library_v1.csv` @ `01b81de` |
| Generated | `outputs/reinvent_generated.csv` (EXP-001 output) |
| Target scores | `outputs/docking_*.csv` (EXP-002 output) |
| Warhead scores | `outputs/warhead_scores.csv` (EXP-003 output) |
| QSAR | `outputs/qsar_predictions.csv` (EXP-004 output) |

## 4. Parameters

```bash
python scripts/rank_hypotheses.py
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
| `outputs/ranked_rescue.csv` | 14 compounds |
| `outputs/ranked_maintenance.csv` | 25 compounds |
| `outputs/ranked_remission.csv` | 99 compounds (library + SFN-class analogs) |
| `outputs/ranked_all.csv` | 138 rows |

The hypothesis docs (`hypotheses/rescue.md`, `maintenance.md`, `remission.md`)
are auto-updated with the latest top-10 tables by the same script.

## 7. Interpretation

### Rescue top 5
| # | Name | Composite | What it is |
|---|---|---|---|
| 1 | Fexofenadine | 0.540 | H1 antihistamine |
| 2 | Cetirizine | 0.539 | H1 antihistamine |
| 3 | Diphenhydramine | 0.534 | H1 antihistamine |
| 4 | Hydroxyzine | 0.532 | H1 antihistamine |
| 5 | Loratadine | 0.523 | H1 antihistamine |

The H1 backbone is exactly the published first-line MCAS rescue regimen.

### Maintenance top 5
| # | Name | Composite |
|---|---|---|
| 1 | Curcumin | 0.628 |
| 2 | Rosmarinic acid | 0.560 |
| 3 | Thymoquinone | 0.559 |
| 4 | Resveratrol | 0.487 |
| 5 | Luteolin | 0.479 |

Note: curcumin jumped to #1 only after EXP-003 (its Michael-acceptor enone
was detected as a real warhead). Without the warhead bonus, quercetin/luteolin
would dominate purely on MRGPRX2 similarity.

### Remission top 5
| # | Name | Composite | hERG | BBB |
|---|---|---|---|---|
| 1 | **Sulforaphane** | 0.628 | 0.24 | 0.92 |
| 2 | Phenethyl-ITC | 0.589 | 0.70 | 0.95 |
| 3 | Erucin | 0.490 | 0.28 | 0.69 |
| 4 | Benzyl-ITC | 0.483 | 0.69 | 0.95 |
| 5 | Masitinib | 0.472 | 0.82 | 0.73 |

Sulforaphane #1 — and the QSAR safety bonus is doing real work: PEITC has
higher KEAP1 similarity (also 1.00) but loses to SFN on hERG + AMES.

## 8. Reproduction

```bash
.venv/bin/python scripts/rank_hypotheses.py
```

Wall-clock: <2 seconds. Memory: <300 MB.

## 9. Limitations

- Weights are author-chosen, not learned. A more principled approach would
  fit weights against known MCAS clinical-response data — that data is sparse.
- The composite is **not** a predicted clinical outcome — it is a triage
  signal for wet-lab and clinician review.
- No prediction of side effects beyond hERG / AMES. No drug-drug interaction
  modeling.

## 10. Next experiments suggested

1. Sensitivity analysis — sweep the 6 weights ±50% and check ranking stability.
2. Train weights against MCAS case-series response data (if/when collected).
3. Add multi-target ("polypharmacology") bonus — reward compounds that hit
   ≥2 MCAS-relevant targets above 0.5.
4. Add selectivity penalty — penalize compounds that score high against
   hERG-, kinome-, or NHR-panel proxies.

## 11. References

- Linked experiments: EXP-001, EXP-002, EXP-003, EXP-004.
- MCAS consensus criteria: Afrin LB et al. *Diagnosis, treatment, and management of MCAS.* 2020.
