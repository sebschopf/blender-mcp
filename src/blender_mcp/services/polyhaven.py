"""Pure helpers for PolyHaven output formatting and light manipulation.

These functions accept plain data structures (dicts/lists) returned by the
download/import layer and produce user-friendly strings. They do not perform
network I/O or interact with Blender directly.
"""

from typing import Any, Dict, Optional

import requests

from .. import downloaders


def format_categories_output(categories: Dict[str, int], asset_type: str) -> str:
    formatted = f"Categories for {asset_type}:\n\n"
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories:
        formatted += f"- {category}: {count} assets\n"
    return formatted


def format_search_assets(
    result: Dict[str, Any], categories: Optional[str] = None
) -> str:
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
        formatted += (
            f"  Type: {['HDRI', 'Texture', 'Model'][asset_data.get('type', 0)]}\n"
        )
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
    api_base: str = "https://polyhaven.com/api", asset_type: str = "hdris"
) -> Dict[str, Any]:
    """Fetch categories for an asset type from PolyHaven API.

    Returns a dict with key 'categories' mapping name->count on success, or
    raises an exception on network errors.
    """
    url = f"{api_base}/list"
    params = {"type": asset_type}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    # Expecting data to include a 'categories' mapping; be defensive
    categories = data.get("categories") or {}
    return {"categories": categories}


def search_assets_network(
    api_base: str = "https://polyhaven.com/api",
    asset_type: str = "all",
    categories: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Search PolyHaven for assets using the public API.

    Returns the parsed JSON dict from the API. Callers should inspect for
    'error' keys and handle accordingly.
    """
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
    """Download an asset. Prefer an explicit `download_url`.

    If only `asset_id` is provided, attempt a best-effort URL construction
    for common PolyHaven content; callers should prefer explicit URLs.
    Returns dict with either 'temp_dir' or 'error'.
    """
    if not download_url:
        if not asset_id:
            return {"error": "Either download_url or asset_id must be provided"}
        # Best-effort construction (may not match all PolyHaven endpoints)
        fmt = file_format or ("gltf.zip" if asset_type == "models" else "zip")
        download_url = f"https://dl.polyhaven.org/file/ph-assets/{asset_type}/{asset_id}/{resolution}.{fmt}"

    try:
        # Use centralized downloader which raises on non-200
        zip_bytes = downloaders.download_bytes(download_url, timeout=120)
        temp_dir = downloaders.secure_extract_zip_bytes(zip_bytes)
        return {"temp_dir": temp_dir}
    except Exception as e:
        return {"error": str(e)}
