"""Service wrapper for object information.

This module provides the canonical service-facing API `get_object_info`
which validates parameters, delegates work to the Blender-side
implementation in `services.addon.objects`, and normalizes the response
to the standard service schema.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..services.addon.objects import get_object_info as _addon_get_object_info

logger = logging.getLogger(__name__)


def get_object_info(params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Service-facing get_object_info.

    Expects params: {"name": <str>}

    Returns: {"status":"success","object": {...}} or
             {"status":"error","message": ...}
    """
    name = None
    if isinstance(params, dict):
        n = params.get("name")
        if isinstance(n, str) and n:
            name = n

    if not name:
        return {"status": "error", "message": "missing or invalid 'name'"}

    try:
        addon_resp = _addon_get_object_info(name)
    except Exception as e:
        logger.exception("addon get_object_info raised")
        return {"status": "error", "message": str(e)}

    if isinstance(addon_resp, dict) and "error" in addon_resp:
        return {"status": "error", "message": addon_resp.get("error")}

    # success path: assume addon returned object info dict
    return {"status": "success", "object": addon_resp}


__all__ = ["get_object_info"]
