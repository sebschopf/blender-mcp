from blender_mcp.command_dispatcher import CommandDispatcher
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
