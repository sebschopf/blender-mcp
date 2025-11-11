"""Scene-related helpers extracted from the addon handlers.

These functions lazy-import Blender modules so they remain importable in CI
and test environments that don't have Blender available.
"""

from __future__ import annotations

from typing import Any, Dict, List


def get_scene_info() -> Dict[str, Any]:
    """Get information about the current Blender scene (lazy-imports bpy)."""
    try:
        import bpy

        # Simplify the scene info to reduce data size
        scene_info: Dict[str, Any] = {
            "name": bpy.context.scene.name,
            "object_count": len(bpy.context.scene.objects),
            "objects": [],
            "materials_count": len(bpy.data.materials),
        }

        # Collect minimal object information (limit to first 10 objects)
        for i, obj in enumerate(bpy.context.scene.objects):
            if i >= 10:
                break

            obj_info = {
                "name": obj.name,
                "type": obj.type,
                "location": [
                    round(float(obj.location.x), 2),
                    round(float(obj.location.y), 2),
                    round(float(obj.location.z), 2),
                ],
            }
            scene_info["objects"].append(obj_info)

        return scene_info
    except Exception as e:
        return {"error": str(e)}


def _get_aabb(obj) -> List[List[float]]:
    """Returns world-space AABB for a Blender object (expects a Blender object)."""
    import mathutils

    if obj.type != "MESH":
        raise TypeError("Object must be a mesh")

    local_bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]
    world_bbox_corners = [obj.matrix_world @ corner for corner in local_bbox_corners]
    min_corner = mathutils.Vector(map(min, zip(*world_bbox_corners)))
    max_corner = mathutils.Vector(map(max, zip(*world_bbox_corners)))
    return [[*min_corner], [*max_corner]]


__all__ = ["get_scene_info", "_get_aabb"]
