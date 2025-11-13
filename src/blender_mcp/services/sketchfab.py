"""Server-side adapters for Sketchfab helpers.

This module exposes small wrappers around the existing `blender_mcp.sketchfab`
helpers so `integrations` can prefer server-side network calls when a
Sketchfab API key is available.
"""

from typing import Any, Dict, Optional

from blender_mcp.errors import InvalidParamsError

from .. import sketchfab as _sketchfab


def get_sketchfab_status_service(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service: return Sketchfab status for an API key.

    Expects params: {"api_key": str | None}
    Returns: {"status":"success","result": {"enabled": bool, "message": str}}
    Never raises for normal conditions; invalid param type raises InvalidParamsError.
    """
    p = params or {}
    api_key = p.get("api_key")
    if api_key is not None and not isinstance(api_key, str):
        raise InvalidParamsError("'api_key' must be a string if provided")
    status = _sketchfab.get_sketchfab_status(api_key)
    return {"status": "success", "result": status}


def get_sketchfab_status(api_key: Optional[str]) -> Dict[str, Any]:
    """Backward-compatible thin wrapper used by existing tests.

    Returns the raw status dict from `blender_mcp.sketchfab.get_sketchfab_status`.
    """
    return _sketchfab.get_sketchfab_status(api_key)


def search_models(
    api_key: str,
    query: str,
    categories: Optional[str],
    count: int = 20,
    downloadable: bool = True,
) -> Dict[str, Any]:
    return _sketchfab.search_models(
        api_key,
        query,
        categories=categories,
        count=count,
        downloadable=downloadable,
    )


def download_model(api_key: str, uid: str) -> Dict[str, Any]:
    return _sketchfab.download_model(api_key, uid)
