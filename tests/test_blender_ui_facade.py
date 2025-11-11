import importlib
import sys
import types


def test_lazy_facade_exposes_legacy_names():
    """Ensure `blender_mcp.blender_ui` exposes legacy module-level
    symbols when a fake `bpy` is injected (prevents regressions).
    """
    # Create a minimal fake `bpy` that provides the attributes submodules expect
    fake_bpy = types.SimpleNamespace()
    fake_types = types.SimpleNamespace(Operator=type, Panel=type, AddonPreferences=object)
    fake_bpy.types = fake_types

    # minimal props module used by props/panel code
    props_mod = types.SimpleNamespace(
        IntProperty=lambda **kw: kw.get("default", 0),
        BoolProperty=lambda **kw: kw.get("default", False),
        EnumProperty=lambda **kw: kw.get("default", ""),
        StringProperty=lambda **kw: kw.get("default", ""),
    )

    # inject into sys.modules before importing package
    sys.modules["bpy"] = fake_bpy
    sys.modules["bpy.props"] = props_mod

    # Ensure a fresh import so our fake bpy is seen by the package loader
    for k in list(sys.modules):
        if k == "blender_mcp.blender_ui" or k.startswith("blender_mcp.blender_ui."):
            del sys.modules[k]

    m = importlib.import_module("blender_mcp.blender_ui")

    # legacy names expected to be accessible
    names = [
        "BLENDERMCP_PT_Panel",
        "BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey",
        "BLENDERMCP_OT_StartServer",
        "BLENDERMCP_OT_StopServer",
        "BLENDERMCP_OT_ApplyRemoteExecSetting",
    ]

    missing = [n for n in names if not hasattr(m, n)]
    assert not missing, f"Missing legacy symbols from facade: {missing}"
