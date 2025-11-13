from __future__ import annotations

from typing import Any, Protocol


class InstrumentationStrategy(Protocol):  # pragma: no cover - structural
    def on_dispatch_start(self, name: str, params: dict[str, Any]) -> None: ...
    def on_dispatch_success(self, name: str, result: Any, elapsed_s: float) -> None: ...
    def on_dispatch_error(self, name: str, error: Exception, elapsed_s: float) -> None: ...
    def on_adapter_invoke(self, adapter_name: str, cmd_type: str, params: dict[str, Any]) -> None: ...


class NoOpInstrumentationStrategy:
    """Default no-op implementation used when instrumentation is not provided.

    Each method intentionally does nothing; this class documents the contract
    and provides a stable type for annotations where needed.
    """

    def on_dispatch_start(self, name: str, params: dict[str, Any]) -> None:  # noqa: D401
        return None

    def on_dispatch_success(self, name: str, result: Any, elapsed_s: float) -> None:  # noqa: D401
        return None

    def on_dispatch_error(self, name: str, error: Exception, elapsed_s: float) -> None:  # noqa: D401
        return None

    def on_adapter_invoke(self, adapter_name: str, cmd_type: str, params: dict[str, Any]) -> None:  # noqa: D401
        return None


__all__ = ["InstrumentationStrategy", "NoOpInstrumentationStrategy"]
