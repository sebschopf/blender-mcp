from __future__ import annotations

from typing import Any, Dict, Optional

from . import polyhaven as _polyhaven


def get_polyhaven_status_service(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Service: report PolyHaven availability.

    Performs a lightweight probe via `fetch_categories` when possible.
    Never raises for normal conditions; network problems return enabled=False.
    """
    try:
        _polyhaven.fetch_categories(asset_type="hdris")
        return {
            "status": "success",
            "result": {
                "enabled": True,
                "message": "PolyHaven endpoints available (network probe ok)",
            },
        }
    except Exception:
        # Do not raise: status endpoints should be non-fatal
        return {
            "status": "success",
            "result": {
                "enabled": False,
                "message": "PolyHaven may be unreachable (probe failed)",
            },
        }


__all__ = ["get_polyhaven_status_service"]
