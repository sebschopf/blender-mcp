"""Blender integration through the Model Context Protocol.

Keep this module small and import-safe. Heavy or Blender-dependent
modules (for example the runtime ``server`` or ``bpy``-using helpers)
should not be imported at package import time. We expose a small
public API and use PEP 562-style lazy attribute import to avoid
import-time side-effects.
"""

__version__ = "0.1.0"

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Help static analyzers know these names exist at import-time while
    # keeping runtime imports lazy and side-effect free.
    from .connection import BlenderConnection  # pragma: no cover
    from .tools import get_blender_connection  # pragma: no cover

__all__ = ["BlenderConnection", "get_blender_connection", "__version__"]


def __getattr__(name: str):
    """Lazily provide package attributes.

    This keeps ``import blender_mcp`` fast and safe in CI/test
    environments where Blender or other optional runtime dependencies
    aren't available.
    """
    if name == "BlenderConnection":
        from .connection import BlenderConnection

        return BlenderConnection
    if name == "get_blender_connection":
        from .tools import get_blender_connection

        return get_blender_connection
    if name == "__version__":
        return __version__
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    names = list(globals().keys()) + ["BlenderConnection", "get_blender_connection"]
    return sorted(set(names))
