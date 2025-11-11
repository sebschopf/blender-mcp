"""Register default service handlers into a CommandDispatcher.

This module exposes a single helper `register_default_handlers(dispatcher)`
which registers handlers for PolyHaven and Sketchfab operations so the MCP
server can perform network actions directly when commands arrive.
"""

import os
from typing import Any, Dict

from ..command_dispatcher import CommandDispatcher
from . import polyhaven, sketchfab


def _get_polyhaven_categories(asset_type: str = "hdris") -> Dict[str, Any]:
    try:
        return polyhaven.fetch_categories(asset_type=asset_type)
    except Exception as e:
        return {"error": str(e)}


def _search_polyhaven_assets(
    asset_type: str = "all",
    categories: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    try:
        return polyhaven.search_assets_network(
            asset_type=asset_type, categories=categories, page=page, per_page=per_page
        )
    except Exception as e:
        return {"error": str(e)}


def _download_polyhaven_asset(
    asset_id: str | None = None,
    download_url: str | None = None,
    asset_type: str = "models",
    resolution: str = "1k",
    file_format: str | None = None,
) -> Dict[str, Any]:
    try:
        return polyhaven.download_asset(
            download_url=download_url,
            asset_id=asset_id,
            asset_type=asset_type,
            resolution=resolution,
            file_format=file_format,
        )
    except Exception as e:
        return {"error": str(e)}


def _get_sketchfab_status(api_key: str | None = None) -> Dict[str, Any]:
    try:
        # Prefer explicit api_key param, fall back to env
        key = api_key or os.environ.get("SKETCHFAB_API_KEY")
        return sketchfab.get_sketchfab_status(key)
    except Exception as e:
        return {"error": str(e)}


def _search_sketchfab_models(
    api_key: str | None = None,
    query: str = "",
    categories: str | None = None,
    count: int = 20,
    downloadable: bool = True,
) -> Dict[str, Any]:
    try:
        key = api_key or os.environ.get("SKETCHFAB_API_KEY")
        if not key:
            return {"error": "No Sketchfab API key configured"}
        return sketchfab.search_models(key, query, categories=categories, count=count, downloadable=downloadable)
    except Exception as e:
        return {"error": str(e)}


def _download_sketchfab_model(api_key: str | None = None, uid: str | None = None) -> Dict[str, Any]:
    try:
        key = api_key or os.environ.get("SKETCHFAB_API_KEY")
        if not key:
            return {"error": "No Sketchfab API key configured"}
        if not uid:
            return {"error": "No UID provided"}
        return sketchfab.download_model(key, uid)
    except Exception as e:
        return {"error": str(e)}


def register_default_handlers(dispatcher: CommandDispatcher) -> None:
    """Register a small set of default handlers.

    Handlers accept keyword arguments matching the command `params` and return
    serializable dicts. They should not raise for normal error conditions;
    instead they return dicts containing `error` keys where appropriate.
    """

    dispatcher.register("get_polyhaven_categories", _get_polyhaven_categories)
    dispatcher.register("search_polyhaven_assets", _search_polyhaven_assets)
    dispatcher.register("download_polyhaven_asset", _download_polyhaven_asset)

    dispatcher.register("get_sketchfab_status", _get_sketchfab_status)
    dispatcher.register("search_sketchfab_models", _search_sketchfab_models)
    dispatcher.register("download_sketchfab_model", _download_sketchfab_model)
