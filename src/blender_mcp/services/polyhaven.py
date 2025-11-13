"""Service-facing wrappers for PolyHaven-related helpers.

Validate parameters, delegate to `services.addon.polyhaven` and normalize
responses to the canonical service schema.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from blender_mcp.errors import ExternalServiceError, InvalidParamsError

from .addon.polyhaven import download_polyhaven_asset as _addon_download_polyhaven_asset
from .addon.polyhaven import get_polyhaven_categories as _addon_get_polyhaven_categories
from .addon.polyhaven import search_polyhaven_assets as _addon_search_polyhaven_assets

logger = logging.getLogger(__name__)


def get_polyhaven_categories(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service: fetch PolyHaven categories with canonical contract.

    Expects params: {"asset_type": str | None}
    Returns: {"status":"success","result":{"categories":{...}}}

    Errors:
    - InvalidParamsError: asset_type provided but not a string
    - ExternalServiceError: network/API failure
    """
    p = params or {}
    asset_type = p.get("asset_type")
    if asset_type is not None and not isinstance(asset_type, str):
        raise InvalidParamsError("'asset_type' must be a string if provided")
    try:
        data = fetch_categories(asset_type=asset_type or "hdris")
        cats = data.get("categories") or {}
        return {"status": "success", "result": {"categories": cats}}
    except Exception as e:
        raise ExternalServiceError(str(e))


def search_polyhaven_assets(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service: search PolyHaven assets with canonical contract.

    Params accepted (all optional unless noted):
    {
      "asset_type": str (one of hdris|textures|models|all, default: "all"),
      "categories": str (comma-separated categories supported by PolyHaven),
      "page": int (>=1, default: 1),
      "per_page": int (1..100, default: 50)
    }

    Returns: {"status":"success","result":{"assets":{...},"total_count":int,"returned_count":int}}

    Errors:
    - InvalidParamsError: bad type/value for any param
    - ExternalServiceError: network/API failure
    """
    p = params or {}
    asset_type = p.get("asset_type", "all")
    categories = p.get("categories")
    page = p.get("page", 1)
    per_page = p.get("per_page", 50)

    if not isinstance(asset_type, str):
        raise InvalidParamsError("'asset_type' must be a string")
    allowed_types = {"hdris", "textures", "models", "all"}
    if asset_type not in allowed_types:
        raise InvalidParamsError(
            f"'asset_type' invalid: {asset_type}. Must be one of: hdris, textures, models, all"
        )
    if categories is not None and not isinstance(categories, str):
        raise InvalidParamsError("'categories' must be a string if provided")
    if not isinstance(page, int) or page < 1:
        raise InvalidParamsError("'page' must be an int >= 1")
    if not isinstance(per_page, int) or not (1 <= per_page <= 100):
        raise InvalidParamsError("'per_page' must be an int between 1 and 100")

    try:
        data = search_assets_network(
            asset_type=asset_type,
            categories=categories,
            page=page,
            per_page=per_page,
        )
    except Exception as e:  # pragma: no cover - defensive boundary
        raise ExternalServiceError(str(e))

    if data.get("error"):
        raise ExternalServiceError(str(data.get("error")))

    assets = data.get("assets") or {}
    total_count = data.get("total_count", 0)
    returned_count = data.get("returned_count", len(assets))
    return {
        "status": "success",
        "result": {
            "assets": assets,
            "total_count": total_count,
            "returned_count": returned_count,
        },
    }


def get_categories(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get PolyHaven categories.

    Expects params: {"asset_type": str (optional, default: "all")}
    Returns: {"status":"success","result":{"categories": ...}} or error
    """
    asset_type = None
    if params:
        asset_type = params.get("asset_type")
    asset_type = asset_type or "all"

    try:
        addon_resp = _addon_get_polyhaven_categories(asset_type)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("addon get_polyhaven_categories failed")
        return {"status": "error", "message": str(exc)}

    if addon_resp.get("error"):
        return {"status": "error", "message": addon_resp.get("error")}

    return {"status": "success", "result": {"categories": addon_resp.get("categories")}}


def download_asset_service(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Download an asset from polyhaven via the addon implementation.

    params: {
        "asset_id": str,
        "asset_type": "hdris"|"textures"|"models",
        "resolution": str,
        "file_format": str
    }
    """
    p = params or {}
    asset_id = p.get("asset_id")
    asset_type = p.get("asset_type", "models")
    resolution = p.get("resolution")
    file_format = p.get("file_format")

    if not asset_id:
        return {"status": "error", "message": "asset_id is required"}

    try:
        addon_resp = _addon_download_polyhaven_asset(
            asset_id, asset_type, resolution=resolution, file_format=file_format
        )
    except Exception as e:  # pragma: no cover - keep defensive boundary
        return {"status": "error", "message": str(e)}

    if addon_resp.get("error"):
        return {"status": "error", "message": addon_resp.get("error")}

    return {"status": "success", "result": {"files_data": addon_resp.get("files_data")}}


def download_polyhaven_asset(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service: download a PolyHaven asset archive and extract it safely.

    Params:
    {
      "asset_id": str,  (required)
      "asset_type": "hdris"|"textures"|"models",  (required)
      "resolution": str (optional, default: "1k"),
      "file_format": str (optional; default depends on type)
    }

    Returns: {"status":"success","result":{"temp_dir": str}}

    Errors:
    - InvalidParamsError: bad/missing params
    - ExternalServiceError: network or extraction failure
    """
    p = params or {}
    asset_id = p.get("asset_id")
    asset_type = p.get("asset_type")
    resolution = p.get("resolution", "1k")
    file_format = p.get("file_format")

    if not isinstance(asset_id, str) or not asset_id:
        raise InvalidParamsError("missing or invalid 'asset_id'")
    if not isinstance(asset_type, str) or asset_type not in {"hdris", "textures", "models"}:
        raise InvalidParamsError("'asset_type' must be one of: hdris, textures, models")
    if resolution is not None and not isinstance(resolution, str):
        raise InvalidParamsError("'resolution' must be a string if provided")
    if file_format is not None and not isinstance(file_format, str):
        raise InvalidParamsError("'file_format' must be a string if provided")

    try:
        res_str: str = resolution or "1k"
        res = download_asset(
            asset_id=asset_id,
            asset_type=asset_type,
            resolution=res_str,
            file_format=file_format,
        )
    except Exception as e:  # pragma: no cover - defensive
        raise ExternalServiceError(str(e))

    if res.get("error"):
        raise ExternalServiceError(str(res.get("error")))

    return {"status": "success", "result": {"temp_dir": res.get("temp_dir")}}


def search_assets(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Search PolyHaven assets via the addon implementation.

    params: {"asset_type": str (optional), "categories": str (optional), "page": int (optional)}
    """
    p = params or {}
    asset_type = p.get("asset_type", "all")
    categories = p.get("categories")

    try:
        # addon.search_polyhaven_assets accepts (asset_type, categories)
        addon_resp = _addon_search_polyhaven_assets(asset_type, categories=categories)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("addon search_polyhaven_assets failed")
        return {"status": "error", "message": str(exc)}

    if addon_resp.get("error"):
        return {"status": "error", "message": addon_resp.get("error")}

    return {"status": "success", "result": addon_resp}


def download_asset_addon(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Download an asset's files metadata from PolyHaven.

    Expects params: {"asset_id": str, "asset_type": str, "resolution": str (optional), "file_format": str (optional)}
    Returns: {"status":"success","result":{"files_data": ...}} or error
    """
    if not params:
        return {"status": "error", "message": "missing params"}

    asset_id = params.get("asset_id")
    asset_type = params.get("asset_type")
    resolution = params.get("resolution", "1k")
    file_format = params.get("file_format")

    if not asset_id or not isinstance(asset_id, str):
        return {"status": "error", "message": "missing or invalid 'asset_id'"}
    if not asset_type or not isinstance(asset_type, str):
        return {"status": "error", "message": "missing or invalid 'asset_type'"}

    try:
        addon_resp = _addon_download_polyhaven_asset(
            asset_id, asset_type, resolution=resolution, file_format=file_format
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("addon download_polyhaven_asset failed")
        return {"status": "error", "message": str(exc)}

    if addon_resp.get("error"):
        return {"status": "error", "message": addon_resp.get("error")}

    return {"status": "success", "result": {"files_data": addon_resp.get("files_data")}}


__all__ = [
    "get_categories",
    "search_assets",
    "search_polyhaven_assets",
    "download_asset_service",
    "download_polyhaven_asset",
    "download_asset_addon",
    "format_categories_output",
    "format_search_assets",
    "download_asset_message",
    "fetch_categories",
    "search_assets_network",
    "download_asset",
]


# --- helper functions (network helpers and formatters) ---
import requests

from blender_mcp import downloaders


def format_categories_output(categories: Dict[str, int], asset_type: str) -> str:
    formatted = f"Categories for {asset_type}:\n\n"
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories:
        formatted += f"- {category}: {count} assets\n"
    return formatted


def format_search_assets(result: Dict[str, Any], categories: Optional[str] = None) -> str:
    assets = result.get("assets", {})
    total_count = result.get("total_count", 0)
    returned_count = result.get("returned_count", 0)

    formatted = f"Found {total_count} assets"
    if categories:
        formatted += f" in categories: {categories}"
    formatted += f"\nShowing {returned_count} assets:\n\n"

    sorted_assets = sorted(assets.items(), key=lambda x: x[1].get("download_count", 0), reverse=True)

    for asset_id, asset_data in sorted_assets:
        formatted += f"- {asset_data.get('name', asset_id)} (ID: {asset_id})\n"
        formatted += f"  Type: {['HDRI', 'Texture', 'Model'][asset_data.get('type', 0)]}\n"
        formatted += f"  Categories: {', '.join(asset_data.get('categories', []))}\n"
        formatted += f"  Downloads: {asset_data.get('download_count', 'Unknown')}\n\n"

    return formatted


def download_asset_message(result: Dict[str, Any], asset_type: str) -> str:
    if result.get("success"):
        message = result.get("message", "Asset downloaded and imported successfully")
        if asset_type == "hdris":
            return f"{message}. The HDRI has been set as the world environment."
        if asset_type == "textures":
            material_name = result.get("material", "")
            maps = ", ".join(result.get("maps", []))
            return f"{message}. Created material '{material_name}' with maps: {maps}."
        if asset_type == "models":
            return f"{message}. The model has been imported into the current scene."
        return message
    return f"Failed to download asset: {result.get('message', 'Unknown error')}"


def fetch_categories(
    api_base: str = "https://api.polyhaven.com",
    asset_type: str = "hdris",
    session: Optional[requests.sessions.Session] = None,
) -> Dict[str, Any]:
    """Fetch categories from PolyHaven API.

    If a `session` is provided, it will be used for the request (useful for
    connection reuse in long-running processes or for test injection). If no
    session is provided, `requests.get` is used for backward compatibility.
    """
    url = f"{api_base}/list"
    params = {"type": asset_type}
    if session is not None:
        resp = session.get(url, params=params, timeout=15)
    else:
        resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    categories = data.get("categories") or {}
    return {"categories": categories}


def search_assets_network(
    api_base: str = "https://api.polyhaven.com",
    asset_type: str = "all",
    categories: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
    session: Optional[requests.sessions.Session] = None,
) -> Dict[str, Any]:
    """Search PolyHaven assets via network API.

    Accepts optional `session` for connection reuse. Returns parsed JSON or
    a dict with an "error" key on JSON parse failure.
    """
    url = f"{api_base}/search"
    params: Dict[str, Any] = {"type": asset_type, "page": page, "per_page": per_page}
    if categories:
        params["categories"] = categories
    if session is not None:
        resp = session.get(url, params=params, timeout=20)
    else:
        resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError as e:
        return {"error": f"Invalid JSON from PolyHaven: {e}"}


def download_asset(
    download_url: Optional[str] = None,
    asset_id: Optional[str] = None,
    asset_type: str = "models",
    resolution: str = "1k",
    file_format: Optional[str] = None,
    session: Optional[requests.sessions.Session] = None,
) -> Dict[str, Any]:
    if not download_url:
        if not asset_id:
            return {"error": "Either download_url or asset_id must be provided"}
        fmt = file_format or ("gltf.zip" if asset_type == "models" else "zip")
        download_url = f"https://dl.polyhaven.org/file/ph-assets/{asset_type}/{asset_id}/{resolution}.{fmt}"

    try:
        if session is None:
            zip_bytes = downloaders.download_bytes(download_url, timeout=120)
        else:
            zip_bytes = downloaders.download_bytes(download_url, timeout=120, session=session)
        temp_dir = downloaders.secure_extract_zip_bytes(zip_bytes)
        return {"temp_dir": temp_dir}
    except Exception as e:
        return {"error": str(e)}
