"""Server-side adapters for Sketchfab helpers.

This module exposes small wrappers around the existing `blender_mcp.sketchfab`
helpers so `integrations` can prefer server-side network calls when a
Sketchfab API key is available.
"""

from typing import Any, Dict, Optional

from .. import sketchfab as _sketchfab


def get_sketchfab_status(api_key: Optional[str]) -> Dict[str, Any]:
    # Keep the service wrapper conservative: do not force a shared session so
    # tests that monkeypatch `sketchfab.requests` continue to work.
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
