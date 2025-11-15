import importlib.util
import os
import socket
import sys

# Ensure repository root is on sys.path so we can import the package when running
# this script directly.
repo_root = os.path.dirname(os.path.dirname(__file__))
# Import the canonical module via normal package import so Python's import system
# and `sys.modules` identity are preserved. If this fails, raise a clear error
# so CI/dev environments can adjust `PYTHONPATH` instead of silently loading a
# duplicate module by path.
try:
    connection_mod = importlib.import_module("blender_mcp.connection_core")
except Exception as e:
    raise ImportError(
        "Could not import 'blender_mcp.connection_core'. Ensure 'src' is on PYTHONPATH."
    ) from e

BlenderConnection = connection_mod.BlenderConnection


def run():
    # Test 1: connection failure
    class BadSocket:
        def __init__(self, *args, **kwargs):
            pass

        def connect(self, addr):
            raise OSError("cannot connect")

    socket.socket = BadSocket
    conn = BlenderConnection("localhost", 9999)
    ok1 = conn.connect() is False

    # Test 2: successful send/receive
    class FakeSocket:
        def __init__(self, *args, **kwargs):
            self._data = [b'{"status":"ok","result": {"message": "ok"}}']
            self.sent = b""

        def connect(self, addr):
            return None

        def settimeout(self, t):
            self.timeout = t

        def sendall(self, b):
            self.sent = b

        def recv(self, bufsize):
            if self._data:
                return self._data.pop(0)
            return b""

        def close(self):
            return None

    socket.socket = FakeSocket
    conn2 = BlenderConnection("localhost", 9999)
    ok2 = False
    try:
        ok2_connect = conn2.connect()
        res = conn2.send_command("test", {"a": 1})
        ok2 = ok2_connect and isinstance(res, dict) and res.get("message") == "ok"
    except Exception as e:
        print("Smoke test exception:", e)

    if ok1 and ok2:
        print("SMOKE_TEST: OK")
        return 0
    print(f"SMOKE_TEST: FAIL (ok1={ok1}, ok2={ok2})")
    return 2


if __name__ == "__main__":
    sys.exit(run())
