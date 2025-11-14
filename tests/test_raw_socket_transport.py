from __future__ import annotations

import json
import socket
import threading
import time
from typing import Any

import pytest

from blender_mcp.services.connection.transport import RawSocketTransport


def _start_echo_server(host: str = "127.0.0.1") -> tuple[int, threading.Thread, threading.Event]:
    """Start a simple TCP echo server that reads a JSON line and replies with a JSON payload.

    Returns (port, thread, stop_event).
    """

    stop_event = threading.Event()

    def server() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((host, 0))
            srv.listen(1)
            port = srv.getsockname()[1]
            # communicate port back via closure attribute
            server.port = port  # type: ignore[attr-defined]

            # accept a single connection then exit
            srv.settimeout(5.0)
            try:
                conn, _ = srv.accept()
            except Exception:
                return
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
                    return

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
                    return

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
