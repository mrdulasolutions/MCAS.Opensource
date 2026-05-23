# Wet-lab pre-registration v1 — OpenMCAS β-hex / LAD2 pilot

> ⚠️ **Not medical advice.** This document pre-registers an in-vitro
> research protocol for academic / CRO use under appropriate oversight.
> It does not authorize human use or self-experimentation. See
> [docs/disclaimers.md](disclaimers.md).

**Status:** pre-registered — not yet run.
**Pre-registration date:** 2026-05-23.
**Tied experiment slot:** `EXP-018-real-wet-lab-pilot.md` (file to be
created on first data drop).
**Pipeline commit at pre-registration:** captured in
`outputs/exp_017/preregistration.commit` on freeze.

## 1. Why pre-register

Pre-registration commits this protocol — hypotheses, comparators, dose
range, primary readout, success criteria, statistical analysis — to the
public record **before** the wet lab runs. Anything reported afterward
that diverges from this document must be flagged as exploratory, not
confirmatory.

This is the same standard we'd apply to a clinical trial — and the
reason the OpenMCAS pipeline can claim "validated" rather than "scored"
when a compound moves.

## 2. Hypotheses

### Primary

**H1 — Sulforaphane class advantage.** At least one of the three
selected REAL-Space-plausible novel SFN-class analogs from EXP-017
(top-20 list) will produce ≥ 30% inhibition of β-hexosaminidase release
in human mast cells (LAD2) under substance-P stimulation at a
concentration ≤ 10 µM, matching or exceeding the inhibition produced
by 10 µM sulforaphane (positive control of the SFN class).

### Secondary

- **H2 — Specificity of stabilization.** The three novel analogs will
  produce minimal inhibition (< 20%) of LAD2 viability at the assay
  concentration, confirming the β-hex effect is stabilization rather
  than cytotoxicity.
- **H3 — Class discrimination.** Cetirizine (10 µM) will NOT inhibit
  β-hex release > 20% in substance-P–triggered LAD2 (substance P acts
  through MRGPRX2, downstream of histamine receptors).
- **H4 — Nrf2 engagement.** At a 24 h pre-incubation timepoint, the
  novel analogs will induce HMOX1 mRNA ≥ 3× relative to vehicle
  control, consistent with KEAP1-C151 modification (mechanism
  predicted by EXP-009 + EXP-012).

### Falsification

H1 is falsified if **none** of the three novel analogs reaches 30%
β-hex inhibition at ≤ 10 µM and Sulforaphane positive control still
hits its expected ≥ 40% inhibition (i.e., the assay worked, the
analogs failed). That would mean the SFN-class scaffold is not
trivially extensible to the chemistry our generator produced and
the pipeline's analog campaign needs revisiting.

## 3. Selection criteria for the 3 candidates

To be locked in **before** procurement quotes come back:

1. Must appear in `outputs/exp_017/enamine_lookup.csv` with
   `real_space_plausible = True`.
2. Must have parent_seed metadata or RL provenance traceable to the
   SFN class (covalent ITC warhead retained).
3. Must span at least 2 distinct sub-scaffolds (e.g., not three close
   chain-length variants of the same Erucin-extension; we want
   discrimination, not redundancy).
4. Procurement quote ≤ $1k each at ≥ 5 mg, ≥ 95% purity.

If 4 cannot be met for any three at once, **stop and renegotiate** —
do not silently substitute.

The three locked-in candidates and their procurement quotes will be
recorded in `EXP-018-real-wet-lab-pilot.md` §3 before assay start.

## 4. Comparators

| Role | Compound | Source | Conc. |
|------|----------|--------|-------|
| Positive (SFN class) | Sulforaphane | Sigma S6317 | 10 µM |
| Positive (cromone class) | Cromolyn sodium | Sigma C0399 | 100 µM |
| Negative (H1, not stabilizer) | Cetirizine | Sigma C3618 | 10 µM |
| Cytotoxicity control | Triton X-100 | — | 0.1% (lysis, 100% release reference) |
| Vehicle control | DMSO | — | 0.1% final |

## 5. Cell system

- **LAD2** human mast cell line, NIH MTA.
- Passage ≤ 20.
- StemPro-34 + 100 ng/mL rhSCF, 37 °C / 5% CO₂.
- Mycoplasma-tested within 30 days of assay.
- ≥ 95% viability (trypan blue) before each plating.

## 6. Stimulus

Substance P (Sigma S6883), 10 µM final, 30-min incubation post-compound.

Rationale: substance P triggers MRGPRX2 — the receptor most relevant
to non-IgE MCAS triggers (opioids, contrast media, certain antibiotics).
Anti-IgE crosslinking is a valid alternative but is less relevant to
the MCAS hypothesis space we score against.

## 7. Dose range

Six points per compound: **0.1, 0.3, 1, 3, 10, 30 µM**.

DMSO held constant at 0.1% across all wells. Each point: ≥ 3 technical
replicates, ≥ 3 biological replicates (separate passages on separate
days).

## 8. Readouts

### 8.1 Primary — β-hexosaminidase release

Plate-based fluorometric, 4-methylumbelliferyl-N-acetyl-β-D-glucosaminide
substrate, 1 h 37 °C, glycine pH 10 stop, read at 360/450 nm.

% release = (supernatant fluorescence − vehicle) / (Triton − vehicle).

### 8.2 Secondary — viability

CellTiter-Glo or equivalent ATP assay on a parallel plate at the same
24 h pre-incubation timepoint. Reject any β-hex data point where
viability < 80% of vehicle.

### 8.3 Secondary — HMOX1 induction (H4)

qPCR on RNA harvested 24 h post-compound (separate plate). HMOX1
relative to GAPDH or ACTB. ΔΔCt vs. vehicle.

## 9. Statistical analysis (locked)

- Dose-response curves fit with 4-parameter logistic (Hill).
- IC50 reported with 95% bootstrap CI (1000 resamples).
- Primary test for H1: one-sided Mann-Whitney U comparing % inhibition
  at 10 µM between (each novel analog) and vehicle, with
  Benjamini-Hochberg FDR ≤ 0.05 across 3 analogs.
- For H4: paired t-test on log₂ fold-change vs. vehicle within each
  biological replicate, FDR ≤ 0.05.

## 10. Stopping rules

- **Assay invalid** if Sulforaphane positive control does not reach
  ≥ 40% β-hex inhibition at 10 µM — report and do not interpret
  novel-analog data from that experiment.
- **Cytotoxic compound flagged** if viability < 80% at ≤ 3 µM —
  remove from dose-response, report toxicity, do not retest at higher
  doses.
- **All 3 fail H1 at ≤ 10 µM** — proceed to publish the negative
  result. Do NOT increase dose to chase a hit; that's HARKing.

## 11. What gets published either way

A negative result is publishable. The EXP-018 report will land
regardless of outcome, with:

- The locked candidate list (§3).
- The procurement audit trail (quote PDFs hashed and stored).
- All raw plate data in `outputs/exp_018/raw/`.
- Curves, IC50s, statistical results in `outputs/exp_018/analysis/`.
- A clear statement of which pre-registered hypotheses were
  supported, falsified, or inconclusive.

## 12. Authorship + funding declaration template

- **Wet-lab institution:** TBD (CRO or academic collaborator).
- **Reagent sources:** declared per compound in §4 + §3.
- **Funding:** none unless a sponsor steps forward; if so, declared
  here before any assay starts.
- **Conflicts of interest:** none in the pipeline authorship as of
  this pre-registration (see `CONTACT.md`).

## 13. Amendments

Amendments to this pre-registration must be added below this line
with a date stamp and the commit hash of the change. Do NOT edit
above this line silently.

— end of locked text —

## 14. Pre-registration sign-off

This document is committed to the public OpenMCAS repository under
MIT license at commit hash (filled by `git log -1` on the merge that
introduces this file). Any wet-lab partner running this protocol
agrees to:

1. Report the result publicly, regardless of direction.
2. Cite this pre-registration commit in any preprint or publication.
3. Make raw data available under CC-BY-4.0 or more permissive.

If those terms are unacceptable, fork the pre-reg and run a separate
protocol — do not run this one.

— OpenMCAS, 2026-05-23
