from __future__ import annotations

import json
import socket
import threading
import time
from typing import Any

import pytest

from blender_mcp.services.connection.receiver import ResponseReceiver


def _start_fragmented_server(host: str = "127.0.0.1", fragments: list[bytes] | None = None, delay: float = 0.05):
    if fragments is None:
        fragments = [b'{"a": 1}\n']

    def server() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((host, 0))
            srv.listen(1)
            server.port = srv.getsockname()[1]  # type: ignore[attr-defined]
            srv.settimeout(5.0)
            try:
                conn, _ = srv.accept()
            except Exception:
                return
            with conn:
                for frag in fragments:
                    try:
                        conn.sendall(frag)
                    except Exception:
                        return
                    time.sleep(delay)

    th = threading.Thread(target=server, daemon=True)
    th.start()
    start = time.time()
    while not hasattr(server, "port"):
        if time.time() - start > 2.0:
            raise RuntimeError("server failed to start")
        time.sleep(0.01)
    return server.port, th


def test_response_receiver_reassembles_fragments() -> None:
    # send a JSON object split in two fragments
    fragments = [b'{"x": ', b'123}\n']
    port, _ = _start_fragmented_server(fragments=fragments, delay=0.02)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", port))
        recv = ResponseReceiver()
        obj = recv.receive_one(s, buffer_size=8, timeout=2.0)
        assert isinstance(obj, dict)
        assert obj.get("x") == 123


def test_response_receiver_timeout_raises() -> None:
    # server that doesn't send anything (client will hit timeout)
    def server_no_send() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", 0))
            srv.listen(1)
            server_no_send.port = srv.getsockname()[1]  # type: ignore[attr-defined]
            try:
                conn, _ = srv.accept()
            except Exception:
                return
            with conn:
                time.sleep(1.0)

    th = threading.Thread(target=server_no_send, daemon=True)
    th.start()
    start = time.time()
    while not hasattr(server_no_send, "port"):
        if time.time() - start > 2.0:
            raise RuntimeError("server failed to start")
        time.sleep(0.01)

    port = server_no_send.port  # type: ignore[attr-defined]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", port))
        recv = ResponseReceiver()
        with pytest.raises(Exception):
            # expect socket.timeout to be raised or bubbled up as Exception
            recv.receive_one(s, buffer_size=8, timeout=0.1)
