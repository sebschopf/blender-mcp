from __future__ import annotations

import socket
import threading
import time

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


def test_response_receiver_large_message_exceeds() -> None:
    # Start a server that sends a single large message without delimiter
    large = b"{" + b"\"x\":" + b"0" * (1024 * 1024) + b"}\n"

    def server_large() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", 0))
            srv.listen(1)
            server_large.port = srv.getsockname()[1]  # type: ignore[attr-defined]
            try:
                conn, _ = srv.accept()
            except Exception:
                return
            with conn:
                # send a payload larger than the receiver max (we'll set a low max)
                try:
                    conn.sendall(large)
                except Exception:
                    return

    th = threading.Thread(target=server_large, daemon=True)
    th.start()
    start = time.time()
    while not hasattr(server_large, "port"):
        if time.time() - start > 2.0:
            raise RuntimeError("server failed to start")
        time.sleep(0.01)

    port = server_large.port  # type: ignore[attr-defined]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", port))
        # small max_message_size to trigger the guard
        recv = ResponseReceiver(max_message_size=1024)
        with pytest.raises(ConnectionError):
            recv.receive_one(s, buffer_size=512, timeout=1.0)


def test_response_receiver_multi_message_single_recv() -> None:
    # server sends two JSON messages in one send
    combined = b'{"a":1}\n{"b":2}\n'

    def server_combo() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", 0))
            srv.listen(1)
            server_combo.port = srv.getsockname()[1]  # type: ignore[attr-defined]
            try:
                conn, _ = srv.accept()
            except Exception:
                return
            with conn:
                try:
                    conn.sendall(combined)
                except Exception:
                    return

    th = threading.Thread(target=server_combo, daemon=True)
    th.start()
    start = time.time()
    while not hasattr(server_combo, "port"):
        if time.time() - start > 2.0:
            raise RuntimeError("server failed to start")
        time.sleep(0.01)

    port = server_combo.port  # type: ignore[attr-defined]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", port))
        recv = ResponseReceiver()
        first = recv.receive_one(s, buffer_size=1024, timeout=1.0)
        assert first == {"a": 1}
        # second message should be read next from same socket
        second = recv.receive_one(s, buffer_size=1024, timeout=1.0)
        assert second == {"b": 2}


def test_response_receiver_invalid_json_chunk_raises() -> None:
    # server sends an invalid JSON line
    bad = b'not-a-json\n'

    def server_bad() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", 0))
            srv.listen(1)
            server_bad.port = srv.getsockname()[1]  # type: ignore[attr-defined]
            try:
                conn, _ = srv.accept()
            except Exception:
                return
            with conn:
                try:
                    conn.sendall(bad)
                except Exception:
                    return

    th = threading.Thread(target=server_bad, daemon=True)
    th.start()
    start = time.time()
    while not hasattr(server_bad, "port"):
        if time.time() - start > 2.0:
            raise RuntimeError("server failed to start")
        time.sleep(0.01)

    port = server_bad.port  # type: ignore[attr-defined]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", port))
        recv = ResponseReceiver()
        with pytest.raises(ValueError):
            recv.receive_one(s, buffer_size=1024, timeout=1.0)
