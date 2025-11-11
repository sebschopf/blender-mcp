"""Re-export of top-level `materials` helpers into the templates package.

This module keeps the original implementation in `blender_mcp.materials` while
exposing the functions from the new `services.templates` package so the
migration can be done incrementally.
"""

from __future__ import annotations

from ... import materials as _materials

# Re-export the two public functions used by the addon
build_material_spec = _materials.build_material_spec
create_material_in_blender = _materials.create_material_in_blender

__all__ = ["build_material_spec", "create_material_in_blender"]
