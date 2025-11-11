"""Adapter that normalizes command dicts into dispatcher calls.

This class encapsulates the logic previously found on
`Dispatcher.dispatch_command`. Extracting it makes the registry
implementation focused on handler management while the adapter handles
normalization, error mapping and response shaping.
"""
from __future__ import annotations

from typing import Any, Dict

from ..types import DispatcherResult
from .abc import AbstractDispatcher


class CommandAdapter:
    def __init__(self, dispatcher: AbstractDispatcher) -> None:
        self._dispatcher = dispatcher

    def dispatch_command(self, command: Dict[str, Any]) -> DispatcherResult:
        """Accept mapping-like commands and return a normalized result.

        Expected shape: {"type": <str>, "params": {...}}
        Returns: {"status": "success", "result": ...} or
                 {"status": "error", "message": ...}
        """
        if not isinstance(command, dict):
            return {"status": "error", "message": "Invalid command format"}

        cmd_type_raw = command.get("type") or command.get("tool")
        if not isinstance(cmd_type_raw, str):
            return {"status": "error", "message": "Invalid or missing command type"}
        cmd_type = cmd_type_raw

        params_raw = command.get("params", {}) or {}
        params = params_raw if isinstance(params_raw, dict) else {}

        if cmd_type not in self._dispatcher.list_handlers():
            return {"status": "error", "message": f"Unknown command type: {cmd_type}"}

        try:
            result = self._dispatcher.dispatch(cmd_type, params)
            return {"status": "success", "result": result}
        except Exception as e:
            # keep the same external behavior as before: return error message
            return {"status": "error", "message": str(e)}
