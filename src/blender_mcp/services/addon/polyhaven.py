"""PolyHaven helper fallbacks extracted from addon handlers."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import requests

from ...http import get_session
from .constants import REQ_HEADERS


def get_polyhaven_categories(asset_type: str, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    try:
        if asset_type not in ["hdris", "textures", "models", "all"]:
            return {"error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"}

        try:
            from blender_mcp.polyhaven import fetch_categories  # type: ignore

            cats = fetch_categories(asset_type, timeout=10)
            return {"categories": cats}
        except Exception:
            try:
                from blender_mcp.downloaders import download_bytes  # type: ignore

                data = download_bytes(
                    f"https://api.polyhaven.com/categories/{asset_type}",
                    timeout=10,
                    headers=REQ_HEADERS,
                )
                return {"categories": json.loads(data.decode("utf-8"))}
            except Exception:
                getter = session.get if session is not None else get_session().get
                response = getter(f"https://api.polyhaven.com/categories/{asset_type}", headers=REQ_HEADERS)
                if response.status_code == 200:
                    return {"categories": response.json()}
                return {"error": f"API request failed with status code {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def search_polyhaven_assets(
    asset_type=None, categories=None, session: Optional[requests.Session] = None
) -> Dict[str, Any]:
    try:
        params = {}
        if asset_type and asset_type != "all":
            if asset_type not in ["hdris", "textures", "models"]:
                return {"error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"}
            params["type"] = asset_type

        if categories:
            params["categories"] = categories

        try:
            from blender_mcp.polyhaven import search_assets  # type: ignore

            assets = search_assets(params, timeout=10)
        except Exception:
            try:
                import urllib.parse

                from blender_mcp.downloaders import download_bytes  # type: ignore

                qs = urllib.parse.urlencode(params, doseq=True)
                full_url = "https://api.polyhaven.com/assets" + ("?" + qs if qs else "")
                data = download_bytes(full_url, timeout=10, headers=REQ_HEADERS)
                assets = json.loads(data.decode("utf-8"))
            except Exception:
                getter = session.get if session is not None else get_session().get
                response = getter("https://api.polyhaven.com/assets", params=params, headers=REQ_HEADERS)
                if response.status_code == 200:
                    assets = response.json()
                else:
                    return {"error": f"API request failed with status code {response.status_code}"}

        limited_assets = {}
        for i, (key, value) in enumerate(assets.items()):
            if i >= 20:
                break
            limited_assets[key] = value

        return {
            "assets": limited_assets,
            "total_count": len(assets),
            "returned_count": len(limited_assets),
        }
    except Exception as e:
        return {"error": str(e)}


def download_polyhaven_asset(
    asset_id, asset_type, resolution="1k", file_format=None, session: Optional[requests.Session] = None
) -> Dict[str, Any]:
    try:
        from blender_mcp.polyhaven import fetch_files_data  # type: ignore

        files_data = fetch_files_data(asset_id)
    except Exception:
        try:
            from blender_mcp.downloaders import download_bytes  # type: ignore

            data = download_bytes(
                f"https://api.polyhaven.com/files/{asset_id}",
                timeout=10,
                headers=REQ_HEADERS,
            )
            files_data = json.loads(data.decode("utf-8"))
        except Exception:
            try:
                getter = session.get if session is not None else get_session().get
                files_response = getter(f"https://api.polyhaven.com/files/{asset_id}", headers=REQ_HEADERS)
                if files_response.status_code != 200:
                    return {"error": f"Failed to get asset files: {files_response.status_code}"}
                files_data = files_response.json()
            except Exception as e:
                return {"error": str(e)}

    return {"files_data": files_data}


__all__ = [
    "get_polyhaven_categories",
    "search_polyhaven_assets",
    "download_polyhaven_asset",
]
