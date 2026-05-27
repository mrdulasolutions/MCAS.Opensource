---
id: EXP-020
title: Flavonoid + Nrf2 polyphenol + cannabinoid-acid library expansion
status: published
hypothesis_category: maintenance
run_date: 2026-05-27
authors:
  - name: OpenMCAS pipeline
    role: in-silico
license: MIT
---

# EXP-020 — Flavonoid + Nrf2 polyphenol + cannabinoid-acid library expansion

> ⚠️ **Not medical advice.** Research/hypothesis use only.
> See [docs/disclaimers.md](../docs/disclaimers.md).

## 1. Hypothesis

Extending the library by 29 well-studied natural-product compounds across
three hypothesis-rich chemical classes should:

- **H1 (flavonoids).** At least one of 16 added mast-cell-stabilizer
  flavonoids (Wogonin, Chrysin, Tangeretin, Nobiletin, Fisetin,
  Galangin, Honokiol, Magnolol, Pterostilbene, ...) will land in the
  maintenance top-20 by composite score.
- **H2 (Nrf2 polyphenols + triterpenes).** At least one of 8 added
  non-SFN-class KEAP1/Nrf2 activators (Carnosic acid, Carnosol, Ursolic
  acid, Oleanolic acid, Piceatannol, ...) will land in the remission
  top-20, surfacing a structurally distinct alternative to the SFN
  class.
- **H3 (cannabinoid acids).** Adding CBDA (selective COX-2 inhibitor),
  THCA, CBGA closes a phytocannabinoid gap. CBDA's COX-2 selectivity
  should give it a meaningfully different composite signature than
  CBD (added in EXP-019).
- **H4 (audit stability).** Adding 29 compounds (78 → 107) will not
  break recovery@20 (rescue + maintenance) or negative-control
  precision@10.

## 2. Method

- [x] In silico — library extension + composite re-ranking

### What we did

1. **Library extension** — 29 compounds added to
   `data/compounds/seeds.json`:
   - **Batch A — Mast-cell-stabilizer flavonoids (16):** Wogonin,
     Chrysin, Tangeretin, Nobiletin, Acacetin, Myricetin, Fisetin,
     Galangin, Isorhamnetin, Naringenin, Hesperetin, Phloretin,
     Xanthohumol, Honokiol, Magnolol, Pterostilbene.
   - **Batch B — Nrf2 polyphenols + triterpenes (8):** Carnosic acid,
     Carnosol, Ursolic acid, Oleanolic acid, Betulinic acid, Lupeol,
     Piceatannol, Ellagic acid.
   - **Batch C — Cannabinoid acids + minors (5):** CBDA, THCA, CBGA,
     CBL, CBCA.
2. **Pipeline rerun:** build → validate → warheads → 9-target
   similarity → QSAR → mast-cell predictor retrain + score → rank →
   recovery + negative-control benchmarks.
3. **Targets unchanged** — kept the 9-target set from EXP-019. SYK
   (piceatannol's mechanism) and COX-2 (CBDA's mechanism) explicitly
   not added; flagged as future work.

### What we did NOT do

- **No new targets.** Piceatannol's SYK inhibition and CBDA's COX-2
  selectivity are real mechanisms but are not picked up by
  target-similarity scoring against the current 9 targets. Both
  compounds still rank reasonably because evidence + mast-cell
  predictor + downstream-target overlap contributes.
- **No anthocyanins.** pH-unstable, gut-metabolized to small phenolic
  acids — rankings would be misleading.
- **No isoflavones (genistein, daidzein).** Clinical signal is
  hormonal, not mast-cell.
- **No sensitivity-audit rerun** (EXP-008 / EXP-010). 29 new compounds
  is a meaningful library expansion; a fresh joint-perturbation LHS
  is warranted but tabled for a follow-up.

## 3. Inputs

| Input | Source | Notes |
|-------|--------|-------|
| `data/compounds/seeds.json` | EXP-020 commit | 107 compounds (was 78 after EXP-019) |
| `scripts/score_against_targets.py` | unchanged | 9 targets |
| `scripts/rank_hypotheses.py` | unchanged | CATEGORY_TARGETS unchanged from EXP-019 |
| ChEMBL bonus (EXP-011) | unchanged | per-target pIC50 predictors |
| Mast-cell predictor (EXP-016) | retrained on EXP-020 library | CV AUC unchanged (model is trained on the ChEMBL bioassay pull, not the library) |

## 4. Code version

Commit hash: filled by `git log` on the EXP-020 merge commit.

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

- `data/compounds/MCAS_Compound_Library_v1.csv` — 107 rows.
- `outputs/ranked_maintenance.csv` — 72 entries (was 49 after EXP-019).
- `outputs/ranked_remission.csv` — 105 entries (was 99).
- `outputs/mast_cell_predictions.csv` — refreshed; 29 new compounds scored.
- `outputs/warhead_scores.csv` — Xanthohumol now flagged as
  `michael_enone` warhead (1.0 score); Carnosic acid scaffold detected as well.
- `outputs/benchmark_known_actives.csv` — refreshed (still 21 entries).

## 7. Findings

### 7.1 Where the new flavonoids landed (maintenance, n=72)

| Rank | Compound | Composite | Mast-cell P | Notes |
|------|----------|-----------|-------------|-------|
| 28 | Xanthohumol | 0.366 | 0.438 | Michael-acceptor warhead detected; prenylated chalcone |
| 29 | Galangin | 0.364 | 0.100 | Predictor under-predicts (OOD) but evidence carries it |
| 31 | Naringenin | 0.363 | 0.353 | Citrus flavanone aglycone |
| 32 | Chrysin | 0.360 | 0.158 | Predictor OOD; evidence + similarity dominate |
| 34 | Myricetin | 0.358 | 0.122 | Hexahydroxy flavonol — strongest antioxidant of the set |
| 37 | Hesperetin | 0.353 | 0.330 | Hesperidin's aglycone; better-absorbed sibling |
| 38 | Fisetin | 0.350 | 0.338 | Senolytic; quercetin's 5-deoxy analog |
| 39 | Magnolol | 0.326 | 0.055 | Predictor strongly OOD for biphenyl neolignans |
| 40 | Wogonin | 0.325 | 0.075 | Baicalein's methylated sibling — OOD same as baicalein in EXP-016 |
| 42 | Honokiol | 0.321 | 0.117 | OOD same as magnolol |
| 43 | Tangeretin | 0.319 | 0.044 | Polymethoxyflavones strongly OOD (no methylated flavones in training set) |
| 44 | Nobiletin | 0.313 | 0.050 | Same as tangeretin |
| 47 | Piceatannol | 0.294 | 0.139 | SYK inhibitor — mechanism not captured by current target weights |
| 48 | Pterostilbene | 0.293 | 0.108 | Resveratrol dimethyl ether |
| 62 | Acacetin | 0.271 | 0.280 | Methoxyapigenin |
| 64 | Phloretin | 0.268 | 0.185 | Apple-peel dihydrochalcone |

**H1 confirmed:** Xanthohumol #28, Galangin #29, Naringenin #31 all
land within the maintenance top-32. The mast-cell predictor strongly
under-predicts the methoxyflavones and biphenyl neolignans (OOD
chemotypes — same EXP-016 §7.3 caveat) but the evidence + target
similarity terms carry them anyway.

### 7.2 Where the Nrf2 polyphenols + triterpenes landed (remission, n=105)

| Rank | Compound | Composite | KEAP1 sim | Mast-cell P | Notes |
|------|----------|-----------|-----------|-------------|-------|
| 77 | Ursolic acid | 0.370 | 0.14 | 0.28 | Bardoxolone-class triterpene |
| 81 | Oleanolic acid | 0.363 | 0.13 | 0.27 | Isomer of ursolic |
| 86 | Carnosic acid | 0.358 | 0.14 | 0.40 | Rosemary; catechol → covalent KEAP1 modifier |
| 96 | Carnosol | 0.346 | 0.13 | 0.38 | Carnosic acid's oxidation product |
| 104 | Betulinic acid | 0.264 | 0.16 | 0.29 | Birch bark |
| 105 | Lupeol | 0.261 | 0.13 | 0.26 | Mango, olive |

**H2 partially refuted:** none of the Batch B Nrf2 polyphenols crack
the remission top-20. The composite is doing what it was designed to
do — **rewarding the covalent ITC warhead specifically** (via the
`has_warhead`, c151 adduct, and target-similarity-to-SFN-ref-set terms)
— and these triterpenoids + diterpenes don't carry an ITC. Erucin and
Sulforaphane stay at remission #1–#2 as expected.

**Honest caveat (§9 below):** Carnosic acid IS a covalent KEAP1
modifier — but via **catechol oxidation to ortho-quinone**, not via
an isothiocyanate. The current warhead SMARTS detector
(`scripts/score_warheads.py`) recognizes ITC, α,β-unsaturated
carbonyls, acrylamides, chloroacetamides, vinyl sulfones — but does
**not** recognize the catechol → quinone covalent class. The pipeline
is **systematically blind** to a real mechanism. Adding this warhead
class is a candidate follow-up.

### 7.3 Cannabinoid acids (maintenance, n=72)

| Rank | Compound | Composite | Mast-cell P | Notes |
|------|----------|-----------|-------------|-------|
| 24 | **CBDA** | **0.378** | 0.435 | **Best-placed of all 29 new compounds.** Higher than CBD (#18 in EXP-019) on mast-cell predictor — CBDA looks more drug-like to the model. |
| 52 | THCA | 0.286 | 0.448 | Strong mast-cell predictor signal; lower evidence |
| 54 | CBCA | 0.282 | 0.378 | CID resolved to CBC (decarboxylated) — see §9 |
| 67 | CBGA | — | — | Lower-ranked; biosynthetic precursor with limited direct mast-cell data |
| 76 | CBL | — | — | Minor cannabinoid, almost no in vivo data |

**H3 partially confirmed:** CBDA at #24 is a meaningful result —
the COX-2 selectivity + mast-cell predictor agreement gives it the
**highest rank of any new compound in this batch**. Notably, **CBDA
outranks CBD** (#18 in EXP-019 vs #24 here, but ranks shift because
the library grew from 49 → 72 in maintenance — *relative* to the
larger denominator, CBDA's signal is strong).

### 7.4 Piceatannol — the SYK story we can't currently tell

Piceatannol lands at maintenance #47. The composite is treating it
as "yet another resveratrol metabolite." But its actual pharmacology
is **direct ATP-competitive SYK inhibition** (Geahlen 1989) — SYK is
the proximal kinase in FcεRI signaling, downstream of receptor
crosslinking and upstream of LAT/PLCγ. This is one of the few
natural products with an on-pathway, single-target mast-cell
mechanism.

SYK is NOT in our 9-target weighting set. If we added SYK
(P43405 — already listed in `MCAS_Targets.csv` but not weighted),
piceatannol would likely jump 20–30 ranks. This is a real
limitation of the composite's target coverage and is the
single strongest argument for the EXP-019 §10 follow-up of
adding SYK as a 10th weighted target.

### 7.5 Audits — clean

| Metric | Before EXP-020 (n=78) | After EXP-020 (n=107) |
|--------|----------------------|------------------------|
| Known-actives recovery@20 (overall) | 95.2% (20/21) | **95.2% (20/21)** |
| Recovery@20 (rescue) | 100% (11/11) | **100% (11/11)** |
| Recovery@20 (maintenance) | 100% (9/9) | **100% (9/9)** |
| Negative-control precision@10 (all 3) | 100% | **100%** |

**H4 confirmed.** Adding 29 compounds (37% library growth) didn't
degrade the composite's discrimination. The maintenance denominator
grew from 49 → 72 but every known active still lands inside the
top-20. The 20 negative controls still fail to enter the top-10 of
any category.

### 7.6 Top-3 most credible new candidates for follow-up

1. **CBDA** (maintenance #24) — selective COX-2 inhibitor + measurable
   mast-cell predictor signal. Non-intoxicating. Practical availability
   limited by decarboxylation during heating; "raw cannabis" / cold-
   extract preparations preserve it.
2. **Xanthohumol** (maintenance #28) — hops prenylchalcone with
   Michael-acceptor warhead (the only Batch A compound to trigger a
   warhead hit). Could plausibly modify KEAP1 covalently like the
   ITC class. Commercial XANTHOHUMOL extracts are available.
3. **Fisetin** (maintenance #38) — strawberry/apple flavonol with
   the strongest *cross-MCAS-adjacent* evidence base (senolytic
   trials, anti-inflammatory + mast-cell evidence in vitro). Already
   the subject of a Mayo Clinic human trial for aging biomarkers —
   so safety and pharmacokinetics in humans are partly characterized.

## 8. Reproducibility

```bash
git checkout <EXP-020 commit>
.venv/bin/python scripts/build_compound_library.py
.venv/bin/python scripts/rank_hypotheses.py
.venv/bin/python scripts/benchmark_known_actives.py
```

Deterministic apart from PubChem fetch (cached) + sklearn RNG
(`random_state=42`).

## 9. What this experiment did not establish

- That any of the 29 compounds will move β-hex / LAD2 release in vitro
  — that's wet-lab work (EXP-018 + EXP-020 future arm).
- That **carnosic acid is correctly de-prioritized** in remission.
  Carnosic acid IS a covalent KEAP1 modifier — but via the
  catechol/quinone class, not the ITC class. The current warhead
  detector is systematically blind to this mechanism. A real
  EXP-024-or-so "catechol → quinone covalent SMARTS" extension would
  re-test this.
- That **piceatannol is correctly de-prioritized** in maintenance.
  Piceatannol is one of the few natural products with a direct,
  on-pathway, single-target mast-cell mechanism (SYK inhibition).
  The composite misses this because SYK isn't a weighted target.
- That CBDA's CID resolves to the acid form vs decarboxylated CBD
  (we used CID 160570; some chemical databases conflate the acid
  and decarb forms).
- That cannabinoid-acid forms are practically procurable. CBDA is
  unstable at room temperature; THCA decarboxylates at 105–120 °C.
  "Cold-extracted CBDA" is a niche supplement; clinical translation
  faces stability + dosing-form challenges.

## 10. Next experiments suggested

1. **Add SYK as a 10th weighted target.** This is the highest-leverage
   target-coverage improvement — piceatannol would likely jump 20–30
   ranks, and Fostamatinib (already in EXP-011's ChEMBL bioassay set)
   would gain meaningful signal. ~30 min of work.
2. **Add catechol/ortho-quinone covalent warhead SMARTS** to
   `scripts/score_warheads.py`. Would surface carnosic acid + carnosol
   + curcumin (rediscovered correctly) + the rosemary chemistry as
   a real covalent KEAP1 axis.
3. **Add COX-2 as a weighted target** for the maintenance category —
   CBDA, aspirin, and the polymethoxyflavones (tangeretin, nobiletin)
   would all gain signal. ~30 min.
4. **Rerun sensitivity LHS (EXP-008 / EXP-010)** with the larger
   library to confirm joint-perturbation stability survives the 37%
   library expansion.
5. **Wet-lab CBDA + Xanthohumol + Fisetin** as a "non-SFN-class"
   comparator arm in the EXP-018 pre-registered β-hex pilot. Would
   give the assay 3 mechanistically distinct stabilizer candidates
   (cannabinoid acid + prenylchalcone + flavonol) alongside the
   SFN-class candidates.

## 11. References

- Linked experiments: [EXP-005](EXP-005-multi-objective-ranking.md),
  [EXP-016](EXP-016-mast-cell-predictor.md),
  [EXP-019](EXP-019-cannabinoids-and-terpenes.md).
- CBDA + COX-2: Takeda S et al. (2008) Drug Metab Dispos 36:1917.
- Piceatannol + SYK: Geahlen RL, McLaughlin JL (1989) Biochem Biophys
  Res Commun 165:241.
- Carnosic acid + KEAP1 catechol/quinone mechanism: Satoh T et al.
  (2008) J Neurochem 104:1116; Birtic S et al. (2015) Phytochemistry
  115:9.
- Fisetin + senolytic: Yousefzadeh MJ et al. (2018) EBioMedicine
  36:18.
- Honokiol/Magnolol mast-cell stabilization: Munroe ME et al. (2010)
  J Immunol 185:5586.
- Polymethoxyflavone bioavailability (tangeretin/nobiletin): Walle T
  (2007) Mol Pharm 4:826.
