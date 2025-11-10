"""Services package for Blender MCP.

Services are small, testable units that implement the behaviour of
individual endpoints. To avoid import-time cycles the package init no
longer imports submodules at import time — import specific service
functions from their modules instead, for example::

    from blender_mcp.services.execute import execute_blender_code

This keeps package import lightweight and avoids circular imports when
refactoring modules.
"""

__all__ = []
