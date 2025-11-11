from typing import Any, List, Tuple, cast

import requests

from blender_mcp.hyper3d import (
    create_rodin_job_fal_ai,
    create_rodin_job_main_site,
    import_generated_asset_fal_ai,
)


class _FakeResp:
    def __init__(self, json_data: Any = None, status: int = 200) -> None:
        self._json: Any = json_data if json_data is not None else {}
        self.status_code = status

    def json(self) -> Any:
        return self._json


class FakeSession:
    def __init__(self, json_data: Any = None) -> None:
        self.posts: List[Tuple[str, Any]] = []
        self._json = json_data

    def post(self, url: str, **kwargs: Any) -> _FakeResp:
        self.posts.append((url, kwargs))
        return _FakeResp(json_data=self._json or {"id": "job-1"}, status=200)

    def get(self, url: str, **kwargs: Any) -> _FakeResp:
        # For import_generated_asset_fal_ai the session.get should return metadata
        return _FakeResp(json_data=self._json or {}, status=200)


def test_create_rodin_job_fal_ai_injected_session() -> None:
    fake = FakeSession(json_data={"job": "ok"})
    res = create_rodin_job_fal_ai("key", text_prompt="hello", session=cast(requests.Session, fake))
    assert isinstance(res, dict)


def test_import_generated_asset_fal_ai_injected_session() -> None:
    # Simulate the metadata endpoint returning a model url
    fake_json = {"model_mesh": {"url": "https://example.com/model.glb"}}
    fake = FakeSession(json_data=fake_json)
    res = import_generated_asset_fal_ai("key", "rid", "name", session=cast(requests.Session, fake))
    assert isinstance(res, dict)


def test_create_rodin_job_main_site_uses_session() -> None:
    sess = FakeSession()
    res = create_rodin_job_main_site(api_key="k", text_prompt="hi", images=None, session=cast(requests.Session, sess))
    assert isinstance(res, dict)
    assert res.get("id") == "job-1"
    assert len(sess.posts) == 1
