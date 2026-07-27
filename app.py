"""OpenMCAS — public hypothesis browser (Streamlit) v0.2.

A read-only viewer for the ranked predictions in this repo. No clone required.

Run locally:
    streamlit run app.py

Deploy: free Hugging Face Space — see docs/deploying-the-viewer.md.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).parent
LIBRARY_CSV = REPO_ROOT / "data" / "compounds" / "MCAS_Compound_Library_v1.csv"
TARGETS_CSV = REPO_ROOT / "data" / "targets" / "MCAS_Targets.csv"
TRIGGERS_CSV = REPO_ROOT / "data" / "triggers" / "MCAS_Triggers_v1.csv"
INJURY_CSV = REPO_ROOT / "data" / "injury_mechanisms" / "MCAS_Injury_Mechanisms_v1.csv"
OUT_DIR = REPO_ROOT / "outputs"
BENCHMARK_CSV = OUT_DIR / "benchmark_known_actives.csv"
NEG_CTRL_CSV = OUT_DIR / "benchmark_negative_controls.csv"
MAST_CELL_CSV = OUT_DIR / "mast_cell_predictions.csv"
MAST_CELL_METRICS_CSV = OUT_DIR / "mast_cell_model_metrics.csv"
CHEMBL_PRED_CSV = OUT_DIR / "chembl_predictions.csv"
C151_CSV = OUT_DIR / "c151_adduct_energies.csv"
VINA_CSV = OUT_DIR / "docking_KEAP1_vina.csv"
RANKED_ALL_CSV = OUT_DIR / "ranked_all.csv"

st.set_page_config(
    page_title="OpenMCAS — Hypothesis Browser",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Light CSS polish (v0.2)
# -----------------------------
st.markdown(
    """
<style>
  .block-container { padding-top: 1.2rem; max-width: 1200px; }
  div[data-testid="stMetric"] {
    background: linear-gradient(180deg, #f7fafc 0%, #eef5f2 100%);
    border: 1px solid #d9e8e0;
    border-radius: 12px;
    padding: 0.6rem 0.8rem;
  }
  .om-card {
    border: 1px solid #d9e8e0;
    border-radius: 14px;
    padding: 0.9rem 1rem;
    background: #ffffff;
    box-shadow: 0 1px 2px rgba(16, 42, 34, 0.04);
    margin-bottom: 0.6rem;
    min-height: 150px;
  }
  .om-card h4 { margin: 0 0 0.25rem 0; font-size: 1.05rem; }
  .om-pill {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    padding: 0.12rem 0.5rem;
    border-radius: 999px;
    background: #e8f5ef;
    color: #1f5c45;
    margin-right: 0.3rem;
  }
  .om-pill.warn { background: #fff4e5; color: #8a5a00; }
  .om-pill.muted { background: #eef1f4; color: #445; }
  .om-why { color: #334; font-size: 0.9rem; margin-top: 0.4rem; line-height: 1.35; }
  .om-score { font-variant-numeric: tabular-nums; color: #0f5132; font-weight: 700; }
  .om-falsify {
    border-left: 3px solid #c45c26;
    background: #fff8f3;
    padding: 0.7rem 0.9rem;
    border-radius: 0 10px 10px 0;
    margin: 0.6rem 0 1rem 0;
  }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Disclaimer (always visible)
# -----------------------------
st.warning(
    "**Not medical advice.** This is a research / hypothesis-generation tool. "
    "It does not diagnose, treat, cure, or prevent any condition. "
    "If you have MCAS / MCAD, work with a mast-cell-knowledgeable clinician. "
    "Full disclaimer: [docs/disclaimers.md](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/disclaimers.md)."
)


# -----------------------------
# Load
# -----------------------------
@st.cache_data
def load_ranked(category: str) -> pd.DataFrame:
    path = OUT_DIR / f"ranked_{category}.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_library() -> pd.DataFrame:
    return pd.read_csv(LIBRARY_CSV)


@st.cache_data
def load_targets() -> pd.DataFrame:
    return pd.read_csv(TARGETS_CSV)


@st.cache_data
def load_triggers() -> pd.DataFrame:
    return pd.read_csv(TRIGGERS_CSV)


@st.cache_data
def load_injury() -> pd.DataFrame:
    return pd.read_csv(INJURY_CSV)


@st.cache_data
def load_benchmark() -> pd.DataFrame:
    if not BENCHMARK_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(BENCHMARK_CSV)


@st.cache_data
def load_negative_controls() -> pd.DataFrame:
    if not NEG_CTRL_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(NEG_CTRL_CSV)


@st.cache_data
def load_mast_cell() -> pd.DataFrame:
    if not MAST_CELL_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(MAST_CELL_CSV)


@st.cache_data
def load_mast_cell_metrics() -> dict:
    if not MAST_CELL_METRICS_CSV.exists():
        return {}
    df = pd.read_csv(MAST_CELL_METRICS_CSV)
    return dict(zip(df["metric"], df["value"]))


@st.cache_data
def load_chembl() -> pd.DataFrame:
    if not CHEMBL_PRED_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(CHEMBL_PRED_CSV)


@st.cache_data
def load_c151() -> pd.DataFrame:
    if not C151_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(C151_CSV)


@st.cache_data
def load_vina() -> pd.DataFrame:
    if not VINA_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(VINA_CSV)


@st.cache_data
def load_ranked_all() -> pd.DataFrame:
    if not RANKED_ALL_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(RANKED_ALL_CSV)


# -----------------------------
# Explanation helpers (no RDKit)
# -----------------------------
CATEGORY_FOCUS = {
    "rescue": ["HRH1", "HRH2", "CYSLTR1", "MRGPRX2"],
    "maintenance": ["CYSLTR1", "HRH1", "BTK", "MRGPRX2", "KEAP1", "CNR2", "SYK", "PTGS2"],
    "remission": ["KEAP1", "KIT", "MRGPRX2", "GLP1R", "CNR2", "SYK"],
}


def _safe_float(val, default=None):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def explain_rank(row: pd.Series, category: str | None = None) -> list[str]:
    """Plain-English drivers for a ranked row (uses only existing CSV columns)."""
    reasons: list[str] = []
    cat = category or str(row.get("category") or "")
    evidence = str(row.get("evidence_level") or "").strip() or "unspecified"
    source = str(row.get("source") or "")
    reasons.append(f"Evidence weight: **{evidence}**"
                   + (" (library / clinical anchor)" if source == "library" else " (AI-generated — not clinical evidence)"))

    focus = CATEGORY_FOCUS.get(cat, [])
    scored = []
    for tgt in focus:
        col = f"score_{tgt}"
        if col in row.index:
            v = _safe_float(row.get(col))
            if v is not None and v > 0:
                ref = row.get(f"ref_{tgt}")
                ref_s = f" (nearest ref: {ref})" if isinstance(ref, str) and ref and ref != "nan" else ""
                scored.append((tgt, v, ref_s))
    scored.sort(key=lambda x: x[1], reverse=True)
    if scored:
        top = scored[:3]
        bits = [f"**{t}** sim `{v:.2f}`{ref}" for t, v, ref in top]
        reasons.append("Strongest target signals: " + "; ".join(bits))

    if bool(row.get("has_warhead")) is True or str(row.get("has_warhead")).lower() == "true":
        wh = str(row.get("warheads") or "reactive group").strip() or "reactive group"
        reasons.append(f"Covalent warhead detected: **{wh}** (KEAP1-axis chemistry)")

    mc = _safe_float(row.get("mast_cell_stabilizer_prob"))
    if mc is not None and mc >= 0.4:
        reasons.append(f"Mast-cell stabilizer model p = **{mc:.2f}** (EXP-016)")

    herg = _safe_float(row.get("hERG_score"))
    ames = _safe_float(row.get("AMES_score"))
    if herg is not None and ames is not None:
        safety = 0.5 * (1 - herg) + 0.5 * (1 - ames)
        label = "favorable" if safety >= 0.55 else ("mixed" if safety >= 0.4 else "cautious")
        reasons.append(
            f"Predicted safety ({label}): hERG `{herg:.2f}`, AMES `{ames:.2f}` "
            f"(lower = better)"
        )

    tan = _safe_float(row.get("tanimoto_to_sfn_class"))
    if tan is None:
        tan = _safe_float(row.get("tanimoto_to_SFN"))
    if tan is not None and source == "reinvent_generated":
        if tan >= 0.9:
            reasons.append(
                f"Near-neighbor of SFN-class seeds (Tanimoto `{tan:.2f}`) — "
                "**not a novel scaffold**; chain/warhead variant (EXP-025)."
            )
        elif tan >= 0.5:
            reasons.append(f"SFN-class neighborhood (Tanimoto `{tan:.2f}`).")
        else:
            reasons.append(f"More distant from SFN-class (Tanimoto `{tan:.2f}`).")

    nov = _safe_float(row.get("novelty_score"))
    if nov is not None and source == "reinvent_generated":
        reasons.append(f"Novelty score `{nov:.2f}` (1 − max Tanimoto to library/seeds)")

    if str(row.get("real_space_plausible")).lower() in ("true", "1", "yes"):
        reasons.append("Enamine REAL-space **plausible** (EXP-017 envelope)")
    elif str(row.get("real_space_plausible")).lower() in ("false", "0", "no"):
        reasons.append("Enamine REAL-space envelope: **not plausible** / check MW")

    btb = _safe_float(row.get("score_btb_covalent"))
    if btb is not None and btb > 0:
        reasons.append(f"BTB Cys-151 covalent proxy score `{btb:.2f}` (EXP-023)")

    le = _safe_float(row.get("vina_ligand_efficiency"))
    if le is not None and le < 0:
        reasons.append(f"KEAP1 Vina ligand efficiency `{le:.3f}` kcal/mol/atom (EXP-009)")

    c151 = _safe_float(row.get("c151_score"))
    if c151 is not None and c151 > 0:
        reasons.append(f"C151 covalent-adduct proxy score `{c151:.2f}` (EXP-012)")

    return reasons


def falsify_bullets(row: pd.Series, category: str | None = None) -> list[str]:
    """What wet-lab / audit result would undermine this ranking."""
    cat = category or str(row.get("category") or "")
    name = str(row.get("name") or "this compound")
    bullets = [
        f"LAD2 / primary human mast-cell **β-hexosaminidase release** shows no "
        f"concentration-dependent stabilization by {name} vs vehicle "
        f"(see `docs/wet-lab-preregistration-v1.md`).",
    ]
    if cat == "remission" or bool(row.get("has_warhead")) is True:
        bullets.append(
            "KEAP1-C151 / Nrf2 pathway assays (NQO1, HO-1 induction) fail to show "
            "electrophile-class activity at non-cytotoxic doses."
        )
    if cat == "rescue":
        bullets.append(
            "H1 / CysLT1 functional antagonism or degranulation blockade is weaker "
            "than the clinical anchor class at equivalent free concentration."
        )
    if str(row.get("source")) == "reinvent_generated":
        bullets.append(
            "Synthetic accessibility or Enamine REAL procurement fails, or the "
            "molecule is a near-duplicate of a known ITC with no differentiated profile."
        )
    bullets.append(
        "Negative-control drugs of the same chemotype rank higher under the same "
        "composite after an independent reweight — see EXP-007 / EXP-022."
    )
    return bullets


def recovery_table(benchmark: pd.DataFrame) -> pd.DataFrame:
    valid = benchmark[benchmark["rank_in_expected_category"].notna()].copy()
    if valid.empty:
        return pd.DataFrame()
    valid["rank_in_expected_category"] = valid["rank_in_expected_category"].astype(int)
    rows = []
    for n in (5, 10, 20, 50):
        hit = (valid["rank_in_expected_category"] <= n).sum()
        rows.append({
            "cutoff": f"@{n}",
            "recovered": f"{hit}/{len(valid)}",
            "rate": f"{100 * hit / len(valid):.1f}%",
            "note": {
                5: "strict — currently weak (self-similarity cap)",
                10: "strict — currently weak",
                20: "headline coarse recovery",
                50: "near-ceiling for n=21 set",
            }[n],
        })
    return pd.DataFrame(rows)


def render_top_cards(df: pd.DataFrame, category: str, n: int = 3) -> None:
    if df.empty:
        st.info("No candidates.")
        return
    cols = st.columns(min(n, len(df)))
    for col, (_, r) in zip(cols, df.head(n).iterrows()):
        score = _safe_float(r.get("composite_score"), 0.0) or 0.0
        evidence = str(r.get("evidence_level") or "—")
        source = str(r.get("source") or "—")
        warhead = bool(r.get("has_warhead")) is True or str(r.get("has_warhead")).lower() == "true"
        why = explain_rank(r, category)
        top_why = why[0] if why else ""
        if len(why) > 1:
            top_why = why[1] if "target" in why[1].lower() or "Strongest" in why[1] else why[0]
        pills = (
            f'<span class="om-pill">{evidence} evidence</span>'
            f'<span class="om-pill muted">{source}</span>'
            + (f'<span class="om-pill warn">warhead</span>' if warhead else "")
        )
        col.markdown(
            f"""
<div class="om-card">
  <h4>{r['name']}</h4>
  <div class="om-score">composite {score:.3f}</div>
  <div style="margin-top:0.35rem">{pills}</div>
  <div class="om-why">{top_why}</div>
</div>
""",
            unsafe_allow_html=True,
        )


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🧬 OpenMCAS")
st.sidebar.markdown(
    "**Open, MIT-licensed hypothesis-generation engine for MCAS / MCAD.**\n\n"
    "Pharma + herbs + supplements + AI-generated analogs, ranked transparently."
)
st.sidebar.caption("Viewer **v0.2** — cards · why-ranked · honest audits · falsify-me")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Quick links**\n"
    "- [Repo](https://github.com/mrdulasolutions/MCAS.Opensource)\n"
    "- [Experiments](https://github.com/mrdulasolutions/MCAS.Opensource/tree/main/experiments)\n"
    "- [Hypotheses](https://github.com/mrdulasolutions/MCAS.Opensource/tree/main/hypotheses)\n"
    "- [Audience guides](https://github.com/mrdulasolutions/MCAS.Opensource/tree/main/audiences)\n"
    "- [Wet-lab prereg](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/wet-lab-preregistration-v1.md)\n"
    "- [Contribute](https://github.com/mrdulasolutions/MCAS.Opensource/issues/new/choose)"
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Provider: **MR Dula Medical** (a DBA of MR Dula Enterprise, LLC, Raleigh, NC). MIT license."
)

# -----------------------------
# Tabs
# -----------------------------
tabs = st.tabs([
    "🏠 Overview",
    "🔴 Rescue",
    "🟡 Maintenance",
    "🟢 Remission",
    "🔬 Mast-cell predictor",
    "🔍 Compound deep-dive",
    "🎯 Targets",
    "⚠️ Triggers",
    "🧪 Injury mechanisms",
    "✅ Benchmarks",
    "ℹ️ About",
])

# -----------------------------
# Tab 0: Overview
# -----------------------------
with tabs[0]:
    st.title("OpenMCAS — Hypothesis Browser")
    st.markdown(
        "**An open, reproducible engine for MCAS / MCAD compound hypotheses.** "
        "Rankings come from a CPU pipeline you can re-run. Every prediction is "
        "auditable in the repo. No paywalls. No IP capture. **Not clinical advice.**"
    )

    library = load_library()
    rescue = load_ranked("rescue")
    maintenance = load_ranked("maintenance")
    remission = load_ranked("remission")
    benchmark = load_benchmark()
    negatives = load_negative_controls()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Anchor compounds", len(library), help="Curated pharma + herbs + supplements + biologics")
    c2.metric("Rescue candidates", len(rescue))
    c3.metric("Maintenance candidates", len(maintenance))
    c4.metric("Remission candidates", len(remission), help="Library + AI-generated SFN-class analogs")

    st.markdown("### Top candidates (with a one-line “why”)")
    for label, cat, df in (
        ("🔴 Rescue", "rescue", rescue),
        ("🟡 Maintenance", "maintenance", maintenance),
        ("🟢 Remission", "remission", remission),
    ):
        st.markdown(f"#### {label}")
        render_top_cards(df, cat, n=3)

    if not benchmark.empty:
        st.markdown("### Held-out known-actives recovery (honest curve)")
        st.markdown(
            "21 clinically established mast-cell drugs scored blind (not in seeds / "
            "reference sets). **Coarse recovery@20 is strong; strict recovery@5/@10 "
            "is weak** — partly because reference self-similarity caps top ranks "
            "([EXP-006](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-006-known-actives-recovery.md))."
        )
        rt = recovery_table(benchmark)
        if not rt.empty:
            mcols = st.columns(4)
            valid = benchmark[benchmark["rank_in_expected_category"].notna()]
            ranks = valid["rank_in_expected_category"].astype(int)
            for col, n in zip(mcols, (5, 10, 20, 50)):
                hit = (ranks <= n).sum()
                col.metric(f"Recovery@{n}", f"{hit}/{len(valid)}", f"{100 * hit / len(valid):.0f}%")
            st.dataframe(rt, use_container_width=True, hide_index=True)

        if not negatives.empty:
            # precision@10: rank > 10 in every category
            def _outside_top10(row) -> bool:
                for cat in ("rescue", "maintenance", "remission"):
                    rk = row.get(f"rank_{cat}")
                    if pd.isna(rk) or float(rk) <= 10:
                        return False
                return True

            prec_n = negatives.apply(_outside_top10, axis=1).sum()
            st.markdown(
                f"**Negative-control precision@10:** `{prec_n}/{len(negatives)}` "
                f"({100 * prec_n / len(negatives):.0f}%) — unrelated drugs "
                f"(statins, antihypertensives, etc.) correctly kept out of every top-10 "
                f"([EXP-007](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-007-negative-control-benchmark.md))."
            )

    st.markdown("---")
    st.markdown(
        "### How to read these rankings\n"
        "Each compound’s **composite score** is a weighted combination of:\n"
        "- `evidence_level` — published evidence weight (high / medium / low)\n"
        "- weighted **target similarity** — ligand-based screen vs curated references\n"
        "- **warhead** chemistry — covalent reactive-group SMARTS (KEAP1 axis)\n"
        "- **safety** — low predicted hERG + AMES (RandomForest QSAR)\n"
        "- optional enrichments — ChEMBL pIC50, mast-cell stabilizer p, Vina LE, C151 adduct\n\n"
        "Full formula: [EXP-005](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-005-multi-objective-ranking.md). "
        "Methods: [methods.md](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/methods.md)."
    )

# -----------------------------
# Category tabs (1, 2, 3)
# -----------------------------
def render_category(tab, category, color, target_cols):
    df = load_ranked(category)
    if df.empty:
        tab.warning("No ranking data found. Run `python scripts/rank_hypotheses.py` first.")
        return

    tab.subheader(f"{color} {category.title()} ranking — {len(df)} candidates")
    tab.caption(
        "Use filters, then open **Why this ranked** for a plain-English driver list. "
        "Generated analogs with high Tanimoto-to-SFN are near-neighbors, not new scaffolds."
    )

    with tab.expander("Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        sources = ["all"] + sorted(df["source"].dropna().unique().tolist()) if "source" in df else ["all"]
        source = col1.selectbox("Source", sources, key=f"src_{category}")
        evidences = ["all", "high", "medium", "low", ""]
        evidence = col2.selectbox("Evidence level", evidences, key=f"ev_{category}")
        only_warhead = col3.checkbox("Only warhead-positive", value=False, key=f"wh_{category}")
        search = st.text_input("Filter by name / mechanism (substring)", "", key=f"search_{category}")

    filtered = df.copy()
    if source != "all" and "source" in filtered:
        filtered = filtered[filtered["source"] == source]
    if evidence != "all" and "evidence_level" in filtered:
        filtered = filtered[filtered["evidence_level"].fillna("") == evidence]
    if only_warhead and "has_warhead" in filtered:
        filtered = filtered[filtered["has_warhead"] == True]  # noqa: E712
    if search:
        mask = filtered["name"].astype(str).str.contains(search, case=False, na=False)
        if "mechanism" in filtered:
            mask |= filtered["mechanism"].astype(str).str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    # Top-5 cards
    tab.markdown("#### Top 5 (cards)")
    render_top_cards(filtered, category, n=5)

    display_cols = [
        "name", "composite_score", "subcategory", "mechanism",
        "evidence_level", "source", "has_warhead", "warheads",
        "score_KEAP1", "score_MRGPRX2", "score_KIT", "score_HRH1",
        "score_SYK", "score_PTGS2",
        "mast_cell_stabilizer_prob",
        "hERG_score", "AMES_score", "BBB_score",
        "tanimoto_to_sfn_class", "novelty_score", "near_duplicate_of_seed",
        "real_space_plausible", "score_btb_covalent", "qed",
    ]
    display_cols = [c for c in display_cols if c in filtered.columns]

    tab.markdown("#### Full table")
    tab.dataframe(
        filtered[display_cols].head(100),
        use_container_width=True,
        hide_index=True,
    )
    tab.caption(
        f"Showing {min(len(filtered), 100)} of {len(filtered)} matching candidates. "
        f"Lower hERG / AMES = better predicted safety. Higher BBB = more brain-penetrant."
    )

    with tab.expander("Why this ranked + how to falsify", expanded=True):
        names = filtered["name"].tolist()
        if names:
            pick = st.selectbox("Compound", names, key=f"pick_{category}")
            row = filtered[filtered["name"] == pick].iloc[0]
            st.markdown(f"**{pick}** — composite `{_safe_float(row.get('composite_score'), 0):.3f}`")
            st.markdown("**Drivers**")
            for line in explain_rank(row, category):
                st.markdown(f"- {line}")
            st.markdown(
                '<div class="om-falsify"><strong>Falsify me</strong> — results that would undermine this rank:</div>',
                unsafe_allow_html=True,
            )
            for line in falsify_bullets(row, category):
                st.markdown(f"- {line}")
            with st.expander("Raw prediction JSON"):
                st.json(row.dropna().to_dict())


with tabs[1]:
    render_category(tabs[1], "rescue", "🔴", ["HRH1", "HRH2", "CYSLTR1", "MRGPRX2"])
with tabs[2]:
    render_category(tabs[2], "maintenance", "🟡", ["CYSLTR1", "HRH1", "BTK", "MRGPRX2", "KEAP1"])
with tabs[3]:
    render_category(tabs[3], "remission", "🟢", ["MRGPRX2", "KIT", "KEAP1", "GLP1R"])

# -----------------------------
# Tab 4: Mast-cell predictor (EXP-016)
# -----------------------------
with tabs[4]:
    st.subheader("🔬 Mast-cell stabilizer predictor (EXP-016)")
    st.markdown(
        "A RandomForest model trained directly on **mast-cell readout assays** from ChEMBL "
        "(β-hexosaminidase release, LAD2 degranulation, HMC-1, histamine release, "
        "tryptase release). It predicts the probability that a compound stabilizes mast "
        "cells — a *direct* phenotypic prediction, not a target-similarity proxy. "
        "Integrated into the composite as a +0.05 universal bonus across all three "
        "categories. See "
        "[EXP-016](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-016-mast-cell-predictor.md)."
    )

    metrics = load_mast_cell_metrics()
    mc = load_mast_cell()
    if mc.empty:
        st.info(
            "No predictions found. Run the mast-cell training + scoring scripts in the repo."
        )
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Training compounds", int(float(metrics.get("n_train_compounds", 0))))
        c2.metric("Active labels", int(float(metrics.get("n_train_active", 0))))
        c3.metric("Inactive labels", int(float(metrics.get("n_train_inactive", 0))))
        c4.metric(
            "5-fold CV AUC",
            f"{float(metrics.get('cv_mean_auc', 0)):.3f}",
            help="Strongest single model in the repo — beats hERG / AMES / BBB baselines."
        )

        st.markdown("### Prediction distribution")
        st.markdown(
            "Higher = more mast-cell-stabilizing-like. The integration bonus is +0.05 × p."
        )

        hist_df = mc.copy()
        hist_df["mast_cell_stabilizer_prob"] = hist_df["mast_cell_stabilizer_prob"].astype(float)
        bins = pd.cut(
            hist_df["mast_cell_stabilizer_prob"],
            bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            include_lowest=True,
        )
        hist_counts = (
            hist_df.groupby([bins, "source"], observed=True)
            .size()
            .reset_index(name="count")
        )
        hist_counts["bin"] = hist_counts["mast_cell_stabilizer_prob"].astype(str)
        st.bar_chart(
            hist_counts.pivot_table(
                index="bin", columns="source", values="count", fill_value=0
            ),
            height=240,
        )

        st.markdown("### Filter")
        f1, f2 = st.columns(2)
        sources_mc = ["all"] + sorted(mc["source"].dropna().unique().tolist())
        src_pick = f1.selectbox("Source", sources_mc, key="mc_src")
        min_p = f2.slider("Minimum predicted probability", 0.0, 1.0, 0.4, 0.05, key="mc_min")

        view = mc.copy()
        view["mast_cell_stabilizer_prob"] = view["mast_cell_stabilizer_prob"].astype(float)
        if src_pick != "all":
            view = view[view["source"] == src_pick]
        view = view[view["mast_cell_stabilizer_prob"] >= min_p].sort_values(
            "mast_cell_stabilizer_prob", ascending=False
        )

        st.markdown(f"### Top compounds — {len(view)} match the filter")
        st.dataframe(
            view.head(50)[["name", "source", "mast_cell_stabilizer_prob", "smiles"]],
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Caveat: the predictor is biased toward chemotypes well-represented in ChEMBL. "
            "Some classical stabilizers (ketotifen, quercetin) can score lower than expected "
            "— see EXP-016 §7.3. The +0.05 bonus is small on purpose."
        )

# -----------------------------
# Tab 5: Compound deep-dive
# -----------------------------
with tabs[5]:
    st.subheader("🔍 Per-compound deep-dive")
    st.markdown(
        "Pick one compound and see every signal the pipeline computes: composite "
        "score per category, target similarities, ChEMBL predicted pIC50s, mast-cell "
        "predictor probability, Vina docking + ligand efficiency (if docked), C151 "
        "covalent-adduct energy (if ITC-class), QSAR safety, **why it ranked**, and "
        "**how to falsify it**."
    )

    ranked_all = load_ranked_all()
    library = load_library()
    chembl = load_chembl()
    c151 = load_c151()
    vina = load_vina()
    mc = load_mast_cell()

    all_names = sorted(set(
        list(ranked_all["name"].dropna().unique()) if not ranked_all.empty else []
    ) | set(library["name"].dropna().unique()))

    if not all_names:
        st.info("No data found. Run the pipeline first.")
    else:
        default_idx = all_names.index("Sulforaphane") if "Sulforaphane" in all_names else 0
        pick = st.selectbox(
            "Compound",
            all_names,
            index=default_idx,
            key="deepdive_pick",
            help="Includes library compounds + AI-generated SFN-class analogs.",
        )

        st.markdown("### Identity")
        lib_row = library[library["name"] == pick]
        is_biologic = False
        biologic_flag = ""
        if not lib_row.empty:
            lib = lib_row.iloc[0]
            biologic_flag = str(lib.get("biologic_flag") or "").strip()
            is_biologic = bool(biologic_flag) and biologic_flag.lower() != "nan"
            i1, i2, i3 = st.columns(3)
            i1.markdown(f"**Category:** `{lib.get('category', '?')}`")
            i2.markdown(f"**Subcategory:** `{lib.get('subcategory', '?')}`")
            i3.markdown(f"**Evidence:** `{lib.get('evidence_level', '?')}`")
            st.markdown(f"**Mechanism:** {lib.get('mechanism', '—')}")
            st.markdown(f"**Target(s):** `{lib.get('target', '—')}`")
            if is_biologic:
                st.markdown(
                    f"**Modality:** `biologic` &nbsp;·&nbsp; `flag = {biologic_flag}`"
                )
            else:
                st.markdown(f"**SMILES:** `{lib.get('canonical_smiles') or lib.get('smiles', '—')}`")
                if pd.notna(lib.get("pubchem_cid")):
                    cid = int(lib["pubchem_cid"])
                    st.markdown(f"**PubChem:** [CID {cid}](https://pubchem.ncbi.nlm.nih.gov/compound/{cid})")
        else:
            if not ranked_all.empty:
                gen = ranked_all[ranked_all["name"] == pick].iloc[0]
                st.markdown(f"**Source:** `{gen.get('source', 'generated')}`")
                st.markdown(f"**SMILES:** `{gen.get('smiles', '—')}`")

        if is_biologic and not lib_row.empty:
            lib = lib_row.iloc[0]
            st.info(
                "**This compound is a biologic** — small-molecule scoring does "
                "not apply. Structure-based scorers need a canonical SMILES."
            )
            st.markdown("### Clinical context")
            st.markdown(f"**Evidence notes:** {lib.get('evidence_notes', '—')}")
            refs = lib.get("source_refs", "")
            if refs and str(refs) != "nan":
                st.markdown(f"**References:** {refs}")
            same_class = library[
                (library["biologic_flag"].notna())
                & (library["biologic_flag"].astype(str).str.strip() != "")
                & (library["name"] != pick)
            ].copy()
            if not same_class.empty:
                st.markdown("### Other biologics in the library")
                show = same_class[["name", "category", "subcategory", "biologic_flag"]].rename(
                    columns={"biologic_flag": "flag"}
                )
                st.dataframe(show, use_container_width=True, hide_index=True)
        else:
            st.markdown("### Composite ranks (per category)")
            cols = st.columns(3)
            row_for_why = None
            for col, cat in zip(cols, ["rescue", "maintenance", "remission"]):
                df = load_ranked(cat)
                if df.empty or pick not in df["name"].values:
                    col.metric(cat.title(), "—", help="Not ranked in this category.")
                else:
                    r = df[df["name"] == pick].iloc[0]
                    rank = int(df.index[df["name"] == pick][0]) + 1
                    col.metric(
                        cat.title(),
                        f"rank {rank}/{len(df)}",
                        f"composite {r['composite_score']:.3f}",
                    )
                    if row_for_why is None:
                        row_for_why = r

            if row_for_why is not None:
                primary_cat = str(row_for_why.get("category") or "remission")
                st.markdown("### Why this ranked")
                for line in explain_rank(row_for_why, primary_cat):
                    st.markdown(f"- {line}")
                st.markdown(
                    '<div class="om-falsify"><strong>Falsify me</strong></div>',
                    unsafe_allow_html=True,
                )
                for line in falsify_bullets(row_for_why, primary_cat):
                    st.markdown(f"- {line}")

            if not mc.empty:
                mrow = mc[mc["name"] == pick]
                if not mrow.empty:
                    p = float(mrow.iloc[0]["mast_cell_stabilizer_prob"])
                    st.markdown("### Mast-cell stabilizer probability (EXP-016)")
                    st.progress(min(max(p, 0.0), 1.0), text=f"p = {p:.3f}")

            if not chembl.empty:
                crow = chembl[chembl["name"] == pick]
                if not crow.empty:
                    st.markdown("### Predicted target binding (ChEMBL, EXP-011)")
                    pIC50_cols = [c for c in chembl.columns if c.startswith("chembl_pIC50_")]
                    pIC50_data = crow.iloc[0][pIC50_cols].to_dict()
                    pIC50_df = pd.DataFrame([
                        {"target": k.replace("chembl_pIC50_", ""), "predicted_pIC50": round(float(v), 3)}
                        for k, v in pIC50_data.items()
                    ]).sort_values("predicted_pIC50", ascending=False)
                    st.dataframe(pIC50_df, use_container_width=False, hide_index=True, width=400)
                    st.caption(
                        "pIC50 = −log10(IC50 in M). 7 ≈ 100 nM (good lead). 6 ≈ 1 µM. 5 ≈ 10 µM."
                    )

            if not vina.empty:
                vrow = vina[vina["name"] == pick]
                if not vrow.empty:
                    v = vrow.iloc[0]
                    st.markdown("### KEAP1 Kelch Vina docking (EXP-009)")
                    v1, v2 = st.columns(2)
                    v1.metric("Vina ΔG (kcal/mol)", f"{float(v.get('vina_dG_kcal_per_mol', v.get('vina_kcal_per_mol', 0))):.2f}")
                    if pd.notna(v.get("ligand_efficiency") if "ligand_efficiency" in v else v.get("vina_ligand_efficiency")):
                        le_val = v.get("ligand_efficiency", v.get("vina_ligand_efficiency"))
                        v2.metric("Ligand efficiency", f"{float(le_val):.3f}")
                    st.caption("PDB 4L7B Kelch domain. Lower ΔG = better predicted affinity.")

            if not c151.empty:
                crow = c151[c151["name"] == pick]
                if not crow.empty:
                    cr = crow.iloc[0]
                    st.markdown("### KEAP1-C151 covalent adduct (EXP-012)")
                    cc1, cc2 = st.columns(2)
                    cc1.metric(
                        "ΔE adduct (kcal/mol)",
                        f"{float(cr.get('dE_kcal_per_mol', 0)):.2f}",
                        help="MMFF94 reaction-energy proxy. More negative = more favorable.",
                    )
                    cc2.metric("score_c151", f"{float(cr.get('score_c151', 0)):.3f}")

            st.markdown("---")
            st.caption(
                "Experiments: "
                "[EXP-005](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-005-multi-objective-ranking.md) · "
                "[EXP-009](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-009-keap1-vina-docking.md) · "
                "[EXP-011](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-011-chembl-bioassay-predictor.md) · "
                "[EXP-012](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-012-covalent-c151-adduct.md) · "
                "[EXP-016](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-016-mast-cell-predictor.md)."
            )

# -----------------------------
# Tab 6: Targets
# -----------------------------
with tabs[6]:
    st.subheader("Druggable MCAS targets")
    st.markdown(
        "UniProt-indexed targets the pipeline scores compounds against. "
        "AlphaFold structures linked per row where available."
    )
    st.dataframe(load_targets(), use_container_width=True, hide_index=True)

# -----------------------------
# Tab 7: Triggers
# -----------------------------
with tabs[7]:
    st.subheader("Reported MCAS triggers")
    st.markdown(
        "Patient-reported + literature-supported triggers mapped to the pathway they act through "
        "and to candidate counter-compounds from the library."
    )
    triggers = load_triggers()
    cats = ["all"] + sorted(triggers["trigger_category"].dropna().unique().tolist())
    cat = st.selectbox("Category", cats, key="trigger_cat")
    if cat != "all":
        triggers = triggers[triggers["trigger_category"] == cat]
    st.dataframe(triggers, use_container_width=True, hide_index=True)

# -----------------------------
# Tab 8: Injury mechanisms
# -----------------------------
with tabs[8]:
    st.subheader("MCAS injury mechanisms")
    st.markdown(
        "Upstream priming injuries, acute triggers, clonal drivers, and downstream tissue damage."
    )
    st.dataframe(load_injury(), use_container_width=True, hide_index=True)

# -----------------------------
# Tab 9: Benchmarks
# -----------------------------
with tabs[9]:
    st.subheader("Audit benchmarks")
    st.markdown(
        "Two complementary checks: **known-actives recovery** (does the ranker find "
        "real mast-cell drugs?) and **negative-control rejection** (does it keep "
        "unrelated drugs out of the top-10?)."
    )

    st.markdown("### Known-Actives Recovery (EXP-006)")
    st.markdown(
        "Blind scoring of 21 clinically established mast-cell drugs **not** in seeds "
        "or reference ligand sets. Read the full curve — not just @20."
    )
    benchmark = load_benchmark()
    if benchmark.empty:
        st.info("Benchmark not run yet. See EXP-006.")
    else:
        valid = benchmark[benchmark["rank_in_expected_category"].notna()].copy()
        valid["rank_in_expected_category"] = valid["rank_in_expected_category"].astype(int)

        c1, c2, c3, c4 = st.columns(4)
        for col, N in zip([c1, c2, c3, c4], [5, 10, 20, 50]):
            hit = (valid["rank_in_expected_category"] <= N).sum()
            col.metric(f"Recovery@{N}", f"{hit}/{len(valid)}", f"{100 * hit / len(valid):.0f}%")

        st.caption(
            "recovery@5/@10 are intentionally weak today (self-similarity + small set). "
            "recovery@20 is the coarse headline metric. Remission expected-set size is small."
        )

        st.markdown("### Per-category recovery")
        cat_rows = []
        for cat in ("rescue", "maintenance", "remission"):
            sub = valid[valid["expected_category"] == cat]
            row = {"category": cat, "n": len(sub)}
            for N in (5, 10, 20, 50):
                row[f"recovery@{N}"] = f"{(sub['rank_in_expected_category'] <= N).sum()}/{len(sub)}"
            cat_rows.append(row)
        st.dataframe(pd.DataFrame(cat_rows), hide_index=True)

        st.markdown("### Per-compound diagnostic")
        st.dataframe(
            valid[[
                "name", "expected_category", "rank_in_expected_category",
                "expected_category_size", "composite_score",
                "has_warhead", "hERG_score", "AMES_score", "BBB_score",
            ]].sort_values(["expected_category", "rank_in_expected_category"]),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    st.markdown("### Negative-control rejection (EXP-007)")
    negatives = load_negative_controls()
    if negatives.empty:
        st.info("Negative-control benchmark not present.")
    else:
        def _outside_top10(row) -> bool:
            for cat in ("rescue", "maintenance", "remission"):
                rk = row.get(f"rank_{cat}")
                if pd.isna(rk) or float(rk) <= 10:
                    return False
            return True

        prec_n = int(negatives.apply(_outside_top10, axis=1).sum())
        st.metric(
            "Precision@10 (outside every top-10)",
            f"{prec_n}/{len(negatives)}",
            f"{100 * prec_n / len(negatives):.0f}%",
        )
        show_cols = [
            c for c in [
                "name", "therapeutic_class", "rationale",
                "rank_rescue", "rank_maintenance", "rank_remission",
                "composite_rescue", "composite_maintenance", "composite_remission",
            ] if c in negatives.columns
        ]
        st.dataframe(negatives[show_cols], use_container_width=True, hide_index=True)
        st.caption(
            "A perfect score means no statin / antihypertensive / anticonvulsant-style "
            "control leaked into any category top-10 under the current composite."
        )

# -----------------------------
# Tab 10: About
# -----------------------------
with tabs[10]:
    st.subheader("About OpenMCAS")
    st.markdown(
        "**Provider:** MR Dula Medical (a DBA of MR Dula Enterprise, LLC, Raleigh, NC, USA).\n\n"
        "**License:** MIT. Fork it, remix it, validate it, refute it. Attribution appreciated.\n\n"
        "**A2A:** This project publishes an Agent2Agent agent card at "
        "`.well-known/agent-card.json` — see "
        "[AGENT_CARD.md](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/AGENT_CARD.md).\n\n"
        "**Status:** v0.1.x alpha · viewer **v0.2**. "
        "Current remission leaders are **Erucin ≈ Sulforaphane** (SFN-class ITCs). "
        "Headline in-silico results have passed internal recovery / negative-control / "
        "sensitivity audits but have **not** been validated in human mast cells. "
        "Wet-lab campaigns are on the roadmap."
    )

    st.markdown("### Limitations (read before citing)")
    st.markdown(
        "- Composite weights are author-chosen, not learned (sensitivity LHS min ρ ≈ 0.93–0.95).\n"
        "- Ligand-based screening is similarity to known references — not full physics docking "
        "(Vina is an enrichment on KEAP1 Kelch only).\n"
        "- QSAR is RandomForest on Morgan FP — strong baseline, not SOTA.\n"
        "- recovery@5/@10 are weak; recovery@20 is the coarse success metric.\n"
        "- No CYP / GST / UGT metabolism, DDI, or efflux modeling yet.\n"
        "- Generated `GEN_*` tops are often near-neighbors of SFN/Erucin/Iberin — check "
        "`tanimoto_to_SFN` before treating them as novel IP.\n"
        "- No human validation. Wet-lab is how this becomes evidence."
    )

    st.markdown("### Contact")
    st.markdown(
        "All routes go through GitHub for public traceability. "
        "See [CONTACT.md](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/CONTACT.md)."
    )

    st.markdown("---")
    st.caption(
        f"Page rendered {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. "
        f"Underlying data refreshes whenever `scripts/rank_hypotheses.py` is rerun in the repo."
    )
