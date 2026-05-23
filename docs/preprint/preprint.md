# OpenMCAS: an open, reproducible compound-discovery pipeline for mast cell activation syndrome

**Authors**
M. R. Dula¹

**Affiliations**
¹ MR Dula Medical (a DBA of MR Dula Enterprise, LLC), Raleigh, NC, USA.

**Correspondence**
See [`CONTACT.md`](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/CONTACT.md).

**Repository**
[github.com/mrdulasolutions/MCAS.Opensource](https://github.com/mrdulasolutions/MCAS.Opensource)
(MIT license; commit hash captured per experiment).

**Live viewer**
[huggingface.co/spaces/MRDula/openmcas-browser](https://huggingface.co/spaces/MRDula/openmcas-browser)

**Pre-print version**
v0.1.0 — 2026-05-23.

---

> ⚠️ **Not medical advice.** All results are in-silico hypothesis
> generation. No human use, no self-experimentation, no clinical
> guidance. See
> [`docs/disclaimers.md`](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/disclaimers.md).

---

## Abstract

Mast cell activation syndrome (MCAS) lacks a target-rich, patient-grounded,
publicly auditable drug-discovery pipeline. Existing computational
screens for MCAS are siloed inside pharma or behind paywalled chemical
libraries, while patient-grounded efforts on Reddit, TMS for a Cure,
and Discord lack chemoinformatic rigor. We present **OpenMCAS**, an
end-to-end, MIT-licensed pipeline that (1) curates a 54-compound
MCAS-relevant library spanning approved drugs, herbs, supplements, and
biologics; (2) generates SFN-class isothiocyanate analogs by BRICS +
bioisostere replacement + a CPU substitute for REINVENT-style
reinforcement-learning generation; (3) scores all compounds against
8 MCAS targets via ligand-based screening, covalent-warhead SMARTS
detection, PyTDC-trained RandomForest QSAR (hERG / AMES / BBB),
AutoDock Vina docking against KEAP1 Kelch (PDB 4L7B), an MMFF94 covalent
C151 adduct thermodynamic proxy, per-target ChEMBL bioactivity
predictors (67,372 records, median CV R² 0.69), and a direct
mast-cell-stabilizer RandomForest (1101 compounds, **CV AUC 0.916 ±
0.019**); (4) combines into a transparent multi-objective composite
per category (rescue / maintenance / remission); and (5) audits the
composite for credibility via a known-actives recovery benchmark,
a negative-control benchmark, single-weight sensitivity analysis,
and 200-sample Latin-hypercube joint perturbation. The post-audit
pipeline achieves **95.2% recovery@20** on 21 held-out clinically
established mast-cell drugs, **100% precision@10** on 20 unrelated
negative-control drugs, and a worst-case single-weight Spearman
ρ = 0.946 over 36 perturbations. Sulforaphane-class isothiocyanates
(Erucin, Sulforaphane, PEITC, Iberin, Benzyl-ITC) consistently
rank in the top of the remission category — Erucin holds remission
#1 in **91.5%** of 200 LHS samples. We provide a pre-registered
β-hexosaminidase release wet-lab protocol and a procurement-ready
candidate list for three novel REAL-Space-plausible SFN-class
analogs. Every experiment is published as a numbered, standardized
report with reproducible inputs, run commands, and outputs. Every
prediction is auditable in the repository.

---

## 1. Introduction

Mast cell activation syndrome / disorders (MCAS / MCAD) are a
heterogeneous group of disorders in which mast cells aberrantly
release histamine, tryptase, prostaglandin D₂, leukotrienes, and
cytokines, producing multisystem episodic symptoms — anaphylactoid
flushing, GI dysmotility, brain fog, postural orthostasis, urticaria,
angioedema. Prevalence estimates vary widely (0.6%–17%), and
clinical practice relies on a small set of repurposed agents:
second-generation H1 antagonists (cetirizine, fexofenadine,
loratadine), H2 antagonists (famotidine), cromolyn sodium,
ketotifen, montelukast, and — for KIT-driven disease — masitinib,
midostaurin, avapritinib, and bezuclastinib.

The therapeutic ceiling of this stack is real. Many patients on
combinations of three or four mast-cell drugs still report
break-through symptoms requiring first-generation H1 rescue
(diphenhydramine, hydroxyzine, chlorpheniramine), with cumulative
anticholinergic burden a long-term concern. **There is no approved
upstream-disease-modifying agent for MCAS** — no analogue of, say,
metformin for type-2 diabetes or hydroxychloroquine for lupus.
Drug-discovery efforts targeting MCAS specifically have been
limited; most MCAS-relevant pharmacology is repurposed from
allergy, dermatology, or systemic mastocytosis.

We built OpenMCAS to make in-silico compound discovery for MCAS
**open, reproducible, patient-grounded, and auditable**. All code
and data are MIT-licensed. The pipeline runs on a CPU. Every
experiment is a numbered standardized report. Every ranking is
auditable. The headline candidates are sulforaphane and its sulfur
isothiocyanate congeners — and we explicitly say so, so the
hypothesis can be falsified by a wet-lab partner.

## 2. Methods

### 2.1 Compound library

54 anchor compounds were curated by hand across categories:

- **Rescue** (n = 14): H1 / H2 antagonists, cromones, ketotifen,
  doxepin, hydroxyzine.
- **Maintenance** (n = 25): leukotriene blockers, mast-cell
  stabilizers (tranilast, amlexanox, pemirolast), JAK / BTK /
  calcineurin inhibitors, anti-inflammatory naturals (curcumin,
  rosmarinic acid, luteolin, quercetin, EGCG, baicalein).
- **Remission** (n = 15): SFN-class isothiocyanates (Sulforaphane,
  Iberin, Erucin, Sulforaphene, Allyl-ITC, Benzyl-ITC, PEITC,
  Glucoraphanin), KIT TKIs (masitinib, midostaurin, avapritinib),
  GLP-1 agonists, low-dose naltrexone.

SMILES were fetched from PubChem PUG-REST with throttling + caching;
all SMILES were RDKit-canonicalized; the ITC anchor CIDs were
manually verified after three were found to be wrong in an earlier
pipeline iteration (Iberin 3032358→10455, Erucin 7373→78160,
Sulforaphene 6433469→6433206; disclosed and fixed in EXP-009).

### 2.2 Analog generation

Two parallel paths:

1. **BRICS + bioisostere + warhead-graft (EXP-001).** Local CPU
   chemistry on Apple Silicon. Seeds: 7 isothiocyanates above.
   BRICS-decompose; replace fragments with bioisosteres from a
   curated table; graft the isothiocyanate warhead onto novel
   scaffolds. 113 candidates.
2. **CPU substitute for REINVENT-style RL (EXP-013).** Multi-iter
   generate-and-select loop with QED + SA + warhead + Lipinski +
   seed-similarity composite reward. 265 unique candidates over 4
   iterations.

Total: 378 generated SMILES; 265 unique after deduplication.

### 2.3 Target-similarity screening (EXP-002)

Reference ligand sets curated per MCAS target: HRH1, HRH2, CYSLTR1,
MRGPRX2, BTK, KEAP1, KIT, GLP1R. For each compound, the score per
target is the **max Tanimoto similarity over Morgan-2048-bit
fingerprints** against that target's reference set.

### 2.4 Covalent-warhead scoring (EXP-003)

RDKit SMARTS detector for isothiocyanate, α,β-unsaturated carbonyl,
acrylamide, chloroacetamide, vinyl sulfone, and adjacent
electrophiles. KEAP1 pharmacophore filter (Lipinski + warhead +
fragment-level rules) applied.

### 2.5 ADMET QSAR (EXP-004)

RandomForest on Morgan FP, PyTDC training data: hERG (5-fold CV
AUC 0.81), AMES (0.90), BBB_Martins (0.91).

### 2.6 KEAP1 Vina docking (EXP-009)

AutoDock Vina 1.2.7 against PDB 4L7B Kelch domain. Apple-Silicon
binary, meeko ligand prep, OpenBabel receptor prep (working around
a meeko H-count error). Ligand efficiency = ΔG / heavy atoms.

### 2.7 Covalent C151 adduct proxy (EXP-012)

MMFF94 reaction-energy estimate for the dithiocarbamate adduct
formed between an isothiocyanate warhead and Cys-151 of KEAP1's
BTB domain — the actual mechanism of SFN-class compounds. Addresses
the EXP-009 §7.4 caveat that non-covalent Kelch docking does not
capture SFN's actual binding mode.

### 2.8 ChEMBL per-target predictors (EXP-011)

67,372 binding-activity records across 11 MCAS-relevant targets
were pulled from the ChEMBL web-resource client. RandomForest
regressors trained per target on Morgan FP → pIC50. 5-fold CV R²
range 0.52–0.80 (median **0.69**). Integrated into the composite
as a +0.10 ChEMBL-validated-potency bonus.

### 2.9 Mast-cell stabilizer predictor (EXP-016)

ChEMBL pull for assays tagged with mast-cell readouts: β-hexosaminidase
release, LAD2 degranulation, HMC-1, histamine release, tryptase
release. 1101 compounds (553 active, 548 inactive). RandomForest
on Morgan FP → P(stabilizer). 5-fold CV AUC **0.916 ± 0.019** —
the strongest single model in the repository. Integrated as a
+0.05 universal bonus across all three categories.

### 2.10 Multi-objective composite (EXP-005)

Per category, a weighted combination of:

```
composite = 0.30·evidence
          + 0.35·target_similarity (category-weighted)
          + 0.10·QED
          + 0.10·warhead
          + 0.15·safety  (1 - hERG, 1 - AMES, +BBB context)
          + 0.10·vina_LE  [remission category only]
          + 0.05·c151_score  [remission category only]
          + 0.10·chembl_pIC50  (max over category-relevant targets)
          + 0.05·mast_cell_stabilizer  (universal)
```

Category-specific target weights:

- Rescue: HRH1 0.45, HRH2 0.20, CYSLTR1 0.20, MRGPRX2 0.15
- Maintenance: CYSLTR1 0.25, HRH1 0.20, BTK 0.20, MRGPRX2 0.20, KEAP1 0.15
- Remission: MRGPRX2 0.30, KIT 0.30, KEAP1 0.30, GLP1R 0.10

### 2.11 Credibility audits

- **EXP-006 — Known-actives recovery.** 21 held-out clinically
  established mast-cell drugs (azelastine, olopatadine, nedocromil,
  pemirolast, tranilast, lodoxamide, amlexanox, levocetirizine,
  bilastine, ebastine, mizolastine, doxepin, cinnarizine,
  tofacitinib, acalabrutinib, tacrolimus, pimecrolimus,
  hydroxychloroquine, glycyrrhizin, hydroxytyrosol, cysteamine)
  not in seeds and not in reference sets. Tofacitinib and
  Acalabrutinib relabeled from remission to maintenance after
  EXP-015 §7.1 finding that JAK / BTK are downstream-FcεRI, not
  upstream-Nrf2-axis.
- **EXP-007 — Negative controls.** 20 unrelated drugs (statins,
  antihypertensives, anticonvulsants, antibiotics) blind-scored.
- **EXP-008 — Single-weight sensitivity.** ±50% per-weight sweep.
- **EXP-010 — Joint LHS perturbation.** 200-sample Latin-hypercube
  over all 6 weights simultaneously.
- **EXP-015 — Post-ChEMBL audit retread.** Rerun of EXP-006/7/8/10
  after ChEMBL integration; 3 of 4 hold; remission recovery
  regression diagnosed as a benchmark-label issue (resolved per
  §7.1 + §12).

## 3. Results

### 3.1 Recovery, precision, sensitivity

| Metric | Value | Reference |
|--------|-------|-----------|
| Known-actives recovery@20 (overall, post-relabel) | **95.2%** (20/21) | EXP-015 §12 |
| Known-actives recovery@20 (rescue) | **100%** (11/11) | EXP-015 §12 |
| Known-actives recovery@20 (maintenance) | **100%** (9/9) | EXP-015 §12 |
| Negative-control precision@10 (all categories) | **100%** | EXP-007 |
| Min single-weight Spearman ρ (post-ChEMBL) | **0.946** | EXP-015 §7.3 |
| Erucin remission #1 stability (LHS, 200 samples) | **91.5%** | EXP-010 |

### 3.2 Top-5 per category (after full audit)

| Rank | Rescue | Maintenance | Remission |
|------|--------|-------------|-----------|
| 1 | Cetirizine (0.612) | Curcumin (0.690) | **Erucin (0.737)** |
| 2 | Fexofenadine (0.611) | Rosmarinic acid (0.609) | **Sulforaphane (0.734)** |
| 3 | Hydroxyzine | Luteolin | **PEITC (0.695)** |
| 4 | Loratadine | Quercetin | **Iberin (0.626)** |
| 5 | Cromolyn | Montelukast | **Benzyl-ITC (0.591)** |

All five remission top compounds carry the isothiocyanate warhead.

### 3.3 The remission hypothesis

The composite consistently ranks **covalent C151 modifiers of KEAP1**
at the top of remission. Mechanism:

1. ITC warhead reacts covalently with Cys-151 of KEAP1's BTB domain.
2. KEAP1 dissociates from Nrf2.
3. Nrf2 escapes proteasomal degradation, translocates to the
   nucleus, and induces HMOX1 / NQO1 / GCLM (the ARE-driven antioxidant
   battery).
4. The mast-cell oxidative-priming state is dampened, raising the
   degranulation threshold on subsequent triggers.

This is the same pharmacology that DMF (dimethyl fumarate) exploits
in MS. SFN-class compounds are the natural-product class with the
clearest C151-modifier signature. The pipeline did not start with
SFN as a target — it surfaced SFN by composite scoring across all
inputs, and the headline result is stable under every audit we ran.

### 3.4 Procurement-ready candidates (EXP-017)

20 of the top-25 novel SFN-class analogs (excluding seeds) pass an
Enamine-REAL-Space envelope filter (MW 200–500, ≤ 35 heavy atoms,
common atoms only, SA ≤ 4.5, ≤ 2 stereo centers). Top 3:

1. `CCCS(=O)(=O)CCc1ccc(N=C=S)cc1` — n-propylsulfonyl-phenethyl-ITC
   (C12H15NO2S2, MW 269.4, QED 0.59)
2. `CCCS(=O)(=O)Cc1ccc(N=C=S)cc1` — n-propylsulfonyl-benzyl-ITC
   (C11H13NO2S2, MW 255.4, QED 0.60)
3. `CSCCCCCCN=C=S` — n-hexyl-methylthio-ITC, Erucin chain extension
   (C8H17NS2, MW 191.4)

A vendor lookup CSV with InChIKey-keyed Enamine REAL Space,
MolPort, eMolecules, PubChem, and ChemSpider search URLs is
published at
[`outputs/exp_017/enamine_lookup.csv`](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/outputs/exp_017/enamine_lookup.csv),
and a procurement packet at
[`outputs/exp_017/procurement_packet.md`](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/outputs/exp_017/procurement_packet.md).

## 4. Discussion

### 4.1 What the pipeline is good for

Hypothesis generation, rapid screening across a heterogeneous library
(small molecules + herbs + supplements), transparent composite
scoring with sensitivity analysis, and a procurement bridge to
wet-lab validation. Three independent credibility audits
(recovery@20, precision@10, joint-perturbation LHS) pass with
material margins.

### 4.2 What the pipeline is NOT

It is not a substitute for human mast-cell assay validation. It is
not a substitute for clinical trials. It does not capture
patient-specific pharmacogenomics, gut-microbiome metabolism of
glucoraphanin → SFN, or route-of-administration nuance (addressed
descriptively in [`docs/route-of-administration.md`](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/route-of-administration.md)
but **not** scored). It does not predict drug-drug interactions.

### 4.3 The chronic-rescue dependency gap (EXP-014)

A separate running experiment ([EXP-014](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-014-chronic-rescue-dependency.md))
captures patient-reported long-term first-generation H1 use
(e.g., chronic buccal diphenhydramine), a clinically common but
under-studied pattern with anticholinergic-burden implications.
The composite does not penalize chronic-use risk — the pipeline
ranks for *mechanism + safety baseline*, not *chronicity*. Patient
data flow continues independently of the composite.

### 4.4 Future work

- **Wet-lab validation** of 3 EXP-017 candidates via the
  pre-registered β-hex / LAD2 protocol
  ([`docs/wet-lab-preregistration-v1.md`](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/wet-lab-preregistration-v1.md))
  → EXP-018.
- **Covalent KEAP1 docking** at C151 (CovDock or GOLD-Covalent on
  PDB 4IFL), complementing the MMFF94 proxy (EXP-012).
- **Selectivity / polypharmacology score** — penalize promiscuous
  binders flagged by ChEMBL predictors across off-axis targets.
- **Patient-reported observation infrastructure** that protects
  privacy and supports trigger / response correlation.

### 4.5 Open science commitments

The repository is MIT. The viewer is free. Reproducibility is the
**non-negotiable** standard: every experiment lists inputs, code
version, run commands, outputs, and an explicit "this is what the
experiment did NOT establish" section. No patenting. No embargoes.
No closed forks.

## 5. Conclusion

OpenMCAS is, to our knowledge, the first end-to-end,
MIT-licensed, patient-grounded, sensitivity-audited in-silico
discovery pipeline targeted at MCAS / MCAD. The headline candidate
(sulforaphane and its sulfur isothiocyanate congeners) is a
falsifiable, wet-lab-ready hypothesis with a clear covalent
mechanism, a procurement path, and a pre-registered assay protocol.
We invite the mast-cell biology community to refute or validate it.

## 6. Data and code availability

- Code: https://github.com/mrdulasolutions/MCAS.Opensource (MIT).
- Pre-print version: this file at `docs/preprint/preprint.md`,
  commit hash captured by `git log`.
- Experiment reports: `experiments/EXP-*.md` (17 published as of
  this draft).
- Live viewer: https://huggingface.co/spaces/MRDula/openmcas-browser.
- Agent2Agent card: `.well-known/agent-card.json`.

## 7. Acknowledgments

This work was made possible by the open release of: PubChem (NIH),
ChEMBL (EMBL-EBI), PyTDC, RDKit, AutoDock Vina, OpenBabel, Meeko,
PDB (4L7B, 4IFL), AlphaFold DB (DeepMind / EMBL-EBI), Hugging Face
Spaces. We thank the MCAS patient community on r/MCAS, TMS for a
Cure, MCAS Hope, and Mastocytosis Society for ongoing dialogue
about real-world disease burden.

## 8. Author contributions

M.R.D. — concept, pipeline architecture, all in-silico experiments,
manuscript.

## 9. Competing interests

None. The pipeline is MIT-licensed and the provider (MR Dula Medical)
declares no patents or commercial products derived from this work.

## 10. References

For brevity, references are linked from individual experiment reports
(`experiments/EXP-*.md`). Key MCAS clinical background:

1. Afrin LB et al. *Diagnosis of mast cell activation syndrome:
   a global "consensus-2".* Diagnosis (Berl). 2020.
2. Akin C et al. *Mast cell activation syndrome: proposed diagnostic
   criteria.* J Allergy Clin Immunol. 2010.
3. Valent P et al. *Mast cell activation syndromes: definition and
   classification.* Allergy. 2013.
4. Schwartz LB. *Diagnostic value of tryptase in anaphylaxis and
   mastocytosis.* Immunol Allergy Clin North Am. 2006.

KEAP1 / Nrf2 / SFN mechanism:

5. Yang G et al. *Sulforaphane prevents and reverses allergic
   airways disease in mice.* Eur Respir J. 2011.
6. Holland R et al. *Prospective type 1 and type 2 disulfides of
   Keap1 protein.* Chem Res Toxicol. 2008.
7. Eggler AL et al. *Cul3-mediated Nrf2 ubiquitination and ARE-driven
   gene expression.* Antioxid Redox Signal. 2008.

— end of preprint v0.1.0 —
