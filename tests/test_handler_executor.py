from __future__ import annotations

import time

from blender_mcp.dispatchers.executor import HandlerExecutor


def test_executor_basic_call() -> None:
    ex = HandlerExecutor()

    def h(params):
        return params.get("x", 1)

    assert ex.execute(h, {"x": 5}) == 5


def test_executor_timeout() -> None:
    ex = HandlerExecutor()

    def slow(_params):
        time.sleep(0.1)
        return "done"

    try:
        ex.execute_with_timeout(slow, {}, timeout=0.01)
        assert False, "expected timeout"
    except TimeoutError:
        pass
