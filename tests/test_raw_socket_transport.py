from __future__ import annotations

import json
import socket
import threading
import time
from typing import Any

import pytest

from blender_mcp.services.connection.transport import RawSocketTransport


def _start_echo_server(host: str = "127.0.0.1", max_connections: int = 1) -> tuple[int, threading.Thread, threading.Event]:
    """Start a simple TCP echo server that reads a JSON line and replies with a JSON payload.

    The server accepts up to `max_connections` sequential connections and then exits.

    Returns (port, thread, stop_event).
    """

    stop_event = threading.Event()

    def server() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((host, 0))
            srv.listen(5)
            port = srv.getsockname()[1]
            # communicate port back via closure attribute
            server.port = port  # type: ignore[attr-defined]

            srv.settimeout(5.0)
            accepted = 0
            while accepted < max_connections:
                try:
                    conn, _ = srv.accept()
                except Exception:
                    break
                accepted += 1
                with conn:
                    conn.settimeout(5.0)
                    data = b""
                    try:
                        while not data.endswith(b"\n"):
                            chunk = conn.recv(4096)
                            if not chunk:
                                break
                            data += chunk
                    except Exception:
                        continue

                    # parse received JSON and send a fixed response
                    try:
                        obj = json.loads(data.decode("utf-8"))
                    except Exception:
                        resp = {"error": "bad-json"}
                    else:
                        resp = {"echo": obj}

                    resp_data = (json.dumps(resp) + "\n").encode("utf-8")
                    try:
                        conn.sendall(resp_data)
                    except Exception:
                        continue

    th = threading.Thread(target=server, daemon=True)
    th.start()

    # Wait for server thread to bind and set server.port
    start = time.time()
    while not hasattr(server, "port"):
        if time.time() - start > 2.0:
            raise RuntimeError("Server failed to start")
        time.sleep(0.01)

    return server.port, th, stop_event


def test_raw_socket_transport_send_and_receive() -> None:
    port, thread, _ = _start_echo_server()

    tr = RawSocketTransport("127.0.0.1", port)

    assert tr.connect() is True

    res = tr.send_command("ping", {"n": 1})

    # The server echoes the parsed JSON under key 'echo'
    assert isinstance(res, dict)
    assert "echo" in res
    assert res["echo"]["type"] == "ping"
    assert res["echo"]["params"] == {"n": 1}

    tr.disconnect()


def test_raw_socket_transport_retry() -> None:
    # Start server that accepts two sequential connections
    port, thread, _ = _start_echo_server(max_connections=2)

    # socket factory that returns a wrapper which fails on first sendall
    # shared state so only the very first send across all sockets fails
    shared_failed: list[bool] = [False]

    class FlakySocket:
        def __init__(self, shared: list[bool]) -> None:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._shared = shared

        def connect(self, addr: tuple[str, int]) -> None:
            return self._sock.connect(addr)

        def settimeout(self, t: float) -> None:
            try:
                self._sock.settimeout(t)
            except Exception:
                pass

        def sendall(self, data: bytes) -> None:
            if not self._shared[0]:
                self._shared[0] = True
                raise OSError("simulated send failure")
            return self._sock.sendall(data)

        def recv(self, buf: int) -> bytes:
            return self._sock.recv(buf)

        def close(self) -> None:
            try:
                self._sock.close()
            except Exception:
                pass

    def factory() -> Any:
        return FlakySocket(shared_failed)

    tr = RawSocketTransport("127.0.0.1", port, socket_factory=factory, retries=2, backoff=0.01)

    assert tr.connect() is True

    res = tr.send_command("ping", {"n": 2})

    assert isinstance(res, dict)
    assert "echo" in res
    assert res["echo"]["type"] == "ping"
    assert res["echo"]["params"] == {"n": 2}

    tr.disconnect()
