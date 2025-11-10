"""Compatibility façade for legacy addon handlers.

This module preserves the public API of the original `addon_handlers.py`
but delegates the implementation to smaller, SRP-focused modules under
`blender_mcp.services.addon`.

The façade keeps the same function names and signatures so existing
callers don't need to change when we refactor internals.
"""

from __future__ import annotations

# Re-export public helpers from the new SOLID modules
from .services.addon import (
    _collect_texture_images,
    _get_aabb,
    _try_create_material,
    download_polyhaven_asset,
    execute_code,
    get_object_info,
    get_polyhaven_categories,
    get_scene_info,
    get_viewport_screenshot,
    search_polyhaven_assets,
    set_texture,
)

# Export constants from a shared module so implementations can import them
from .services.addon.constants import REQ_HEADERS, RODIN_FREE_TRIAL_KEY

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
