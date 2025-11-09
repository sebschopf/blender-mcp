import subprocess

import pytest

from blender_mcp import embedded_server_adapter as adapter


class DummyProcess:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.pid = 12345
        self._alive = True

    def poll(self):
        return None if self._alive else 0

    def terminate(self):
        self._alive = False

    def wait(self, timeout=None):
        return 0

    def kill(self):
        self._alive = False


def test_start_server_process_monkeypatched(monkeypatch):
    captured = {}

    def fake_popen(cmd, cwd=None, stdout=None, stderr=None):
        captured['cmd'] = cmd
        captured['cwd'] = cwd
        return DummyProcess()

    monkeypatch.setattr(subprocess, 'Popen', fake_popen)
    proc = adapter.start_server_process(command=['echo', 'hi'], cwd='/',)
    assert adapter.is_running(proc)
    assert captured['cmd'] == ['echo', 'hi']


def test_stop_server_process(monkeypatch):
    dummy = DummyProcess()

    # stop should not raise
    adapter.stop_server_process(dummy)
    assert not adapter.is_running(dummy)


def test_default_command_nonwindows(monkeypatch):
    # On non-Windows platforms the adapter should raise if no command is passed
    monkeypatch.setattr(adapter.platform, 'system', lambda: 'Linux')
    with pytest.raises(RuntimeError):
        adapter.start_server_process(command=None)
