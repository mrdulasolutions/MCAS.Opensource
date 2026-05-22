#!/usr/bin/env bash
# Deploy the OpenMCAS Streamlit viewer to a Hugging Face Space.
#
# Usage:
#   HF_TOKEN=hf_xxx HF_USER=mrdulasolutions HF_SPACE=openmcas-browser ./huggingface-space/deploy.sh
#
# Or (if you're already authenticated via `huggingface-cli login`):
#   HF_USER=mrdulasolutions HF_SPACE=openmcas-browser ./huggingface-space/deploy.sh
#
# What it does:
#   1. Creates the Space (idempotent — no-op if it already exists).
#   2. Clones the Space's git repo to a tmp dir.
#   3. Syncs the files the Streamlit app needs (app.py, requirements,
#      data, outputs, docs/disclaimers.md) and the SPACE_README.md as
#      the Space's README.md.
#   4. Commits + pushes.
#   5. Prints the live Space URL.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

: "${HF_USER:=mrdulasolutions}"
: "${HF_SPACE:=openmcas-browser}"

echo "Target: https://huggingface.co/spaces/${HF_USER}/${HF_SPACE}"

# 1. Create the Space (programmatic; idempotent).
echo "[1/4] Ensuring Space exists..."
python3 - <<PY
import os, sys
try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    sys.exit("huggingface_hub not installed. pip install huggingface_hub")

token = os.environ.get("HF_TOKEN")
if not token:
    # Fall back to cached token from huggingface-cli login
    from huggingface_hub import HfFolder
    token = HfFolder.get_token()
if not token:
    sys.exit("No HF_TOKEN. Either set HF_TOKEN env var or run 'huggingface-cli login' first.")

repo_id = f"${HF_USER}/${HF_SPACE}"
try:
    create_repo(
        repo_id=repo_id,
        token=token,
        repo_type="space",
        space_sdk="streamlit",
        exist_ok=True,
        private=False,
    )
    print(f"Space ensured: {repo_id}")
except Exception as e:
    sys.exit(f"create_repo failed: {e}")
PY

# 2. Clone the Space repo into a tmp dir.
echo "[2/4] Cloning Space repo..."
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
SPACE_URL="https://${HF_USER}:${HF_TOKEN:-$(python3 -c "from huggingface_hub import HfFolder; print(HfFolder.get_token())")}@huggingface.co/spaces/${HF_USER}/${HF_SPACE}"
git -C "$TMPDIR" clone "$SPACE_URL" space
SPACE_DIR="$TMPDIR/space"

# 3. Sync needed files.
echo "[3/4] Syncing files..."
cp "${REPO_ROOT}/app.py"                          "${SPACE_DIR}/app.py"
cp "${REPO_ROOT}/requirements-app.txt"            "${SPACE_DIR}/requirements.txt"
cp "${REPO_ROOT}/huggingface-space/SPACE_README.md" "${SPACE_DIR}/README.md"
mkdir -p "${SPACE_DIR}/data/compounds" "${SPACE_DIR}/data/triggers" "${SPACE_DIR}/data/injury_mechanisms" "${SPACE_DIR}/data/targets"
cp "${REPO_ROOT}/data/compounds/MCAS_Compound_Library_v1.csv"    "${SPACE_DIR}/data/compounds/"
cp "${REPO_ROOT}/data/triggers/MCAS_Triggers_v1.csv"             "${SPACE_DIR}/data/triggers/"
cp "${REPO_ROOT}/data/injury_mechanisms/MCAS_Injury_Mechanisms_v1.csv" "${SPACE_DIR}/data/injury_mechanisms/"
cp "${REPO_ROOT}/data/targets/MCAS_Targets.csv"                  "${SPACE_DIR}/data/targets/"
mkdir -p "${SPACE_DIR}/outputs"
cp "${REPO_ROOT}/outputs/"ranked_*.csv                           "${SPACE_DIR}/outputs/" 2>/dev/null || true
cp "${REPO_ROOT}/outputs/"docking_*.csv                          "${SPACE_DIR}/outputs/" 2>/dev/null || true
cp "${REPO_ROOT}/outputs/warhead_scores.csv"                     "${SPACE_DIR}/outputs/" 2>/dev/null || true
cp "${REPO_ROOT}/outputs/qsar_predictions.csv"                   "${SPACE_DIR}/outputs/" 2>/dev/null || true
cp "${REPO_ROOT}/outputs/reinvent_generated.csv"                 "${SPACE_DIR}/outputs/" 2>/dev/null || true
cp "${REPO_ROOT}/outputs/benchmark_known_actives.csv"            "${SPACE_DIR}/outputs/" 2>/dev/null || true

# 4. Commit + push.
echo "[4/4] Committing + pushing..."
cd "${SPACE_DIR}"
git config user.email "deploy@mrdula.solutions"
git config user.name "MR Dula Medical (deploy bot)"
git add -A
if git diff --cached --quiet; then
    echo "Nothing to push — Space is already up to date."
else
    git commit -m "Sync OpenMCAS Streamlit viewer from MCAS.Opensource@$(git -C "${REPO_ROOT}" rev-parse --short HEAD)"
    git push origin main
    echo
    echo "✅ Live at: https://huggingface.co/spaces/${HF_USER}/${HF_SPACE}"
fi
