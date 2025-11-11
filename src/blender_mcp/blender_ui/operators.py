"""Operator classes for BlenderMCP UI (start/stop, set API key, apply settings).

Operators are defined only when `bpy` is available. When `bpy` isn't
present we expose lightweight placeholders so imports remain safe during
test collection.
"""

from typing import Optional

# Live process object kept here when the addon starts an external helper
_server_proc: Optional[object] = None


RODIN_FREE_TRIAL_KEY = "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez"


def _has_real_bpy() -> bool:
    """Return True when a real or sufficiently-featured fake `bpy` is available."""
    try:
        import importlib

        bpy = importlib.import_module("bpy")
        return bool(getattr(bpy, "types", None) and getattr(bpy.types, "Operator", None))
    except Exception:
        return False


if _has_real_bpy():
    import importlib

    bpy = importlib.import_module("bpy")  # type: ignore

    class BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey(bpy.types.Operator):
        bl_idname = "blendermcp.set_hyper3d_free_trial_api_key"
        bl_label = "Set Free Trial API Key"

        def execute(self, context):
            context.scene.blendermcp_hyper3d_api_key = RODIN_FREE_TRIAL_KEY
            context.scene.blendermcp_hyper3d_mode = "MAIN_SITE"
            self.report({"INFO"}, "API Key set successfully!")
            return {"FINISHED"}

    class BLENDERMCP_OT_StartServer(bpy.types.Operator):
        bl_idname = "blendermcp.start_server"
        bl_label = "Connect to Gemini"
        bl_description = "Start the BlenderMCP server to connect with Gemini"

        def execute(self, context):  # noqa: C901
            scene = context.scene
            global _server_proc

            # Check preferences (use sys.modules to allow tests to inject fake bpy)
            try:
                import sys

                bpy_mod = sys.modules.get("bpy", bpy)

                prefs_container = None
                if (
                    getattr(bpy_mod, "context", None) is not None
                    and getattr(bpy_mod.context, "preferences", None) is not None
                ):
                    prefs_container = bpy_mod.context.preferences
                elif getattr(bpy_mod, "preferences", None) is not None:
                    prefs_container = bpy_mod.preferences

                allow = True
                if prefs_container is not None:
                    addons_map = getattr(prefs_container, "addons", {})
                    prefs_obj = None
                    if isinstance(addons_map, dict):
                        prefs_obj = addons_map.get("blender_mcp")
                    else:
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

            # Try to start an external server adapter (lazy import)
            try:
                # Import the adapter from its new package location.
                # Tests and callers should patch `blender_mcp.servers.embedded_adapter`.
                from blender_mcp.servers import embedded_adapter as adapter

                proc = adapter.start_server_process()
                _server_proc = proc
                try:
                    scene.blendermcp_server_pid = getattr(proc, "pid", 0)
                except Exception:
                    scene.blendermcp_server_pid = 0
                scene.blendermcp_server_running = True
                self.report({"INFO"}, "Started external MCP server (or launched helper script)")
                return {"FINISHED"}
            except Exception as e:
                self.report({"ERROR"}, f"Failed to start external MCP server: {e}")
                return {"CANCELLED"}

    class BLENDERMCP_OT_StopServer(bpy.types.Operator):
        bl_idname = "blendermcp.stop_server"
        bl_label = "Disconnect from MCP server"

        def execute(self, context):
            scene = context.scene
            global _server_proc
            try:
                from blender_mcp.servers import embedded_adapter as adapter

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
                self.report(
                    {"INFO"},
                    f"BLENDER_MCP_ALLOW_EXECUTE set to {os.environ['BLENDER_MCP_ALLOW_EXECUTE']}",
                )
                return {"FINISHED"}
            except Exception as e:
                self.report({"ERROR"}, f"Failed to apply setting: {e}")
                return {"CANCELLED"}

else:
    # Fallback placeholders when bpy is not present. These are simple classes
    # that mirror the public names; they are not real Operators and should not
    # be registered with Blender.

    class BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey:  # type: ignore
        pass

    class BLENDERMCP_OT_StartServer:  # type: ignore
        pass

    class BLENDERMCP_OT_StopServer:  # type: ignore
        pass

    class BLENDERMCP_OT_ApplyRemoteExecSetting:  # type: ignore
        pass
