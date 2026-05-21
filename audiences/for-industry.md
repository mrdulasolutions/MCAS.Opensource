# For industry / pharma / biotech

Short version: this repo is MIT-licensed, patent-incompatible by design,
and exists explicitly so that no MCAS hypothesis here can be closed off
from patients via IP. That's the line. Inside the line, we welcome
industry engagement.

## What you can do

### 1. Use the data
Everything in [`data/`](../data/) and [`outputs/`](../outputs/) is free
to use under MIT. Train your own models on it, cite the commit hash.

### 2. Validate at scale
Industry typically has assay throughput academic labs lack (1k+ compounds
per week on a degranulation panel is routine for a CRO-equipped pharma
team). Running our top-100 ranked compounds through your routine LAD2 /
HMC-1 panel and publishing the results — even as a pre-competitive
disclosure — would be a major contribution.

### 3. Pre-competitive partnership
Some pharma is already pre-competitive on rare-disease infrastructure
(see e.g. SGC for kinase chemical biology). We're open to a similar
posture: industry funds wet-lab validation; the results land in the public
repo with full attribution; nobody acquires exclusive rights to follow-on
work.

### 4. Make-on-demand synthesis (Enamine REAL etc.)
The generated SFN-class analogs in [`outputs/reinvent_generated.csv`](../outputs/reinvent_generated.csv)
are deterministic and reproducible. Many are in scope for Enamine REAL Space
make-on-demand (~$100/compound, 2–4 weeks). If your group already has
catalog credit, running the top-20 through your pipeline and publishing
the QC + assay data would short-circuit a major bottleneck.

## What we will refuse

- IP transfer of any compound, analog, or hypothesis published here.
- Embargoes longer than 90 days on assay results.
- Removing or quietly de-ranking compounds from public view.
- Sponsorship arrangements that would bias the ranking.
- Co-authorship without a contribution traceable to a specific
  `EXP-NNN` report.

## The license logic, explicit

MIT lets you:
- Use, modify, redistribute, build commercial products on top of it.
- Cite + acknowledge.
- Not sublicense in restrictive ways.

MIT does not let you:
- Patent anything derived directly from contributions here — that would
  violate the prior art established by the commit history. Every
  contribution carries a public timestamp under a permissive license,
  which prevents downstream patent claims on the same compound + indication
  combination unless meaningful novel structure/method is added.

If your interest is specifically in patentable novel chemistry built on
top of these public hypotheses (e.g. novel covalent KEAP1 binders with
non-obvious modifications), there's nothing here that prevents that —
but the *starting point* stays public.

## Reach us

The project entity is **MR Dula Medical** (a DBA of **MR Dula Enterprise,
LLC**), Raleigh, NC, USA. Canonical contact directory: [CONTACT.md](../CONTACT.md).

Open an [issue tagged `industry-engagement`](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?labels=industry-engagement)
with the broad strokes. We will publicly post the outline of any
engagement (parties, scope, deliverables) before signing.
