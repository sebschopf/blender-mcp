"""Service-facing wrapper for screenshots.

Validates params, delegates to the Blender-side implementation in
`services.addon.screenshots` and normalizes responses to the canonical
service schema: {"status":"success","result":...} or
{"status":"error","message":...}.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .addon.screenshots import get_viewport_screenshot as _addon_get_viewport_screenshot

logger = logging.getLogger(__name__)


def get_viewport_screenshot(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service-facing get_viewport_screenshot.

    Expects params: {"filepath": str, "max_size": int (optional), "format": str (optional)}
    Returns: {"status":"success","result": {"width":int,"height":int,"filepath":str}}
             or {"status":"error","message": str}
    """
    if not params:
        return {"status": "error", "message": "missing params"}

    filepath = params.get("filepath")
    if not filepath or not isinstance(filepath, str):
        return {"status": "error", "message": "missing or invalid 'filepath'"}

    max_size = params.get("max_size", 800)
    fmt = params.get("format", "png")

    try:
        addon_resp = _addon_get_viewport_screenshot(max_size=int(max_size), filepath=filepath, format=str(fmt))
    except Exception as e:
        logger.exception("addon get_viewport_screenshot failed")
        return {"status": "error", "message": str(e)}

    if isinstance(addon_resp, dict) and addon_resp.get("error"):
        return {"status": "error", "message": addon_resp.get("error")}

    if isinstance(addon_resp, dict) and addon_resp.get("success"):
        return {
            "status": "success",
            "result": {
                "width": addon_resp.get("width"),
                "height": addon_resp.get("height"),
                "filepath": addon_resp.get("filepath"),
            },
        }

    return {"status": "error", "message": "unexpected addon response"}


__all__ = ["get_viewport_screenshot"]
