"""Archived copy of the top-level compatibility façade.

This file preserves the removed compatibility module so history and
reference remain in-tree. The real implementations live under
``blender_mcp.services.addon`` and the UI-facing helpers are available at
``blender_mcp.blender_ui.addon_handlers``.

Kept as-is for archival purposes; do not import this module from the
active codepath.
"""

from __future__ import annotations

raise ImportError(
    "The compatibility module 'blender_mcp.addon_handlers' has been removed. "
    "Import helpers from 'blender_mcp.services.addon' or 'blender_mcp.blender_ui.addon_handlers' instead."
)
