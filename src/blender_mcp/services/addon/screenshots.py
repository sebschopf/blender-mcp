"""Screenshot helpers extracted from addon handlers."""

from __future__ import annotations

from typing import Any, Dict, Optional


def get_viewport_screenshot(max_size: int = 800, filepath: Optional[str] = None, format: str = "png") -> Dict[str, Any]:
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


__all__ = ["get_viewport_screenshot"]
