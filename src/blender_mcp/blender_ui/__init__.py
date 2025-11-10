"""BlenderMCP UI package façade.

This package contains the split UI pieces (props, operators, panel) and
re-exports a compatibility-friendly API so existing imports of
`blender_mcp.blender_ui` continue to work.
"""

from typing import Iterable

import bpy

# Preserve the AddonPreferences base selection strategy from the original
try:
    _AddonPrefsBase = bpy.types.AddonPreferences
except Exception:
    _AddonPrefsBase = object


class BLENDERMCP_AddonPreferences(_AddonPrefsBase):
    bl_idname = "blender_mcp"

    allow_ui_start_server = bpy.props.BoolProperty(
        name="Allow UI to start external MCP server",
        description="If enabled, the Start button in the addon UI may launch an external MCP process",
        default=True,
    )

    def draw(self, context):
        try:
            layout = self.layout
            layout.label(text="BlenderMCP preferences")
            layout.prop(self, "allow_ui_start_server")
        except Exception:
            # Import-safe: tests may provide a fake `bpy` without a full UI
            pass


from . import props
from . import operators
from . import panel

# Re-export classes at package level for backward compatibility
BLENDERMCP_PT_Panel = panel.BLENDERMCP_PT_Panel
BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey = operators.BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey
BLENDERMCP_OT_StartServer = operators.BLENDERMCP_OT_StartServer
BLENDERMCP_OT_StopServer = operators.BLENDERMCP_OT_StopServer
BLENDERMCP_OT_ApplyRemoteExecSetting = operators.BLENDERMCP_OT_ApplyRemoteExecSetting
BLENDERMCP_AddonPreferences = BLENDERMCP_AddonPreferences


def _classes() -> Iterable[type]:
    return (
        BLENDERMCP_PT_Panel,
        BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey,
        BLENDERMCP_OT_StartServer,
        BLENDERMCP_OT_StopServer,
        BLENDERMCP_OT_ApplyRemoteExecSetting,
        BLENDERMCP_AddonPreferences,
    )


def register() -> None:
    """Register UI classes and scene properties."""
    props._register_scene_properties()
    for cls in _classes():
        try:
            bpy.utils.register_class(cls)
        except Exception:
            # Best-effort: if registration fails (already registered etc.)
            pass
    print("BlenderMCP addon registered (package façade)")


def unregister() -> None:
    """Unregister UI classes and scene properties."""
    for cls in _classes():
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    props._unregister_scene_properties()
    print("BlenderMCP addon unregistered (package façade)")
