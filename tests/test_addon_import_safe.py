def test_addon_import_is_import_safe():
    """Importing `addon.py` must not require Blender (no top-level `bpy` imports).

    The addon should remain import-safe so tests and CI can import it without
    Blender present. If this environment already provides `bpy` (running inside
    Blender), skip the strict absence assertion.
    """
    import importlib
    import sys

    import pytest

    mod = importlib.import_module("addon")
    assert hasattr(mod, "register")

    # If running inside Blender, don't assert absence of `bpy`.
    if "bpy" in sys.modules:
        pytest.skip("bpy present in environment; skip import-safety assertion")

    # Importing the addon must not have imported bpy at top-level
    assert "bpy" not in sys.modules

    # Calling register/unregister must not raise in headless CI
    mod.register()
    if hasattr(mod, "unregister"):
        mod.unregister()
