"""Bridge service for Gemini -> dispatcher flows with injectable dependencies.

This encapsulates the interactive loop previously implemented in
`dispatcher.run_bridge` and makes the external callers injectable for
testing and policy-wiring.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List


def call_gemini_cli(user_req: str, use_api: bool = False):
    """Placeholder for the Gemini client call; tests monkeypatch this.

    Kept in this module so the BridgeService can default to using the
    project-level stub. Tests should monkeypatch `bridge.call_gemini_cli`.
    """
    raise NotImplementedError("call_gemini_cli should be provided by environment/tests")


def call_mcp_tool(tool: str, params: Dict[str, Any]):
    """Placeholder for a function that calls an MCP tool remotely; tests monkeypatch this."""
    raise NotImplementedError("call_mcp_tool should be provided by environment/tests")


class BridgeService:
    """Encapsulate the Gemini->tool bridging flow.

    gemini_caller: Callable[[str, bool], Any]
      function that accepts the user request and use_api flag and returns
      either a mapping describing an action or a dict with 'clarify'.

    mcp_tool_caller: Callable[[str, Dict[str, Any]], Any]
      function to call remote MCP tools if the dispatcher does not have the
      requested tool locally.
    """

    def __init__(
        self,
        gemini_caller: Callable[..., Any],
        mcp_tool_caller: Callable[..., Any],
    ) -> None:
        # Use very permissive callables so callers can pass functions with
        # keyword args (tests use keyword `use_api`). We don't bind to a
        # strict signature here to keep the seam flexible for DI.
        self._gemini = gemini_caller
        self._mcp_tool = mcp_tool_caller

    def run(
        self,
        user_req: str,
        config: Any,
        dispatcher: Any,
        use_api: bool = False,
    ) -> None:
        """Execute the bridge flow using injected callers and provided dispatcher.

        The dispatcher is expected to expose `list_handlers()` and
        `dispatch(name, params, config)` (compat wrapper) or similar.
        """
        resp: Any = self._gemini(user_req, use_api=use_api)
        while True:
            if isinstance(resp, dict) and "clarify" in resp:
                data = resp
                prompts_raw = data.get("clarify", []) or []
                prompts: List[str]
                if isinstance(prompts_raw, list):
                    prompts = [str(p) for p in prompts_raw]
                else:
                    prompts = [str(prompts_raw)]

                for p in prompts:
                    try:
                        ans = input(p + " ")
                    except Exception:
                        ans = ""
                    resp = self._gemini(ans or user_req, use_api=use_api)
                    # loop continues and will handle the new resp
            elif isinstance(resp, dict) and "tool" in resp:
                data = resp
                tool_raw = data.get("tool")
                params_raw = data.get("params", {}) or {}
                tool = str(tool_raw) if tool_raw is not None else ""
                params = params_raw if isinstance(params_raw, dict) else {}

                # if the dispatcher knows this tool, call the local handler
                if tool in dispatcher.list_handlers():
                    # compat dispatchers expect (name, params, config)
                    # but we simply call dispatch and let wrappers adapt
                    try:
                        dispatcher.dispatch(tool, params, config)
                    except TypeError:
                        # some wrappers expect different signatures; try again
                        dispatcher.dispatch(tool, params)
                else:
                    # otherwise call remote MCP tool
                    self._mcp_tool(tool, params)
                return
            else:
                return
