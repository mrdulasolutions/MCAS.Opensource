# Deploying the public viewer

The Streamlit app in [`app.py`](../app.py) is a zero-clone, browser-friendly
front-end to every ranking in the repo. **The Space auto-redeploys on every
push to `main` that touches `app.py`, `data/`, `outputs/`, or the Space
README** — see the GitHub Actions section below.

## Live URL

🌐 https://huggingface.co/spaces/MRDula/openmcas-browser

## Auto-sync via GitHub Actions (recommended, zero-touch)

The repo ships with [`.github/workflows/sync-hf-space.yml`](../.github/workflows/sync-hf-space.yml).
It re-syncs the Space whenever:
- A push to `main` changes any of: `app.py`, `requirements-app.txt`,
  `huggingface-space/SPACE_README.md`, `scripts/sync_hf_space.py`,
  `data/**`, `outputs/**`, the workflow file itself.
- Someone clicks **Run workflow** in the Actions tab (manual override
  with an optional `repo_id` input).

### One-time setup

1. Generate a write-scoped HF token at https://huggingface.co/settings/tokens.
2. In the GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**.
3. Name: `HF_TOKEN`. Value: the token (starts with `hf_...`).
4. (Optional) Add repo Variables `HF_USER` and `HF_SPACE` if your fork
   deploys to a different namespace.

That's it. The next push that touches one of the watched paths will
fire the workflow, sync the Space, and post a summary with the live URL.

## Manual sync (no GitHub Actions, no clone)

```bash
HF_TOKEN=hf_xxx python scripts/sync_hf_space.py --wait
```

The `--wait` flag polls the Space's runtime stage until it reports
`RUNNING` (or fails). Without `--wait` the script returns as soon as
the upload commits.

## Three alternative deployment paths (manual)

### 1. Hugging Face Spaces (manual)

1. Create a new Space at https://huggingface.co/new-space.
   - **SDK:** Streamlit
   - **Hardware:** CPU basic (free tier — sufficient for read-only viewer).
2. In the Space's `README.md`, add the YAML frontmatter (the Hugging Face
   Spaces config block):

   ```yaml
   ---
   title: OpenMCAS Hypothesis Browser
   emoji: 🧬
   colorFrom: green
   colorTo: blue
   sdk: streamlit
   sdk_version: "1.32.0"
   app_file: app.py
   pinned: false
   license: mit
   ---
   ```
3. Push this entire repo to the Space:

   ```bash
   git remote add hf https://huggingface.co/spaces/<your-handle>/openmcas-browser
   git push hf main
   ```
4. The Space will auto-detect `requirements-app.txt`, install streamlit + pandas,
   and serve `app.py`. Build takes ~1–2 minutes.

### 2. Streamlit Community Cloud

1. Connect the GitHub repo to https://streamlit.io/cloud.
2. Point the deployment at:
   - **Main file path:** `app.py`
   - **Requirements file:** `requirements-app.txt`
3. Auto-deploys on every push.

### 3. Local

```bash
pip install -r requirements-app.txt
streamlit run app.py
```

Browser opens at `http://localhost:8501`.

## Data freshness

The app reads the same CSV files that `scripts/rank_hypotheses.py` writes.
Every commit that re-runs the ranking pipeline updates the viewer.

If you want the viewer to display *predicted* rankings for a SMILES the
user pastes in, that requires running the scoring pipeline inside the
Streamlit process. RDKit + scikit-learn make this feasible but multiply
the Space's RAM requirement. A self-contained "score-my-SMILES" variant
is on the [roadmap](../ROADMAP.md) — open an issue if you want to drive
it.

## Disclaimer (please don't strip)

The viewer surfaces an "Not medical advice" banner at the top of every
page. Don't remove it. If you deploy a fork, please keep:
- the disclaimer banner,
- the link to [docs/disclaimers.md](disclaimers.md),
- the provider attribution to MR Dula Medical.
