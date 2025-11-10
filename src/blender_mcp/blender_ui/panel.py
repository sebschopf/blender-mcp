"""UI Panel for the BlenderMCP add-on.

Contains the single `BLENDERMCP_PT_Panel` class which references scene
properties and invokes operators by id. Kept minimal and declarative.
"""

import bpy


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
                "blendermcp.set_hyper3d_free_trial_api_key", text="Set Free Trial API Key"
            )

        layout.prop(scene, "blendermcp_use_sketchfab", text="Use assets from Sketchfab")
        if scene.blendermcp_use_sketchfab:
            layout.prop(scene, "blendermcp_sketchfab_api_key", text="API Key")

        if not scene.blendermcp_server_running:
            layout.operator("blendermcp.start_server", text="Connect to MCP server")
        else:
            layout.operator("blendermcp.stop_server", text="Disconnect from MCP server")
            layout.label(text=f"Running on port {scene.blendermcp_port}")

        # WARNING: remote code execution
        box = layout.box()
        box.label(text="Remote code execution (dangerous)")
        box.label(text="execute_blender_code is disabled by default.")
        box.prop(scene, "blendermcp_allow_remote_exec", text="Allow remote execution")
        box.operator("blendermcp.apply_remote_exec_setting", text="Apply setting")
