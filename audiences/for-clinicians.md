# For clinicians

You're managing MCAS / MCAD patients with the tools you have: H1, H2,
leukotriene antagonists, cromolyn, ketotifen, omalizumab in select cases,
and increasingly KIT inhibitors for clonal disease. You know how thin the
evidence base is for everything else.

This repo is a public, MIT-licensed hypothesis-generation layer for what
could come next. Your input shapes whether it's useful or noise.

> ⚠️ Nothing here is a treatment recommendation. See [docs/disclaimers.md](../docs/disclaimers.md).

## See current rankings without cloning the repo

🌐 [huggingface.co/spaces/MRDula/openmcas-browser](https://huggingface.co/spaces/MRDula/openmcas-browser) — read-only Streamlit viewer with per-compound composite, target similarity, warhead status, and predicted hERG / AMES / BBB. Updates whenever the pipeline reruns.

## What you'll get from spending 10 minutes here

- A current snapshot of what AI + ligand-based screening + QSAR + warhead
  analysis suggests for **rescue / maintenance / remission** of MCAS,
  ranked transparently and reproducibly: [`outputs/ranked_*.csv`](../outputs/).
- A pre-computed evidence map: every compound is tagged `high` / `medium` /
  `low` evidence with citations in [`data/compounds/seeds.json`](../data/compounds/seeds.json).
- A mechanism-of-injury and trigger map you can hand a patient to validate
  their own pattern: [`hypotheses/injury_mechanisms.md`](../hypotheses/injury_mechanisms.md),
  [`hypotheses/triggers.md`](../hypotheses/triggers.md).

## Three high-leverage ways to contribute

### 1. De-identified case observations

If you've seen a patient respond (or fail) on a compound or combo, please
submit a [case observation](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?template=compound_suggestion.md).
Anonymized at intake. The aggregate informs ranking weights and surface
patterns nobody can see from single-clinic data.

Useful structure:
- Demographic bucket (age range, sex, MCAS subtype if known)
- Compound / dose / duration
- Effect direction + magnitude (subjective scale acceptable; we have no
  better data yet)
- Side effects encountered
- Caveats

### 2. Push back on the rankings

The composite ranking in [EXP-005](../experiments/EXP-005-multi-objective-ranking.md)
is author-weighted, not learned. If you think the rescue list under-weights
something (e.g. cromolyn's GI utility) or the remission list over-weights
something, open a [hypothesis proposal issue](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?template=hypothesis_proposal.md).
We will rerun the pipeline with your proposed weighting and publish the diff.

### 3. Pre-register a real validation

If you have access to LAD2 or primary human mast cells (or a CRO budget), the
[wet-lab protocol references](../docs/wet_lab_protocols.md) describe the
standard β-hex / CD63 / tryptase panel + simulated injury stimuli (H₂O₂,
substance P, LPS, IgE-crosslink) we'd want to use to validate the top hits.

Pre-register by opening an issue tagged `wet-lab-preregistration` **before**
running — protects against cherry-picking and gives the work credibility.
We'll publish results regardless of direction.

## What you won't be asked to do

- Send PHI. Ever.
- Sign anything that constrains your clinical autonomy.
- Promote any compound to patients. Everything here is hypothesis-stage.
- Pay anything.

## Existing ranked snapshots (live, auto-updated)

- [Rescue — top 10](../hypotheses/rescue.md#top-ai-ranked-candidates)
- [Maintenance — top 10](../hypotheses/maintenance.md#top-ai-ranked-candidates)
- [Remission — top 10](../hypotheses/remission.md#top-ai-ranked-candidates)

Each row carries the QSAR safety filter outputs (hERG / AMES / BBB) so you
can read the predicted liability profile before deciding which to engage with.

## If you want to formally collaborate

See [audiences/for-academia.md](for-academia.md) for the collaboration
pathway — it covers IRB framing, MTA-able cell lines, and authorship norms.

## Reach us

- General clinical input: [open an issue](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new) tagged `clinical-input`.
- Private channel (de-identified case discussion, MTA logistics, IRB
  questions): open an issue requesting a private email handoff and we'll
  reply privately.
