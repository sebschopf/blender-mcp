"""Blender UI for the BlenderMCP add-on.

This module defines the Blender UI panel and operators used by the
add-on. It intentionally keeps behavior minimal: operators only toggle UI
state and inform users how to start/stop the external MCP server.

Design notes:
- Keep imports of `bpy` at module level because Blender requires it for
    register/unregister when running inside Blender. Tests run with a mocked
    `bpy` module.
"""

import bpy
from bpy.props import IntProperty

RODIN_FREE_TRIAL_KEY = (
    "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez"
)


# Blender UI Panel
class BLENDERMCP_PT_Panel(bpy.types.Panel):
    bl_label = "Blender MCP"
    bl_idname = "BLENDERMCP_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderMCP"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "blendermcp_port")
        layout.prop(
            scene, "blendermcp_use_polyhaven", text="Use assets from Poly Haven"
        )

        layout.prop(
            scene,
            "blendermcp_use_hyper3d",
            text="Use Hyper3D Rodin 3D model generation",
        )
        if scene.blendermcp_use_hyper3d:
            layout.prop(scene, "blendermcp_hyper3d_mode", text="Rodin Mode")
            layout.prop(scene, "blendermcp_hyper3d_api_key", text="API Key")
            layout.operator(
                "blendermcp.set_hyper3d_free_trial_api_key",
                text="Set Free Trial API Key",
            )

        layout.prop(scene, "blendermcp_use_sketchfab", text="Use assets from Sketchfab")
        if scene.blendermcp_use_sketchfab:
            layout.prop(scene, "blendermcp_sketchfab_api_key", text="API Key")

        if not scene.blendermcp_server_running:
            layout.operator("blendermcp.start_server", text="Connect to MCP server")
        else:
            layout.operator("blendermcp.stop_server", text="Disconnect from MCP server")
            layout.label(text=f"Running on port {scene.blendermcp_port}")


# Operator to set Hyper3D API Key
class BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey(bpy.types.Operator):
    bl_idname = "blendermcp.set_hyper3d_free_trial_api_key"
    bl_label = "Set Free Trial API Key"

    def execute(self, context):
        context.scene.blendermcp_hyper3d_api_key = RODIN_FREE_TRIAL_KEY
        context.scene.blendermcp_hyper3d_mode = "MAIN_SITE"
        self.report({"INFO"}, "API Key set successfully!")
        return {"FINISHED"}


# Operator to start the server
class BLENDERMCP_OT_StartServer(bpy.types.Operator):
    bl_idname = "blendermcp.start_server"
    bl_label = "Connect to Gemini"
    bl_description = "Start the BlenderMCP server to connect with Gemini"

    def execute(self, context):
        scene = context.scene
        # Do not start background processes from the addon UI.
        # Starting the MCP server is an external operation (use start-server.ps1
        # or run `blender-mcp` in a terminal). Here we only set the UI flag so
        # users can indicate that they've started the server externally.
        scene.blendermcp_server_running = True
        self.report({"INFO"}, "Marked server as running — start the MCP server externally.")
        return {"FINISHED"}


# Operator to stop the server
class BLENDERMCP_OT_StopServer(bpy.types.Operator):
    bl_idname = "blendermcp.stop_server"
    bl_label = "Stop the connection to Gemini"
    bl_description = "Stop the connection to Gemini"

    def execute(self, context):
        scene = context.scene
        # Do not stop external processes from the addon UI. Just clear the UI flag.
        # If a server was started inside Blender by other means, it should be
        # stopped by that process. This avoids the addon terminating processes
        # unexpectedly during refactor/migration.
        scene.blendermcp_server_running = False
        self.report({"INFO"}, "Marked server as stopped — stop the MCP server externally if running.")
        return {"FINISHED"}


def register():
    """Register blender UI classes and properties.

    Properties are registered on `bpy.types.Scene` so they persist with the
    Blender file. Keeping property registration in a single helper makes it
    easier to audit and test.
    """

    _register_scene_properties()

    for cls in (
        BLENDERMCP_PT_Panel,
        BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey,
        BLENDERMCP_OT_StartServer,
        BLENDERMCP_OT_StopServer,
    ):
        bpy.utils.register_class(cls)

    print("BlenderMCP addon registered")


def unregister():
    """Unregister UI classes and remove Scene properties.

    We avoid stopping external processes here; the UI does not manage server
    lifecycle. Just clean up classes and properties so Blender does not keep
    stale references.
    """

    for cls in (
        BLENDERMCP_PT_Panel,
        BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey,
        BLENDERMCP_OT_StartServer,
        BLENDERMCP_OT_StopServer,
    ):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            # Best effort unregister; ignore if class wasn't registered.
            pass

    _unregister_scene_properties()

    print("BlenderMCP addon unregistered")


def _register_scene_properties() -> None:
    """Register scene-level properties used by the addon."""
    bpy.types.Scene.blendermcp_port = IntProperty(
        name="Port",
        description="Port for the BlenderMCP server",
        default=9876,
        min=1024,
        max=65535,
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


def _unregister_scene_properties() -> None:
    """Remove scene-level properties previously registered.

    Unregistering is best-effort: missing attributes are ignored to avoid
    raising during unregister cleanup.
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
    ):
        try:
            delattr(bpy.types.Scene, name)
        except Exception:
            # Ignore missing attributes
            try:
                delattr(bpy.context.scene, name)
            except Exception:
                pass
