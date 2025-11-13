from __future__ import annotations

from typing import Any, Dict, List, Literal, NotRequired, TypedDict


class ToolCommand(TypedDict, total=False):
    """A lightweight TypedDict for Gemini/MCP tool mapping JSON.

    Examples:
    - {"tool": "execute_script", "params": {...}}
    - {"clarify": ["which object?"]}
    """

    tool: NotRequired[str]
    params: NotRequired[Dict[str, Any]]
    clarify: NotRequired[List[str]]


class DispatcherResult(TypedDict, total=False):
    """Normalized dispatcher response used by `dispatch_command`.

    - success path: {"status":"success","result":...}
    - error path:   {"status":"error","message":...}
    """

    status: NotRequired[Literal["success", "error"]]
    result: NotRequired[Any]
    message: NotRequired[str]
    # stable machine-readable error code added for normalized error handling
    error_code: NotRequired[str]


class ToolInfo(TypedDict, total=False):
    """Small TypedDict describing a tool entry returned by /tools endpoints."""

    name: NotRequired[str]
    tool: NotRequired[str]
    signature: NotRequired[str]
    doc: NotRequired[str]
