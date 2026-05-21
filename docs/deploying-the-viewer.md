# Deploying the public viewer

The Streamlit app in [`app.py`](../app.py) is a zero-clone, browser-friendly
front-end to every ranking in the repo. Three ways to deploy:

## 1. Hugging Face Spaces (recommended — free, easy)

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

## 2. Streamlit Community Cloud

1. Connect the GitHub repo to https://streamlit.io/cloud.
2. Point the deployment at:
   - **Main file path:** `app.py`
   - **Requirements file:** `requirements-app.txt`
3. Auto-deploys on every push.

## 3. Local

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
