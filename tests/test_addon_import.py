def test_addon_importable():
    """Ensure the top-level `addon.py` module is importable and its
    register/unregister functions are callable without requiring Blender.
    """
    import importlib

    mod = importlib.import_module("addon")
    assert hasattr(mod, "register"), "addon module should expose register()"
    # Calling register/unregister should not raise in a headless/test environment
    mod.register()
    if hasattr(mod, "unregister"):
        mod.unregister()
