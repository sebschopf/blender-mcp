"""Service wrapper for object information.

This module provides the canonical service-facing API `get_object_info`
which validates parameters, delegates work to the Blender-side
implementation in `services.addon.objects`, and normalizes the response
to the standard service schema.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from blender_mcp.errors import InvalidParamsError, ExternalServiceError, HandlerError
from .addon.objects import get_object_info as _addon_get_object_info

logger = logging.getLogger(__name__)


def _parse_name(params: Dict[str, Any] | None) -> Optional[str]:
    if not params:
        return None
    name = params.get("name")
    return name if isinstance(name, str) else None


def get_object_info(params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Service-facing get_object_info.

    Expects params: {"name": <str>}

    Returns: {"status":"success","object": {...}} or
             {"status":"error","message": ...}
    """
    name = _parse_name(params)
    if not name:
        raise InvalidParamsError("missing or invalid 'name'")

    try:
        addon_resp = _addon_get_object_info(name)
    except Exception as e:
        logger.exception("addon get_object_info failed")
        raise HandlerError("get_object_info", e)

    # If the addon returned an error dict, normalize it
    if isinstance(addon_resp, dict) and addon_resp.get("error"):
        msg = addon_resp.get("error") or ""
        if "bpy" in msg or "Blender" in msg:
            raise ExternalServiceError(msg)
        raise HandlerError("get_object_info", Exception(msg))

    # Expect addon to return object info dict on success
    if isinstance(addon_resp, dict):
        return {"status": "success", "object": addon_resp}

    # Fallback: unexpected shape
    raise HandlerError("get_object_info", Exception("unexpected addon response"))


__all__ = ["get_object_info"]
