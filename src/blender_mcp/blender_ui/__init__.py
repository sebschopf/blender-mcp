"""BlenderMCP UI package façade.

This package contains the split UI pieces (props, operators, panel) and
re-exports a compatibility-friendly API so existing imports of
`blender_mcp.blender_ui` continue to work.
"""

from typing import Iterable, Optional

# Keep the package import-safe: defer importing `bpy` and submodules until
# runtime functions are called. Some test modules import package-level
# façades (like `blender_mcp.addon_handlers`) during collection and must not
# fail when `bpy` is not available.

_props = None
_operators = None
_panel = None


def _load_submodules() -> None:
    """Lazily import submodules into package globals.

    Safe to call multiple times; imports are cached by Python.
    """
    global _props, _operators, _panel
    if _props is None:
        from . import props as _p

        _props = _p
    if _operators is None:
        from . import operators as _o

        _operators = _o
    if _panel is None:
        from . import panel as _pa

        _panel = _pa


def _classes() -> Iterable[type]:
    _load_submodules()
    # Re-export classes at package level for backward compatibility. Use
    # attributes from submodules rather than importing them at top-level.
    try:
        return (
            _panel.BLENDERMCP_PT_Panel,
            _operators.BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey,
            _operators.BLENDERMCP_OT_StartServer,
            _operators.BLENDERMCP_OT_StopServer,
            _operators.BLENDERMCP_OT_ApplyRemoteExecSetting,
            # AddonPreferences is defined dynamically inside register()
        )
    except Exception:
        # If submodules are not available (import error), return empty tuple
        return ()


# If `bpy` is already present in sys.modules (tests may inject a fake),
# eagerly load submodules and expose the historical module-level names so
# `importlib.import_module('blender_mcp.blender_ui')` yields the same
# attributes consumers expect.
try:
    import sys

    if "bpy" in sys.modules:
        _load_submodules()
        try:
            BLENDERMCP_PT_Panel = _panel.BLENDERMCP_PT_Panel
            BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey = _operators.BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey
            BLENDERMCP_OT_StartServer = _operators.BLENDERMCP_OT_StartServer
            BLENDERMCP_OT_StopServer = _operators.BLENDERMCP_OT_StopServer
            BLENDERMCP_OT_ApplyRemoteExecSetting = _operators.BLENDERMCP_OT_ApplyRemoteExecSetting
        except Exception:
            # best-effort; leave module-level names unset if something fails
            pass
except Exception:
    pass


def _get_addon_preferences_class():
    """Return a AddonPreferences subclass when `bpy` is available.

    This is created on demand so importing the package remains safe when
    `bpy` is absent during test collection.
    """
    try:
        import bpy

        _AddonPrefsBase = getattr(bpy.types, "AddonPreferences", object)

        class BLENDERMCP_AddonPreferences(_AddonPrefsBase):
            bl_idname = "blender_mcp"

            allow_ui_start_server = bpy.props.BoolProperty(
                name="Allow UI to start external MCP server",
                description="If enabled, the Start button in the addon UI may launch an external MCP process",
                default=True,
            )

            def draw(self, context):
                try:
                    layout = self.layout
                    layout.label(text="BlenderMCP preferences")
                    layout.prop(self, "allow_ui_start_server")
                except Exception:
                    pass

        return BLENDERMCP_AddonPreferences
    except Exception:
        return None


def register() -> None:
    """Register UI classes and scene properties."""
    _load_submodules()
    # create AddonPreferences class dynamically (requires bpy)
    AddonPrefs = _get_addon_preferences_class()
    classes = list(_classes())
    if AddonPrefs is not None:
        classes.append(AddonPrefs)

    # register scene properties and classes (will raise if bpy missing)
    _props._register_scene_properties()
    try:
        import bpy

        for cls in classes:
            try:
                bpy.utils.register_class(cls)
            except Exception:
                pass
    except Exception:
        # If bpy is not available, registration is a no-op in this import-safe
        # façade; callers in Blender should call register() when bpy is present.
        pass

    print("BlenderMCP addon registered (package façade)")


def __getattr__(name: str):
    """Lazy attribute loader for legacy module-level symbols.

    This avoids importing `bpy` at package import time while still
    exposing the historical names when callers request them (tests often
    import the package and then access these attributes).
    """
    legacy_names = {
        "BLENDERMCP_PT_Panel",
        "BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey",
        "BLENDERMCP_OT_StartServer",
        "BLENDERMCP_OT_StopServer",
        "BLENDERMCP_OT_ApplyRemoteExecSetting",
    }
    if name in legacy_names:
        _load_submodules()
        # search in known submodules
        for mod in (_panel, _operators):
            if mod is None:
                continue
            if hasattr(mod, name):
                return getattr(mod, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    base = set(globals().keys())
    base.update([
        "BLENDERMCP_PT_Panel",
        "BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey",
        "BLENDERMCP_OT_StartServer",
        "BLENDERMCP_OT_StopServer",
        "BLENDERMCP_OT_ApplyRemoteExecSetting",
    ])
    return sorted(base)


def unregister() -> None:
    """Unregister UI classes and scene properties."""
    _load_submodules()
    AddonPrefs = _get_addon_preferences_class()
    classes = list(_classes())
    if AddonPrefs is not None:
        classes.append(AddonPrefs)

    try:
        import bpy

        for cls in classes:
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass
    except Exception:
        # No-op if bpy not present
        pass

    _props._unregister_scene_properties()
    print("BlenderMCP addon unregistered (package façade)")
