"""Service-facing wrappers for PolyHaven-related helpers.

Validate parameters, delegate to `services.addon.polyhaven` and normalize
responses to the canonical service schema.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import logging

from .addon.polyhaven import (
    download_polyhaven_asset as _addon_download_polyhaven_asset,
    get_polyhaven_categories as _addon_get_polyhaven_categories,
    search_polyhaven_assets as _addon_search_polyhaven_assets,
)

logger = logging.getLogger(__name__)


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
    resolution = p.get("resolution", "1k")
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
    "download_asset_service",
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

    sorted_assets = sorted(
        assets.items(), key=lambda x: x[1].get("download_count", 0), reverse=True
    )

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


def fetch_categories(api_base: str = "https://api.polyhaven.com", asset_type: str = "hdris") -> Dict[str, Any]:
    url = f"{api_base}/list"
    params = {"type": asset_type}
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
) -> Dict[str, Any]:
    url = f"{api_base}/search"
    params: Dict[str, Any] = {"type": asset_type, "page": page, "per_page": per_page}
    if categories:
        params["categories"] = categories
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
) -> Dict[str, Any]:
    if not download_url:
        if not asset_id:
            return {"error": "Either download_url or asset_id must be provided"}
        fmt = file_format or ("gltf.zip" if asset_type == "models" else "zip")
        download_url = f"https://dl.polyhaven.org/file/ph-assets/{asset_type}/{asset_id}/{resolution}.{fmt}"

    try:
        zip_bytes = downloaders.download_bytes(download_url, timeout=120)
        temp_dir = downloaders.secure_extract_zip_bytes(zip_bytes)
        return {"temp_dir": temp_dir}
    except Exception as e:
        return {"error": str(e)}

