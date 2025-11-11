"""Small command dispatcher relocated into the `dispatchers` package.

This file is a near-copy of the top-level `command_dispatcher.py` and
keeps the same public API.
"""

from typing import Any, Callable, Dict, Optional


class CommandDispatcher:
    def __init__(
        self, handlers: Optional[Dict[str, Callable[..., Any]]] = None
    ) -> None:
        # handlers: mapping from command type -> callable(**params)
        self.handlers: Dict[str, Callable[..., Any]] = {}
        if handlers:
            self.handlers.update(handlers)

    def register(self, command_type: str, handler: Callable[..., Any]) -> None:
        """Register a handler for a command type."""
        self.handlers[command_type] = handler

    def unregister(self, command_type: str) -> None:
        self.handlers.pop(command_type, None)

    def dispatch(self, command: Any) -> Dict[str, Any]:
        """Dispatch the given command dict and return a result dict.

        Expected command shape: {"type": <str>, "params": { ... }}
        """
        if not isinstance(command, dict):
            return {"status": "error", "message": "Invalid command format"}

        cmd_type = command.get("type")
        if not isinstance(cmd_type, str):
            return {"status": "error", "message": "Invalid or missing command type"}

        params = command.get("params", {}) or {}

        handler = self.handlers.get(cmd_type)
        if not handler:
            return {"status": "error", "message": f"Unknown command type: {cmd_type}"}

        try:
            result = handler(**params)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
