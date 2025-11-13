"""Service-facing wrapper for texture operations.

Exceptions-first canonical service that validates params, delegates to
`services.addon.textures.set_texture` and normalizes responses.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from blender_mcp.errors import HandlerError, InvalidParamsError

from .addon.textures import set_texture as _addon_set_texture

logger = logging.getLogger(__name__)


def set_texture(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service wrapper for applying a texture to an object.

    Expects params: {"object_name": str, "texture_id": str}
    Returns success dict with either {material} or {images}.

    Raises InvalidParamsError for bad input and HandlerError for addon failures.
    """
    p = params or {}
    object_name = p.get("object_name")
    texture_id = p.get("texture_id")
    if not isinstance(object_name, str) or not object_name:
        raise InvalidParamsError("missing or invalid 'object_name'")
    if not isinstance(texture_id, str) or not texture_id:
        raise InvalidParamsError("missing or invalid 'texture_id'")

    try:
        addon_resp = _addon_set_texture(object_name, texture_id)
    except Exception as e:  # pragma: no cover - defensive boundary
        logger.exception("addon set_texture failed")
        raise HandlerError("set_texture", e)

    if addon_resp.get("error"):
        raise HandlerError("set_texture", Exception(str(addon_resp.get("error"))))

    if addon_resp.get("success"):
        return {"status": "success", "result": {"material": addon_resp.get("material")}}

    if "images" in addon_resp:
        return {"status": "success", "result": {"images": addon_resp.get("images")}}

    raise HandlerError("set_texture", Exception("unexpected addon response"))


__all__ = ["set_texture"]
