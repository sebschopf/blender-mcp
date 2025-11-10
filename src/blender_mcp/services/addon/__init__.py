"""SOLID split for addon handlers package.

This package contains small responsibility-focused modules extracted from
the legacy `addon_handlers.py`. The top-level `blender_mcp.addon_handlers`
file will remain a compatibility façade that re-exports these helpers.
"""

from .execution import execute_code
from .objects import get_object_info
from .polyhaven import (
    download_polyhaven_asset,
    get_polyhaven_categories,
    search_polyhaven_assets,
)
from .scene import _get_aabb, get_scene_info
from .screenshots import get_viewport_screenshot
from .textures import _collect_texture_images, _try_create_material, set_texture

__all__ = [
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
