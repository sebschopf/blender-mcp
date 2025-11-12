"""Service to capture and encode the viewport as an image.

Design:
- Lazy import `bpy`. If `bpy` is not available, return an error dict.
- Expect a minimal helper API in `bpy` for the porting stage: if `bpy` exposes
  `capture_viewport_bytes()` return raw PNG bytes. This keeps the service
  small and testable: tests can inject a fake `bpy` with that function.
- The service returns a dict {status, image_base64} on success.
"""

from __future__ import annotations

import base64
import importlib
import logging
from typing import Any, Dict, Optional

from blender_mcp.errors import ExternalServiceError, HandlerError

logger = logging.getLogger(__name__)


def get_viewport_screenshot(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Capture the viewport and return a base64-encoded PNG string.

    params (optional):
      - format: str, optional (e.g. 'png') — currently informational only

    The function tries to lazily import `bpy` and call a small helper
    `bpy.capture_viewport_bytes()` that should return raw PNG bytes. If
    this helper is not available, the function returns an error dict so
    the caller can fall back or report to the user.
    """
    try:
        bpy = importlib.import_module("bpy")
    except Exception:
        logger.debug("bpy not available when calling get_viewport_screenshot")
        raise ExternalServiceError("Blender (bpy) not available")

    # attempt to use a small well-defined helper implemented in the addon
    capture = getattr(bpy, "capture_viewport_bytes", None)
    if capture is None or not callable(capture):
        logger.debug("bpy.capture_viewport_bytes not available")
        raise ExternalServiceError("capture_viewport_bytes not available on bpy")

    try:
        img_bytes = capture()
        if not isinstance(img_bytes, (bytes, bytearray)):
            raise ExternalServiceError("capture returned non-bytes")
        b64 = base64.b64encode(bytes(img_bytes)).decode("ascii")
        return {"status": "success", "image_base64": b64}
    except ExternalServiceError:
        raise
    except Exception as e:
        logger.exception("error capturing viewport")
        # wrap handler exceptions for adapters
        raise HandlerError("get_viewport_screenshot", e)


__all__ = ["get_viewport_screenshot"]
