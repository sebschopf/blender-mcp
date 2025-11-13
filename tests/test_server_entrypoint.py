import importlib


def test_server_façade_exports():
    mod = importlib.import_module("blender_mcp.server")
    # expected facade names
    assert hasattr(mod, "BlenderMCPServer") or hasattr(mod, "_process_bbox")
    # the facade should at least define __all__ exposing known names
    assert hasattr(mod, "__all__")
