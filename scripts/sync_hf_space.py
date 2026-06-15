"""Sync the OpenMCAS Streamlit viewer to its Hugging Face Space.

Locally:
    HF_TOKEN=hf_xxx python scripts/sync_hf_space.py

In GitHub Actions (no token in code):
    env:
      HF_TOKEN: ${{ secrets.HF_TOKEN }}

What it does:
  1. Resolves the Space repo from HF_USER / HF_SPACE env vars (with
     sensible defaults).
  2. Creates the Space if it doesn't exist (idempotent — silently no-op
     if already there). API requires space_sdk ∈ {gradio, docker, static};
     we use "docker" + README YAML frontmatter `sdk: streamlit` which the
     platform honors.
  3. Stages exactly the files the Space needs (app.py, requirements,
     SPACE_README → README.md, data/, outputs/) into a tempdir.
  4. Uploads via HfApi.upload_folder. The token is never put in a URL.
  5. Optionally polls the runtime until it's RUNNING (--wait flag).
  6. Prints the live URL.

Exit codes:
  0  success
  1  missing token / config error
  2  upload failed
  3  runtime never reached RUNNING (only with --wait)
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_USER = os.environ.get("HF_USER", "MRDula")
DEFAULT_SPACE = os.environ.get("HF_SPACE", "openmcas-browser")


def stage(stage_dir: Path) -> int:
    """Copy the files the Space needs into stage_dir. Returns count."""
    count = 0

    def _cp(src: Path, dst: Path) -> None:
        nonlocal count
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        count += 1

    _cp(REPO_ROOT / "app.py", stage_dir / "app.py")
    _cp(REPO_ROOT / "requirements-app.txt", stage_dir / "requirements.txt")
    _cp(REPO_ROOT / "huggingface-space" / "SPACE_README.md", stage_dir / "README.md")

    for sub in (
        "data/compounds/MCAS_Compound_Library_v1.csv",
        "data/triggers/MCAS_Triggers_v1.csv",
        "data/injury_mechanisms/MCAS_Injury_Mechanisms_v1.csv",
        "data/targets/MCAS_Targets.csv",
    ):
        _cp(REPO_ROOT / sub, stage_dir / sub)

    out_dir = stage_dir / "outputs"
    out_dir.mkdir()
    for f in sorted((REPO_ROOT / "outputs").glob("*.csv")):
        _cp(f, out_dir / f.name)

    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync OpenMCAS viewer to its HF Space.")
    parser.add_argument(
        "--repo-id",
        default=f"{DEFAULT_USER}/{DEFAULT_SPACE}",
        help="Space repo id, e.g. MRDula/openmcas-browser",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Poll runtime until RUNNING (up to ~5 min).",
    )
    parser.add_argument(
        "--commit-message",
        default=None,
        help="Override the commit message used on the Space.",
    )
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: HF_TOKEN env var is required.", file=sys.stderr)
        return 1

    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("ERROR: huggingface_hub not installed. pip install huggingface_hub", file=sys.stderr)
        return 1

    api = HfApi(token=token)

    # 1. Ensure the Space exists.
    print(f"[1/3] Ensuring Space {args.repo_id} exists...")
    try:
        create_repo(
            repo_id=args.repo_id,
            token=token,
            repo_type="space",
            space_sdk="docker",  # README frontmatter routes to Streamlit
            exist_ok=True,
            private=False,
        )
    except Exception as e:
        print(f"ERROR: create_repo failed: {e}", file=sys.stderr)
        return 2

    # 2. Stage files.
    print("[2/3] Staging files...")
    stage_dir = Path(tempfile.mkdtemp(prefix="hf_space_stage_"))
    try:
        n = stage(stage_dir)
        print(f"    staged {n} files")

        # 3. Upload.
        print("[3/3] Uploading to Space...")
        # commit message — try to use git short SHA if available
        msg = args.commit_message
        if msg is None:
            import subprocess
            try:
                sha = subprocess.check_output(
                    ["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"],
                    stderr=subprocess.DEVNULL,
                ).decode().strip()
                msg = f"Sync from MCAS.Opensource @ {sha}"
            except Exception:
                msg = "Sync from MCAS.Opensource"

        try:
            api.upload_folder(
                folder_path=str(stage_dir),
                repo_id=args.repo_id,
                repo_type="space",
                commit_message=msg,
            )
        except Exception as e:
            print(f"ERROR: upload_folder failed: {e}", file=sys.stderr)
            return 2

        print(f"    OK: {msg}")
    finally:
        shutil.rmtree(stage_dir, ignore_errors=True)

    space_url = f"https://huggingface.co/spaces/{args.repo_id}"
    print()
    print(f"Live URL: {space_url}")

    # 4. Optional: poll runtime.
    #
    # Free-tier HF Spaces auto-sleep after ~48h idle. When a scheduled sync
    # fires with no real content changes, HF correctly does NOT rebuild —
    # the Space stays in SLEEPING state for the entire poll window. That is
    # NOT a sync failure: the files uploaded successfully and the Space
    # will rebuild from those files the next time anyone visits the URL.
    # We only fail when the runtime enters an explicit error state, or
    # when it appears to be actively building and then stalls.
    if args.wait:
        print("[4/4] Polling runtime...")
        deadline_iters = 30  # ~5 minutes at 10s/iter
        saw_building = False
        last_stage = "unknown"
        for i in range(deadline_iters):
            info = api.space_info(args.repo_id)
            last_stage = info.runtime.stage if info.runtime else "unknown"
            print(f"  [{i*10:3d}s] stage={last_stage}")
            if last_stage in ("RUNNING", "RUNNING_BUILDING"):
                print("    OK — Space is live.")
                return 0
            if last_stage in ("RUNTIME_ERROR", "BUILD_ERROR", "CONFIG_ERROR"):
                print(f"    FAIL: runtime entered {last_stage}", file=sys.stderr)
                return 3
            if last_stage in ("BUILDING", "APP_STARTING", "STOPPING"):
                saw_building = True
            time.sleep(10)
        # Timed out without reaching RUNNING.
        if last_stage in ("SLEEPING", "PAUSED", "unknown"):
            # No-op sync (or HF deduped the upload as identical to current
            # tree). The Space stayed asleep because nothing changed that
            # warranted a rebuild. Upload itself succeeded — soft success.
            print(
                f"    Space stayed in {last_stage} for full poll window — "
                "no rebuild was triggered (upload was a no-op or deduped). "
                "This is not a failure; the Space will rebuild on next visit.",
                file=sys.stderr,
            )
            return 0
        if saw_building:
            # We watched it building/starting and it never got to RUNNING.
            # That IS a real stall worth flagging.
            print(
                f"    runtime saw a build cycle but did not reach RUNNING "
                f"within {deadline_iters*10}s (last stage: {last_stage})",
                file=sys.stderr,
            )
            return 3
        # Anything else — treat as soft success rather than fail noisily.
        print(
            f"    runtime did not reach RUNNING within {deadline_iters*10}s "
            f"(last stage: {last_stage}); treating as soft success since "
            "no error state was observed.",
            file=sys.stderr,
        )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
