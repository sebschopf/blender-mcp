from typing import Any, List, Tuple, cast
import requests

from blender_mcp.sketchfab import get_sketchfab_status, search_models


class _FakeResp:
    def __init__(self, json_data: Any = None, status: int = 200) -> None:
        self._json: Any = json_data if json_data is not None else {}
        self.status_code = status

    def json(self) -> Any:
        return self._json


class FakeSession:
    def __init__(self, json_data: Any = None) -> None:
        self.calls: List[Tuple[str, Any]] = []
        self._json = json_data

    def get(self, url: str, **kwargs: Any) -> _FakeResp:
        self.calls.append((url, kwargs))
        return _FakeResp(json_data=self._json or {"username": "tester"}, status=200)


def test_get_sketchfab_status_with_session() -> None:
    sess = FakeSession()
    result = get_sketchfab_status(api_key="fake-key", session=cast(requests.Session, sess))
    assert result["enabled"] is True
    assert "Logged in as: tester" in result["message"]
    assert len(sess.calls) == 1


def test_search_models_injected_session() -> None:
    data = {"results": [{"uid": "1", "name": "m"}], "count": 1}
    fake = FakeSession(json_data=data)
    out = search_models("k", "chair", session=cast(requests.Session, fake))
    assert isinstance(out, dict)

