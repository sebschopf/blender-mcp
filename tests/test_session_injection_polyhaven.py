from typing import Any, List, Tuple, cast

import requests

from blender_mcp.polyhaven import fetch_categories, fetch_files_data


class _FakeResp:
    def __init__(self, json_data: Any = None, status: int = 200) -> None:
        self._json: Any = json_data if json_data is not None else {}
        self.status_code = status

    def json(self) -> Any:
        return self._json


class FakeSession:
    def __init__(self) -> None:
        self.calls: List[Tuple[str, Any]] = []

    def get(self, url: str, **kwargs: Any) -> _FakeResp:
        self.calls.append((url, kwargs))
        return _FakeResp(json_data={"files": {"fileA": {}}}, status=200)


def test_fetch_categories_with_injected_session() -> None:
    fake = FakeSession()
    # fetch_categories expects a session-like object with .get
    res = fetch_categories("hdris", session=cast(requests.Session, fake))
    assert isinstance(res, dict)


def test_fetch_files_data_uses_injected_session() -> None:
    sess = FakeSession()
    res = fetch_files_data("asset-id-123", session=cast(requests.Session, sess))
    assert isinstance(res, dict)
    assert res.get("files") == {"fileA": {}}
    assert len(sess.calls) == 1
