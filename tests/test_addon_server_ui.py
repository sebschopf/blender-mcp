import importlib
import sys
import types


def make_fake_bpy():
    fake = types.ModuleType("bpy")

    # minimal props helpers returning defaults or simple callables
    class Props:
        @staticmethod
        def IntProperty(**kwargs):
            return kwargs.get("default", 0)

        @staticmethod
        def BoolProperty(**kwargs):
            return kwargs.get("default", False)

        @staticmethod
        def EnumProperty(**kwargs):
            return kwargs.get("default", "")

        @staticmethod
        def StringProperty(**kwargs):
            return kwargs.get("default", "")

    fake.props = Props()

    # minimal types with Operator and Panel base classes
    class Operator:
        def report(self, level, message):
            # mimic Blender operator reporting
            return None

    class Panel:
        pass

    fake.types = types.SimpleNamespace(Operator=Operator, Panel=Panel)

    # utils no-ops
    fake.utils = types.SimpleNamespace(register_class=lambda cls: None, unregister_class=lambda cls: None)

    # scene container used by the UI
    fake_scene = types.SimpleNamespace()
    fake_scene.blendermcp_port = 9876
    fake_scene.blendermcp_server_running = False
    fake_scene.blendermcp_server_pid = 0
    fake_scene.blendermcp_use_polyhaven = False
    fake_scene.blendermcp_use_hyper3d = False
    fake_scene.blendermcp_hyper3d_mode = "MAIN_SITE"
    fake_scene.blendermcp_hyper3d_api_key = ""
    fake_scene.blendermcp_use_sketchfab = False
    fake_scene.blendermcp_sketchfab_api_key = ""

    fake.context = types.SimpleNamespace(scene=fake_scene)

    # minimal preferences with addon prefs map used by the UI
    fake_pref = types.SimpleNamespace()
    fake_pref.addons = {"blender_mcp": types.SimpleNamespace(preferences=types.SimpleNamespace(allow_ui_start_server=True))}
    fake.preferences = fake_pref

    return fake


def test_start_stop_server_ui(monkeypatch):
    fake = make_fake_bpy()
    # ensure submodules like bpy.props are importable when blender_ui
    # does `from bpy.props import IntProperty`
    sys.modules["bpy"] = fake
    props_mod = types.SimpleNamespace(
        IntProperty=lambda **kw: kw.get("default", 0),
        BoolProperty=lambda **kw: kw.get("default", False),
        EnumProperty=lambda **kw: kw.get("default", ""),
        StringProperty=lambda **kw: kw.get("default", ""),
    )
    sys.modules["bpy.props"] = props_mod
    try:
        # monkeypatch the adapter to avoid launching real processes
        class DummyProc:
            pid = 4242

        def fake_start():
            return DummyProc()

        def fake_stop(p):
            return None

        # import the module under test after installing fake bpy
        mod = importlib.import_module("blender_mcp.blender_ui")
        # patch the adapter module in its package location
        monkeypatch.setattr("blender_mcp.embedded_server_adapter.start_server_process", fake_start)
        monkeypatch.setattr("blender_mcp.embedded_server_adapter.stop_server_process", fake_stop)

        # Create operator instances and call execute with a fake context
        start_op = mod.BLENDERMCP_OT_StartServer()
        res = start_op.execute(fake.context)
        assert res == {"FINISHED"}
        assert fake.context.scene.blendermcp_server_running is True
        assert fake.context.scene.blendermcp_server_pid == 4242

        stop_op = mod.BLENDERMCP_OT_StopServer()
        res2 = stop_op.execute(fake.context)
        assert res2 == {"FINISHED"}
        assert fake.context.scene.blendermcp_server_running is False
        assert fake.context.scene.blendermcp_server_pid == 0
    finally:
        del sys.modules["bpy"]
        del sys.modules["bpy.props"]
