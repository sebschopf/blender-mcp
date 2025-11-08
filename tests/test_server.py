import json

from blender_mcp.server import BlenderMCPServer


class FakeClient:
    def __init__(self):
        self.sent = b""

    def sendall(self, data: bytes):
        self.sent += data


def test_schedule_execute_wrapper_sends_response():
    server = BlenderMCPServer()

    # Replace execute_command with a predictable response
    def fake_execute(command):
        return {"status": "ok", "handled": True, "cmd": command}

    server.execute_command = fake_execute

    client = FakeClient()
    cmd = {"type": "noop", "params": {}}

    # Call the scheduling wrapper; in CI/test env no bpy is present so it runs sync
    server._schedule_execute_wrapper(client, cmd)

    assert client.sent, "Expected the fake client to have received bytes"
    decoded = json.loads(client.sent.decode("utf-8"))
    assert decoded["status"] == "ok"
    assert decoded["handled"] is True
    assert decoded["cmd"]["type"] == "noop"
