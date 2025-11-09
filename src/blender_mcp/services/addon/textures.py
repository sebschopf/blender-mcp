"""Texture/material helpers extracted from addon handlers."""

from __future__ import annotations

import traceback
from typing import Any, Dict


def set_texture(object_name: str, texture_id: str) -> Dict[str, Any]:
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}

        if not hasattr(obj, "data") or not hasattr(obj.data, "materials"):
            return {"error": f"Object {object_name} cannot accept materials"}

        texture_images = _collect_texture_images(texture_id)

        if not texture_images:
            return {
                "error": f"No texture images found for: {texture_id}. Please download the texture first."
            }

        images_map_names = {k: img.name for k, img in texture_images.items()}
        mat_name = _try_create_material(images_map_names, texture_id, object_name)
        if mat_name:
            return {"success": True, "material": mat_name}

        return {"images": list(texture_images.keys())}

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


def _collect_texture_images(texture_id: str) -> Dict[str, Any]:
    try:
        import bpy
    except Exception:
        return {}

    texture_images: Dict[str, Any] = {}
    for img in bpy.data.images:
        if not img.name.startswith(texture_id + "_"):
            continue
        map_type = img.name.split("_")[-1].split(".")[0]
        try:
            img.reload()
        except Exception:
            pass
        try:
            if map_type.lower() in ["color", "diffuse", "albedo"]:
                img.colorspace_settings.name = "sRGB"
            else:
                img.colorspace_settings.name = "Non-Color"
        except Exception:
            pass
        try:
            if not img.packed_file:
                img.pack()
        except Exception:
            pass
        texture_images[map_type] = img
    return texture_images


def _try_create_material(images_map_names: dict, texture_id: str, object_name: str) -> str | None:
    try:
        from blender_mcp.materials import create_material_in_blender  # type: ignore

        return create_material_in_blender(
            images_map_names, f"{texture_id}_material_{object_name}"
        )
    except Exception:
        return None


__all__ = ["set_texture", "_collect_texture_images", "_try_create_material"]
