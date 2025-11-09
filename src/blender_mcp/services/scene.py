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

from .addon.scene import get_scene_info as _addon_get_scene_info

logger = logging.getLogger(__name__)


def _normalize_objects(addon_objects: Any) -> list[Dict[str, Any]]:
    """Normalize the addon 'objects' into the lightweight list of {name,type}.

    The addon implementation may return richer per-object dicts
    (including location). For the service contract we only expose name
    and type to keep the response compact and stable.
    """
    out: list[Dict[str, Any]] = []
    if not isinstance(addon_objects, list):
        return out
    for o in addon_objects:
        if isinstance(o, dict):
            out.append({"name": o.get("name"), "type": o.get("type")})
        else:
            # fallback: best-effort stringification
            out.append({"name": str(o), "type": None})
    return out


def get_scene_info(params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Canonical service-facing get_scene_info.

    Delegates the extraction work to the addon implementation
    (`services.addon.scene.get_scene_info`) which may import `bpy` and
    return detailed data. This function normalizes that output to the
    standard service schema: {"status":"success", ...} or
    {"status":"error","message":...}.
    """
    try:
        addon_result = _addon_get_scene_info()
    except Exception as e:
        logger.exception("addon scene extraction failed")
        return {"status": "error", "message": str(e)}

    # If the addon returned an error dict, try to normalize or fall back to
    # the older in-module extraction logic for compatibility with tests and
    # different fake bpy shapes used in CI.
    if isinstance(addon_result, dict) and "error" in addon_result:
        msg = addon_result.get("error") or ""
        # Preserve the older explicit message when bpy is not importable
        if "No module named 'bpy'" in msg or "cannot import name 'bpy'" in msg:
            return {"status": "error", "message": "Blender (bpy) not available"}

        # Otherwise try a best-effort fallback that mirrors the previous
        # implementation (query bpy.data.objects, etc.) so tests that
        # provide different fake bpy shapes keep working.
        try:
            bpy = importlib.import_module("bpy")
        except Exception:
            return {"status": "error", "message": msg}

        return _fallback_get_scene_info(bpy)


def _fallback_get_scene_info(bpy) -> Dict[str, Any]:
    """Backward-compatible extraction when the addon helper fails.

    Mirrors previous behavior: prefer `bpy.data.objects` for object list
    and read `bpy.context.scene` for scene metadata.
    """
    try:
        scene = getattr(bpy, "context", None)
        scene_name = getattr(getattr(scene, "scene", None), "name", None)

        data = getattr(bpy, "data", None)
        objects = []
        if data is not None and hasattr(data, "objects"):
            for o in data.objects:
                objects.append({"name": getattr(o, "name", None), "type": getattr(o, "type", None)})

        active_cam = None
        if scene is not None and hasattr(scene, "scene"):
            ac = getattr(scene.scene, "camera", None)
            if ac is not None:
                active_cam = getattr(ac, "name", None)

        return {
            "status": "success",
            "scene_name": scene_name,
            "objects": objects,
            "active_camera": active_cam,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

    # Build canonical response
    try:
        scene_name = addon_result.get("name") if isinstance(addon_result, dict) else None
        objects = _normalize_objects(addon_result.get("objects") if isinstance(addon_result, dict) else None)

        # active camera: try to read from bpy (best-effort, non-fatal)
        active_cam = None
        try:
            bpy = importlib.import_module("bpy")
            scene = getattr(bpy, "context", None)
            if scene is not None and hasattr(scene, "scene"):
                ac = getattr(scene.scene, "camera", None)
                if ac is not None:
                    active_cam = getattr(ac, "name", None)
        except Exception:
            # not running inside Blender; active_cam remains None
            pass

        return {
            "status": "success",
            "scene_name": scene_name,
            "objects": objects,
            "active_camera": active_cam,
        }
    except Exception as e:
        logger.exception("unexpected error normalizing addon scene info")
        return {"status": "error", "message": str(e)}


__all__ = ["get_scene_info"]
