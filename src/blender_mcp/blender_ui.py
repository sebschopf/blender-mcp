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
from typing import Optional

# Addon preferences: register this so users can control whether the UI may start
# an external server process. We defensively pick a base class so importing
# the module during tests (with a minimal fake `bpy`) does not crash.
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
        # When running inside Blender this will show in User Preferences.
        try:
            layout = self.layout
            layout.label(text="BlenderMCP preferences")
            layout.prop(self, "allow_ui_start_server")
        except Exception:
            # In tests the layout may not exist; ignore draw-time errors.
            pass

# Holds the live process object when the adapter starts an external server
# during a Blender session. Kept module-level so operators can stop it later.
_server_proc: Optional[object] = None

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

        # WARNING: remote code execution is dangerous. This UI shows the
        # current preference and provides a one-click apply button to set the
        # runtime env var that enables the execution endpoint. We do NOT enable
        # execution automatically to avoid accidental execution in CI.
        box = layout.box()
        box.label(text="Remote code execution (dangerous)")
        box.label(text="execute_blender_code is disabled by default.")
        box.prop(scene, "blendermcp_allow_remote_exec", text="Allow remote execution")
        box.operator("blendermcp.apply_remote_exec_setting", text="Apply setting")


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
        global _server_proc
        # Check Addon preferences: only start if allowed. Use the live `bpy`
        # from sys.modules if present so tests that swap `sys.modules['bpy']`
        # are respected even if this module was imported earlier.
        try:
            import sys

            bpy_mod = sys.modules.get("bpy", bpy)

            # Prefer preferences attached to the active context (Blender UI path).
            # In tests the minimal fake installs `bpy.preferences`, so fall back to
            # that if `bpy.context.preferences` is not present.
            prefs_container = None
            if getattr(bpy_mod, "context", None) is not None and getattr(bpy_mod.context, "preferences", None) is not None:
                prefs_container = bpy_mod.context.preferences
            elif getattr(bpy_mod, "preferences", None) is not None:
                prefs_container = bpy_mod.preferences

            allow = True
            if prefs_container is not None:
                addons_map = getattr(prefs_container, "addons", {})
                # Prefer explicit addon key 'blender_mcp'
                prefs_obj = None
                if isinstance(addons_map, dict):
                    prefs_obj = addons_map.get("blender_mcp")
                else:
                    # fallback: try attribute access
                    prefs_obj = getattr(addons_map, "blender_mcp", None)
                if prefs_obj is not None:
                    prefs = getattr(prefs_obj, "preferences", None)
                    if prefs is not None:
                        allow = bool(getattr(prefs, "allow_ui_start_server", False))
        except Exception:
            allow = True

        if not allow:
            self.report({"ERROR"}, "Addon preferences forbid starting server from the UI")
            return {"CANCELLED"}

        # Attempt to start an external server process using the adapter.
        # Import lazily so the module remains import-safe in tests and
        # non-Blender environments.
        try:
            from . import embedded_server_adapter as adapter

            proc = adapter.start_server_process()
            _server_proc = proc
            # store pid in the scene for visibility
            try:
                scene.blendermcp_server_pid = getattr(proc, "pid", 0)
            except Exception:
                scene.blendermcp_server_pid = 0
            scene.blendermcp_server_running = True
            self.report({"INFO"}, "Started external MCP server (or launched helper script)")
            return {"FINISHED"}
        except Exception as e:

        # Attempt to stop an external server previously started via the adapter.
        try:
            from . import embedded_server_adapter as adapter

            if _server_proc is not None:
                adapter.stop_server_process(_server_proc)
                _server_proc = None
            scene.blendermcp_server_pid = 0
            scene.blendermcp_server_running = False
            self.report({"INFO"}, "Stopped external MCP server (if it was started by the addon)")
            return {"FINISHED"}
        except Exception as e:
            scene.blendermcp_server_running = False
            self.report({"ERROR"}, f"Failed to stop external MCP server: {e}")
            return {"CANCELLED"}



        class BLENDERMCP_OT_ApplyRemoteExecSetting(bpy.types.Operator):
            bl_idname = "blendermcp.apply_remote_exec_setting"
            bl_label = "Apply remote-exec setting"

            def execute(self, context):
                try:
                    import os

                    enabled = bool(getattr(context.scene, "blendermcp_allow_remote_exec", False))
                    os.environ["BLENDER_MCP_ALLOW_EXECUTE"] = "1" if enabled else "0"
                    self.report({"INFO"}, f"BLENDER_MCP_ALLOW_EXECUTE set to {os.environ["BLENDER_MCP_ALLOW_EXECUTE"]}")
                    return {"FINISHED"}
                except Exception as e:
                    self.report({"ERROR"}, f"Failed to apply setting: {e}")
                    return {"CANCELLED"}


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
        BLENDERMCP_OT_ApplyRemoteExecSetting,
        BLENDERMCP_OT_StopServer,
        BLENDERMCP_AddonPreferences,
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
        BLENDERMCP_OT_ApplyRemoteExecSetting,
        BLENDERMCP_OT_StopServer,
        BLENDERMCP_AddonPreferences,
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
        "blendermcp_allow_remote_exec",
    ):
        try:
            delattr(bpy.types.Scene, name)
        except Exception:
            # Ignore missing attributes
            try:
                delattr(bpy.context.scene, name)
            except Exception:
                pass
