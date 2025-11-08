"""Handlers for local primitive generation and mapping.

Contains pure/side-effecting helpers that generate Blender code and call MCP.
"""
from __future__ import annotations

import os
from typing import Any

from .mcp_client import call_mcp_tool


def handle_add_primitive_mapping(params: dict[str, Any] | None, config) -> Any:
    """Generate primitive code (via blender_codegen when available) and call MCP.

    This function returns the parsed MCP response.
    """
    try:
        from .blender_codegen import append_save_blend, generate_primitive_code  # type: ignore

        code = generate_primitive_code(params or {})
    except Exception:
        prim = ""
        if params:
            prim = (params.get("primitive_type") or params.get("type") or "").upper()

        primitive_map = {
            "CYLINDER": "bpy.ops.mesh.primitive_cylinder_add(vertices={vertices}, radius={radius}, depth={depth})",
            "CUBE": "bpy.ops.mesh.primitive_cube_add(size={size})",
            "UV_SPHERE": "bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius={radius})",
        }
        if prim in primitive_map:
            template = primitive_map[prim]
            fmt: dict[str, Any] = {}
            for k in ("vertices", "radius", "depth", "size"):
                if params and params.get(k) is not None:
                    fmt[k] = params.get(k)
            code = "import bpy\n" + template.format(**fmt) + "\n"
        else:
            code = (
                "import bpy\n"
                "# Unknown primitive requested, creating a default cube\n"
                "bpy.ops.mesh.primitive_cube_add(size=1)\n"
            )

    if getattr(config, "verbose", False):
        print("--- Generated Blender Python code ---")
        print(code)
        print("--- end generated code ---")

    if getattr(config, "save_blend", False):
        try:
            code = append_save_blend(code)  # type: ignore
        except Exception:
            save_dir = os.path.abspath(os.path.join(os.getcwd(), "output"))
            os.makedirs(save_dir, exist_ok=True)
            import datetime

            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"designed_scene_{ts}.blend"
            save_path = os.path.join(save_dir, filename)
            save_path_escaped = save_path.replace("\\", "\\\\")
            code += (
                "\n# Auto-save from bridge\n"
                "import bpy\n"
                + "bpy.ops.wm.save_mainfile(filepath=r'" + save_path_escaped + "')\n"
            )

    return call_mcp_tool("execute_blender_code", {"code": code})
