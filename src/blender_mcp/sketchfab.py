"""Helpers to interact with the Sketchfab API.

These are pure helpers that centralize network I/O and parsing so they can
be unit-tested independently of the Blender addon.

Deprecated: utiliser désormais ``blender_mcp.services.sketchfab`` pour une
validation des paramètres et un schéma de réponse canonique. Ce module reste
temporairement pour compatibilité et sera retiré dans un cycle futur.
"""

from __future__ import annotations

import json
import warnings as _warnings
from typing import Any, Dict, Optional

import requests

_warnings.warn(
    "blender_mcp.sketchfab est déprécié; utiliser blender_mcp.services.sketchfab.",
    DeprecationWarning,
    stacklevel=2,
)

_warnings.warn(
    "blender_mcp.sketchfab est déprécié; utiliser blender_mcp.services.sketchfab.",
    DeprecationWarning,
    stacklevel=2,
)

from . import downloaders  # type: ignore

# Base endpoints can be overridden in tests by passing a session that wraps
# the desired base URL. Keeping them as module constants makes the helpers
# easier to test and adapt in the future.
SKETCHFAB_API_BASE = "https://api.sketchfab.com/v3"
SKETCHFAB_SEARCH_ENDPOINT = f"{SKETCHFAB_API_BASE}/search"
SKETCHFAB_ME_ENDPOINT = f"{SKETCHFAB_API_BASE}/me"

REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "blender-mcp"})


def get_sketchfab_status(api_key: Optional[str], session: Optional[requests.Session] = None) -> Dict[str, Any]:
    """Return a small status dict for the provided API key.

    This mirrors the behaviour previously embedded in the addon but is
    testable in isolation.
    """
    if not api_key:
        return {"enabled": False, "message": "No API key provided"}

    headers = {"Authorization": f"Token {api_key}"}
    try:
        if session is None:
            resp = requests.get(SKETCHFAB_ME_ENDPOINT, headers=headers, timeout=10)
        else:
            resp = session.get(SKETCHFAB_ME_ENDPOINT, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            username = data.get("username", "Unknown user")
            return {"enabled": True, "message": f"Logged in as: {username}"}
        return {"enabled": False, "message": f"Invalid key (status {resp.status_code})"}
    except requests.exceptions.Timeout:
        return {"enabled": False, "message": "Timeout connecting to Sketchfab"}
    except Exception as e:
        return {"enabled": False, "message": str(e)}


def search_models(
    api_key: str,
    query: str,
    categories: Optional[str] = None,
    count: int = 20,
    downloadable: bool = True,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    headers = {"Authorization": f"Token {api_key}"}
    params = {
        "type": "models",
        "q": query,
        "count": count,
        "downloadable": downloadable,
        "archives_flavours": False,
    }
    if categories:
        params["categories"] = categories

    # requests expects params values to be strings or sequences; coerce to strings to satisfy type checkers
    params_cast = {k: str(v) for k, v in params.items() if v is not None}
    if session is None:
        resp = requests.get(SKETCHFAB_SEARCH_ENDPOINT, headers=headers, params=params_cast, timeout=30)
    else:
        resp = session.get(SKETCHFAB_SEARCH_ENDPOINT, headers=headers, params=params_cast, timeout=30)
    if resp.status_code == 401:
        return {"error": "Authentication failed (401)"}
    if resp.status_code != 200:
        return {"error": f"API request failed with status code {resp.status_code}"}

    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON from Sketchfab: {e}"}

    return data


def download_model(api_key: str, uid: str, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    """Download a model by uid and extract it into a temp dir.

    Returns a dict with either 'error' or 'temp_dir' (path to extracted files).
    """
    headers = {"Authorization": f"Token {api_key}"}
    download_endpoint = f"https://api.sketchfab.com/v3/models/{uid}/download"

    if session is None:
        resp = requests.get(download_endpoint, headers=headers, timeout=30)
    else:
        resp = session.get(download_endpoint, headers=headers, timeout=30)
    if resp.status_code == 401:
        return {"error": "Authentication failed (401)"}
    if resp.status_code != 200:
        return {"error": f"Download request failed with status code {resp.status_code}"}

    data = resp.json()
    gltf = data.get("gltf")
    if not gltf or not isinstance(gltf, dict):
        return {"error": "No gltf download available for this model"}

    download_url = gltf.get("url")
    if not download_url:
        return {"error": "No download URL found in Sketchfab response"}

    # Prefer centralized downloader; it may raise on non-200
    try:
        if session is None:
            zip_bytes = downloaders.download_bytes(download_url, timeout=60)
        else:
            zip_bytes = downloaders.download_bytes(download_url, timeout=60, session=session)
        temp_dir = downloaders.secure_extract_zip_bytes(zip_bytes)
        return {"temp_dir": temp_dir}
    except Exception as e:
        # Surface the error to caller for appropriate handling
        return {"error": str(e)}
