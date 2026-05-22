---
id: EXP-014
title: Chronic rescue dependency — patient-reported survey on long-term first-gen H1 use
status: running
hypothesis_category: methodology
run_date: 2026-05-22
authors:
  - name: MR Dula Medical
    role: provider
    affiliation: "DBA of MR Dula Enterprise, LLC; Raleigh, NC, USA"
  - name: OpenMCAS contributors
    role: maintainer
license: MIT
---

# Chronic rescue dependency — surveying the gap our composite ranking missed

> ⚠️ **Not medical advice.** This is a research experiment. Participation
> is anonymous. Nothing in this experiment recommends or implies any
> particular protocol for any individual.

## Headline

Anecdotal pattern surfaced via repo Issue #1: **a non-trivial fraction
of MCAS patients have been using daily fast-onset first-gen H1
rescue (typically diphenhydramine via buccal / sublingual route) for
multiple years**, often because no other tool reliably stops their
reactions in <15 minutes.

The composite ranking in EXP-005 doesn't capture this. Our rescue
top-5 leads with second-gen H1s (Fexofenadine, Cetirizine) which are
the *daily-use-safe* choices — but for patients in chronic-rescue
dependency, the existing protocol is **already a maintenance protocol
in disguise**, and the right framing isn't "which rescue compound is
best by composite" but "how do we move this patient from chronic
high-burden rescue to lower-burden maintenance + remission?"

This experiment surveys patient-reported patterns to answer:

1. How common is multi-year daily first-gen H1 dependency in the
   MCAS community?
2. What protocols have patients successfully transitioned to (and
   from)?
3. What underlying drivers (post-viral, mold, clonal, gut) correlate
   with successful transition?

## 1. Hypothesis

> A meaningful fraction of patients with severe MCAS who use daily
> fast-onset first-gen H1 rescue (diphenhydramine, hydroxyzine) via
> buccal / sublingual / IM route can transition to lower-burden
> protocols (second-gen H1 backbone + maintenance stack +
> remission-axis intervention) — and the patient-reported patterns of
> *what worked* are informative about which mechanistic subtypes of
> MCAS respond to which protocol changes.

Falsifiable: if survey responses show no consistent pattern across
successful transitions (i.e., outcomes are random with respect to
intervention class), the framework's "three-layer off-ramp" is not
useful guidance.

## 2. Method

Observational — anonymous patient survey via GitHub issues.

### 2.1 Data collection

Patients self-identify via the
[response observation issue template](../.github/ISSUE_TEMPLATE/response_observation.md)
with these additional fields recommended:

- **Years of daily/regular first-gen H1 use**: <1 / 1-3 / 3-5 / 5-10 / 10+
- **Route(s) primarily used**: oral swallow / buccal / sublingual / IM / IV / mixed
- **Estimated daily dose range**: 25mg / 50mg / 100mg / >100mg
- **Concurrent anticholinergic burden**: any other anticholinergic
  meds (yes/no/list categories — not specific names)
- **Cognitive symptoms (subjective)**: none / mild / moderate / severe
- **Anticholinergic burden symptoms**: which clusters
- **Reduction or transition attempted?**: yes/no
- **If yes, what worked**: switched to second-gen / sublingual ketotifen /
  cromolyn / omalizumab / GLP-1 RA / KIT inhibitor / sulforaphane /
  trigger elimination / multi-modal
- **Underlying driver identified**: post-viral / mold / gut / clonal
  KIT / unclear / not investigated
- **Time horizon of successful transition**: weeks / months / >1 year

### 2.2 Inclusion criteria

- Self-report of MCAS / MCAD diagnosis OR consistent symptom pattern
- ≥1 year of regular first-gen H1 use
- Willingness to share pattern (no PHI required)

### 2.3 Analysis plan

Once n ≥ 30 responses:

1. Cross-tabulate transition success by intervention class.
2. Survival curve: time-to-transition-attempt-success vs.
   pre-transition use duration.
3. Subtype analysis: which underlying drivers correlate with which
   successful protocols.
4. Confidence intervals on each pattern using Wilson score interval
   (small-n appropriate).

### 2.4 Pre-registration commitment

- This experiment is pre-registered before data collection. The
  analysis plan above is fixed; we will not change it after data
  comes in.
- Negative or null results will be reported on the same timeline as
  positive results.
- Raw response data (anonymized) will be published as
  `outputs/exp_014_survey_responses.csv` when n ≥ 30.

## 3. Inputs

| Input | File / reference |
|-------|------------------|
| Survey instrument | [`.github/ISSUE_TEMPLATE/response_observation.md`](../.github/ISSUE_TEMPLATE/response_observation.md) |
| Background framework | [Wiki: Chronic First-Gen H1 Use](https://github.com/mrdulasolutions/MCAS.Opensource/wiki/Chronic-First-Gen-H1-Use) |
| Anchor case | [Issue #1](https://github.com/mrdulasolutions/MCAS.Opensource/issues/1) |

## 4. Parameters

This is a community-data experiment, not a script. There is no `python
scripts/x.py` command. The "parameters" are the survey questions in
§2.1 and the inclusion criteria in §2.2.

## 5. Environment

n/a — observational survey.

## 6. Outputs (planned)

| File | Description |
|------|-------------|
| `outputs/exp_014_survey_responses.csv` | Anonymized per-respondent pattern data (will be written when n ≥ 30) |
| `outputs/exp_014_summary.md` | Findings + cross-tabulations + confidence intervals |

Schema: `response_id, years_of_use, route, dose_range, ACB_class,
cognitive_symptom_class, attempted_transition, transition_class,
transition_success, underlying_driver, time_horizon, free_text_quote`.

## 7. Interpretation (pending)

To be filled in when data is available. This is a `status: running`
experiment.

The headline hypotheses that data will test:

- **H1.** Most chronic first-gen H1 users have NOT had a structured
  maintenance + remission workup. → If true, the off-ramp framework
  is under-deployed, not unsuccessful.
- **H2.** Among patients who DID attempt structured transition,
  multi-modal protocols (maintenance + remission together) succeed
  more often than single-component swaps. → If true, "switch
  rescue compound" alone is the wrong intervention; the underlying
  driver must be addressed.
- **H3.** Patients with identified underlying driver (mold,
  post-viral, clonal KIT) have higher successful-transition rates
  than patients with unclassified MCAS. → If true, diagnostic
  workup precision matters for transition feasibility.

## 8. Reproduction

n/a until data collection completes. After completion, raw
anonymized data will be published in this repo for independent
re-analysis.

## 9. Limitations

- **Self-selection bias.** Patients motivated to find a wiki + GitHub
  issue and submit a structured report are not a random sample.
- **Self-report inaccuracy.** "Successful transition" is patient-
  defined, not clinically validated.
- **Small expected n.** GitHub issue intake will likely yield n <
  100 even over a year. Statistical power is for direction-of-effect,
  not precise magnitude.
- **No clinician validation.** Each report is a single patient's
  account; we do not verify diagnoses or claims.
- **Underlying-driver self-classification** is approximate.

These limitations are real and explicit. The experiment isn't trying
to be a clinical trial; it's trying to surface patterns the framework
predicts.

## 10. Next experiments suggested

1. Once n ≥ 30: write up findings as EXP-015 (interpretation).
2. If patterns suggest a specific protocol succeeds, draft a wet-lab
   pre-registration for a CRO-run validation campaign on the relevant
   compound combination.
3. Build a structured-intake web form (beyond GitHub issues) for n
   scaling — coordinate with the patient-data infrastructure roadmap
   item.

## 11. References

- Anchor case: [Issue #1 — Buccal diphenhydramine ~10 min onset](https://github.com/mrdulasolutions/MCAS.Opensource/issues/1) and follow-up comment thread.
- Framework documentation: [Wiki: Chronic First-Gen H1 Use](https://github.com/mrdulasolutions/MCAS.Opensource/wiki/Chronic-First-Gen-H1-Use).
- Composite ranking limitation acknowledged in: [`hypotheses/rescue.md` — Route of Administration section](../hypotheses/rescue.md#route-of-administration-matters-as-much-as-compound-choice).
- Linked experiments: [EXP-005](EXP-005-multi-objective-ranking.md),
  [EXP-006](EXP-006-known-actives-recovery.md).
