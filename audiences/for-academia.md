# For academic labs

If you're a PI, grad student, post-doc, or lab manager considering using or
collaborating with this project, this page is for you.

## What collaborating looks like

We do **not** want exclusive arrangements, embargoed data, or first-author
gatekeeping. We do want:

- **Pre-registration** of wet-lab campaigns before unblinded results.
- **Public posting** of results, positive or negative, within 90 days of
  the experiment finishing.
- **Author tags** (academic + contributor) in the experiment report and
  any downstream paper.
- **MTA hygiene** — LAD2 from NIAID, HMC-1 from licensed providers, etc.
- **IRB / IBC** for any human or animal work, sourced from the
  collaborating institution.

## What we can offer

1. **A pre-built target index** with UniProt IDs and AlphaFold links:
   [`data/targets/MCAS_Targets.csv`](../data/targets/MCAS_Targets.csv).
2. **A pre-ranked candidate list per category** ready for wet-lab triage:
   [`outputs/ranked_*.csv`](../outputs/).
3. **A standardized experiment report template** that doubles as
   pre-registration:
   [`experiments/EXPERIMENT_TEMPLATE.md`](../experiments/EXPERIMENT_TEMPLATE.md).
4. **A protocol-references doc** with the standard mast-cell readouts:
   [`docs/wet_lab_protocols.md`](../docs/wet_lab_protocols.md).
5. **Open citation** — MIT-licensed code, attribution-friendly. You cite
   the repo + commit hash and we cite your follow-up paper.

## Quick-start collaboration paths

### A. Validate a top-ranked hypothesis at the bench
Run any subset of the top-10 from [`outputs/ranked_remission.csv`](../outputs/ranked_remission.csv)
through the LAD2 β-hex / CD63 / tryptase panel against simulated injury
(H₂O₂ / substance P / LPS / anti-IgE) and report. We will pre-publish your
intended protocol and budget on the repo so funders can see what we're
buying.

### B. Train a better predictor
Pull ChEMBL / PubChem mast-cell assays, train a stronger QSAR than the
RandomForest baseline (EXP-004), and submit it as a new
`scripts/run_qsar_<your-name>.py`. We rerun the ranking with both
predictors and publish the disagreement matrix.

### C. KEAP1 docking
KEAP1 Kelch crystal structures (PDB 4L7B, 5FNQ, 6T7V) + Vina/smina or
CovDock for the top-50 SFN-class candidates. We currently run only
ligand-based similarity — physics would be a real upgrade.

### D. Patient-data partnership
If your group is collecting prospective MCAS cohort data with biomarkers,
we want to discuss a data-sharing structure where (a) patient privacy is
absolute, (b) the hypothesis ranking can be back-tested against real
response patterns, and (c) credit and authorship are explicit upfront.

## Authorship norms

For any paper that uses this repo:

- Cite the repo + commit hash + relevant `EXP-NNN` IDs.
- If you used predictions from a specific experiment, add the experiment's
  contributors to acknowledgments (or co-authorship if the contribution
  was substantial).
- If you generate a new experiment that's substantial work, add it under
  `experiments/EXP-NNN-*.md` and we'll list you as the author.

We never claim authorship on work we didn't do. We expect the same.

## Funding pipelines we'd happily co-apply with

- NIH / NIAID (MCAS, mastocytosis, mast cell biology).
- NSF (cheminformatics / open data infrastructure).
- The Mastocytosis Society research grants.
- Pre-clinical foundations open to patient-led research.
- HHMI / philanthropic foundations interested in open biomedical science.

If you're prepping a grant and want to cite this repo as collaborator
infrastructure, see [`CITATION.cff`](../CITATION.cff) and email us via the
contact in the repo profile.

## Things we cannot do

- Sign exclusivity / embargo agreements.
- Hide negative results.
- Make clinical recommendations.
- Provide cell lines, reagents, or IRB-approved patient data ourselves
  (we don't have a wet lab — yet).

## Reach us

The project entity is **MR Dula Medical** (a DBA of **MR Dula Enterprise,
LLC**), Raleigh, NC, USA. Canonical contact directory: [CONTACT.md](../CONTACT.md).

To start a collaboration conversation, open an [issue tagged `academic-collaboration`](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?template=academic_collaboration.md)
with the broad strokes (your lab, the question you want to ask, what you
can contribute, what you need from us). We respond within a week.
