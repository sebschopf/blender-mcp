"""Service to get information about a named object in the scene.

Pattern: lazy import of `bpy` so the module is safe to import in CI.
The function returns a JSON-serializable dict with basic object properties.
"""
from __future__ import annotations

import importlib
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _parse_name(params: Dict[str, Any] | None) -> Optional[str]:
    if not params:
        return None
    name = params.get("name")
    return name if isinstance(name, str) else None


def _import_bpy() -> Optional[object]:
    try:
        return importlib.import_module("bpy")
    except Exception:
        logger.debug("bpy not available when calling get_object_info")
        return None


def _find_object(bpy: object, name: str) -> Optional[object]:
    # Search in bpy.data.objects
    data = getattr(bpy, "data", None)
    if data is not None and hasattr(data, "objects"):
        for o in data.objects:
            if getattr(o, "name", None) == name:
                return o

    # Fallback: search in context.scene.objects
    ctx = getattr(bpy, "context", None)
    scene = getattr(ctx, "scene", None) if ctx is not None else None
    if scene is not None and hasattr(scene, "objects"):
        for o in scene.objects:
            if getattr(o, "name", None) == name:
                return o

    return None


def _extract_location(obj: object) -> Optional[list[float]]:
    loc = getattr(obj, "location", None)
    if loc is None:
        return None

    # 1) Attribute-style access (x, y, z)
    try:
        vals = [getattr(loc, i) for i in ("x", "y", "z")]
        return [float(v) for v in vals]
    except Exception:
        pass

    # 2) Mapping-like access (dict or similar)
    try:
        if hasattr(loc, "get"):
            if all(k in loc for k in ("x", "y", "z")):  # type: ignore[arg-type]
                return [float(loc["x"]), float(loc["y"]), float(loc["z"])]
    except Exception:
        pass

    # 3) Iterable/sequence access: require exactly 3 components (x,y,z)
    try:
        seq = list(loc)
        if len(seq) != 3:
            return None
        return [float(v) for v in seq]
    except Exception:
        return None


def _collect_info(obj: object) -> Dict[str, Any]:
    info: Dict[str, Any] = {"name": getattr(obj, "name", None), "type": getattr(obj, "type", None)}
    location = _extract_location(obj)
    if location is not None:
        info["location"] = location
    return info


def get_object_info(params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return basic info about a named object.

    Expected params:
    - name: str

    Returns a dict with status and object info or an error message.
    """
    name = _parse_name(params)
    if not name:
        return {"status": "error", "message": "missing or invalid 'name'"}

    bpy = _import_bpy()
    if bpy is None:
        return {"status": "error", "message": "Blender (bpy) not available"}

    try:
        obj = _find_object(bpy, name)
        if obj is None:
            return {"status": "error", "message": f"object '{name}' not found"}

        info = _collect_info(obj)
        return {"status": "success", "object": info}
    except Exception:
        logger.exception("unexpected error in get_object_info")
        return {"status": "error", "message": "unexpected error"}


__all__ = ["get_object_info"]
