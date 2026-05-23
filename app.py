"""OpenMCAS — public hypothesis browser (Streamlit).

A read-only viewer for the ranked predictions in this repo. No clone required.

Run locally:
    streamlit run app.py

Deploy: free Hugging Face Space — see docs/deploying-the-viewer.md.
"""
from __future__ import annotations

from datetime import datetime
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
# Sidebar
# -----------------------------
st.sidebar.title("🧬 OpenMCAS")
st.sidebar.markdown(
    "**Open, MIT-licensed hypothesis-generation engine for MCAS / MCAD.**\n\n"
    "Pharma + herbs + supplements + AI-generated analogs, ranked transparently."
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Quick links**\n"
    "- [Repo](https://github.com/mrdulasolutions/MCAS.Opensource)\n"
    "- [Experiments](https://github.com/mrdulasolutions/MCAS.Opensource/tree/main/experiments)\n"
    "- [Hypotheses](https://github.com/mrdulasolutions/MCAS.Opensource/tree/main/hypotheses)\n"
    "- [Audience guides](https://github.com/mrdulasolutions/MCAS.Opensource/tree/main/audiences)\n"
    "- [Glossary](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/glossary.md)\n"
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
    "✅ Benchmark",
    "ℹ️ About",
])

# -----------------------------
# Tab 0: Overview
# -----------------------------
with tabs[0]:
    st.title("OpenMCAS — Hypothesis Browser")
    st.markdown(
        "**An open, reproducible engine for MCAS / MCAD compound hypotheses.** "
        "Every ranking on this site is generated from a 7-script CPU pipeline. "
        "Every prediction is auditable in the repo. No paywalls. No IP capture."
    )

    library = load_library()
    rescue = load_ranked("rescue")
    maintenance = load_ranked("maintenance")
    remission = load_ranked("remission")
    benchmark = load_benchmark()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Anchor compounds", len(library), help="Curated pharma + herbs + supplements + biologics")
    c2.metric("Rescue candidates", len(rescue))
    c3.metric("Maintenance candidates", len(maintenance))
    c4.metric("Remission candidates", len(remission), help="Library + AI-generated SFN-class analogs")

    st.markdown("### Top-3 across categories")
    cols = st.columns(3)
    for col, (name, df) in zip(cols, [("🔴 Rescue", rescue), ("🟡 Maintenance", maintenance), ("🟢 Remission", remission)]):
        col.markdown(f"**{name}**")
        for _, r in df.head(3).iterrows():
            col.markdown(
                f"- **{r['name']}** — composite `{r['composite_score']:.3f}`"
            )

    if not benchmark.empty:
        st.markdown("### Held-out known-actives recovery")
        valid = benchmark[benchmark["rank_in_expected_category"].notna()]
        c1, c2, c3 = st.columns(3)
        for col, N in zip([c1, c2, c3], [10, 20, 50]):
            hit = (valid["rank_in_expected_category"].astype(int) <= N).sum()
            col.metric(
                f"Recovery@{N}",
                f"{hit}/{len(valid)}",
                f"{100*hit/len(valid):.0f}%"
            )
        st.caption(
            "21 clinically established mast-cell drugs were scored blind (not in seeds, "
            "not in reference sets). See EXP-006."
        )

    st.markdown("---")
    st.markdown(
        "### How to read these rankings\n"
        "Each compound's **composite score** is a weighted combination of:\n"
        "- `evidence_level` — published evidence weight (high / medium / low)\n"
        "- `weighted_target_similarity` — ligand-based screen vs. curated references per target\n"
        "- `warhead_score` — covalent reactive-group SMARTS detection (KEAP1 axis)\n"
        "- `safety_bonus` — predicted low hERG + low AMES from RandomForest QSAR\n"
        "- `BBB_score` — contextual (helps for neuro / remission, neutral for rescue)\n\n"
        "Full formula: [EXP-005](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-005-multi-objective-ranking.md). "
        "Pipeline overview: [methods.md](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/docs/methods.md)."
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

    display_cols = [
        "name", "composite_score", "subcategory", "mechanism",
        "evidence_level", "source", "has_warhead",
        "score_KEAP1", "score_MRGPRX2", "score_KIT", "score_HRH1",
        "hERG_score", "AMES_score", "BBB_score",
    ]
    display_cols = [c for c in display_cols if c in filtered.columns]

    tab.dataframe(
        filtered[display_cols].head(100),
        use_container_width=True,
        hide_index=True,
    )
    tab.caption(
        f"Showing {min(len(filtered), 100)} of {len(filtered)} matching candidates. "
        f"Lower hERG / AMES = better predicted safety. Higher BBB = more brain-penetrant."
    )

    with tab.expander("Inspect a single compound"):
        names = filtered["name"].tolist()
        if names:
            pick = st.selectbox("Compound", names, key=f"pick_{category}")
            row = filtered[filtered["name"] == pick].iloc[0]
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
            "No predictions found. Run `python scripts/build_mast_cell_predictor.py` "
            "and `python scripts/score_mast_cell.py`."
        )
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Training compounds", int(float(metrics.get("n_train_compounds", 0))))
        c2.metric("Active labels", int(float(metrics.get("n_train_active", 0))))
        c3.metric("Inactive labels", int(float(metrics.get("n_train_inactive", 0))))
        c4.metric(
            "5-fold CV AUC",
            f"{float(metrics.get('cv_mean_auc', 0)):.3f}",
            help="Strongest single model in the repo — beats hERG (0.81), AMES (0.90), BBB (0.91)."
        )

        st.markdown("### Prediction distribution")
        st.markdown(
            "Higher = more mast-cell-stabilizing-like. The integration bonus is +0.05 × p, "
            "so a compound predicted 0.8 gets +0.040 over an all-zero prior."
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
            "Caveat: the predictor is biased toward the chemotypes well-represented in the "
            "ChEMBL training data. Some classical mast-cell stabilizers (ketotifen, "
            "quercetin) score lower than expected — see EXP-016 §7.3. The universal +0.05 "
            "bonus is small precisely because the model is an out-of-distribution "
            "generalizer for natural-product chemotypes."
        )

# -----------------------------
# Tab 5: Compound deep-dive
# -----------------------------
with tabs[5]:
    st.subheader("🔍 Per-compound deep-dive")
    st.markdown(
        "Pick one compound and see every signal the pipeline computes for it: composite "
        "score per category, target similarities, ChEMBL predicted pIC50s, mast-cell "
        "predictor probability, Vina docking + ligand efficiency (if docked), C151 "
        "covalent-adduct energy (if ITC-class), and QSAR safety predictions."
    )

    ranked_all = load_ranked_all()
    library = load_library()
    chembl = load_chembl()
    c151 = load_c151()
    vina = load_vina()
    mc = load_mast_cell()

    # Build the union of all names that have any prediction.
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
            help="Includes library compounds (54) + AI-generated SFN-class analogs.",
        )

        # --- Identity ---
        st.markdown("### Identity")
        lib_row = library[library["name"] == pick]
        if not lib_row.empty:
            lib = lib_row.iloc[0]
            i1, i2, i3 = st.columns(3)
            i1.markdown(f"**Category:** `{lib.get('category', '?')}`")
            i2.markdown(f"**Subcategory:** `{lib.get('subcategory', '?')}`")
            i3.markdown(f"**Evidence:** `{lib.get('evidence_level', '?')}`")
            st.markdown(f"**Mechanism:** {lib.get('mechanism', '—')}")
            st.markdown(f"**Target(s):** `{lib.get('target', '—')}`")
            st.markdown(f"**SMILES:** `{lib.get('canonical_smiles') or lib.get('smiles', '—')}`")
            if pd.notna(lib.get("pubchem_cid")):
                cid = int(lib["pubchem_cid"])
                st.markdown(f"**PubChem:** [CID {cid}](https://pubchem.ncbi.nlm.nih.gov/compound/{cid})")
        else:
            # generated analog
            if not ranked_all.empty:
                gen = ranked_all[ranked_all["name"] == pick].iloc[0]
                st.markdown(f"**Source:** `{gen.get('source', 'generated')}`")
                st.markdown(f"**SMILES:** `{gen.get('smiles', '—')}`")

        # --- Composite scores ---
        st.markdown("### Composite ranks (per category)")
        cols = st.columns(3)
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

        # --- Mast-cell predictor ---
        if not mc.empty:
            mrow = mc[mc["name"] == pick]
            if not mrow.empty:
                p = float(mrow.iloc[0]["mast_cell_stabilizer_prob"])
                st.markdown("### Mast-cell stabilizer probability (EXP-016)")
                st.progress(min(max(p, 0.0), 1.0), text=f"p = {p:.3f}")

        # --- ChEMBL pIC50 across targets ---
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
                    "pIC50 = −log10(IC50 in M). 7 = 100 nM (good lead). 6 = 1 µM (moderate). "
                    "5 = 10 µM (weak). Per-target predictor CV R² varies — see EXP-011."
                )

        # --- Vina docking + LE ---
        if not vina.empty:
            vrow = vina[vina["name"] == pick]
            if not vrow.empty:
                v = vrow.iloc[0]
                st.markdown("### KEAP1 Kelch Vina docking (EXP-009)")
                v1, v2 = st.columns(2)
                v1.metric("Vina ΔG (kcal/mol)", f"{float(v.get('vina_dG_kcal_per_mol', 0)):.2f}")
                if pd.notna(v.get("ligand_efficiency")):
                    v2.metric("Ligand efficiency", f"{float(v['ligand_efficiency']):.3f}")
                st.caption("PDB 4L7B Kelch domain. Lower ΔG = better predicted affinity.")

        # --- C151 covalent adduct ---
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
            "Want to dig deeper? Click through to the experiments: "
            "[EXP-005 (ranking)](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-005-multi-objective-ranking.md) · "
            "[EXP-009 (Vina)](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-009-keap1-vina-docking.md) · "
            "[EXP-011 (ChEMBL)](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-011-chembl-bioassay-predictor.md) · "
            "[EXP-012 (C151)](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-012-covalent-c151-adduct.md) · "
            "[EXP-016 (mast-cell predictor)](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/experiments/EXP-016-mast-cell-predictor.md)."
        )

# -----------------------------
# Tab 6: Targets
# -----------------------------
with tabs[6]:
    st.subheader("Druggable MCAS targets")
    st.markdown(
        "UniProt-indexed targets the pipeline scores compounds against. "
        "AlphaFold structures linked per row."
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
# Tab 9: Benchmark
# -----------------------------
with tabs[9]:
    st.subheader("Known-Actives Recovery benchmark (EXP-006)")
    st.markdown(
        "Blind scoring of 21 clinically established mast-cell drugs that are **not** in our "
        "seeds JSON and **not** in the reference ligand sets. The pipeline should recover them "
        "into the top of their expected category."
    )
    benchmark = load_benchmark()
    if benchmark.empty:
        st.info("Benchmark not run yet. See EXP-006.")
    else:
        valid = benchmark[benchmark["rank_in_expected_category"].notna()].copy()
        valid["rank_in_expected_category"] = valid["rank_in_expected_category"].astype(int)

        c1, c2, c3 = st.columns(3)
        for col, N in zip([c1, c2, c3], [10, 20, 50]):
            hit = (valid["rank_in_expected_category"] <= N).sum()
            col.metric(f"Overall recovery@{N}", f"{hit}/{len(valid)}", f"{100*hit/len(valid):.0f}%")

        st.markdown("### Per-category recovery")
        cat_rows = []
        for cat in ("rescue", "maintenance", "remission"):
            sub = valid[valid["expected_category"] == cat]
            row = {"category": cat, "n": len(sub)}
            for N in (10, 20, 50):
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
        "[AGENT_CARD.md](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/AGENT_CARD.md) "
        "for the human-readable version.\n\n"
        "**Status:** v0.1.0 — alpha. The headline result (sulforaphane #1 in remission) "
        "has passed an internal recovery audit but has **not** been validated in human "
        "mast cells. Wet-lab campaigns are on the roadmap."
    )

    st.markdown("### Limitations (read before citing)")
    st.markdown(
        "- Composite weights are author-chosen, not learned.\n"
        "- Ligand-based screening is similarity to known references — not physics-based docking.\n"
        "- QSAR is RandomForest on Morgan FP — strong baseline, not state-of-the-art.\n"
        "- No predictions of CYP / GST / UGT metabolism, drug-drug interactions, or efflux.\n"
        "- Reference ligand self-similarity caps recovery@5/@10 (see EXP-006 §7).\n"
        "- 21-compound recovery benchmark is small; expansion to 50+ is on the roadmap."
    )

    st.markdown("### Contact")
    st.markdown(
        "All routes go through GitHub for public traceability. "
        "See [CONTACT.md](https://github.com/mrdulasolutions/MCAS.Opensource/blob/main/CONTACT.md)."
    )

    st.markdown("---")
    st.caption(
        f"Page rendered {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}. "
        f"Underlying data refreshes whenever `scripts/rank_hypotheses.py` is rerun in the repo."
    )
