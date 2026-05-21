# FAQ

## Patient + caregiver questions

**Q: Is sulforaphane a treatment for MCAS?**
A: No. Sulforaphane currently ranks first on our **computational hypothesis** for upstream remission. It has never been validated in a clinical trial specifically for MCAS. We are publishing this hypothesis openly so that researchers can validate it. Until that happens, do not interpret this as a treatment recommendation. **Talk to a mast-cell specialist before starting any supplement.**

**Q: Should I eat broccoli sprouts?**
A: Not a question we can answer for you. MCAS patients react to many "healthy" foods, and brassicas (broccoli, cabbage, etc.) trigger flares in some. If you and your clinician decide to trial broccoli-sprout extract, that's a decision between you two — not something this repo prescribes.

**Q: Why isn't there a "Top 10 cures" list?**
A: Because there are no cures yet. Hypothesis-generation isn't curing.

**Q: Where do I find a mast-cell specialist?**
A: The Mastocytosis Society maintains a list at [tmsforacure.org](https://tmsforacure.org). In the UK, [mastcellaction.org](https://www.mastcellaction.org/).

**Q: How can I help if I'm not a scientist?**
A: Two ways. (1) Submit a [trigger report](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?template=trigger_report.md) — anonymous, no PHI required. (2) Suggest a compound a clinician has used with you via [compound suggestion](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?template=compound_suggestion.md). Both contribute directly to refining the ranking.

## Researcher + clinician questions

**Q: How is the composite ranking weighted?**
A: See [EXP-005](../experiments/EXP-005-multi-objective-ranking.md). 0.30 evidence + 0.35 target similarity + 0.10 QED + 0.10 warhead + 0.15 safety + ε BBB context − ε KEAP1-lookalike-no-warhead penalty. Weights are author-chosen, not learned. Sensitivity analysis is on the [roadmap](../ROADMAP.md).

**Q: Why ligand-based screening instead of docking?**
A: CPU-laptop accessibility. Ligand-based screening with curated reference sets produces reproducible, audit-able rankings in seconds on commodity hardware. The output schema is intentionally identical to what physics-based docking would produce, so when Vina/smina/DiffDock runs land (top of the [roadmap](../ROADMAP.md)), they overwrite the `outputs/docking_*.csv` files and the ranking script keeps working unchanged.

**Q: Why KEAP1 instead of Nrf2 (NFE2L2) as the target?**
A: Because that's the actual covalent binding site. Sulforaphane and other electrophiles modify KEAP1 (Q14145) at Cys-151/273/288, which liberates Nrf2 from sequestration. We initially named the target `NFE2L2` (the transcription factor itself), which has no druggable small-molecule pocket. We corrected this in [EXP-002](../experiments/EXP-002-ligand-based-target-screening.md).

**Q: What's the difference between Tanimoto = 1.0 self-match and a real prediction?**
A: A compound that's in both the library AND its target's reference set will trivially score 1.0 against itself. The ranking script knows this and weights by the broader composite. The interesting predictions are the *novel* compounds (generated analogs prefixed `GEN_NNNN`) or the library compounds scoring high against a target they're *not* in the reference set for.

**Q: How do I cite this?**
A: See [CITATION.cff](../CITATION.cff). Cite the repo + the commit hash you used. Quarterly Zenodo DOI snapshots are on the [roadmap](../ROADMAP.md).

**Q: Can I use this in a paper?**
A: Yes. MIT license. We ask only that you cite us and that you publish your follow-on results openly (positive or negative).

**Q: Will you collaborate on a wet-lab campaign?**
A: Yes. See [for-academia.md](../audiences/for-academia.md) for the pathway. Pre-registration before unblinded results is non-negotiable.

## Nonprofit + funder questions

**Q: Are you a 501(c)(3)?**
A: Not yet. We're looking for a fiscal sponsor; see [for-nonprofits.md](../audiences/for-nonprofits.md).

**Q: Where would funding actually go?**
A: In order of leverage: (1) wet-lab validation campaigns ($5–25k each), (2) patient-data infrastructure ($10–40k), (3) cloud compute ($1–10k/yr). Full transparency ledger on the [roadmap](../ROADMAP.md).

## Developer questions

**Q: What Python version?**
A: 3.9+ tested. 3.10+ recommended.

**Q: Do I need a GPU?**
A: No for the core pipeline. Yes for REINVENT 4 RL + DiffDock (Colab GPU is free + sufficient).

**Q: How do I run the whole pipeline?**
A: See [for-developers.md](../audiences/for-developers.md). End-to-end runs in ~3 minutes on a CPU laptop.

**Q: Can I run this in CI / cron?**
A: Yes. The validate workflow already runs on PRs touching `data/`. Expanding CI to cover the full pipeline is on the [roadmap](../ROADMAP.md).

## Press questions

See [for-press.md](../audiences/for-press.md) — quotable framing, caveats, and contact.

## Anything else

Open an [issue tagged `faq`](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?labels=faq) with your question and we'll add it here.
