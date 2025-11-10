"""Service-facing wrapper for texture operations.

Validates params, delegates to `services.addon.textures.set_texture`
and normalizes responses to the canonical service schema.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .addon.textures import set_texture as _addon_set_texture

logger = logging.getLogger(__name__)


def set_texture(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service wrapper for applying a texture to an object.

    Expects params: {"object_name": str, "texture_id": str}
    Returns: {"status":"success","result":{"material": <name>}} or
             {"status":"error","message": <str>} or {"status":"success","result":{"images": [...]}}
    """
    if not params:
        return {"status": "error", "message": "missing params"}

    object_name = params.get("object_name")
    texture_id = params.get("texture_id")
    if not object_name or not isinstance(object_name, str):
        return {"status": "error", "message": "missing or invalid 'object_name'"}
    if not texture_id or not isinstance(texture_id, str):
        return {"status": "error", "message": "missing or invalid 'texture_id'"}

    try:
        addon_resp = _addon_set_texture(object_name, texture_id)
    except Exception as e:
        logger.exception("addon set_texture failed")
        return {"status": "error", "message": str(e)}

    if addon_resp.get("error"):
        return {"status": "error", "message": addon_resp.get("error")}

    # success cases
    if addon_resp.get("success"):
        return {"status": "success", "result": {"material": addon_resp.get("material")}}

    if "images" in addon_resp:
        return {"status": "success", "result": {"images": addon_resp.get("images")}}

    return {"status": "error", "message": "unexpected addon response"}


__all__ = ["set_texture"]
