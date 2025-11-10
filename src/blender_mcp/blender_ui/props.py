"""Scene property registration for BlenderMCP UI.

This module registers/unregisters bpy.types.Scene properties used by the
UI. It mirrors the original `_register_scene_properties`/_unregister helper.
"""

import bpy
from bpy.props import IntProperty


def _register_scene_properties() -> None:
    """Register scene-level properties used by the addon."""
    bpy.types.Scene.blendermcp_port = IntProperty(
        name="Port",
        description="Port for the BlenderMCP server",
        default=9876,
        min=1024,
        max=65535,
    )

    bpy.types.Scene.blendermcp_server_pid = IntProperty(
        name="Server PID", description="PID of external MCP server", default=0
    )

    bpy.types.Scene.blendermcp_server_running = bpy.props.BoolProperty(
        name="Server Running", default=False
    )

    bpy.types.Scene.blendermcp_use_polyhaven = bpy.props.BoolProperty(
        name="Use Poly Haven",
        description="Enable Poly Haven asset integration",
        default=False,
    )

    bpy.types.Scene.blendermcp_use_hyper3d = bpy.props.BoolProperty(
        name="Use Hyper3D Rodin",
        description="Enable Hyper3D Rodin generatino integration",
        default=False,
    )

    bpy.types.Scene.blendermcp_hyper3d_mode = bpy.props.EnumProperty(
        name="Rodin Mode",
        description="Choose the platform used to call Rodin APIs",
        items=[
            ("MAIN_SITE", "hyper3d.ai", "hyper3d.ai"),
            ("FAL_AI", "fal.ai", "fal.ai"),
        ],
        default="MAIN_SITE",
    )

    bpy.types.Scene.blendermcp_hyper3d_api_key = bpy.props.StringProperty(
        name="Hyper3D API Key",
        subtype="PASSWORD",
        description="API Key provided by Hyper3D",
        default="",
    )

    bpy.types.Scene.blendermcp_use_sketchfab = bpy.props.BoolProperty(
        name="Use Sketchfab",
        description="Enable Sketchfab asset integration",
        default=False,
    )

    bpy.types.Scene.blendermcp_sketchfab_api_key = bpy.props.StringProperty(
        name="Sketchfab API Key",
        subtype="PASSWORD",
        description="API Key provided by Sketchfab",
        default="",
    )

    bpy.types.Scene.blendermcp_allow_remote_exec = bpy.props.BoolProperty(
        name="Allow remote execution",
        description="Enable remote execution of Python snippets (dangerous). Requires explicit opt-in and caution.",
        default=False,
    )


def _unregister_scene_properties() -> None:
    """Remove scene-level properties previously registered.

    Unregistering is best-effort: missing attributes are ignored.
    """
    for name in (
        "blendermcp_port",
        "blendermcp_server_running",
        "blendermcp_use_polyhaven",
        "blendermcp_use_hyper3d",
        "blendermcp_hyper3d_mode",
        "blendermcp_hyper3d_api_key",
        "blendermcp_use_sketchfab",
        "blendermcp_sketchfab_api_key",
        "blendermcp_allow_remote_exec",
        "blendermcp_server_pid",
    ):
        try:
            delattr(bpy.types.Scene, name)
        except Exception:
            try:
                delattr(bpy.context.scene, name)
            except Exception:
                pass
