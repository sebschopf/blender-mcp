"""Archived copy of the top-level embedded_server_adapter façade.

Snapshot of `src/blender_mcp/embedded_server_adapter.py` kept for
historical reference.
"""

from .servers.embedded_adapter import is_running, start_server_process, stop_server_process  # noqa: F401

__all__ = ["start_server_process", "stop_server_process", "is_running"]
