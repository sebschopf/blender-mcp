"""Small helpers for interacting with the PolyHaven files API.

These helpers keep network & parsing logic separate from Blender-specific
code so we can unit-test the behaviour without Blender.

Deprecated: use the service-layer helpers under ``blender_mcp.services.polyhaven``.
They provide validated parameters and canonical response formatting. This
module remains as a compatibility façade and will be removed in a future
release cycle.
"""

from __future__ import annotations

import warnings as _warnings
from typing import Any, Dict, Optional

import requests
import warnings as _warnings

_warnings.warn(
    "blender_mcp.polyhaven est déprécié; utiliser blender_mcp.services.polyhaven à la place.",
    DeprecationWarning,
    stacklevel=2,
)

_warnings.warn(
    "blender_mcp.polyhaven est déprécié; utiliser blender_mcp.services.polyhaven à la place.",
    DeprecationWarning,
    stacklevel=2,
)

# Prefer the shared session headers but keep a module-level default for callers
_REQ_HEADERS = requests.utils.default_headers()
_REQ_HEADERS.update({"User-Agent": "blender-mcp"})


def fetch_files_data(
    asset_id: str, *, timeout: int = 10, session: Optional[requests.sessions.Session] = None
) -> Dict[str, Any]:
    """Fetch files metadata for a PolyHaven asset.

    Raises RuntimeError on non-200 responses.
    """
    url = f"https://api.polyhaven.com/files/{asset_id}"
    if session is None:
        # maintain test- and backwards-compatibility (tests monkeypatch poly.requests.get)
        resp = requests.get(url, headers=_REQ_HEADERS, timeout=timeout)
    else:
        sess = session
        # merge headers so caller-provided session headers take precedence
        headers = dict(_REQ_HEADERS)
        headers.update(getattr(sess, "headers", {}))
        resp = sess.get(url, headers=headers, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to get asset files: {resp.status_code}")
    return resp.json()


def fetch_categories(
    asset_type: str, *, timeout: int = 10, session: Optional[requests.sessions.Session] = None
) -> Dict[str, Any]:
    """Fetch categories for a given asset type from PolyHaven.

    Raises RuntimeError on non-200 responses.
    """
    url = f"https://api.polyhaven.com/categories/{asset_type}"
    if session is None:
        resp = requests.get(url, headers=_REQ_HEADERS, timeout=timeout)
    else:
        sess = session
        headers = dict(_REQ_HEADERS)
        headers.update(getattr(sess, "headers", {}))
        resp = sess.get(url, headers=headers, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to get categories: {resp.status_code}")
    return resp.json()


def search_assets(
    params: Dict[str, Any], *, timeout: int = 10, session: Optional[requests.sessions.Session] = None
) -> Dict[str, Any]:
    """Search assets on PolyHaven using the /assets endpoint.

    params: query parameters forwarded to the API (e.g. type, categories)
    Returns parsed JSON (dict of assets).
    """
    url = "https://api.polyhaven.com/assets"
    if session is None:
        resp = requests.get(url, params=params, headers=_REQ_HEADERS, timeout=timeout)
    else:
        sess = session
        headers = dict(_REQ_HEADERS)
        headers.update(getattr(sess, "headers", {}))
        resp = sess.get(url, params=params, headers=headers, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to search assets: {resp.status_code}")
    return resp.json()


def find_texture_map_urls(files_data: Dict[str, Any], resolution: str, file_format: str) -> Dict[str, str]:
    """Return a mapping map_type -> download URL for texture maps matching
    the requested resolution and file_format.

    Returns empty dict if nothing found.
    """
    out: Dict[str, str] = {}
    for map_type, entry in files_data.items():
        if map_type in ("blend", "gltf"):
            continue
        # entry is expected to be a dict keyed by resolution
        if not isinstance(entry, dict):
            continue
        res_block = entry.get(resolution)
        if not isinstance(res_block, dict):
            continue
        fmt_block = res_block.get(file_format)
        if not isinstance(fmt_block, dict):
            continue
        url = fmt_block.get("url")
        if url:
            out[map_type] = url
    return out


def find_model_file_info(files_data: Dict[str, Any], file_format: str, resolution: str) -> Optional[Dict[str, Any]]:
    """Return the file_info dict for a model in the requested format/resolution,
    or None if not found.
    """
    ff_block = files_data.get(file_format)
    if not isinstance(ff_block, dict):
        return None
    res_block = ff_block.get(resolution)
    if not isinstance(res_block, dict):
        return None
    # Some responses nest again with file_format as key; try to be permissive
    if file_format in res_block and isinstance(res_block[file_format], dict):
        return res_block[file_format]
    # Otherwise assume res_block is directly the file_info
    return res_block


def download_bytes(url: str, *, timeout: int = 30, session: Optional[requests.sessions.Session] = None) -> bytes:
    """Download bytes from url, raising RuntimeError on non-200.

    Accepts an optional `requests.Session` (or session-like) for testing and
    connection reuse. Falls back to the shared `get_session()`.
    """
    if session is None:
        resp = requests.get(url, timeout=timeout)
    else:
        sess = session
        resp = sess.get(url, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to download URL: {resp.status_code}")
    return resp.content


def prepare_model_files(
    file_info: Dict[str, Any],
    *,
    base_temp_dir: Optional[str] = None,
    session: Optional[requests.sessions.Session] = None,
) -> tuple[str, str]:
    """Download main model file and any included files to a temporary dir.

    Returns (temp_dir, main_file_path).

    file_info is expected to contain at least a 'url' key and optionally an
    'include' mapping where keys are relative paths and values contain 'url'.
    """
    import os
    import tempfile

    temp_dir = base_temp_dir or tempfile.mkdtemp(prefix="blender_mcp_")

    # Main file
    main_url = file_info.get("url")
    if not main_url:
        raise RuntimeError("No main file URL in file_info")

    main_name = main_url.split("/")[-1]
    main_path = os.path.join(temp_dir, main_name)

    # Download main file
    # Call download_bytes compatibly: only pass `session` kw when provided so
    # tests that monkeypatch poly.download_bytes (without session kw) keep working.
    if session is None:
        content = download_bytes(main_url)
    else:
        content = download_bytes(main_url, session=session)
    with open(main_path, "wb") as fh:
        fh.write(content)

    # Handle includes
    includes = file_info.get("include") or {}
    for rel_path, inc_info in includes.items():
        inc_url = inc_info.get("url") if isinstance(inc_info, dict) else None
        if not inc_url:
            continue
        dest_path = os.path.join(temp_dir, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        if session is None:
            inc_bytes = download_bytes(inc_url)
        else:
            inc_bytes = download_bytes(inc_url, session=session)
        with open(dest_path, "wb") as fh:
            fh.write(inc_bytes)

    return temp_dir, main_path
