# Route of administration — why the *same* compound behaves very differently

> ⚠️ **Not medical advice.** Pharmacology primer for researchers and educated
> patients. Always discuss route changes with a mast-cell-knowledgeable
> clinician. See [docs/disclaimers.md](disclaimers.md).

For acute mast-cell reactions, **how** you deliver a rescue compound is
often as important as **which** compound you pick. Standard oral
swallow can be too slow when reactions are stopping in minutes. This
doc covers the major alternative routes, their physicochemistry, and
which compounds in our library are plausibly suited to each.

## The five-second summary

| Route | Onset | Avoid first-pass? | Best for compounds with… |
|-------|-------|-------------------|---------------------------|
| Oral (swallowed) | 30–180 min | No | Anything; default |
| **Buccal** (between cheek + gum) | **5–15 min** | **Yes** | Small + lipophilic + neutral / single-charge |
| **Sublingual** (under tongue) | 5–15 min | Yes | Same as buccal; usually faster onset |
| Nasal | 5–30 min | Mostly | Polar / formulated for mucosal absorption |
| Inhaled | 1–10 min | Yes | Volatile / aerosolized / cromone-class |
| Subcutaneous / IM injection | 5–30 min | Yes | Engineered for injection (epinephrine, omalizumab) |
| IV (clinical) | seconds | Yes | Hospital-grade |
| Rectal | 15–60 min | Partial | GI-active compounds; bypasses oral mucosa |

## What makes a compound good for buccal / sublingual rescue

The buccal mucosa and sublingual region are thin, highly vascular
membranes with a venous drainage that goes **straight to systemic
circulation** — skipping the liver entirely (no first-pass
metabolism). For a compound to absorb fast across this membrane it
helps to be:

1. **Small** — MW < 500 Da. Hard cap around 700 Da.
2. **Lipophilic enough to cross the lipid bilayer** — `logP` ideally
   in the 1–3 range.
3. **Not strongly charged at oral pH (~6.8)** — neutral or weakly
   ionized molecules diffuse much faster. Strong acids / strong bases
   / permanent zwitterions stay in the saliva.
4. **Not a P-glycoprotein efflux substrate** — P-gp pumps molecules
   back out of mucosal cells before they reach circulation.
5. **Stable to saliva** — won't be destroyed by salivary amylase /
   peptidases over the 5–15 min residence time.

## Library compounds rated for buccal absorption potential

These are **physicochemistry-derived predictions**, not clinical
recommendations. They are based on the published properties + our
QSAR layer (`outputs/qsar_predictions.csv`). A high BBB-penetration
prediction is a useful proxy because the same chemistry that lets a
molecule cross the blood-brain barrier also lets it cross buccal
mucosa.

### 🟢 Plausibly buccal-friendly

| Compound | MW | logP | BBB (QSAR) | Why |
|---|---|---|---|---|
| **Diphenhydramine** | 255 | 3.3 | **1.00** | Small, lipophilic, single tertiary amine. Anecdotal patient reports of fast buccal rescue are physicochemistry-consistent. |
| Hydroxyzine | 374 | 2.7 | 0.94 | Bigger but still BBB-penetrant. Similar first-gen profile. |
| Doxepin | 279 | 3.4 | high | TCA with strong H1+H2 antagonism. Already used sublingually in some formulations (e.g. Silenor for insomnia uses a low-dose oral; clinical sublingual would be off-label). |
| Ketotifen | 309 | 3.0 | 0.91 | Dual H1 + mast cell stabilizer. Reasonable buccal candidate. |
| Cetirizine | 388 | 1.7 (zwitterion) | 0.33 | **Borderline.** It's small enough but the carboxylic acid creates a zwitterion that resists passive diffusion. Some absorption possible but onset would be slower than diphenhydramine. |
| Quercetin | 302 | 1.5 | 0.61 | Polyphenol. Bioavailability is the headline issue — phytosomal formulations (Quercefit etc.) are designed to improve it. Buccal route plausibly useful. |
| Luteolin | 286 | 2.5 | 0.54 | Smaller / more lipophilic than quercetin. Plausibly buccal-friendly. |
| **Sulforaphane** | 177 | 0.7 | **0.92** | Small + volatile + lipophilic. Already absorbed sublingually from chewed broccoli sprouts. |

### 🔴 Not expected to be buccal-friendly

| Compound | MW | logP | BBB (QSAR) | Why |
|---|---|---|---|---|
| **Fexofenadine** | 502 | 2.8 (zwitterion) | **0.12** | At the size cutoff, zwitterionic, and a known P-glycoprotein substrate. Engineered to be peripherally-restricted. Slower onset by all routes. Crushing + gumming would not give the same fast onset as diphenhydramine — the chemistry is opposite. |
| Loratadine / Desloratadine | 311 / 311 | 5.2 | 0.33 | Lipophilic enough but second-gen H1s are engineered for slow/sustained release. |
| Cromolyn sodium | 468 | -1.9 | 0.71 (proxy) | Polar disodium salt. **Poorly absorbed by any oral route.** Designed for inhaled / topical use. Oral cromolyn (Gastrocrom) works because it acts *locally* on GI mast cells, not because it's absorbed. |
| Montelukast | 586 | 8.8 | 0.77 | Too large + too lipophilic. Designed for once-daily oral. |
| Omalizumab | ~149 kDa | n/a | n/a | Antibody. Subcutaneous injection only. |
| Semaglutide / Tirzepatide | ~4.1 kDa | n/a | n/a | Peptides. Injection or specialized oral formulation (semaglutide has the SNAC permeation enhancer for one specific product). |

## Per-compound buccal physicochemistry tags in `seeds.json`

The library now carries a `route_recommended` field on small molecules
where the chemistry strongly supports or contraindicates a route. See
[`data/compounds/seeds.json`](../data/compounds/seeds.json).

## Why this matters for our rescue ranking

The composite ranking in `rank_hypotheses.py` does NOT currently
weight route-of-administration. A compound that ranks #1 for rescue
by composite (Fexofenadine at the time of writing) is **not
necessarily the right rescue compound at the right route for a given
flare timeline**. A patient who needs reactions stopped in 10 minutes
may correctly be using a lower-composite-ranked but buccal-friendly
compound.

**This is an explicit limitation of the ranking, and we will not
"fix" it by adding a route weight** — because the right route is
genuinely patient-specific (which mucosa is accessible, what
formulation is available, what side effects are tolerable). Instead,
the per-compound `route_recommended` tag and this doc surface the
information so a clinician + patient pair can make the call.

## Routes we are NOT covering and why

- **Intramuscular epinephrine** — this is the universal first response
  to anaphylaxis. If you carry epi, use epi; nothing in this doc
  changes that. The compounds covered here are adjuncts.
- **Rectal / suppository** — under-discussed but real for pediatric
  + perioperative use. We don't have specific compound data for it
  yet. Open an issue if you have a use case.
- **Inhaled cromolyn / nedocromil** — clinical use is well-established
  for asthma; off-label use for MCAS pulmonary symptoms is common.
  Out of scope for this doc but a candidate for a follow-up wiki page.

## Anonymous reports welcome

If you have a route + compound + onset pattern that has worked or
hasn't worked for you, please submit a
[response observation](../.github/ISSUE_TEMPLATE/response_observation.md).
Anonymous by design. We aggregate the patterns; no PHI.

## References

- Madhav NVS, Shakya AK, Shakya P, Singh K. *Orotransmucosal drug
  delivery systems: A review.* J Controlled Release 2009.
- Patel VF, Liu F, Brown MB. *Advances in oral transmucosal drug
  delivery.* J Controlled Release 2011.
- Fexofenadine P-gp efflux: Cvetkovic M et al. *OATP and P-glycoprotein
  transporters mediate the cellular uptake and excretion of
  fexofenadine.* Drug Metab Dispos 1999.
- Buccal histamine antagonist pharmacokinetics: Cooper EC, Robson PJ.
  *Sublingual administration of antihistamines.* Clin Pharmacokinet 2014.
