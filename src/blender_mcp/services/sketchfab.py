"""Server-side adapters for Sketchfab helpers.

This module exposes small wrappers around the existing `blender_mcp.sketchfab`
helpers so `integrations` can prefer server-side network calls when a
Sketchfab API key is available.
"""

import os
from typing import Any, Dict, Optional

from blender_mcp.errors import ExternalServiceError, InvalidParamsError

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


def _resolve_api_key(p: Dict[str, Any]) -> str:
    api_key = p.get("api_key")
    if api_key is None:
        api_key = os.environ.get("SKETCHFAB_API_KEY")
    if not isinstance(api_key, str) or not api_key:
        raise InvalidParamsError("missing or invalid 'api_key'")
    return api_key


def search_sketchfab_models(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service: search Sketchfab models (exceptions-first).

    Params: { api_key?: str, query: str, categories?: str, count?: int, downloadable?: bool }
    api_key can be omitted if SKETCHFAB_API_KEY env var is set.
    """
    p = params or {}
    api_key = _resolve_api_key(p)
    query = p.get("query", "")
    categories = p.get("categories")
    count = p.get("count", 20)
    downloadable = p.get("downloadable", True)

    if not isinstance(query, str):
        raise InvalidParamsError("'query' must be a string")
    if categories is not None and not isinstance(categories, str):
        raise InvalidParamsError("'categories' must be a string if provided")
    if not isinstance(count, int) or count <= 0:
        raise InvalidParamsError("'count' must be a positive integer")
    if not isinstance(downloadable, bool):
        raise InvalidParamsError("'downloadable' must be a boolean")

    try:
        data = _sketchfab.search_models(api_key, query, categories=categories, count=count, downloadable=downloadable)
    except Exception as e:  # pragma: no cover
        raise ExternalServiceError(str(e))
    if data.get("error"):
        raise ExternalServiceError(str(data.get("error")))
    return {"status": "success", "result": data}


def download_sketchfab_model(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service: download a model and return extracted temp_dir.

    Params: { api_key?: str, uid: str }
    api_key can be omitted if SKETCHFAB_API_KEY env var is set.
    """
    p = params or {}
    api_key = _resolve_api_key(p)
    uid = p.get("uid")
    if not isinstance(uid, str) or not uid:
        raise InvalidParamsError("missing or invalid 'uid'")
    try:
        data = _sketchfab.download_model(api_key, uid)
    except Exception as e:  # pragma: no cover
        raise ExternalServiceError(str(e))
    if data.get("error"):
        raise ExternalServiceError(str(data.get("error")))
    return {"status": "success", "result": data}
