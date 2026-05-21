# Glossary

Plain-language definitions for the terms you'll encounter in this repo.

## MCAS / mast-cell terms

| Term | Plain-English meaning |
|---|---|
| **MCAS** | Mast Cell Activation Syndrome. A condition where mast cells release their contents inappropriately, in response to triggers that shouldn't trigger them. |
| **MCAD** | Mast Cell Activation Disorder. Broader umbrella term sometimes used interchangeably with MCAS, sometimes to cover the whole disease family (incl. mastocytosis). |
| **Mastocytosis** | A clonal mast-cell disorder where there are *too many* abnormal mast cells (often driven by KIT D816V mutation). MCAS without proven clonality is non-clonal MCAS. |
| **Mast cell** | An immune cell. Lives in tissues (skin, GI, lung, around blood vessels, brain). Releases histamine + tryptase + cytokines + leukotrienes when activated. |
| **Degranulation** | The process of a mast cell releasing the contents of its storage granules. The thing you want to *prevent* in MCAS. |
| **Tryptase** | A mast-cell-specific enzyme. Released during degranulation. Used as a clinical biomarker. |
| **Histamine** | The most famous mast cell mediator. Causes itching, flushing, hives, GI symptoms, hypotension. |
| **Leukotrienes** | Lipid mediators released by mast cells. Cause bronchoconstriction + inflammation. Blocked by montelukast. |
| **Prostaglandins** | More lipid mediators. PGD₂ is the mast-cell-dominant one. |
| **TILT** | Toxicant-Induced Loss of Tolerance. A framework for chemical-driven mast cell sensitization (mold, VOCs, etc). |

## Receptors + targets

| Term | Plain-English meaning |
|---|---|
| **FcεRI** | High-affinity IgE receptor on mast cells. Crosslinking by allergen-bound IgE → classical Type I allergy → degranulation. |
| **MRGPRX2** | A GPCR on mast cells that triggers degranulation *without* IgE. Activated by drugs (opioids, contrast, some antibiotics), peptides (substance P), and likely fragrance VOCs. The "pseudo-allergy" receptor. |
| **KIT** | A receptor tyrosine kinase. Gain-of-function mutations (D816V most common) drive clonal mastocytosis. |
| **HRH1, HRH2, HRH3, HRH4** | Histamine receptors. Blocking them is what antihistamines do. |
| **CYSLTR1** | Cysteinyl leukotriene receptor 1. Blocked by montelukast. |
| **KEAP1 / Nrf2** | KEAP1 holds Nrf2 (a master antioxidant transcription factor) in the cytoplasm. Cysteine-reactive electrophiles (like sulforaphane) covalently modify KEAP1 and free Nrf2 to enter the nucleus and turn on dozens of cytoprotective genes. The proposed "upstream remission" axis. |
| **BTK** | Bruton tyrosine kinase. Downstream of FcεRI. Target of newer-generation MCAS-relevant drugs (remibrutinib). |
| **GLP1R** | GLP-1 receptor. Target of semaglutide/tirzepatide; surprising 2025 MCAS case-series response signal. |

## Cheminformatics + AI terms

| Term | Plain-English meaning |
|---|---|
| **SMILES** | A line-format chemical structure notation. `CS(=O)CCCCN=C=S` is sulforaphane. |
| **Tanimoto similarity** | A 0-to-1 score for how similar two molecules' fingerprints are. ≥0.5 usually means "same chemotype." |
| **Morgan fingerprint** | A widely-used circular fingerprint encoding atoms + their neighborhoods. Standard for similarity work. |
| **QSAR** | Quantitative Structure-Activity Relationship. Predicting bioactivity from structure with a learned model. |
| **QED** | Quantitative Estimate of Drug-likeness. 0–1 score; higher = more drug-like. |
| **SAS** | Synthetic Accessibility Score. 1 (easy) to 10 (hard) to synthesize. |
| **Lipinski's Rule of Five** | Classic drug-likeness heuristic: MW ≤ 500, logP ≤ 5, ≤ 5 H-bond donors, ≤ 10 acceptors. |
| **ADMET** | Absorption, Distribution, Metabolism, Excretion, Toxicity. The pharmacokinetic / safety profile. |
| **hERG** | A cardiac potassium channel. Blocking it can cause arrhythmia. Standard safety screen. |
| **AMES** | Mutagenicity assay (the Ames test). A standard genotoxicity screen. |
| **BBB** | Blood-brain barrier. Whether a drug crosses into the brain — relevant for neuro-MCAS. |
| **REINVENT 4** | An open-source generative-AI framework for drug design using reinforcement learning. |
| **PyTDC / TDC** | Therapeutics Data Commons. A Python package with curated ADMET / toxicity / drug-target datasets. |
| **DeepChem** | An open-source Python library for ML in drug discovery. |
| **Docking** | Computationally placing a small molecule into a protein pocket to estimate binding. |
| **AlphaFold** | DeepMind's protein-structure prediction model. We use it for targets without crystal structures. |
| **PubChem** | NIH's public chemical-information database. The source of every SMILES in our library. |
| **ChEMBL** | A curated bioactivity database. Source of training data for QSAR. |
| **ZINC / ZINC-22** | An open library of commercially-available molecules for virtual screening. |
| **Enamine REAL** | A "make-on-demand" virtual library of synthesizable compounds. |

## "Pharmacophore", "warhead", and the SFN class

| Term | Plain-English meaning |
|---|---|
| **Warhead** | A reactive chemical group designed to form a covalent bond with the target. SFN's isothiocyanate (`N=C=S`) is a warhead. |
| **Covalent inhibitor** | A drug that forms a permanent (or nearly-permanent) bond with its target. Different from a normal reversible binder. |
| **Cysteine-reactive electrophile** | A chemical group that reacts with the thiol (-SH) on a cysteine amino acid. SFN, dimethyl fumarate, bardoxolone — all act this way on KEAP1. |
| **Pharmacophore** | The minimum 3D arrangement of features that defines a molecule's biological activity (e.g. electrophilic head + linker + polar anchor). |
| **Michael acceptor** | A specific kind of electrophile: an α,β-unsaturated carbonyl. Curcumin has one. Bardoxolone has a more reactive cyanoenone variant. |
| **Isothiocyanate** | The `R-N=C=S` warhead. SFN, iberin, erucin, allyl-, benzyl-, phenethyl- isothiocyanate all share it. The chemical signature of the brassica family (broccoli, cabbage, wasabi, mustard, watercress, etc). |

## Project-specific terms

| Term | Plain-English meaning |
|---|---|
| **Rescue** | Acute mediator blockade — stop a flare in progress. |
| **Maintenance** | Daily stabilization — raise the threshold so triggers don't tip you over. |
| **Remission** | Upstream / root-cause reversal — fix the underlying priming, not just the symptoms. |
| **EXP-NNN** | A standardized experiment report. Numbered. See [experiments/](../experiments/). |
| **Composite score** | Our 5-component ranking signal (evidence + target similarity + warhead + safety + drug-likeness). |
