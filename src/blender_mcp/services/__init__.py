"""Services package for Blender MCP.

Services are small, testable units that implement the behaviour of
individual endpoints. They must avoid importing Blender (`bpy`) at
module import time — use lazy imports inside functions.
"""

from .execute import execute_blender_code, send_command_over_network
from .scene import get_scene_info
from .screenshot import get_viewport_screenshot

__all__ = [
    "execute_blender_code",
    "send_command_over_network",
    "get_scene_info",
    "get_viewport_screenshot",
]
