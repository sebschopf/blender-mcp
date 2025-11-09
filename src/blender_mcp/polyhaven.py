"""Small helpers for interacting with the PolyHaven files API.

These helpers keep network & parsing logic separate from Blender-specific
code so we can unit-test the behaviour without Blender.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "blender-mcp"})


def fetch_files_data(asset_id: str, *, timeout: int = 10) -> Dict[str, Any]:
    """Fetch files metadata for a PolyHaven asset.

    Raises RuntimeError on non-200 responses.
    """
    url = f"https://api.polyhaven.com/files/{asset_id}"
    resp = requests.get(url, headers=REQ_HEADERS, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to get asset files: {resp.status_code}")
    return resp.json()


def fetch_categories(asset_type: str, *, timeout: int = 10) -> Dict[str, Any]:
    """Fetch categories for a given asset type from PolyHaven.

    Raises RuntimeError on non-200 responses.
    """
    url = f"https://api.polyhaven.com/categories/{asset_type}"
    resp = requests.get(url, headers=REQ_HEADERS, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to get categories: {resp.status_code}")
    return resp.json()


def search_assets(params: Dict[str, Any], *, timeout: int = 10) -> Dict[str, Any]:
    """Search assets on PolyHaven using the /assets endpoint.

    params: query parameters forwarded to the API (e.g. type, categories)
    Returns parsed JSON (dict of assets).
    """
    url = "https://api.polyhaven.com/assets"
    resp = requests.get(url, params=params, headers=REQ_HEADERS, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to search assets: {resp.status_code}")
    return resp.json()


def find_texture_map_urls(
    files_data: Dict[str, Any], resolution: str, file_format: str
) -> Dict[str, str]:
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


def find_model_file_info(
    files_data: Dict[str, Any], file_format: str, resolution: str
) -> Optional[Dict[str, Any]]:
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


def download_bytes(url: str, *, timeout: int = 30) -> bytes:
    """Download bytes from url, raising RuntimeError on non-200."""
    resp = requests.get(url, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to download URL: {resp.status_code}")
    return resp.content


def prepare_model_files(
    file_info: Dict[str, Any], *, base_temp_dir: Optional[str] = None
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
    content = download_bytes(main_url)
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
        inc_bytes = download_bytes(inc_url)
        with open(dest_path, "wb") as fh:
            fh.write(inc_bytes)

    return temp_dir, main_path
