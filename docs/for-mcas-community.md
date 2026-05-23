# OpenMCAS — for the MCAS / MCAD community

> ⚠️ **This is not medical advice.** It is a plain-language summary of
> a research project. Nothing here recommends self-experimentation,
> changing your medications, or starting any supplement. Always work
> with a clinician who knows mast cells. See
> [`docs/disclaimers.md`](disclaimers.md).

## What is OpenMCAS in one sentence

It's an open, free, public project that uses computers and AI to look
for compounds — drugs, herbs, supplements, or never-before-made
molecules — that might help with mast cell activation syndrome,
**so that real researchers and labs can decide what to test next.**

## What it isn't

- It is **not** a treatment.
- It is **not** a doctor.
- It is **not** an app that picks medication for you.
- It does **not** sell anything.
- It does **not** collect your data unless you choose to share an
  observation through a public GitHub issue.

## Why this project exists

If you have MCAS or MCAD you already know:

- You are often on a stack of four or five drugs and still flaring.
- Standard rescue (Benadryl, hydroxyzine, chlorpheniramine) helps
  acutely but has long-term costs — anticholinergic burden, brain
  fog, drug tolerance.
- The maintenance drugs (cromolyn, montelukast, ketotifen, H1/H2
  blockers) work for many people but don't cure anything; you stay
  on them indefinitely.
- There is **no FDA-approved drug that turns off the underlying
  hypersensitivity.** Avapritinib and bezuclastinib are approved for
  systemic mastocytosis, not non-clonal MCAS.

That last gap — the *remission* drug — is what this project is
trying to find. Specifically, we are looking for compounds that
**reduce mast-cell hypersensitivity at the source** instead of
blocking the chemicals mast cells release after they've already
fired.

## What we have found so far

The pipeline keeps surfacing the same family of natural compounds
at the top of the **remission** category:

- **Sulforaphane** — broccoli sprout compound, formed from
  glucoraphanin by the enzyme myrosinase.
- **Erucin** — sulfide form of sulforaphane, found in arugula,
  cabbage; the body converts it back and forth with sulforaphane.
- **Phenethyl isothiocyanate (PEITC)** — found in watercress.
- **Iberin** — found in horseradish, cabbage.
- **Benzyl isothiocyanate** — found in garden cress, papaya seeds.

They all share a chemical group called an **isothiocyanate**, which
chemists know reacts gently and permanently with one specific spot
on a protein called KEAP1. When that spot reacts, KEAP1 lets go of
another protein called Nrf2, which then turns on the body's
antioxidant defense system.

In plain words: **these molecules quietly retune the dial that
controls how easily a mast cell decides to fire.** They don't block
histamine — they make the cell less twitchy in the first place.

## Why we haven't told you to eat broccoli sprouts

You may already be doing this. Many MCAS patients try sulforaphane
supplements. Some report help, some report worsening (sulfur foods
can be triggers, like all cruciferous vegetables), some report
nothing.

There are three honest reasons we are NOT recommending this:

1. **Computer predictions are not human evidence.** Even our best
   predictor (the mast-cell stabilizer model, which beats every
   other model in our project at AUC 0.916) is still a model. It
   has been wrong before and will be again. Until a real mast-cell
   lab tests these compounds on real human mast cells, the
   predictions are *hypotheses*, not facts.
2. **Sulforaphane supplement quality is wildly variable.** Most
   "sulforaphane" pills on the market actually contain
   glucoraphanin — the precursor — and rely on your gut bacteria
   to convert it. If your gut is dysbiotic (very common in MCAS),
   the conversion rate is unpredictable.
3. **Sulfur compounds are themselves a known MCAS trigger
   category.** Garlic, onion, broccoli, and other sulfur-rich foods
   are on many MCAS food-trigger lists. If sulforaphane works for
   some patients and triggers others, the answer is probably
   subgroup-specific — and the *only* way to find out which subgroup
   is which is real research, not anecdote.

## What we are doing next

1. **Pre-registered wet-lab test.** We have written and publicly
   posted ([wet-lab-preregistration-v1.md](wet-lab-preregistration-v1.md))
   the exact protocol a lab would run to test three brand-new
   sulforaphane-class compounds against human mast cells (the LAD2
   cell line). The protocol is locked. Whatever the lab finds —
   positive, negative, mixed — gets published.
2. **CRO outreach.** We are sending the protocol and the candidate
   list ([procurement_packet.md](../outputs/exp_017/procurement_packet.md))
   to mast-cell-capable contract research organizations and academic
   labs.
3. **Negative results are a win, too.** If the compounds don't work,
   that is a real finding — it eliminates a wrong direction and
   refines the search. We will publish either way.

## How you can help (no spending required)

- **Share what helps you and what doesn't.** Use the GitHub issue
  template at
  [`Compound response observation`](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new/choose).
  You can use a pseudonym. You don't need to share names, dates,
  diagnoses, or any health info you're not comfortable making
  public.
- **Tell a clinician about us.** Especially mast-cell-knowledgeable
  allergists, immunologists, hematologists. If your clinician would
  consider running a β-hex pilot, point them at
  [`docs/cro-outreach-packet.md`](cro-outreach-packet.md).
- **Spread the word in MCAS communities** (r/MCAS, TMS for a Cure,
  MCAS Hope, Mastocytosis Society, your local support group).
  Honest, skeptical engagement is more useful to us than
  cheerleading.
- **Read the experiments.** Each one ([experiments/](https://github.com/mrdulasolutions/MCAS.Opensource/tree/main/experiments))
  is written to be readable by a motivated non-scientist. If a
  section isn't clear, file an issue — we'll fix the wording.

## How we promise to behave

- We don't sell, we don't collect, we don't lobby.
- We don't patent compounds (everything stays open).
- We don't run closed forks, embargoed results, or paywalled
  studies.
- We publish negative results.
- If a method is wrong, we say so and fix it (we have already done
  this three times — see EXP-009 §"Disclosure" for an example).

## How we won't behave

- We won't tell you to take any compound.
- We won't suggest you stop your prescriptions.
- We won't post you a curated "MCAS protocol" of supplements.
- We won't accept funding that comes with publication restrictions.
- We won't pretend the pipeline is more certain than it is.

## Where to find everything

- **Project home:** https://github.com/mrdulasolutions/MCAS.Opensource
- **Live viewer (no install):** https://huggingface.co/spaces/MRDula/openmcas-browser
- **Experiments:** https://github.com/mrdulasolutions/MCAS.Opensource/tree/main/experiments
- **Disclaimers (read once):** [`docs/disclaimers.md`](disclaimers.md)
- **Glossary (when a word stumps you):** [`docs/glossary.md`](glossary.md)
- **Contact:** [`CONTACT.md`](../CONTACT.md)

## A note from the project lead

I have MCAS. I've been on chronic buccal diphenhydramine for five
years for breakthrough flares. I built this project because the
existing tools for finding upstream MCAS therapies are either
behind paywalls, behind pharma, or behind the language barrier of
academic chemistry. None of them are accountable to patients.

OpenMCAS is — at least, that's the standard we're trying to hold
it to. If we fall short, please file an issue and tell us how.

— OpenMCAS
