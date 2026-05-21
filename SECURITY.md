# Security and safety reporting

This project has two kinds of "security" — software security in the
conventional sense, and **patient safety** in the medical-information
sense. We treat both as the highest priority.

## Patient safety reports

If you believe content in this repository could lead patients to harm
themselves — e.g. a compound listed without proper contraindications, a
hypothesis written in a way that reads as clinical recommendation, a
trigger framing that could push patients into unsafe self-experimentation —
**open an issue tagged `safety` immediately**.

We will:
- Acknowledge within 24 hours.
- Hide the offending content (issue / PR / file section) within 48 hours
  if the risk is real and ongoing.
- Publish a public correction with rationale.

Examples of past / hypothetical safety reports:
- "The maintenance.md doc mentions LDN but doesn't flag that it requires
  prescription + clinician supervision."
- "The trigger doc lists aspirin without flagging that NSAID-intolerant
  MCAS patients can have severe reactions."

## Software security

If you discover a vulnerability in any code in this repository (we run
no production services; this is essentially client-side cheminformatics
software), **do not open a public issue**. Instead:

- Open a private GitHub Security Advisory: `Security` tab → `Report a vulnerability`.
- For private channels outside GitHub, see [CONTACT.md](CONTACT.md). The
  responsible entity is **MR Dula Medical** (DBA of MR Dula Enterprise, LLC,
  Raleigh, NC, USA).

We will respond within a week. Critical fixes ship same-day where
possible.

## In scope

- Code in `scripts/`, `notebooks/`, `.github/workflows/`.
- Supply-chain risk (deps in `pyproject.toml`, `requirements-colab.txt`).
- Data integrity in `data/` (SMILES injection, malformed CSVs leading
  to unsafe downstream processing).

## Out of scope

- The accuracy of any prediction in `outputs/`. Predictions are
  hypotheses, not security claims. Use the [hypothesis_proposal](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new?template=hypothesis_proposal.md)
  template for those.
- The robustness of any third-party service we reference (PubChem,
  PyTDC, Colab, Enamine, AlphaFold). Report those upstream.

## Coordinated disclosure

For software vulnerabilities, we follow standard 90-day coordinated
disclosure: report → acknowledge → patch → publish. We will credit
reporters who request it.

## What you'll never be asked for

- Personally identifying patient information.
- Credentials, keys, or tokens.
- Payment.

## What you can rely on

- We do not collect telemetry or analytics.
- The repo has no backend; running scripts/notebooks does not phone home.
- The only network calls are to public scientific APIs (PubChem,
  AlphaFold, PyTDC) and only when explicitly invoked.
