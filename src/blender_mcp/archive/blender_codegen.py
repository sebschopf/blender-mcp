"""Archived snapshot of `blender_codegen.py` kept for history.

The implementation has been moved to `blender_mcp.codegen.blender_codegen`.
"""

from __future__ import annotations

import datetime
import os
from typing import Any, Dict


def generate_primitive_code(params: Dict[str, Any] | None) -> str:
    primitive_map = {
        "CYLINDER": "bpy.ops.mesh.primitive_cylinder_add(vertices={vertices}, radius={radius}, depth={depth})",
        "CUBE": "bpy.ops.mesh.primitive_cube_add(size={size})",
        "UV_SPHERE": "bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius={radius})",
    }

    prim = ""
    if params:
        prim = (params.get("primitive_type") or params.get("type") or "").upper()

    if prim in primitive_map:
        template = primitive_map[prim]
        fmt: Dict[str, Any] = {}
        defaults: Dict[str, Any] = {"vertices": 32, "radius": 1, "depth": 1, "size": 1}
        for k in ("vertices", "radius", "depth", "size"):
            if params and params.get(k) is not None:
                fmt[k] = params.get(k)
            else:
                fmt[k] = defaults[k]
        code = "import bpy\n" + template.format(**fmt) + "\n"
    else:
        code = (
            "import bpy\n"
            "# Unknown primitive requested, creating a default cube\n"
            "bpy.ops.mesh.primitive_cube_add(size=1)\n"
        )

    return code


def append_save_blend(code: str, output_dir: str | None = None) -> str:
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.getcwd(), "output"))
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"designed_scene_{ts}.blend"
    save_path = os.path.join(output_dir, filename)
    save_path_escaped = save_path.replace("\\", "\\\\")
    code += (
        "\n# Auto-save from bridge\n"
        "import bpy\n" + "bpy.ops.wm.save_mainfile(filepath=r'" + save_path_escaped + "')\n"
    )
    return code
