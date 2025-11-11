def test_search_models_uses_provided_session(monkeypatch):
    from blender_mcp import sketchfab

    class FakeResp:
        status_code = 200

        def json(self):
            return {"results": []}

    class FakeSession:
        def __init__(self):
            self.calls = []

        def get(self, url, headers=None, params=None, timeout=None):
            self.calls.append((url, headers, params, timeout))
            return FakeResp()

    s = FakeSession()
    res = sketchfab.search_models("fakekey", "chair", session=s)
    assert isinstance(res, dict)
    assert len(s.calls) == 1
    assert s.calls[0][0].endswith("/search")


def test_get_status_uses_session(monkeypatch):
    from blender_mcp import sketchfab

    class FakeResp:
        status_code = 200

        def json(self):
            return {"username": "tester"}

    class FakeSession:
        def get(self, url, headers=None, timeout=None):
            return FakeResp()

    s = FakeSession()
    st = sketchfab.get_sketchfab_status("k", session=s)
    assert st["enabled"] is True
    assert "Logged in as" in st["message"]
