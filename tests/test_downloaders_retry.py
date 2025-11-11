import pytest
import requests

from blender_mcp import downloaders


def test_download_bytes_retries_success(monkeypatch):
    calls = {"n": 0}

    class GoodResp:
        status_code = 200

        def raise_for_status(self):
            return None

        content = b"OK"

    def fake_get(url, timeout=None, headers=None):
        calls["n"] += 1
        if calls["n"] < 3:
            raise requests.exceptions.Timeout()
        return GoodResp()

    # Patch sleep to avoid test delay, and requests.get to simulate timeouts
    monkeypatch.setattr(downloaders, "time", type("T", (), {"sleep": lambda *_: None}))
    monkeypatch.setattr(downloaders.requests, "get", fake_get)

    res = downloaders.download_bytes("http://example.com/a.bin", max_retries=4, backoff_factor=0.01)
    assert res == b"OK"
    assert calls["n"] == 3


def test_download_bytes_uses_session(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.called = 0

        def get(self, url, timeout=None, headers=None):
            self.called += 1

            class R:
                status_code = 200

                def raise_for_status(self):
                    return None

                content = b"S"

            return R()

    session = FakeSession()
    res = downloaders.download_bytes("http://example.com/s", session=session)
    assert res == b"S"
    assert session.called == 1


def test_download_bytes_no_retry_on_4xx(monkeypatch):
    calls = {"n": 0}

    class Resp404:
        status_code = 404

        def raise_for_status(self):
            e = requests.exceptions.HTTPError("404")
            # attach response so downloaders can detect 4xx and avoid retries
            e.response = self
            raise e

    def fake_get(url, timeout=None, headers=None):
        calls["n"] += 1
        return Resp404()

    monkeypatch.setattr(downloaders.requests, "get", fake_get)
    # Patch sleep to avoid delay if retry attempted
    monkeypatch.setattr(downloaders, "time", type("T", (), {"sleep": lambda *_: None}))

    with pytest.raises(requests.exceptions.HTTPError):
        downloaders.download_bytes("http://example.com/notfound", max_retries=3, backoff_factor=0.01)

    # Should not retry on 4xx: only one call
    assert calls["n"] == 1
