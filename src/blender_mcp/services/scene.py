"""Service to retrieve basic scene information from Blender.

This service uses lazy import of `bpy` so it is safe to import the
package in CI or outside Blender. The function returns a dictionary with
lightweight, JSON-serializable scene information useful for tests and
clients.
"""
from __future__ import annotations

import importlib
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _obj_to_dict(obj: Any) -> Dict[str, Any]:
    return {"name": getattr(obj, "name", "<unknown>"), "type": getattr(obj, "type", "<unknown>")}


def get_scene_info(params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return simple scene information.

    - scene_name
    - objects: list of {name,type}
    - active_camera: name or None

    If `bpy` is not importable, returns an error dict.
    """
    try:
        bpy = importlib.import_module("bpy")
    except Exception:
        logger.debug("bpy not available when calling get_scene_info")
        return {"status": "error", "message": "Blender (bpy) not available"}

    try:
        scene = getattr(bpy, "context", None)
        scene_name = getattr(getattr(scene, "scene", None), "name", None)

        # gather objects from bpy.data.objects if available
        data = getattr(bpy, "data", None)
        objects = []
        if data is not None and hasattr(data, "objects"):
            for o in data.objects:
                objects.append(_obj_to_dict(o))

        # active camera if available
        active_cam = None
        if scene is not None and hasattr(scene, "scene"):
            ac = getattr(scene.scene, "camera", None)
            if ac is not None:
                active_cam = getattr(ac, "name", None)

        return {"status": "success", "scene_name": scene_name, "objects": objects, "active_camera": active_cam}
    except Exception as e:
        logger.exception("unexpected error in get_scene_info")
        return {"status": "error", "message": str(e)}


__all__ = ["get_scene_info"]
