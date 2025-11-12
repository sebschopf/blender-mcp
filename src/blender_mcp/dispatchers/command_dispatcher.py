"""Small command dispatcher relocated into the `dispatchers` package.

This file is a near-copy of the top-level `command_dispatcher.py` and
keeps the same public API.
"""

from typing import Any, Callable, Dict, Optional

from ..errors import (
    ExecutionTimeoutError,
    ExternalServiceError,
    InvalidParamsError,
    PolicyDeniedError,
)
from ..logging_utils import log_action


class CommandDispatcher:
    def __init__(self, handlers: Optional[Dict[str, Callable[..., Any]]] = None) -> None:
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
            return {
                "status": "error",
                "message": "Invalid command format",
                "error_code": "invalid_command"
            }

        cmd_type = command.get("type")
        if not isinstance(cmd_type, str):
            return {
                "status": "error",
                "message": "Invalid or missing command type",
                "error_code": "invalid_command_type",
            }

        params = command.get("params", {}) or {}

        handler = self.handlers.get(cmd_type)
        if not handler:
            log_action(
                "command_dispatcher", "unknown_command",
                    {"type": cmd_type, "params": params},
                    None
            )

            return {
                "status": "error",
                "message": f"Unknown command type: {cmd_type}",
                "error_code": "not_found"
            }

        try:
            result = handler(**params)
            log_action(
                "command_dispatcher",
                "dispatch_success",
                {"type": cmd_type},
                result
            )
            
            return {"status": "success", "result": result}
        
        except InvalidParamsError as ipe:
            log_action(
                "command_dispatcher",
                "invalid_params",
                {"type": cmd_type, "params": params},
                str(ipe)
            )
            
            return {
                "status": "error",
                "message": str(ipe),
                "error_code": "invalid_params"
            }
        
        except PolicyDeniedError as pde:
            log_action(
                "command_dispatcher",
                "policy_denied",
                {"type": cmd_type, "params": params},
                str(pde)
            )
            return {
                "status": "error",
                "message": str(pde),
                "error_code": "policy_denied"
            }
        
        except ExecutionTimeoutError:
            log_action(
                "command_dispatcher",
                "timeout",
                {"type": cmd_type},
                None
            )

            return {
                "status": "error",
                "message": "Handler timed out",
                "error_code": "timeout"
            }
        
        except ExternalServiceError as ese:
            log_action(
                "command_dispatcher",
                "external_error",
                {"type": cmd_type},
                str(ese)
            )

            return {
                "status": "error",
                "message": str(ese),
                "error_code": "external_error"
            }
        
        except Exception as e:
            log_action(
                "command_dispatcher",
                "internal_error",
                {"type": cmd_type, "params": params},
                str(e)
            )
            return {
                "status": "error",
                "message": str(e),
                "error_code": "internal_error"
            }
