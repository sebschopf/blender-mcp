"""Blender-side handlers extracted from the legacy addon.

These functions perform Blender-specific actions but import `bpy` lazily
so the module can be imported in test runners that don't have Blender.

They intentionally re-declare a small set of constants (headers, keys)
so they don't rely on importing the top-level `addon.py` (avoids circular
imports).
"""
from __future__ import annotations

import io
import json
import traceback
from contextlib import redirect_stdout

import requests

# Minimal required constants (kept local to avoid circular imports)
REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "blender-mcp"})

RODIN_FREE_TRIAL_KEY = (
    "k9TcfFoEhNd9cCPP2guHAHHHkctZHIRhZDywZ1euGUXwihbYLpOjQhofby80NJez"
)


def get_scene_info():
    """Get information about the current Blender scene (lazy-imports bpy)."""
    try:
        import bpy

        # Simplify the scene info to reduce data size
        scene_info = {
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


def _get_aabb(obj):
    """Returns world-space AABB for a Blender object (expects a Blender object)."""
    import mathutils

    if obj.type != "MESH":
        raise TypeError("Object must be a mesh")

    local_bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]
    world_bbox_corners = [obj.matrix_world @ corner for corner in local_bbox_corners]
    min_corner = mathutils.Vector(map(min, zip(*world_bbox_corners)))
    max_corner = mathutils.Vector(map(max, zip(*world_bbox_corners)))
    return [[*min_corner], [*max_corner]]


def get_object_info(name: str):
    try:
        import bpy

        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object not found: {name}")

        obj_info = {
            "name": obj.name,
            "type": obj.type,
            "location": [obj.location.x, obj.location.y, obj.location.z],
            "rotation": [
                obj.rotation_euler.x,
                obj.rotation_euler.y,
                obj.rotation_euler.z,
            ],
            "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            "visible": obj.visible_get(),
            "materials": [],
        }

        if obj.type == "MESH":
            obj_info["world_bounding_box"] = _get_aabb(obj)

        for slot in obj.material_slots:
            if slot.material:
                obj_info["materials"].append(slot.material.name)

        if obj.type == "MESH" and obj.data:
            mesh = obj.data
            obj_info["mesh"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
            }

        return obj_info
    except Exception as e:
        return {"error": str(e)}


def get_viewport_screenshot(max_size=800, filepath=None, format="png"):
    try:
        if not filepath:
            return {"error": "No filepath provided"}

        import bpy

        area = None
        for a in bpy.context.screen.areas:
            if a.type == "VIEW_3D":
                area = a
                break

        if not area:
            return {"error": "No 3D viewport found"}

        with bpy.context.temp_override(area=area):
            bpy.ops.screen.screenshot_area(filepath=filepath)

        img = bpy.data.images.load(filepath)
        width, height = img.size

        if max(width, height) > max_size:
            scale = max_size / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img.scale(new_width, new_height)
            img.file_format = format.upper()
            img.save()
            width, height = new_width, new_height

        bpy.data.images.remove(img)

        return {"success": True, "width": width, "height": height, "filepath": filepath}
    except Exception as e:
        return {"error": str(e)}


def execute_code(code: str):
    try:
        import bpy

        namespace = {"bpy": bpy}
        capture_buffer = io.StringIO()
        with redirect_stdout(capture_buffer):
            exec(code, namespace)
        captured_output = capture_buffer.getvalue()
        return {"executed": True, "result": captured_output}
    except Exception as e:
        raise Exception(f"Code execution error: {str(e)}")


def get_polyhaven_categories(asset_type: str):
    try:
        if asset_type not in ["hdris", "textures", "models", "all"]:
            return {"error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"}

        try:
            from blender_mcp.polyhaven import fetch_categories  # type: ignore

            cats = fetch_categories(asset_type, timeout=10)
            return {"categories": cats}
        except Exception:
            try:
                from blender_mcp.downloaders import download_bytes  # type: ignore

                data = download_bytes(
                    f"https://api.polyhaven.com/categories/{asset_type}", timeout=10, headers=REQ_HEADERS
                )
                return {"categories": json.loads(data.decode("utf-8"))}
            except Exception:
                response = requests.get(f"https://api.polyhaven.com/categories/{asset_type}", headers=REQ_HEADERS)
                if response.status_code == 200:
                    return {"categories": response.json()}
                return {"error": f"API request failed with status code {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def search_polyhaven_assets(asset_type=None, categories=None):
    try:
        params = {}
        if asset_type and asset_type != "all":
            if asset_type not in ["hdris", "textures", "models"]:
                return {"error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"}
            params["type"] = asset_type

        if categories:
            params["categories"] = categories

        try:
            from blender_mcp.polyhaven import search_assets  # type: ignore

            assets = search_assets(params, timeout=10)
        except Exception:
            try:
                import urllib.parse

                from blender_mcp.downloaders import download_bytes  # type: ignore

                qs = urllib.parse.urlencode(params, doseq=True)
                full_url = "https://api.polyhaven.com/assets" + ("?" + qs if qs else "")
                data = download_bytes(full_url, timeout=10, headers=REQ_HEADERS)
                assets = json.loads(data.decode("utf-8"))
            except Exception:
                response = requests.get("https://api.polyhaven.com/assets", params=params, headers=REQ_HEADERS)
                if response.status_code == 200:
                    assets = response.json()
                else:
                    return {"error": f"API request failed with status code {response.status_code}"}

        limited_assets = {}
        for i, (key, value) in enumerate(assets.items()):
            if i >= 20:
                break
            limited_assets[key] = value

        return {"assets": limited_assets, "total_count": len(assets), "returned_count": len(limited_assets)}
    except Exception as e:
        return {"error": str(e)}


def download_polyhaven_asset(asset_id, asset_type, resolution="1k", file_format=None):
    try:
        from blender_mcp.polyhaven import fetch_files_data  # type: ignore

        files_data = fetch_files_data(asset_id)
    except Exception:
        try:
            from blender_mcp.downloaders import download_bytes  # type: ignore

            data = download_bytes(f"https://api.polyhaven.com/files/{asset_id}", timeout=10, headers=REQ_HEADERS)
            files_data = json.loads(data.decode("utf-8"))
        except Exception:
            try:
                files_response = requests.get(f"https://api.polyhaven.com/files/{asset_id}", headers=REQ_HEADERS)
                if files_response.status_code != 200:
                    return {"error": f"Failed to get asset files: {files_response.status_code}"}
                files_data = files_response.json()
            except Exception as e:
                return {"error": str(e)}

    # The rest of the polyhaven handling is intentionally left to the
    # addon fallback (which has rich Blender interaction). Here we simply
    # return the parsed files data so the caller can decide how to import.
    return {"files_data": files_data}


def set_texture(object_name, texture_id):
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object not found: {object_name}"}

        if not hasattr(obj, "data") or not hasattr(obj.data, "materials"):
            return {"error": f"Object {object_name} cannot accept materials"}

        texture_images = _collect_texture_images(texture_id)

        if not texture_images:
            return {"error": f"No texture images found for: {texture_id}. Please download the texture first."}

        images_map_names = {k: img.name for k, img in texture_images.items()}
        mat_name = _try_create_material(images_map_names, texture_id, object_name)
        if mat_name:
            return {"success": True, "material": mat_name}

        # If helper not available, fall back to returning images so caller
        # can create material inline.
        return {"images": list(texture_images.keys())}

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


def _collect_texture_images(texture_id: str):
    """Collect images matching a texture id and normalize their color space.

    This helper lazily imports bpy and performs safe operations on images.
    """
    try:
        import bpy
    except Exception:
        return {}

    texture_images = {}
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
    """Attempt to create a material using the project helper; return name or None."""
    try:
        from blender_mcp.materials import create_material_in_blender  # type: ignore

        return create_material_in_blender(images_map_names, f"{texture_id}_material_{object_name}")
    except Exception:
        return None
