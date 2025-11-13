import importlib
import sys
import warnings

import pytest


@pytest.mark.parametrize(
    "module_name, expected_substring",
    [
        ("blender_mcp.simple_dispatcher", "deprecated; use blender_mcp.dispatchers"),
        (
            "blender_mcp.command_dispatcher",
            "deprecated; use blender_mcp.dispatchers.command_dispatcher",
        ),
        ("blender_mcp.server_shim", "deprecated; use blender_mcp.servers.shim"),
        (
            "blender_mcp.server",
            "compatibility façade; import from blender_mcp.servers.server",
        ),
        (
            "blender_mcp.connection_core",
            "deprecated; migrate to blender_mcp.services.connection.network_core",
        ),
    ],
)
def test_legacy_modules_emit_deprecation_warning(module_name: str, expected_substring: str) -> None:
    # Ensure a fresh import so the warning triggers
    if module_name in sys.modules:
        del sys.modules[module_name]
    importlib.invalidate_caches()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        mod = importlib.import_module(module_name)
        assert mod is not None
        # Find the first DeprecationWarning for this import
        msgs = [str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)]
        assert any(expected_substring in m for m in msgs), f"No expected DeprecationWarning for {module_name}: {msgs}"
