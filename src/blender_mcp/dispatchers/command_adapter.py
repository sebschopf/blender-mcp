"""Adapter that normalizes command dicts into dispatcher calls.

This class encapsulates the logic previously found on
`Dispatcher.dispatch_command`. Extracting it makes the registry
implementation focused on handler management while the adapter handles
normalization, error mapping and response shaping.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from ..errors import (
    ExecutionTimeoutError,
    ExternalServiceError,
    HandlerNotFoundError,
    InvalidParamsError,
    PolicyDeniedError,
)
from ..errors import (
    HandlerError as CanonicalHandlerError,
)
from ..logging_utils import log_action
from ..types import DispatcherResult
from .abc import AbstractDispatcher
from .policies import PolicyChecker


class CommandAdapter:
    def __init__(self, dispatcher: AbstractDispatcher, policy_check: Optional[PolicyChecker] = None) -> None:
        self._dispatcher = dispatcher
        self._policy_check = policy_check

    def dispatch_command(self, command: Dict[str, Any]) -> DispatcherResult:
        """Accept mapping-like commands and return a normalized result.

        Expected shape: {"type": <str>, "params": {...}}
        Returns: {"status": "success", "result": ...} or
                 {"status": "error", "message": ...}
        """
        if not isinstance(command, dict):
            return {
                "status": "error",
                "message": "Invalid command format",
                "error_code": "invalid_command",
            }

        cmd_type_raw = command.get("type") or command.get("tool")
        if not isinstance(cmd_type_raw, str):
            return {
                "status": "error",
                "message": "Invalid or missing command type",
                "error_code": "invalid_command_type",
            }
        cmd_type = cmd_type_raw

        params_raw = command.get("params", {}) or {}
        params = params_raw if isinstance(params_raw, dict) else {}

        # Run policy check if provided. If the checker returns a string,
        # treat it as an error message and short-circuit the dispatch.
        if self._policy_check is not None:
            try:
                policy_result = self._policy_check(cmd_type, params)
            except PolicyDeniedError as pde:
                log_action(
                    "command_adapter",
                    "policy_denied",
                    {"type": cmd_type, "params": params},
                    str(pde),
                )
                return {
                    "status": "error",
                    "message": str(pde),
                    "error_code": "policy_denied",
                }
            if isinstance(policy_result, str) and policy_result:
                # keep backward-compatible string-based policy_result
                log_action(
                    "command_adapter",
                    "policy_blocked",
                    {"type": cmd_type, "params": params},
                    policy_result,
                )
                return {
                    "status": "error",
                    "message": f"Blocked by policy: {policy_result}",
                    "error_code": "policy_denied",
                }

        if cmd_type not in self._dispatcher.list_handlers():
            log_action(
                "command_adapter",
                "unknown_command",
                {"type": cmd_type, "params": params},
                None,
            )
            return {
                "status": "error",
                "message": f"Unknown command type: {cmd_type}",
                "error_code": "not_found",
            }

        try:
            result = self._dispatcher.dispatch(cmd_type, params)
            log_action("command_adapter", "dispatch_success", {"type": cmd_type}, result)
            return {"status": "success", "result": result}
        except Exception as e:
            return self._map_exception(e, cmd_type, params)

    def _map_exception(self, exc: Exception, cmd_type: str, params: Dict[str, Any]) -> DispatcherResult:
        """Map exceptions to normalized DispatcherResult responses.

        Centralizing mapping here keeps the public flow linear and easier to
        unit-test while satisfying complexity checks.
        """
        if isinstance(exc, InvalidParamsError):
            log_action("command_adapter", "invalid_params", {"type": cmd_type, "params": params}, str(exc))
            return {"status": "error", "message": str(exc), "error_code": "invalid_params"}
        if isinstance(exc, HandlerNotFoundError):
            log_action("command_adapter", "handler_not_found", {"type": cmd_type}, str(exc))
            return {"status": "error", "message": str(exc), "error_code": "not_found"}
        if isinstance(exc, ExecutionTimeoutError):
            log_action("command_adapter", "timeout", {"type": cmd_type}, None)
            return {"status": "error", "message": "Handler timed out", "error_code": "timeout"}
        if isinstance(exc, CanonicalHandlerError):
            log_action("command_adapter", "handler_error", {"type": cmd_type}, str(exc))
            return {"status": "error", "message": str(exc), "error_code": "handler_error"}
        if isinstance(exc, ExternalServiceError):
            log_action("command_adapter", "external_error", {"type": cmd_type}, str(exc))
            return {"status": "error", "message": str(exc), "error_code": "external_error"}
        # Fallback for unexpected exceptions
        log_action("command_adapter", "internal_error", {"type": cmd_type, "params": params}, str(exc))
        return {"status": "error", "message": str(exc), "error_code": "internal_error"}
