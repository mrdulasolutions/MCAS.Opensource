---
id: EXP-019
title: Cannabinoid + terpene library expansion and CB2-axis scoring
status: published
hypothesis_category: maintenance
run_date: 2026-05-23
authors:
  - name: OpenMCAS pipeline
    role: in-silico
license: MIT
---

# EXP-019 — Cannabinoid + terpene library expansion and CB2-axis scoring

> ⚠️ **Not medical advice.** Research/hypothesis use only.
> See [docs/disclaimers.md](../docs/disclaimers.md).

## 1. Hypothesis

**The OpenMCAS composite, extended to cover the cannabinoid + terpene
chemical space and the CB2 (CNR2) receptor, will rank at least one
member of these classes inside the maintenance top-10.** The strongest
prior candidates: **palmitoylethanolamide (PEA)** — high-evidence
ALIAmide mast-cell stabilizer with ~30 clinical trials — and
**β-caryophyllene** — the only dietary FDA-GRAS selective CB2 agonist.

If neither lands in the top-10 *and* the audits stay clean, that means
the composite is over-weighting the SFN/Nrf2 axis at the expense of
real CB2-axis pharmacology, and the weights need revisiting.

## 2. Method

- [x] In silico — library extension + ligand-based screening +
  composite re-ranking

### What we did

1. **Library extension.** Added 24 compounds to `data/compounds/seeds.json`,
   verified PubChem CIDs, RDKit-canonicalized SMILES via PUG-REST fetch:
   - **Phytocannabinoids (8):** CBD, CBG, CBC, CBN, Δ9-THC, Δ8-THC, THCV, CBDV.
   - **Endocannabinoid-likes (4):** PEA, OEA, anandamide (AEA), 2-AG.
   - **Terpenes (12):** β-caryophyllene, α-humulene, α-pinene, β-pinene,
     D-limonene, linalool, β-myrcene, eucalyptol, terpinolene,
     geraniol, α-bisabolol, nerolidol.
2. **Target extension.** Added **CNR2 (CB2)** as the 9th MCAS target in
   `data/targets/MCAS_Targets.csv`. Reference ligand set in
   `scripts/score_against_targets.py`:
   β-caryophyllene, HU-308, JWH-133, AM-1241, CBD, Δ9-THC.
3. **Target weighting.** Inserted CNR2 into `rank_hypotheses.py`
   per-category target weights:
   - maintenance: `CYSLTR1 0.25 + HRH1 0.15 + BTK 0.15 + MRGPRX2 0.15 + KEAP1 0.15 + CNR2 0.15`
   - remission:   `MRGPRX2 0.25 + KIT 0.25 + KEAP1 0.30 + GLP1R 0.10 + CNR2 0.10`
   - rescue:      unchanged (CB2 not relevant to acute H1/cromone rescue).
4. **Reran:** `build_compound_library.py` → `validate_smiles.py` →
   `score_warheads.py` → `score_against_targets.py` (9 targets now) →
   `run_qsar.py` → `train_mast_cell_predictor.py` (retrains + rescore) →
   `rank_hypotheses.py` → `benchmark_known_actives.py` →
   `benchmark_negative_controls.py`.

### What we did NOT do

- **Did not add CB1 (CNR1)** — CB1 agonism brings intoxication and
  the CB1 target list overlaps heavily with the cannabinoids being
  scored, which would artificially inflate self-scores. CB2 is the
  more mast-cell-relevant receptor.
- **Did not penalize the "bidirectional" stabilizer-vs-trigger
  reality** in the composite (linalool, limonene, etc. are both
  stabilizers in vitro AND common MCAS VOC triggers). The
  bidirectionality is **cross-referenced** per §7.4 in this report
  and surfaced via the `trigger_overlap` field on each affected
  compound in seeds.json, but it is not a numeric penalty term.
  That choice avoids baking a contested weight into the composite —
  the same molecule can be a stabilizer for one patient and a
  trigger for another at the same dose, and route-of-exposure
  matters (oral β-caryophyllene capsule ≠ inhaled lavender).

## 3. Inputs

| Input | Source | Notes |
|-------|--------|-------|
| `data/compounds/seeds.json` | EXP-019 commit | 78 compounds (was 54) |
| `data/targets/MCAS_Targets.csv` | EXP-019 commit | 16 entries (CNR2 added) |
| `scripts/score_against_targets.py` | EXP-019 commit | CNR2 ref set added (6 ligands) |
| `scripts/rank_hypotheses.py` | EXP-019 commit | CATEGORY_TARGETS rebalanced for CNR2 |

## 4. Code version

Commit hash: filled by `git log` on the EXP-019 merge.

## 5. Run command

```bash
.venv/bin/python scripts/build_compound_library.py
.venv/bin/python scripts/validate_smiles.py
.venv/bin/python scripts/score_warheads.py
.venv/bin/python scripts/score_against_targets.py
.venv/bin/python scripts/run_qsar.py
.venv/bin/python scripts/train_mast_cell_predictor.py
.venv/bin/python scripts/rank_hypotheses.py
.venv/bin/python scripts/benchmark_known_actives.py
.venv/bin/python scripts/benchmark_negative_controls.py
```

## 6. Outputs

- `data/compounds/MCAS_Compound_Library_v1.csv` — 78 rows (was 54).
- `outputs/docking_CNR2.csv` — new, 178 unique molecules scored.
- `outputs/ranked_maintenance.csv` — 49 entries (was 25).
- `outputs/mast_cell_predictions.csv` — refreshed with the 24 new
  compounds scored.
- `outputs/benchmark_known_actives.csv` — refreshed (still 21 entries).
- `outputs/benchmark_negative_controls.csv` — refreshed.

## 7. Findings

### 7.1 Where the new compounds landed in maintenance (n=49)

| Rank | Compound | Composite | CNR2 sim | Mast-cell P | Evidence |
|------|----------|-----------|----------|-------------|----------|
| **9** | **Palmitoylethanolamide** | **0.504** | 0.14 | 0.21 | **high** |
| 17 | Delta-9-THC | 0.402 | 1.00 | 0.47 | medium |
| 18 | Cannabidiol | 0.401 | 1.00 | 0.46 | medium |
| 24 | Linalool | 0.373 | 0.23 | 0.22 | medium |
| 25 | β-Caryophyllene | 0.372 | 0.24 | 0.36 | medium |
| 26 | α-Bisabolol | 0.368 | 0.26 | 0.36 | medium |
| 27 | D-Limonene | 0.363 | 0.30 | 0.19 | medium |
| 30 | Eucalyptol | 0.355 | 0.15 | 0.27 | medium |
| 32 | Delta-8-THC | 0.312 | 1.00 | 0.47 | low |
| 35–37 | THCV, CBDV, CBC | 0.288–0.283 | 0.34–0.86 | 0.29–0.38 | low |
| 41–48 | CBG, AEA, β-myrcene, CBN, α-pinene, 2-AG, terpinolene | 0.262–0.273 | — | — | low |

**H1 confirmed: PEA lands at #9 maintenance** — within top-10 — driven
by its "high" evidence_level (the ALIAmide clinical literature) plus a
moderate mast-cell predictor score. None of the others crack top-10,
which is the right answer given their evidence base:

- Cannabinoids carry "medium" evidence at best (mostly in-vitro on
  LAD2/HMC-1 with limited human MCAS data).
- Terpenes carry "medium" to "low" evidence; most clinical signals are
  from non-MCAS adjacencies (asthma, eczema, anxiety).
- The mast-cell predictor (CV AUC 0.916) under-scores PEA itself
  (0.21) — the same dataset-coverage bias documented in EXP-016 §7.3
  for ketotifen (0.081) and quercetin (0.182). PEA is a lipid
  fatty-acid amide; the training set is biased toward conventional
  small molecules. The composite still ranks PEA #9 because the
  evidence + target similarity terms compensate.

### 7.2 CB2 (CNR2) reference-ligand correlations

`outputs/docking_CNR2.csv` top-10 by Tanimoto similarity to the CB2
reference set:

| Compound | Max sim | Closest ref |
|----------|---------|-------------|
| Cannabidiol | 1.00 | Cannabidiol (self — in ref set) |
| Delta-9-THC | 1.00 | Δ9-THC (self — in ref set) |
| Beta-caryophyllene | 1.00 | β-Caryophyllene (self) |
| Cannabidivarin | 0.86 | Cannabidiol |
| Tetrahydrocannabivarin | 0.86 | Δ9-THC |
| Delta-8-THC | 0.69 | Δ9-THC |
| Cannabinol | 0.41 | Δ9-THC |
| Cannabichromene | 0.38 | Cannabidiol |
| Cannabigerol | 0.34 | Cannabidiol |
| α-Bisabolol | 0.26 | β-Caryophyllene |

Self-similarity at 1.0 for in-ref-set compounds is the expected
behavior of the Tanimoto screen and is the same artifact we see for
Cetirizine vs HRH1, Sulforaphane vs KEAP1, etc.

### 7.3 Audits still hold

| Metric | Before EXP-019 | After EXP-019 |
|--------|---------------|---------------|
| Known-actives recovery@20 (overall) | 95.2% (20/21) | **95.2% (20/21)** |
| Known-actives recovery@20 (rescue) | 100% (11/11) | **100% (11/11)** |
| Known-actives recovery@20 (maintenance) | 100% (9/9) | **100% (9/9)** |
| Negative-control precision@10 (all 3 cats) | 100% | **100%** |

The maintenance ranking denominator grew from 25 → 49, but every
known active still lands in the top-20 of its category. The negative
controls still fail to enter the top-10 of any category. The
CB2-axis additions did not corrupt the composite's ability to
distinguish real mast-cell drugs from unrelated drugs.

### 7.4 Stabilizer ⇄ trigger bidirectionality (cross-reference)

Several of the new terpenes ARE on the MCAS VOC/fragrance trigger
list. The same molecule, depending on dose, route, and individual
sensitivity, can be:

- A **mast-cell stabilizer** at oral/systemic exposure (the
  pharmacological literature behind in-vitro β-hex inhibition).
- A **mast-cell trigger** at inhaled-fragrance exposure via MRGPRX2
  hypersensitivity (the patient-reported clinical reality).

The composite ranks the *stabilizer* potential. The trigger reality
is captured separately in `data/triggers/MCAS_Triggers_v1.csv` under
the `smell_fragrance_VOC` row. Compounds carrying `trigger_overlap: true`
in seeds.json:

| Compound | Stabilizer mechanism | Trigger context |
|----------|---------------------|------------------|
| α-Pinene | Bronchodilator + anti-inflammatory | Conifer VOC; can trigger via MRGPRX2 |
| β-Pinene | Anti-inflammatory | Same as α-pinene |
| D-Limonene | LAD2 β-hex inhibition (Hirota 2010) | Top citrus fragrance trigger |
| Linalool | Compound 48/80 inhibition (Kim 1999) | Lavender fragrance trigger |
| Eucalyptol | NF-κB suppression; EU-approved mucolytic | Respiratory irritant for some |
| Geraniol | Mast-cell stabilizer in vitro (Lei 2019) | EU fragrance allergen #26 |

**Operational interpretation:** an MCAS patient considering one of
these terpenes should think route — an encapsulated oral β-caryophyllene
or α-bisabolol product is mechanistically distinct from a diffused
lavender essential oil. The composite cannot make that distinction
for you. A clinician + a personal challenge-response observation
(see [`docs/route-of-administration.md`](../docs/route-of-administration.md)
and the GitHub issue template "Compound response observation") can.

### 7.5 Top-3 most credible new candidates for follow-up

1. **PEA (palmitoylethanolamide)** — #9 maintenance, high-evidence
   ALIAmide. ~30 clinical trials. Safest profile. Ultra-micronized
   formulations available OTC in EU.
2. **β-Caryophyllene** — #25 maintenance, the only FDA-GRAS dietary
   selective CB2 agonist. Non-intoxicating. Cross-class evidence
   (colitis, arthritis, neuropathic pain).
3. **α-Bisabolol** — #26 maintenance, the mast-cell stabilizer
   constituent of chamomile. Long topical safety record. Low trigger
   overlap.

The cannabinoids (CBD, Δ9-THC) rank slightly above the terpenes by
composite (CB2 self-similarity = 1.0), but evidence-level is "medium"
and Δ9-THC has regulatory headwinds. CBD is the more practical
cannabinoid candidate; Δ9-THC scoring is more "mechanism check" than
recommendation.

## 8. Reproducibility

```bash
git checkout <EXP-019 commit>
.venv/bin/python scripts/build_compound_library.py
.venv/bin/python scripts/score_against_targets.py
.venv/bin/python scripts/train_mast_cell_predictor.py
.venv/bin/python scripts/rank_hypotheses.py
diff outputs/ranked_maintenance.csv <pre-EXP-019 ranked_maintenance.csv>
```

The pipeline is deterministic given a fixed PubChem fetch (cached) +
fixed sklearn RNG. The mast-cell predictor training uses `random_state=42`.

## 9. What this experiment did not establish

- That any of the 24 compounds will produce ≥30% β-hex inhibition
  on substance-P-triggered LAD2 cells at ≤10 µM. **That's the wet
  lab's job, per `docs/wet-lab-preregistration-v1.md`.**
- That PEA is the right next wet-lab candidate to *test* — it's the
  best-validated. The wet lab pre-registration prioritizes novel
  SFN-class analogs (EXP-017 top-3) because they are *less* studied
  and so more valuable to test. PEA could be a positive comparator
  *alongside* sulforaphane.
- That β-caryophyllene works *in MCAS specifically* — its CB2 evidence
  is from colitis + arthritis + pain models, not MCAS β-hex assays.
- That cannabis-derived compounds are appropriate clinically — that's
  a clinician + jurisdiction question, not an in-silico question.

## 10. Next experiments suggested

1. **EXP-020 — Wet-lab PEA validation** as a positive-control arm in
   the EXP-018 LAD2 β-hex pilot. PEA is widely available, cheap, and
   would give the assay a known-positive stabilizer beyond Sulforaphane.
2. **Re-run EXP-008 / EXP-010 sensitivity audits** including the new
   CNR2 target weight to verify joint-perturbation stability.
3. **Add a `route_sensitivity` field** to compounds in seeds.json:
   compounds whose stabilization-vs-trigger split depends strongly
   on route (oral capsule vs inhaled fragrance) should be flagged
   for the deep-dive viewer.

## 11. References

- Linked experiments: [EXP-002](EXP-002-ligand-based-target-screening.md),
  [EXP-005](EXP-005-multi-objective-ranking.md),
  [EXP-016](EXP-016-mast-cell-predictor.md).
- CB2 mast-cell pharmacology: Facci L et al. (1995) PNAS 92:3376;
  Bisogno T et al. (1997) FEBS Letters 416:148.
- β-Caryophyllene as dietary CB2 agonist: Gertsch J et al. (2008)
  PNAS 105:9099.
- PEA as ALIAmide mast-cell stabilizer: Aloe L, Leon A, Levi-Montalcini R
  (1993) Agents Actions 39:C145; Skaper SD et al. (2015) Inflammopharmacology
  23:79.
- Stabilizer ⇄ trigger bidirectionality discussion: this is documented
  patient experience captured in `MCAS_Triggers_v1.csv` —
  formal literature on dose-response duality is sparse.
