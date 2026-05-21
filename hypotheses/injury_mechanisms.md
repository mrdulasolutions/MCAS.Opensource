# Injury mechanism hypotheses

> ⚠️ **Not medical advice.** Research/hypothesis use only. See [docs/disclaimers.md](../docs/disclaimers.md).

"Injury" here = whatever upstream insult primes mast cells for inappropriate
degranulation, plus the downstream tissue damage produced by chronic mediator
release. The dataset behind this doc is
[data/injury_mechanisms/MCAS_Injury_Mechanisms_v1.csv](../data/injury_mechanisms/MCAS_Injury_Mechanisms_v1.csv).

## Map of injury categories

| Category | Specific injuries | Pathway / target | Strongest counter-compounds |
|---|---|---|---|
| **Upstream — oxidative** | Chronic ROS damages RNA/proteins, suppresses Nrf2 via KEAP1 oxidation + promoter methylation | Nrf2 / HO-1 / NF-kB / caspase-1 | Sulforaphane, glucoraphanin, resveratrol, curcumin, EGCG, NAC, α-lipoic acid |
| **Upstream — epigenetic** | Aberrant DNA/histone methylation + miRNA dysregulation alters degranulation gene expression | DNMT, HDAC, miRNA targets | Sulforaphane (DNMT inhibitor), curcumin, EGCG, butyrate |
| **Upstream — post-viral** | Persistent SARS-CoV-2 / EBV / HHV-6 antigens drive TLR + ACE2 + substance P; MRGPRX2 priming | TLR, MRGPRX2, NK1R | Resveratrol, quercetin, luteolin, SFN, famotidine |
| **Upstream — gut barrier** | Dysbiosis + leaky gut → LPS + antigen translocation → secondary activation | LPS-TLR4, FcεRI | Butyrate, curcumin, quercetin, baicalein, omega-3 |
| **Upstream — toxin / TILT** | Mycotoxins + heavy metals + xenobiotics overload phase II detox; AhR / Nrf2 dysregulation | Phase II, AhR, Nrf2 | Sulforaphane, NAC, α-lipoic acid, silibinin, curcumin |
| **Trigger — chemical / MRGPRX2** | Opioids, NSAIDs, contrast, fragrances, venoms | MRGPRX2 GPCR | Resveratrol, quercetin, luteolin, cromolyn, ketotifen |
| **Trigger — IgE / FcεRI** | Classical allergen crosslink | FcεRI → SYK → degranulation | Omalizumab, cromolyn, ketotifen, flavonoids |
| **Trigger — neurogenic** | Stress / vagal dysregulation → substance P / CRH | MRGPRX2, NK1R | Luteolin (BBB), quercetin, LDN, baicalein |
| **Clonal — KIT** | D816V (and other) gain-of-function | KIT tyrosine kinase | Masitinib, avapritinib, midostaurin |
| **Downstream — chronic inflammation** | Sustained histamine / tryptase / IL-6 / TNF / IL-1β → fibrosis + nerve sensitization | Cytokine signaling, complement | Curcumin, omega-3, LDN, GLP-1 agonists |
| **Downstream — neuro-inflammation** | Brain mast cells + microglia → POTS / brain fog / dysautonomia | CNS mast cells, HRH3, microglia | Luteolin, quercetin, curcumin, PEA |

## Core hypotheses

### H1 — The Nrf2 priming hypothesis
> Cumulative oxidative + xenobiotic + post-viral injury suppresses Nrf2 tone
> via KEAP1 oxidation **and** epigenetic promoter methylation. Reduced Nrf2
> tone lowers the mast cell degranulation threshold and primes MRGPRX2
> hypersensitivity. Sulforaphane reverses both via direct KEAP1 binding **and**
> DNMT inhibition → durable remission in oxidative / post-viral phenotypes.

**AI test:** Score the library + REINVENT-generated analogs for combined
KEAP1 docking + Nrf2 docking + low covalent off-target risk. See
[hypotheses/remission.md](remission.md) Axis 3.

### H2 — The MRGPRX2 priming hypothesis
> Chronic low-level xenobiotic + neuropeptide exposure (VOCs, opioids, stress
> peptides) raises baseline MRGPRX2 signaling. Acute triggers then exceed
> threshold easily. Direct MRGPRX2 antagonism (resveratrol-class) breaks the
> loop.

**AI test:** Notebook 04 — dock library + generated SMILES against MRGPRX2
(UniProt Q96LB1). Notebook 05 — composite rank with QSAR safety.

### H3 — The gut–mast axis hypothesis
> Dysbiosis + low SCFA + leaky gut create chronic LPS + antigen load that
> secondarily activates mast cells. Gut repair (butyrate + polyphenols +
> omega-3) reduces the load and downstream MCAS burden.

**AI test:** Composite scoring weighted toward TLR4 + gut-restricted compounds.

### H4 — The cumulative-injury bucket hypothesis
> No single injury causes MCAS — instead a "bucket" of priming exposures
> (post-viral + toxin + stress + gut dysbiosis) raises baseline activation
> until any trigger overflows. Reducing **any** axis reduces flares; combining
> multiple axes produces remission.

**AI test:** Multi-target composite scoring (notebook 05) intentionally
rewards compounds that hit two or more injury axes (e.g., SFN: Nrf2 + DNMT +
gut barrier).

## Wet-lab validation

Simulate each injury axis on LAD2 cells:
- **Oxidative:** H₂O₂ pretreatment.
- **MRGPRX2:** Substance P stimulation.
- **Gut / endotoxin:** LPS pretreatment.
- **IgE:** Anti-IgE crosslink.

Read out β-hexosaminidase release, tryptase ELISA, HMOX1 / NQO1 mRNA, and CD63
flow. See [docs/wet_lab_protocols.md](../docs/wet_lab_protocols.md).
