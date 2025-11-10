"""Top-level compatibility façade for addon handlers.

This module preserves the historical import path `blender_mcp.addon_handlers`
but delegates the implementation to `blender_mcp.blender_ui.addon_handlers`.
Keeping this tiny façade avoids changing any external import sites while
we move code under the `blender_ui` package.
"""

from __future__ import annotations

from .blender_ui.addon_handlers import *  # re-export everything from the package

__all__ = [
    "REQ_HEADERS",
    "RODIN_FREE_TRIAL_KEY",
    "get_scene_info",
    "_get_aabb",
    "get_object_info",
    "get_viewport_screenshot",
    "execute_code",
    "get_polyhaven_categories",
    "search_polyhaven_assets",
    "download_polyhaven_asset",
    "set_texture",
    "_collect_texture_images",
    "_try_create_material",
]
