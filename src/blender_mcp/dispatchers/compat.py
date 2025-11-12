"""Compatibility thin shim.

Expose the historical ``CommandDispatcher`` name by importing the
small command dispatcher implementation. Keeping this file minimal
reduces the maintenance surface and avoids duplicating logic.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List


class _CommandDispatcherCompat:
	"""Lightweight compatibility wrapper exposing a simple register/dispatch API.

		API:
			- register(name, handler)
			- unregister(name)
			- list_handlers()
			- dispatch(name, params=None, config=None) -> result

		Handlers registered here are expected to accept (params, config) but
		wrappers are tolerant and will pass whatever positional args the
		handler accepts.
	"""

	def __init__(self) -> None:
		self._handlers: Dict[str, Callable[..., Any]] = {}

	def register(self, name: str, handler: Callable[..., Any]) -> None:
		self._handlers[name] = handler

	def unregister(self, name: str) -> None:
		self._handlers.pop(name, None)

	def list_handlers(self) -> List[str]:
		return sorted(self._handlers.keys())

	def dispatch(self, name: str, params: Dict[str, Any] | None = None, config: Any | None = None) -> Any:
		if name not in self._handlers:
			raise KeyError(name)
		handler = self._handlers[name]
		# Try calling with (params, config), fall back to single-arg or no-arg
		try:
			return handler(params, config)
		except TypeError:
			try:
				return handler(params)
			except TypeError:
				return handler()


CommandDispatcher = _CommandDispatcherCompat

__all__ = ["CommandDispatcher"]
