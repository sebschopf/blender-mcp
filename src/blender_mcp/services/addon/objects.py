"""Object-related helpers extracted from addon handlers."""

# ruff: noqa: C901  -- helper performs many compatibility branches for fake bpy objects in tests

from __future__ import annotations

from typing import Any, Dict


def _coerce_f(v: Any) -> Any:
    try:
        return float(v)
    except Exception:
        return None


def _parse_location(loc: Any) -> Any:
    # attribute-style (Vector-like)
    if hasattr(loc, "x") and hasattr(loc, "y") and hasattr(loc, "z"):
        x = _coerce_f(getattr(loc, "x"))
        y = _coerce_f(getattr(loc, "y"))
        z = _coerce_f(getattr(loc, "z"))
        if None not in (x, y, z):
            return [x, y, z]

    # mapping-like
    try:
        if isinstance(loc, dict) or hasattr(loc, "get"):
            gx = getattr(loc, "get", None)
            if callable(gx):
                x = _coerce_f(loc.get("x"))
                y = _coerce_f(loc.get("y"))
                z = _coerce_f(loc.get("z"))
                if None not in (x, y, z):
                    return [x, y, z]
    except Exception:
        pass

    # sequence-like (list/tuple/array)
    try:
        if hasattr(loc, "__iter__") and not isinstance(loc, (str, bytes)):
            seq = list(loc)
            if len(seq) == 3:
                coerced = [_coerce_f(v) for v in seq]
                if None not in coerced:
                    return coerced
    except Exception:
        pass

    return None


def _find_object(name: str, bpy_module: Any) -> Any:
    objs = getattr(getattr(bpy_module, "data", None), "objects", None)
    obj = None
    if objs is None:
        raise ValueError("bpy.data.objects is not available")

    if hasattr(objs, "get") and callable(getattr(objs, "get")):
        obj = objs.get(name)
    else:
        try:
            for o in objs:
                if getattr(o, "name", None) == name:
                    obj = o
                    break
        except TypeError:
            obj = None

    # fallback: search in context.scene.objects if present
    if not obj:
        scene = getattr(bpy_module, "context", None)
        scene = getattr(scene, "scene", None) if scene is not None else None
        if scene is not None:
            s_objs = getattr(scene, "objects", None)
            if s_objs is not None:
                if hasattr(s_objs, "get") and callable(getattr(s_objs, "get")):
                    obj = s_objs.get(name)
                else:
                    try:
                        for o in s_objs:
                            if getattr(o, "name", None) == name:
                                obj = o
                                break
                    except TypeError:
                        obj = None

    if not obj:
        raise ValueError(f"Object not found: {name}")

    return obj


def get_object_info(name: str) -> Dict[str, Any]:
    try:
        import bpy
    except ModuleNotFoundError:
        return {"error": "Blender (bpy) not available"}
    except Exception as e:
        return {"error": str(e)}

    try:
        obj = _find_object(name, bpy)

        # parse and include location only when parse succeeds

        rotation = getattr(obj, "rotation_euler", None)
        scale = getattr(obj, "scale", None)

        obj_info: Dict[str, Any] = {
            "name": getattr(obj, "name", None),
            "type": getattr(obj, "type", None),
            "rotation": [
                getattr(rotation, "x", None) if rotation is not None else None,
                getattr(rotation, "y", None) if rotation is not None else None,
                getattr(rotation, "z", None) if rotation is not None else None,
            ],
            "scale": [
                getattr(scale, "x", None) if scale is not None else None,
                getattr(scale, "y", None) if scale is not None else None,
                getattr(scale, "z", None) if scale is not None else None,
            ],
            "visible": (getattr(obj, "visible_get", lambda: False)()),
            "materials": [],
        }

        loc = _parse_location(getattr(obj, "location", None))
        if loc is not None:
            obj_info["location"] = loc

        if obj.type == "MESH":
            from .scene import _get_aabb

            try:
                obj_info["world_bounding_box"] = _get_aabb(obj)
            except Exception:
                # mathutils or scene helpers may be unavailable in test fakes; skip
                pass

        for slot in getattr(obj, "material_slots", []) or []:
            mat = getattr(slot, "material", None)
            if mat is not None and getattr(mat, "name", None):
                obj_info["materials"].append(mat.name)

        if getattr(obj, "type", None) == "MESH" and getattr(obj, "data", None):
            mesh = getattr(obj, "data")
            try:
                obj_info["mesh"] = {
                    "vertices": len(mesh.vertices),
                    "edges": len(mesh.edges),
                    "polygons": len(mesh.polygons),
                }
            except Exception:
                # best-effort: skip mesh stats if mesh API not present in fake env
                pass

        return obj_info
    except Exception as e:
        return {"error": str(e)}


__all__ = ["get_object_info"]
