# Roadmap

A living document. Things at the top of each section are higher priority.

## Now (v0.x)

- ✅ Curated 54-compound MCAS library (pharma + herbs + supplements + biologics).
- ✅ Injury-mechanism + trigger frameworks.
- ✅ 7 natural ITC seeds for SFN-class generation (113 candidates).
- ✅ Ligand-based screening across 8 MCAS targets.
- ✅ Covalent-warhead SMARTS detection + KEAP1 pharmacophore filter.
- ✅ ADMET QSAR (hERG / AMES / BBB), AUC 0.89–0.91.
- ✅ Multi-objective ranking → rescue / maintenance / remission top-10s.
- ✅ Standardized experiment report format (6 published).
- ✅ Audience-segmented onboarding docs.
- ✅ A2A agent card + canonical contact info.
- ✅ **Known-Actives Recovery benchmark — 100% recovery@20** (EXP-006).
- ✅ Auto-generated hypothesis tables with timestamp + commit-hash provenance.
- ✅ Streamlit public viewer + Hugging Face Spaces deployment recipe.
- ✅ **Live public viewer deployed:** https://huggingface.co/spaces/MRDula/openmcas-browser
- ✅ **GitHub Actions auto-sync** of the HF Space on every pipeline rerun (sync-hf-space.yml).
- ✅ **Negative-control benchmark** (EXP-007) — 100% precision@10 across all categories under realistic scoring.
- ✅ **Sensitivity analysis** (EXP-008) — min Spearman ρ = 0.93 under ±50% weight sweeps; SFN #1 stable in 100% of remission perturbations.
- ✅ **KEAP1 Vina docking** (EXP-009) — real AutoDock Vina docking on PDB 4L7B Kelch domain for top-50 remission candidates; ligand-efficiency normalization shows all top-15 LE compounds carry the ITC warhead. Also disclosed + fixed three wrong PubChem CIDs (Iberin, Erucin, Sulforaphene) that had been silently propagating through the pipeline.
- ✅ **Joint-perturbation LHS** (EXP-010) — 200-sample Latin-hypercube sweep of all 6 weights; Erucin holds remission #1 in 91.5% of samples.
- ✅ **Scheduled refresh** — weekly cron workflows (`refresh-pipeline.yml` + cron on `sync-hf-space.yml`).
- ✅ **Covalent C151 adduct proxy** (EXP-012) — MMFF94 dithiocarbamate adduct energy for ITC-class compounds; addresses the EXP-009 §7.4 mechanism caveat.
- ✅ **Iterative RL-style generation** (EXP-013) — CPU substitute + hardened Colab notebook path; 265 candidates over 4 iterations.
- ✅ **ChEMBL bioassay pull + predictor** (EXP-011) — 67,372 records across 11 targets; CV R² 0.52–0.80 (median 0.69); integrated as +0.10 ChEMBL-validated potency bonus. **Hydroxyzine jumped to #3 in rescue, Montelukast entered maintenance top-5** on real-bioactivity grounding.
- ✅ **Audit retread on post-ChEMBL composite** (EXP-015) — precision@10 = 100% held, min Spearman ρ tightened 0.933→0.946; remission recovery regression surfaced a benchmark-label issue (JAK/BTK should be relabeled as maintenance, not remission).
- ✅ **Mast-cell-specific predictor** (EXP-016) — direct stabilizer classifier from ChEMBL β-hex / LAD2 / HMC-1 / histamine release assays. **CV AUC 0.916 ± 0.019 — strongest single model in the repo.** Luteolin 0.728, Midostaurin 0.840. Integrated as +0.05 universal bonus across all three categories. Cetirizine edged Fexofenadine to #1 in rescue; Luteolin entered maintenance top-5.
- ✅ **JAK/BTK relabel applied** (EXP-015 §12) — Tofacitinib + Acalabrutinib reclassified from remission to maintenance per the §7.1 finding that JAK/BTK are downstream-FcεRI, not upstream-Nrf2 axis. Recovery@20: rescue 100%, maintenance 100%, overall 95.2%.
- ✅ **Refresh pipeline manual verification** — `refresh-pipeline.yml` triggered ad-hoc and completed clean before the next Sunday cron.
- ✅ **Streamlit viewer v2** — added Mast-cell Predictor tab + per-compound Deep-Dive tab (composite ranks across all three categories, ChEMBL pIC50 table, Vina ΔG + LE, C151 score, mast-cell probability — all in one place).
- ✅ **Procurement packet for top generated analogs** (EXP-017) — 20 / 25 novel SFN-class analogs pass the Enamine REAL Space envelope; vendor lookup URLs (Enamine / MolPort / eMolecules / PubChem / ChemSpider) keyed by InChIKey, published as `outputs/exp_017/procurement_packet.md`.
- ✅ **Pre-registered β-hex / LAD2 wet-lab protocol** — `docs/wet-lab-preregistration-v1.md` (locked dose-response, FDR-controlled stats, stopping rules, falsification criterion).
- ✅ **CRO + academic outreach packet** — `docs/cro-outreach-packet.md` (cover-email template, target lab list, no-IP / no-NDA / publish-either-way terms).
- ✅ **bioRxiv-style preprint v0.1.0** — `docs/preprint/preprint.md` (abstract, methods, results, discussion, refs).
- ✅ **Lay-language patient summary** — `docs/for-mcas-community.md` (plain English, what we found, what we won't do, how to help without spending).
- ✅ **Cannabinoid + terpene expansion** (EXP-019) — 24 new compounds (8 phytocannabinoids + 4 endocannabinoid-likes + 12 terpenes); CB2 (CNR2) wired as 9th MCAS target; **PEA lands #9 in maintenance**, β-caryophyllene #25, α-bisabolol #26; all audits hold (recovery@20 = 95.2%, precision@10 = 100%). Stabilizer ⇄ trigger bidirectionality cross-referenced in MCAS_Triggers_v1.csv (limonene, linalool, eucalyptol, pinenes, geraniol).
- ✅ **Flavonoid + polyphenol + cannabinoid-acid expansion** (EXP-020) — 29 new compounds across 3 batches. **Library now 107 anchors.** Best new landings: CBDA #24, Xanthohumol #28 (Michael-acceptor warhead detected!), Fisetin #38 in maintenance. Audits hold. Surfaced two real composite gaps — piceatannol-SYK mechanism (SYK not weighted) and carnosic-acid-quinone covalent KEAP1 modification (catechol warhead not in detector) — both filed as next-step targets.
- ✅ **Three composite gaps closed + 9 more compounds** (EXP-021) — SYK + PTGS2 (COX-2) wired as 10th + 11th weighted targets; catechol/pyrogallol/hydroquinone covalent SMARTS added to warhead detector. Added Methylene blue, NAD+ / NMN / NR, Ivermectin, Lycopodine, Testosterone, Methyl red, Bovista. **Library now 116 anchors.** Piceatannol jumped maintenance #47 → #12, Luteolin #5 → #2, Baicalein entered top-5, Carnosic acid remission #86 → #53 — all the EXP-020 §10 predictions confirmed. **recovery@10 improved from 4.8% → 9.5%** while precision@10 stayed at 100% and recovery@20 stayed at 95.2%. Strongest single methodology improvement since EXP-011.
- ✅ **Sensitivity LHS rerun over EXP-021 composite** (EXP-022) — 200-sample joint perturbation over 6 macro-weights. **Curcumin maintenance #1 in 100% of samples** (PTGS2 + catechol made it immovable). **Combined SFN class top-1 in 100% of remission samples** (Erucin/Sulforaphane split moved from 91.5/8.5 → 60/40 — fairer reflection that the two are chemically interchangeable). Piceatannol top-10 in 47% of samples (was nowhere pre-EXP-021). 62 new compounds across EXP-019→021 did NOT introduce any new top-1 candidates — composite headline behavior is robustly conservative.

## Next (v0.x+1) — credibility & accessibility first

These five are the next 2–4 weeks of high-leverage work (per the
"100x vision" framing — credibility, accessibility, polish):

1. **Covalent KEAP1 docking** at C151 (BTB domain) — non-covalent
   Kelch docking is now done (EXP-009), but SFN's actual mechanism is
   covalent. Needs CovDock / GOLD-Covalent on PDB 4IFL or similar.
2. **Expand recovery + control sets via ChEMBL bioassay pull** (`β-hexosaminidase release`,
   `mast cell degranulation`, `LAD2`). Targets: 50+ actives, 100+ controls.
3. **Joint-perturbation Latin-hypercube weight sweep** — 200-point
   sweep over all six weights simultaneously; report 95% CI on each
   compound's rank (extends EXP-008).
4. **Pipeline-driven Space refresh** — extend the sync workflow to
   also rebuild the rankings (run the full pipeline) on a schedule,
   commit refreshed CSVs, and let the existing sync job pick them up.
5. **Real REINVENT 4 RL run on Colab** seeded on top-10 SFN-class
   analogs from EXP-001; replace the deterministic BRICS generator
   with policy-gradient generation for the next analog batch.

## Then (v0.x+2)

- ChEMBL bioassay pull → train a true mast-cell-degranulation predictor.
- Polypharmacology bonus + selectivity penalty in `rank_hypotheses.py`.
- DeepChem GraphConv QSAR for AUC delta vs. RandomForest.
- REINVENT 4 on Colab GPU — actual RL run seeded on top-10.
- Enamine REAL Space availability check for top generated analogs.
- PubMed auto-scan per top compound (prior art surfacing).

## Later (v0.5)

- Patient-data infrastructure beyond GitHub issues (structured intake,
  privacy-preserving, optional clinician validation).
- Multi-pred QSAR — CYP1A2 / 2C9 / 2C19 / 2D6 / 3A4 inhibition.
- xTB / DFT electrophilicity ranking for covalent warheads.
- KEAP1 covalent docking (CovDock or GOLD-Covalent at Cys-151).
- iPSC-derived mast cell readouts in the wet-lab protocol references.
- Combination scoring (synergy predictions for pairs / triples).
- Pre-registration registry with DOI minting per experiment.
- Quarterly Zenodo DOI snapshots.

## Big-picture (v1.0)

- A wet-lab partner running a continuous validation campaign on the
  current top-30 every quarter, published as new `EXP-NNN` reports.
- A 501(c)(3) fiscal home (or hosted under an existing one — see
  [audiences/for-nonprofits.md](audiences/for-nonprofits.md)).
- A patient-coreference network for trigger / response data without
  PHI capture.
- A 1.0 release with the first wet-lab-validated remission candidate
  (positive or negative — both are publishable).

## Not on the roadmap (intentionally)

- Selling anything.
- Recommending self-experimentation.
- Patenting compounds.
- Closed-source forks.
- Embargoed results.

## How to push something onto the roadmap

Open an [issue tagged `roadmap`](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?labels=roadmap)
with: (a) what, (b) why, (c) who would do it, (d) what success looks like.
