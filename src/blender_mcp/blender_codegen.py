"""Small helper to generate Blender Python code for simple primitives.

This module keeps codegen pure (no bpy import at module import time) so it can be
unit-tested. It returns the Python source as a string which can then be sent to the
MCP `execute_blender_code` tool.
"""
from __future__ import annotations

import datetime
import os
from typing import Any, Dict


def generate_primitive_code(params: Dict[str, Any] | None) -> str:
    """Return Python source that creates a simple primitive in Blender.

    This function intentionally does not import `bpy` at module import time.

    Args:
        params: mapping that may contain 'primitive_type' or 'type' and parameters
            like 'size', 'radius', 'depth', 'vertices'.

    Returns:
        Source code string (UTF-8) creating the requested primitive.
    """
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
        # sensible defaults so format() won't fail when keys are missing
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
    """Append a save step to the generated code and return the new source.

    If `output_dir` is None, uses ./output under current working dir.
    """
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.getcwd(), "output"))
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"designed_scene_{ts}.blend"
    save_path = os.path.join(output_dir, filename)
    save_path_escaped = save_path.replace("\\", "\\\\")
    code += (
        "\n# Auto-save from bridge\n"
        "import bpy\n"
        + "bpy.ops.wm.save_mainfile(filepath=r'" + save_path_escaped + "')\n"
    )
    return code
