"""PubChem PUG-REST client for fetching canonical SMILES.

Throttled to 5 req/s (PubChem's published limit). Caches responses to
data/compounds/.smiles_cache.json so reruns are free.

Usage:
    from fetch_smiles import fetch_by_cid, fetch_by_name
    smiles = fetch_by_cid(5280343)
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

import requests

PUG_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
RATE_LIMIT_PER_SEC = 5
_LAST_CALL = [0.0]

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = REPO_ROOT / "data" / "compounds" / ".smiles_cache.json"


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True))


def _throttle() -> None:
    elapsed = time.time() - _LAST_CALL[0]
    min_interval = 1.0 / RATE_LIMIT_PER_SEC
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    _LAST_CALL[0] = time.time()


def _request_json(url: str, retries: int = 3, backoff: float = 1.5) -> Optional[dict]:
    for attempt in range(retries):
        _throttle()
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 404:
                return None
            if resp.status_code in (429, 503):
                time.sleep(backoff ** (attempt + 1))
                continue
            return None
        except requests.RequestException:
            time.sleep(backoff ** (attempt + 1))
    return None


def fetch_by_cid(cid: int) -> dict:
    """Return {'isomeric_smiles': ..., 'canonical_smiles': ...} or empty dict.

    PubChem's modern PUG-REST returns 'SMILES' (isomeric with stereo) and
    'ConnectivitySMILES' (no stereo). We also fall back to the legacy
    'IsomericSMILES' / 'CanonicalSMILES' keys in case of API rollback.
    """
    cache = _load_cache()
    key = f"cid:{cid}"
    if key in cache and cache[key]:
        return cache[key]
    url = f"{PUG_BASE}/compound/cid/{cid}/property/SMILES,ConnectivitySMILES/JSON"
    data = _request_json(url)
    result: dict = {}
    if data:
        try:
            props = data["PropertyTable"]["Properties"][0]
            iso = props.get("SMILES") or props.get("IsomericSMILES") or ""
            can = props.get("ConnectivitySMILES") or props.get("CanonicalSMILES") or iso
            result = {
                "isomeric_smiles": iso,
                "canonical_smiles": can,
            }
        except (KeyError, IndexError):
            result = {}
    cache[key] = result
    _save_cache(cache)
    return result


def fetch_by_name(name: str) -> dict:
    """Lookup CID by name then fetch SMILES. Returns {'cid', 'isomeric_smiles', 'canonical_smiles'}."""
    cache = _load_cache()
    key = f"name:{name.lower()}"
    if key in cache:
        return cache[key]
    url = f"{PUG_BASE}/compound/name/{requests.utils.quote(name)}/cids/JSON"
    data = _request_json(url)
    if not data:
        cache[key] = {}
        _save_cache(cache)
        return {}
    try:
        cid = data["IdentifierList"]["CID"][0]
    except (KeyError, IndexError):
        cache[key] = {}
        _save_cache(cache)
        return {}
    smiles = fetch_by_cid(cid)
    result = {"cid": cid, **smiles}
    cache[key] = result
    _save_cache(cache)
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fetch_smiles.py <CID or name>")
        sys.exit(1)
    arg = sys.argv[1]
    if arg.isdigit():
        print(json.dumps(fetch_by_cid(int(arg)), indent=2))
    else:
        print(json.dumps(fetch_by_name(arg), indent=2))
