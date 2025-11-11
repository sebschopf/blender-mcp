"""HandlerExecutor: encapsulate handler invocation strategies.

This class centralizes how handlers are executed (direct call, with
timeout via ThreadPoolExecutor, etc.). It accepts an optional
executor_factory so tests can inject synchronous or mock executors.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutTimeout
from typing import Any, Callable, Dict, Optional

Handler = Callable[[Dict[str, Any]], Any]


class HandlerExecutor:
    def __init__(self, executor_factory: Optional[Callable[[], ThreadPoolExecutor]] = None) -> None:
        self._executor_factory = executor_factory

    def execute(self, handler: Handler, params: Optional[Dict[str, Any]] = None) -> Any:
        return handler(params or {})

    def execute_with_timeout(
        self,
        handler: Handler,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 5.0,
    ) -> Any:
        # Prefer injected factory to allow test doubles
        if self._executor_factory is not None:
            with self._executor_factory() as ex:
                fut = ex.submit(handler, params or {})
                try:
                    return fut.result(timeout=timeout)
                except FutTimeout as e:
                    raise TimeoutError(f"handler timed out after {timeout} seconds") from e
        else:
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(handler, params or {})
                try:
                    return fut.result(timeout=timeout)
                except FutTimeout as e:
                    raise TimeoutError(f"handler timed out after {timeout} seconds") from e
