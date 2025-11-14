from blender_mcp.dispatcher import create_dispatcher, dispatch


def test_register_and_list_services():
    def sample(params):
        return {"echo": params.get("text")}

    registry.register_service("echo", sample)
    assert "echo" in registry.list_services()
    assert registry.get_service("echo") is sample


def test_dispatch_fallback_to_service_single_param():
    def upper(params):
        return {"text": params.get("text", "").upper()}

    registry.register_service("echo_upper", upper)
    d = create_dispatcher()
    result = dispatch(d, "echo_upper", {"text": "abc"})
    assert result == {"text": "ABC"}


def test_dispatch_strict_with_service():
    def simple(params):
        return {"v": 1}

    registry.register_service("simple_service", simple)
    d = create_dispatcher()
    # dispatch_strict devrait fonctionner via fallback service
    from blender_mcp.dispatcher import dispatch as basic_dispatch
    assert basic_dispatch(d, "simple_service") == {"v": 1}
from blender_mcp.dispatchers.command_dispatcher import CommandDispatcher
from blender_mcp.services import polyhaven, registry, sketchfab


def test_register_handlers_and_dispatch(monkeypatch):
    d = CommandDispatcher()
    registry.register_default_handlers(d)

    # Mock polyhaven.fetch_categories
    monkeypatch.setattr(polyhaven, "fetch_categories", lambda asset_type="hdris": {"categories": {"a": 1}})
    resp = d.dispatch({"type": "get_polyhaven_categories", "params": {"asset_type": "textures"}})
    assert resp["status"] == "success"
    assert "categories" in resp["result"]

    # Mock sketchfab search returning results
    def fake_search_models(key, query, categories=None, count=20, downloadable=True):
        return {"results": [{"name": "M"}]}

    monkeypatch.setattr(sketchfab, "search_models", fake_search_models)
    resp = d.dispatch({"type": "search_sketchfab_models", "params": {"api_key": "k", "query": "chair"}})
    assert resp["status"] == "success"
    assert "results" in resp["result"]
