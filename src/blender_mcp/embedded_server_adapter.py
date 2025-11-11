"""Top-level compatibility façade for the embedded server adapter.

Implementation has been moved to `blender_mcp.servers.embedded_adapter`.
This façade keeps existing imports stable.
"""

from .servers.embedded_adapter import start_server_process, stop_server_process, is_running  # noqa: F401

__all__ = ["start_server_process", "stop_server_process", "is_running"]
