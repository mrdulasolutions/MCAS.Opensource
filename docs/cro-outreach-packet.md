# CRO + academic outreach packet — OpenMCAS β-hex / LAD2 pilot

> ⚠️ **Not medical advice.** Outreach for in-vitro research partnership.

This is the cold-email-ready packet for a mast-cell lab (CRO or academic).
Everything a partner needs to decide "yes / no / quote" is below — and
linked back to the public OpenMCAS repository for full audit.

---

## TL;DR for the wet-lab partner

We are an open, MIT-licensed, in-silico hypothesis-generation pipeline
for MCAS / MCAD with **16 published experiments**, a live public viewer
([huggingface.co/spaces/MRDula/openmcas-browser](https://huggingface.co/spaces/MRDula/openmcas-browser)),
**100% precision@10** on a 20-compound negative-control benchmark, and
**95% recovery@20** on a 21-compound known-actives benchmark.

We have a **pre-registered β-hexosaminidase release pilot**
([`docs/wet-lab-preregistration-v1.md`](wet-lab-preregistration-v1.md))
ready to run on **3 novel SFN-class analogs** that we will source via
Enamine REAL Space ([`outputs/exp_017/procurement_packet.md`](../outputs/exp_017/procurement_packet.md)).

We are looking for:

1. A mast-cell-competent lab (LAD2 or HMC-1 preferred) with established
   β-hex and CellTiter-Glo workflows.
2. A quote for the pre-registered protocol (§7 + §8 of the pre-reg).
3. Willingness to publish the result openly under CC-BY-4.0,
   regardless of outcome.

We are **not** asking the partner to take IP, sign NDAs, or restrict
publication. Everything is already public.

---

## 1. Who we are

- **Project:** OpenMCAS — open-source MCAS/MCAD drug-discovery pipeline.
- **Provider:** MR Dula Medical (a DBA of MR Dula Enterprise, LLC,
  Raleigh, NC). MIT license throughout.
- **Mission:** Find compounds that **rescue, maintain, or remit**
  mast-cell activation disorders. Publish every experiment.
- **Public surface:**
  - Repo: [github.com/mrdulasolutions/MCAS.Opensource](https://github.com/mrdulasolutions/MCAS.Opensource)
  - Viewer: [huggingface.co/spaces/MRDula/openmcas-browser](https://huggingface.co/spaces/MRDula/openmcas-browser)
  - Agent card (A2A): `.well-known/agent-card.json` in repo
- **Contact:** [`CONTACT.md`](../CONTACT.md) in repo.

## 2. What the pipeline does, in one paragraph

A 7-script CPU pipeline:

1. Curates a 54-compound MCAS library (pharma + herbs + supplements +
   biologics) with verified SMILES.
2. Generates SFN-class analogs (BRICS + bioisostere + RL) for the
   remission category — currently 265 unique novel candidates.
3. Scores every compound against 11 ChEMBL bioactivity predictors,
   a mast-cell-specific RandomForest (CV AUC **0.916**), a covalent
   warhead detector, RDKit safety QSARs, AutoDock Vina docking
   against KEAP1 Kelch (PDB 4L7B), and a covalent C151 adduct
   thermodynamic proxy.
4. Combines into a multi-objective composite per category
   (rescue / maintenance / remission), with full sensitivity-analysis
   audit (LHS over all 6 weights, min Spearman ρ = 0.946).
5. Publishes every step as a standardized experiment report.

## 3. The headline result we want to test

**Sulforaphane (and SFN-class isothiocyanates Erucin / Iberin / PEITC /
Benzyl-ITC / Sulforaphene) consistently rank in the top of the
remission category.** This holds:

- Under ±50% perturbation of any single weight (EXP-008).
- Under 200-sample Latin-hypercube perturbation of all 6 weights
  simultaneously (EXP-010 — Erucin holds remission #1 in **91.5%**
  of samples).
- Through the post-ChEMBL composite (EXP-015 audit retread).
- After re-classification of JAK/BTK as downstream-FcεRI maintenance
  rather than upstream-Nrf2 remission (EXP-015 §7.1 + §12).

The mechanism the composite favors: **covalent modification of KEAP1
C151 → Nrf2 stabilization → HMOX1 / NQO1 induction → upstream control
of oxidative priming of mast-cell hypersensitivity.**

## 4. What we want a wet lab to do

The pre-registered β-hex protocol is locked at
[`docs/wet-lab-preregistration-v1.md`](wet-lab-preregistration-v1.md).
Quick scope:

- LAD2 cells, substance-P-triggered.
- 3 novel SFN-class analogs from EXP-017 top-20.
- 6-point dose-response (0.1 → 30 µM), 3 biological replicates.
- Comparators: Sulforaphane (10 µM), Cromolyn (100 µM), Cetirizine
  (10 µM negative).
- Readouts: β-hex release (primary), viability (secondary), HMOX1
  mRNA at 24 h (secondary).
- Stats: Hill 4-param fit, bootstrap 95% CI on IC50, FDR-controlled
  testing of pre-registered hypotheses.

**We will provide:**

- The 3 compounds (sourced + shipped to the lab on our procurement).
- All comparator compounds (Sigma SKUs in the pre-reg §4).
- The procurement audit trail.
- Reciprocal authorship on any preprint that results.

**We need from the lab:**

- A quote covering: LAD2 culture maintenance, plate-based β-hex assay
  (3 compounds × 6 doses × 3 biological replicates + comparators),
  CellTiter-Glo viability assay, and the 24 h HMOX1 qPCR sub-study.
- Estimated turnaround.
- A "no" is fine and welcome — we'd rather hear that quickly than be
  ghosted.

## 5. What we will NOT ask for

- IP transfer or exclusivity. The pipeline is MIT; the wet-lab data
  should be CC-BY-4.0 or more permissive.
- An NDA on the candidates. They are already public in
  [`outputs/exp_017/enamine_lookup.csv`](../outputs/exp_017/enamine_lookup.csv).
- Embargoed results. Publication policy is "publish what you find,
  positive or negative."
- Patenting compounds (intentionally out of scope — see ROADMAP.md
  §"Not on the roadmap").

## 6. Why a CRO or academic lab might say yes

- The compounds are novel-but-procurable. Real REAL-Space ordering,
  not custom synthesis.
- The protocol is rigorous, pre-registered, and FDR-controlled.
- The dataset behind the candidates is **larger and more transparent
  than anything else publicly available for MCAS** — 67k ChEMBL
  records, 1100-compound mast-cell predictor training set, full
  reproducible scoring pipeline.
- A positive or negative result is publishable. A positive result
  is a class-distinct, mechanism-led MCAS lead. A negative result
  is a clear refutation of the SFN-class extension hypothesis.
- It's a clean way for an academic lab to expand into MCAS without
  patient recruitment.

## 7. Suggested contact targets

(For our own outreach planning — not a directive to the partner.)

### Academic / non-profit
- US: NIH NIAID mast cell biology branch (Metcalfe lab alumni network),
  Cem Akin (Michigan), Lawrence Afrin (private, but maintains academic
  collaborations), Joshua Milner (Columbia).
- EU: Frank Siebenhaar (Charité Berlin), Marcus Maurer (Charité),
  Hans Jürgen Hoffmann (Aarhus), Marek Jutel (Wrocław).
- Patient-org adjacencies: TMS for a Cure (US), MCAS Hope.

### CRO
- **Mast-cell-specific:** Indiana Biosciences Research Institute,
  Charles River (Discovery Boston), Eurofins Cerep, Cyprotex,
  Reaction Biology, SB Drug Discovery.
- **Generic + qualified:** Reaction Biology, Eurofins DiscoverX,
  Bienta (Enamine sister CRO, would simplify supply chain).

### Industry
- **MCAS-active pharma:** Blueprint Medicines (avapritinib /
  bezuclastinib developer), Cogent Biosciences (bezuclastinib),
  Allakos.

For each, a "this is the same packet you got 10 of last week — here's
what's different" cover paragraph. The differentiator: **pre-registered**,
**reproducible**, **open**, **patient-grounded**.

## 8. Cover-email template

> Subject: 3-compound β-hex pilot — pre-registered, REAL-procurable, MCAS-targeted
>
> Hi [Name],
>
> I lead OpenMCAS, an open-source MCAS/MCAD compound-discovery
> pipeline (https://github.com/mrdulasolutions/MCAS.Opensource —
> 16 experiments published, viewer at
> https://huggingface.co/spaces/MRDula/openmcas-browser). We have a
> pre-registered β-hex / LAD2 pilot ready to run on 3 novel
> sulforaphane-class isothiocyanates — REAL-Space-procurable, with
> a locked dose response and FDR-controlled stats.
>
> The pre-registration:
> https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/wet-lab-preregistration-v1.md
>
> The candidate list:
> https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/outputs/exp_017/procurement_packet.md
>
> I'd love a quote, or a "not us, try [X]" — both are useful.
> Everything is MIT/CC-BY; no NDAs, no IP transfer, full publication
> rights regardless of result.
>
> Happy to jump on a 20-minute call to walk through it.
>
> Best,
> [signature — see CONTACT.md]

## 9. Pipeline → wet-lab handoff diagram

```
EXP-001 → EXP-013       generation:    SFN seeds + BRICS + RL → 265 novel analogs
EXP-002 → EXP-005       scoring:       8 targets × ligand similarity → composite
EXP-009 + EXP-012       physics:       Vina + C151 covalent proxy
EXP-011 + EXP-016       data:          ChEMBL pIC50 + mast-cell predictor
EXP-006 → EXP-015       audit:         recovery + negatives + sensitivity + retread
EXP-017                 procurement:   REAL-Space envelope + lookup URLs
─────────────────────────────────────────────────────────────────────
docs/wet-lab-preregistration-v1.md     pre-reg:      3 compounds, locked protocol
EXP-018 (to be created)                wet lab:      β-hex / viability / HMOX1
```

## 10. License + use grant

This packet, the pre-registration, the procurement list, and the full
pipeline are MIT-licensed. Wet-lab data generated under this protocol
should be released CC-BY-4.0 or more permissive.

If the wet-lab partner's institution requires a different license,
talk to us first — we will not silently accept restrictive terms.

— OpenMCAS, 2026-05-23
