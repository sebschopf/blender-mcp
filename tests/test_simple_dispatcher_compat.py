def test_simple_dispatcher_compat_import_and_basic():
    # import via old path
    from blender_mcp.simple_dispatcher import Dispatcher as SimpleDispatcher
    from blender_mcp.dispatchers.dispatcher import Dispatcher as CanonicalDispatcher

    sd = SimpleDispatcher()
    cd = CanonicalDispatcher()

    def h(p):
        return p.get("x", 0)

    sd.register("h", h)
    cd.register("h", h)

    assert sd.dispatch("h", {"x": 5}) == 5
    assert cd.dispatch("h", {"x": 7}) == 7
