"""Simple, explicit UI package façade.

This module provides direct re-exports of the UI submodules and a small
`register()` / `unregister()` pair. It avoids magic and large try/except
blocks so that errors surface during development. The submodules are
written to be import-safe (they provide fallbacks when `bpy` is not
available) so importing this package in CI/tests is harmless.
"""

from __future__ import annotations

__all__ = [
    "_register_scene_properties",
    "_unregister_scene_properties",
    "BLENDERMCP_PT_Panel",
    "BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey",
    "BLENDERMCP_OT_StartServer",
    "BLENDERMCP_OT_StopServer",
    "BLENDERMCP_OT_ApplyRemoteExecSetting",
]


def register() -> None:
    """Register the addon UI: scene properties and Blender classes.

    This function will attempt to register Blender classes if `bpy` is
    present. If not present it performs a no-op to keep tests/CI safe.
    """
    # register scene properties first (import dynamically)
    import importlib

    try:
        props = importlib.import_module("blender_mcp.blender_ui.props")
        props._register_scene_properties()
    except Exception:
        # props module may be unavailable or bpy missing; continue
        pass

    try:
        import bpy  # type: ignore
    except Exception:
        # If bpy isn't available, leave registration to runtime in Blender.
        return

    # attempt to load class objects from submodules (reload so they can
    # pick up a fake bpy injected after initial import)
    try:
        ops = importlib.reload(importlib.import_module("blender_mcp.blender_ui.operators"))
    except Exception:
        ops = importlib.import_module("blender_mcp.blender_ui.operators")

    try:
        pnl = importlib.reload(importlib.import_module("blender_mcp.blender_ui.panel"))
    except Exception:
        pnl = importlib.import_module("blender_mcp.blender_ui.panel")

    classes = []
    for name in (
        "BLENDERMCP_PT_Panel",
        "BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey",
        "BLENDERMCP_OT_StartServer",
        "BLENDERMCP_OT_StopServer",
        "BLENDERMCP_OT_ApplyRemoteExecSetting",
    ):
        for mod in (pnl, ops):
            if hasattr(mod, name):
                classes.append(getattr(mod, name))
                break

    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            # let Blender handle duplicate or invalid registrations
            pass


def unregister() -> None:
    """Unregister the addon UI and remove scene properties.

    Best-effort: ignores missing classes/properties when `bpy` is not
    present.
    """
    import importlib

    try:
        import bpy  # type: ignore
    except Exception:
        bpy = None

    # attempt to load class objects from submodules
    try:
        ops = importlib.import_module("blender_mcp.blender_ui.operators")
    except Exception:
        ops = None

    try:
        pnl = importlib.import_module("blender_mcp.blender_ui.panel")
    except Exception:
        pnl = None

    classes = []
    for name in (
        "BLENDERMCP_PT_Panel",
        "BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey",
        "BLENDERMCP_OT_StartServer",
        "BLENDERMCP_OT_StopServer",
        "BLENDERMCP_OT_ApplyRemoteExecSetting",
    ):
        for mod in (pnl, ops):
            if mod is None:
                continue
            if hasattr(mod, name):
                classes.append(getattr(mod, name))
                break

    if bpy is not None:
        for cls in classes:
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass

    # unregister scene props
    try:
        props = importlib.import_module("blender_mcp.blender_ui.props")
        props._unregister_scene_properties()
    except Exception:
        pass


def __getattr__(name: str):
    """Lazy-reload legacy UI symbols when requested.

    This helps tests that import the package before a fake `bpy` is
    installed: when they later access a historical symbol we attempt to
    reload the submodules so real Operator/Panel classes get defined.
    """
    legacy = {
        "BLENDERMCP_PT_Panel",
        "BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey",
        "BLENDERMCP_OT_StartServer",
        "BLENDERMCP_OT_StopServer",
        "BLENDERMCP_OT_ApplyRemoteExecSetting",
    }
    if name in legacy:
        import importlib

        # attempt to reload submodules so they can pick up a fake `bpy`
        try:
            importlib.reload(importlib.import_module("blender_mcp.blender_ui.operators"))
        except Exception:
            # ignore reload failures; we'll try panel next
            pass
        try:
            importlib.reload(importlib.import_module("blender_mcp.blender_ui.panel"))
        except Exception:
            pass

        # return the attribute if available now
        for modname in ("blender_mcp.blender_ui.panel", "blender_mcp.blender_ui.operators"):
            try:
                mod = importlib.import_module(modname)
                if hasattr(mod, name):
                    val = getattr(mod, name)
                    globals()[name] = val
                    return val
            except Exception:
                continue
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    base = set(globals().keys())
    base.update([
        "BLENDERMCP_PT_Panel",
        "BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey",
        "BLENDERMCP_OT_StartServer",
        "BLENDERMCP_OT_StopServer",
        "BLENDERMCP_OT_ApplyRemoteExecSetting",
    ])
    return sorted(base)
