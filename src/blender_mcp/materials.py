"""Compatibility façade: re-export material helpers from the package structure.

This file keeps existing imports working:
    from blender_mcp.materials import build_material_spec, _build_spec_from_keys
    from blender_mcp.materials import create_material_in_blender
"""

from .materials import (  # type: ignore F401
    _build_spec_from_keys,
    build_material_spec,
    create_material_in_blender,
)

__all__ = [
    "build_material_spec",
    "_build_spec_from_keys",
    "create_material_in_blender",
]
