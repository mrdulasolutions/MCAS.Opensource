# EXP-017 — Procurement packet for top generated analogs

**Generated:** 2026-05-23 14:32 UTC  ·  **Pipeline commit:** see `git log` in repo  ·  **License:** MIT (data) / Apache-2.0 (code paths upstream).

## Purpose

This file is a vendor-ready summary of the **top novel SFN-class analogs** from the OpenMCAS generative pipeline (EXP-013 + EXP-001). The intent is to attach this packet to a quote request to Enamine REAL Space, MolPort, and / or eMolecules to verify which structures are commercially procurable (or REAL-on-demand synthesizable) before any wet-lab β-hexosaminidase / LAD2 mast-cell assay is funded.

## What we did vs. what we did NOT do

- ✅ Computed canonical SMILES, InChI, InChIKey, MW, formula, Lipinski compliance, QED, RDKit SA-proxy.
- ✅ Filtered to compounds inside the published Enamine REAL Space envelope (MW 200–500, ≤ 35 heavy atoms, common atoms, SA ≤ 4.5, ≤ 2 stereo centers).
- ❌ **Did NOT** query the Enamine REAL Space catalog directly — there is no public unauthenticated API. The `enamine_real_search` URLs in the CSV are manual lookup links a CRO can click.
- ❌ **Did NOT** confirm catalog presence, in-stock status, or purity grade. Treat every link as a *probe*, not a guarantee.

## Methodology

Top novel analogs (seeds excluded) are sorted by the generative model's composite reward (warhead + QED + SA + seed-similarity + Lipinski). The seed compounds themselves (Sulforaphane, Iberin, Erucin, Sulforaphene, Allyl-ITC, Benzyl-ITC, PEITC) are off-the-shelf from Sigma / TCI / Cayman and are NOT included in this packet.

## Top-20 REAL-Space-plausible candidates

| Rank | SMILES | Formula | MW | QED | SA | Lipinski | Parent seed |
|------|--------|---------|----|-----|----|-----|----|
| 1 | `CCCS(=O)(=O)CCc1ccc(N=C=S)cc1` | C12H15NO2S2 | 269.4 | 0.59 | 1.3 | ✅ | — |
| 2 | `CCCS(=O)(=O)Cc1ccc(N=C=S)cc1` | C11H13NO2S2 | 255.4 | 0.60 | 1.3 | ✅ | — |
| 4 | `CSCCCCCCCN=C=S` | C9H17NS2 | 203.4 | 0.34 | 1.2 | ✅ | — |
| 5 | `CCSCCCCCCCN=C=S` | C10H19NS2 | 217.4 | 0.33 | 1.3 | ✅ | — |
| 6 | `CS(=O)CCCCCCN=C=S` | C8H15NOS2 | 205.3 | 0.36 | 1.4 | ✅ | — |
| 7 | `CCCCS(=O)(=O)CCc1ccc(N=C=S)cc1` | C13H17NO2S2 | 283.4 | 0.57 | 1.4 | ✅ | — |
| 8 | `CCCCS(=O)Cc1ccc(N=C=S)cc1` | C12H15NOS2 | 253.4 | 0.57 | 1.5 | ✅ | — |
| 9 | `CS(=O)CCCCCCCN=C=S` | C9H17NOS2 | 219.4 | 0.36 | 1.5 | ✅ | — |
| 10 | `CCS(=O)CCCCCCN=C=S` | C9H17NOS2 | 219.4 | 0.36 | 1.5 | ✅ | — |
| 11 | `CCS(=O)(=O)CCc1ccc(N=C=S)cc1` | C11H13NO2S2 | 255.4 | 0.60 | 1.3 | ✅ | — |
| 12 | `CCCCS(=O)CCc1ccc(N=C=S)cc1` | C13H17NOS2 | 267.4 | 0.56 | 1.5 | ✅ | — |
| 13 | `CCS(=O)CCCCCCCN=C=S` | C10H19NOS2 | 233.4 | 0.35 | 1.5 | ✅ | — |
| 14 | `CCCCS(=O)(=O)Cc1ccc(N=C=S)cc1` | C12H15NO2S2 | 269.4 | 0.59 | 1.3 | ✅ | — |
| 17 | `CCCS(=O)CCCCCCCN=C=S` | C11H21NOS2 | 247.4 | 0.34 | 1.5 | ✅ | — |
| 18 | `CCSCCCCCCN=C=S` | C9H17NS2 | 203.4 | 0.34 | 1.2 | ✅ | — |
| 19 | `CCCSCCCCCCN=C=S` | C10H19NS2 | 217.4 | 0.33 | 1.3 | ✅ | — |
| 22 | `CCCCS(=O)(=O)/C=C/CCN=C=S` | C9H15NO2S2 | 233.4 | 0.39 | 1.3 | ✅ | — |
| 23 | `CCCS(=O)CCc1ccc(N=C=S)cc1` | C12H15NOS2 | 253.4 | 0.58 | 1.5 | ✅ | — |
| 24 | `CCCCS(=O)/C=C/CCN=C=S` | C9H15NOS2 | 217.4 | 0.37 | 1.5 | ✅ | — |
| 25 | `CCCCS(=O)CCCCCN=C=S` | C10H19NOS2 | 233.4 | 0.35 | 1.5 | ✅ | — |

## Lookup URLs per candidate

Paste these into the vendor's search box. Enamine REAL Space is searched by InChIKey for exact match (REAL-Space members do not always have a CAS or canonical name).

### #1 — `CCCS(=O)(=O)CCc1ccc(N=C=S)cc1`

- **InChIKey:** `PZEAZBOUYRIQSF-UHFFFAOYSA-N`
- **Formula:** C12H15NO2S2, **MW** 269.39, **logP** 2.79
- **Enamine REAL search:** https://newreal.enamine.net/search?query=PZEAZBOUYRIQSF-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCS%28%3DO%29%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCS%28%3DO%29%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=PZEAZBOUYRIQSF-UHFFFAOYSA-N

### #2 — `CCCS(=O)(=O)Cc1ccc(N=C=S)cc1`

- **InChIKey:** `PMPYUIRSJWWWHY-UHFFFAOYSA-N`
- **Formula:** C11H13NO2S2, **MW** 255.36, **logP** 2.75
- **Enamine REAL search:** https://newreal.enamine.net/search?query=PMPYUIRSJWWWHY-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCS%28%3DO%29%28%3DO%29Cc1ccc%28N%3DC%3DS%29cc1
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCS%28%3DO%29%28%3DO%29Cc1ccc%28N%3DC%3DS%29cc1
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=PMPYUIRSJWWWHY-UHFFFAOYSA-N

### #4 — `CSCCCCCCCN=C=S`

- **InChIKey:** `LDIRGNDMTOGVRB-UHFFFAOYSA-N`
- **Formula:** C9H17NS2, **MW** 203.38, **logP** 3.40
- **Enamine REAL search:** https://newreal.enamine.net/search?query=LDIRGNDMTOGVRB-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CSCCCCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CSCCCCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=LDIRGNDMTOGVRB-UHFFFAOYSA-N

### #5 — `CCSCCCCCCCN=C=S`

- **InChIKey:** `PSHWGFUORXYKNB-UHFFFAOYSA-N`
- **Formula:** C10H19NS2, **MW** 217.40, **logP** 3.79
- **Enamine REAL search:** https://newreal.enamine.net/search?query=PSHWGFUORXYKNB-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCSCCCCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCSCCCCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=PSHWGFUORXYKNB-UHFFFAOYSA-N

### #6 — `CS(=O)CCCCCCN=C=S`

- **InChIKey:** `XQZVZULJKVALRI-UHFFFAOYSA-N`
- **Formula:** C8H15NOS2, **MW** 205.35, **logP** 2.03
- **Enamine REAL search:** https://newreal.enamine.net/search?query=XQZVZULJKVALRI-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CS%28%3DO%29CCCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CS%28%3DO%29CCCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=XQZVZULJKVALRI-UHFFFAOYSA-N

### #7 — `CCCCS(=O)(=O)CCc1ccc(N=C=S)cc1`

- **InChIKey:** `PAESGFQQCUAVAV-UHFFFAOYSA-N`
- **Formula:** C13H17NO2S2, **MW** 283.42, **logP** 3.18
- **Enamine REAL search:** https://newreal.enamine.net/search?query=PAESGFQQCUAVAV-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCCS%28%3DO%29%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCCS%28%3DO%29%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=PAESGFQQCUAVAV-UHFFFAOYSA-N

### #8 — `CCCCS(=O)Cc1ccc(N=C=S)cc1`

- **InChIKey:** `QJLNHSUDLHGCIR-UHFFFAOYSA-N`
- **Formula:** C12H15NOS2, **MW** 253.39, **logP** 3.47
- **Enamine REAL search:** https://newreal.enamine.net/search?query=QJLNHSUDLHGCIR-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCCS%28%3DO%29Cc1ccc%28N%3DC%3DS%29cc1
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCCS%28%3DO%29Cc1ccc%28N%3DC%3DS%29cc1
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=QJLNHSUDLHGCIR-UHFFFAOYSA-N

### #9 — `CS(=O)CCCCCCCN=C=S`

- **InChIKey:** `OGYHCBGORZWBPH-UHFFFAOYSA-N`
- **Formula:** C9H17NOS2, **MW** 219.38, **logP** 2.42
- **Enamine REAL search:** https://newreal.enamine.net/search?query=OGYHCBGORZWBPH-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CS%28%3DO%29CCCCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CS%28%3DO%29CCCCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=OGYHCBGORZWBPH-UHFFFAOYSA-N

### #10 — `CCS(=O)CCCCCCN=C=S`

- **InChIKey:** `FJTSCXGBXURGRW-UHFFFAOYSA-N`
- **Formula:** C9H17NOS2, **MW** 219.37, **logP** 2.42
- **Enamine REAL search:** https://newreal.enamine.net/search?query=FJTSCXGBXURGRW-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCS%28%3DO%29CCCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCS%28%3DO%29CCCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=FJTSCXGBXURGRW-UHFFFAOYSA-N

### #11 — `CCS(=O)(=O)CCc1ccc(N=C=S)cc1`

- **InChIKey:** `ZJMBRWWQXMBEGY-UHFFFAOYSA-N`
- **Formula:** C11H13NO2S2, **MW** 255.36, **logP** 2.40
- **Enamine REAL search:** https://newreal.enamine.net/search?query=ZJMBRWWQXMBEGY-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCS%28%3DO%29%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCS%28%3DO%29%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=ZJMBRWWQXMBEGY-UHFFFAOYSA-N

### #12 — `CCCCS(=O)CCc1ccc(N=C=S)cc1`

- **InChIKey:** `NTBOOLJUFBUPQR-UHFFFAOYSA-N`
- **Formula:** C13H17NOS2, **MW** 267.42, **logP** 3.51
- **Enamine REAL search:** https://newreal.enamine.net/search?query=NTBOOLJUFBUPQR-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCCS%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCCS%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=NTBOOLJUFBUPQR-UHFFFAOYSA-N

### #13 — `CCS(=O)CCCCCCCN=C=S`

- **InChIKey:** `FVTXJVCICHVYRB-UHFFFAOYSA-N`
- **Formula:** C10H19NOS2, **MW** 233.40, **logP** 2.81
- **Enamine REAL search:** https://newreal.enamine.net/search?query=FVTXJVCICHVYRB-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCS%28%3DO%29CCCCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCS%28%3DO%29CCCCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=FVTXJVCICHVYRB-UHFFFAOYSA-N

### #14 — `CCCCS(=O)(=O)Cc1ccc(N=C=S)cc1`

- **InChIKey:** `PVINSDFUZKBSAA-UHFFFAOYSA-N`
- **Formula:** C12H15NO2S2, **MW** 269.39, **logP** 3.14
- **Enamine REAL search:** https://newreal.enamine.net/search?query=PVINSDFUZKBSAA-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCCS%28%3DO%29%28%3DO%29Cc1ccc%28N%3DC%3DS%29cc1
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCCS%28%3DO%29%28%3DO%29Cc1ccc%28N%3DC%3DS%29cc1
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=PVINSDFUZKBSAA-UHFFFAOYSA-N

### #17 — `CCCS(=O)CCCCCCCN=C=S`

- **InChIKey:** `DUESPPKXNNIVPO-UHFFFAOYSA-N`
- **Formula:** C11H21NOS2, **MW** 247.43, **logP** 3.20
- **Enamine REAL search:** https://newreal.enamine.net/search?query=DUESPPKXNNIVPO-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCS%28%3DO%29CCCCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCS%28%3DO%29CCCCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=DUESPPKXNNIVPO-UHFFFAOYSA-N

### #18 — `CCSCCCCCCN=C=S`

- **InChIKey:** `MCTGFAZGYCGCLY-UHFFFAOYSA-N`
- **Formula:** C9H17NS2, **MW** 203.38, **logP** 3.40
- **Enamine REAL search:** https://newreal.enamine.net/search?query=MCTGFAZGYCGCLY-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCSCCCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCSCCCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=MCTGFAZGYCGCLY-UHFFFAOYSA-N

### #19 — `CCCSCCCCCCN=C=S`

- **InChIKey:** `GQCQYDWJSHTUGC-UHFFFAOYSA-N`
- **Formula:** C10H19NS2, **MW** 217.40, **logP** 3.79
- **Enamine REAL search:** https://newreal.enamine.net/search?query=GQCQYDWJSHTUGC-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCSCCCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCSCCCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=GQCQYDWJSHTUGC-UHFFFAOYSA-N

### #22 — `CCCCS(=O)(=O)/C=C/CCN=C=S`

- **InChIKey:** `KHOZNHIHNSDYKG-VMPITWQZSA-N`
- **Formula:** C9H15NO2S2, **MW** 233.36, **logP** 2.21
- **Enamine REAL search:** https://newreal.enamine.net/search?query=KHOZNHIHNSDYKG-VMPITWQZSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCCS%28%3DO%29%28%3DO%29%2FC%3DC%2FCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCCS%28%3DO%29%28%3DO%29%2FC%3DC%2FCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=KHOZNHIHNSDYKG-VMPITWQZSA-N

### #23 — `CCCS(=O)CCc1ccc(N=C=S)cc1`

- **InChIKey:** `KIWSHKLQZATRDJ-UHFFFAOYSA-N`
- **Formula:** C12H15NOS2, **MW** 253.39, **logP** 3.12
- **Enamine REAL search:** https://newreal.enamine.net/search?query=KIWSHKLQZATRDJ-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCS%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCS%28%3DO%29CCc1ccc%28N%3DC%3DS%29cc1
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=KIWSHKLQZATRDJ-UHFFFAOYSA-N

### #24 — `CCCCS(=O)/C=C/CCN=C=S`

- **InChIKey:** `PCXNJZYQHPVARW-VMPITWQZSA-N`
- **Formula:** C9H15NOS2, **MW** 217.36, **logP** 2.54
- **Enamine REAL search:** https://newreal.enamine.net/search?query=PCXNJZYQHPVARW-VMPITWQZSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCCS%28%3DO%29%2FC%3DC%2FCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCCS%28%3DO%29%2FC%3DC%2FCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=PCXNJZYQHPVARW-VMPITWQZSA-N

### #25 — `CCCCS(=O)CCCCCN=C=S`

- **InChIKey:** `LKHUPZZHESCXFH-UHFFFAOYSA-N`
- **Formula:** C10H19NOS2, **MW** 233.40, **logP** 2.81
- **Enamine REAL search:** https://newreal.enamine.net/search?query=LKHUPZZHESCXFH-UHFFFAOYSA-N
- **MolPort search:** https://www.molport.com/shop/swl-step-1?compound-smile=CCCCS%28%3DO%29CCCCCN%3DC%3DS
- **eMolecules search:** https://search.emolecules.com/search/#?p=ssr&q=CCCCS%28%3DO%29CCCCCN%3DC%3DS
- **PubChem (already known?):** https://pubchem.ncbi.nlm.nih.gov/#query=LKHUPZZHESCXFH-UHFFFAOYSA-N

## Candidates filtered OUT (and why)

| Rank | SMILES | Reason(s) filtered |
|------|--------|--------------------|
| 3 | `CSCCCCCCN=C=S` | mw_out_of_envelope(189.35) |
| 15 | `CCSCCCCCN=C=S` | mw_out_of_envelope(189.35) |
| 16 | `CSCCCCCN=C=S` | mw_out_of_envelope(175.32) |
| 20 | `CS(=O)CCCCCN=C=S` | mw_out_of_envelope(191.32) |
| 21 | `CSCCCN=C=S` | mw_out_of_envelope(147.27) |

## Next steps after a quote comes back

1. Confirm 3 procurable candidates with the most upstream-distinct structures (don't buy 3 close analogs).
2. Order 5–10 mg each, ≥ 95% purity, in DMSO-soluble form.
3. Run the β-hex / LAD2 protocol referenced in [`docs/wet_lab_protocols.md`](../docs/wet_lab_protocols.md) alongside Sulforaphane (positive class control) + Cetirizine (non-stabilizer negative).
4. File the result as **EXP-018-real-wet-lab-pilot**, regardless of whether the candidate moves or fails — publishable either way.

## Disclaimer

Not medical advice. Not a recommendation that any specific compound is safe, effective, or appropriate for any human use. This packet exists to surface in-silico hypotheses for in-vitro testing. See [`docs/disclaimers.md`](../docs/disclaimers.md).