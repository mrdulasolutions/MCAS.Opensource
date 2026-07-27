"""Prepare (and optionally deposit) a Zenodo snapshot of OpenMCAS.

Usage:
  # Write local deposit metadata + file manifest (no network):
  python scripts/deposit_zenodo.py --prepare-only

  # Create a Zenodo deposition (requires ZENODO_TOKEN):
  python scripts/deposit_zenodo.py --deposit
  # Use sandbox:
  python scripts/deposit_zenodo.py --deposit --sandbox

Token: set env ZENODO_TOKEN (or ZENODO_SANDBOX_TOKEN for --sandbox).
Creates/updates:
  - .zenodo.json  (DataCite-ish metadata for the GitHub–Zenodo integration)
  - outputs/zenodo/deposit_metadata.json
  - outputs/zenodo/FILELIST.md
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "outputs" / "zenodo"


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def build_metadata(version: str, sha: str) -> dict:
    return {
        "title": f"OpenMCAS: open MCAS/MCAD compound hypothesis pipeline ({version})",
        "upload_type": "software",
        "description": (
            "OpenMCAS is an MIT-licensed, CPU-reproducible cheminformatics pipeline "
            "that ranks pharma drugs, herbs, supplements, and AI-generated analogs "
            "for mast cell activation syndrome (MCAS/MCAD) across rescue, maintenance, "
            "and remission categories. This snapshot freezes code, curated data, "
            f"ranked outputs, and experiment reports at git commit {sha[:12]}."
        ),
        "creators": [
            {
                "name": "Dula, M. R.",
                "affiliation": "MR Dula Medical (DBA of MR Dula Enterprise, LLC), Raleigh, NC, USA",
            }
        ],
        "keywords": [
            "MCAS",
            "MCAD",
            "mast cell",
            "drug discovery",
            "cheminformatics",
            "open science",
            "KEAP1",
            "sulforaphane",
        ],
        "license": "mit",
        "access_right": "open",
        "related_identifiers": [
            {
                "identifier": "https://github.com/mrdulasolutions/MCAS.Opensource",
                "relation": "isSupplementTo",
                "resource_type": "software",
            },
            {
                "identifier": "https://huggingface.co/spaces/MRDula/openmcas-browser",
                "relation": "isSupplementTo",
                "resource_type": "other",
            },
        ],
        "version": version,
        "notes": f"Git commit: {sha}",
    }


def write_filelist() -> list[str]:
    patterns = [
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "pyproject.toml",
        "app.py",
        "scripts/*.py",
        "data/**/*",
        "outputs/*.csv",
        "outputs/exp_017/*",
        "outputs/keap1_btb/*",
        "experiments/*.md",
        "docs/**/*",
        "hypotheses/*.md",
        "audiences/*.md",
    ]
    lines = [
        f"# OpenMCAS Zenodo file list — {date.today().isoformat()}",
        "",
        "Primary artifacts to include in a software snapshot:",
        "",
    ]
    for p in patterns:
        lines.append(f"- `{p}`")
    lines.append("")
    lines.append("Exclude: `.venv/`, `.tools/vina` binary (link to upstream release), "
                 "`__pycache__/`, large raw ChEMBL dumps if re-fetchable.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "FILELIST.md").write_text("\n".join(lines) + "\n")
    return patterns


def prepare(version: str) -> Path:
    sha = git_sha()
    meta = build_metadata(version, sha)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "deposit_metadata.json"
    path.write_text(json.dumps(meta, indent=2) + "\n")
    # GitHub–Zenodo integration file at repo root
    zenodo_root = {
        "title": meta["title"],
        "description": meta["description"],
        "creators": meta["creators"],
        "keywords": meta["keywords"],
        "license": "MIT",
        "upload_type": "software",
        "access_right": "open",
        "version": version,
    }
    (REPO_ROOT / ".zenodo.json").write_text(json.dumps(zenodo_root, indent=2) + "\n")
    write_filelist()
    print(f"wrote {path.relative_to(REPO_ROOT)}")
    print(f"wrote .zenodo.json")
    print(f"wrote {OUT_DIR.relative_to(REPO_ROOT)}/FILELIST.md")
    print(f"commit {sha}")
    return path


def deposit(version: str, sandbox: bool) -> int:
    token = os.environ.get("ZENODO_SANDBOX_TOKEN" if sandbox else "ZENODO_TOKEN")
    if not token:
        print(
            "[FAIL] Set ZENODO_TOKEN (or ZENODO_SANDBOX_TOKEN with --sandbox).",
            file=sys.stderr,
        )
        print("Prepared local metadata only would work with --prepare-only.", file=sys.stderr)
        return 1
    import urllib.request

    base = "https://sandbox.zenodo.org/api" if sandbox else "https://zenodo.org/api"
    meta_path = prepare(version)
    meta = json.loads(meta_path.read_text())
    # Create deposition
    req = urllib.request.Request(
        f"{base}/deposit/depositions",
        data=json.dumps({"metadata": meta}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            dep = json.load(resp)
    except Exception as e:
        print(f"[FAIL] create deposition: {e}", file=sys.stderr)
        return 1
    print(f"created deposition id={dep.get('id')} "
          f"draft={dep.get('links', {}).get('html')}")
    (OUT_DIR / "deposition_response.json").write_text(json.dumps(dep, indent=2) + "\n")
    print("Upload archive files via the Zenodo UI or extend this script with "
          "bucket uploads. Metadata draft is ready.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--prepare-only", action="store_true")
    p.add_argument("--deposit", action="store_true")
    p.add_argument("--sandbox", action="store_true")
    p.add_argument("--version", default="0.2.0")
    args = p.parse_args()
    if args.deposit:
        return deposit(args.version, args.sandbox)
    prepare(args.version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
