from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict

from blender_mcp.dispatchers.dispatcher import Dispatcher


def test_dispatch_with_timeout_raises() -> None:
    d = Dispatcher()

    def slow(_: Dict[str, Any]) -> Dict[str, bool]:  # sleep longer than timeout
        time.sleep(0.2)
        return {"ok": True}

    d.register("slow", slow)
    start = time.perf_counter()
    try:
        d.dispatch_with_timeout("slow", {}, timeout=0.05)
        assert False, "Expected TimeoutError"
    except TimeoutError:
        pass
    elapsed = time.perf_counter() - start
    # Le temps doit être proche du timeout (0.05) et < durée totale du handler (0.2) avec marge.
    assert elapsed < 0.25


def test_dispatch_with_timeout_success() -> None:
    d = Dispatcher()

    def fast(_: Dict[str, Any]) -> Dict[str, int]:
        return {"value": 42}

    d.register("fast", fast)
    res = d.dispatch_with_timeout("fast", {}, timeout=0.2)
    assert res == {"value": 42}


def test_concurrent_handlers_run_in_parallel() -> None:
    d = Dispatcher()

    def h1(_: Dict[str, Any]) -> int:
        time.sleep(0.1)
        return 1

    def h2(_: Dict[str, Any]) -> int:
        time.sleep(0.1)
        return 2

    d.register("h1", h1)
    d.register("h2", h2)

    start = time.perf_counter()
    # Use ThreadPoolExecutor to call dispatch_with_timeout concurrently
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(d.dispatch_with_timeout, "h1", {}, 0.5)
        f2 = ex.submit(d.dispatch_with_timeout, "h2", {}, 0.5)
        r1 = f1.result()
        r2 = f2.result()
    elapsed = time.perf_counter() - start

    assert {r1, r2} == {1, 2}
    # If sequential would be ~0.2s; allow small overhead but ensure <0.18
    assert elapsed < 0.18
