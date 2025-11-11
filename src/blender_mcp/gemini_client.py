"""Client utilities to call Gemini via CLI or API and parse tool JSON responses.

This module is self-contained so tests can mock network/subprocess calls.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from typing import Any, Optional, cast

from .http import get_session
from .types import ToolCommand

# Configuration
GEMINI_CMD = os.environ.get("GEMINI_CMD", "gemini chat -o json")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

PROMPT_TEMPLATE = (
    "You are an assistant that controls a local Blender MCP server.\n"
    "When you want Blender to run a tool, reply with a single JSON object only, nothing else.\n"
    '{"tool": "<tool_name>", "params": { ... }}\n'
    'If you need user clarification, instead return JSON: {"clarify": ["question 1"] }\n'
    "User request:\n{user_request}\n"
)


def find_inner_json(obj: Any) -> Any | None:
    """Try to find a JSON object inside arbitrary nested output/string.

    Returns the first dict-like JSON object found, or None.
    """
    # If it's a plain string, try to extract {...}
    if isinstance(obj, str):
        return _extract_first_json_from_string(obj)

    if isinstance(obj, dict):
        if "tool" in obj:
            return obj
        for v in obj.values():
            found = find_inner_json(v)
            if found is not None:
                return found
    if isinstance(obj, list):
        for v in obj:
            found = find_inner_json(v)
            if found is not None:
                return found
    return None


def _extract_first_json_from_string(s: str) -> Optional[ToolCommand]:
    """Try to extract the first top-level JSON object from a string.

    Returns a mapping (dict) when found, otherwise None.
    """
    m = re.search(r"(\{[\s\S]*\})", s)
    if m:
        try:
            parsed = json.loads(m.group(1))
            if isinstance(parsed, dict):
                return cast(ToolCommand, parsed)
        except Exception:
            return None
    for mm in re.finditer(r"(\{[\s\S]*?\})", s):
        try:
            parsed = json.loads(mm.group(1))
            if isinstance(parsed, dict):
                return cast(ToolCommand, parsed)
        except Exception:
            continue
    return None


def get_local_tool_catalog() -> str:
    """Get a short textual summary of available tools from the running MCP server
    or by scanning the local `src/blender_mcp/server.py` as a fallback.
    """
    MCP_BASE = os.environ.get("MCP_BASE", "http://127.0.0.1:8000")
    tools: list[str] = []
    try:
        url = f"{MCP_BASE}/tools"
        resp = get_session().get(url, timeout=3)
        if resp.ok:
            j = resp.json()
            for t in j.get("tools", []):
                name = t.get("name") or t.get("tool") or str(t)
                sig = t.get("signature", "")
                doc = t.get("doc", "")
                line = name + (f"{sig}" if sig else "")
                if doc:
                    line += f": {doc[:80]}"
                tools.append(line)
            return "\n".join(tools[:40])
    except Exception:
        pass

    # fallback to static scan
    src_path = os.path.join(os.getcwd(), "src", "blender_mcp", "server.py")
    if not os.path.exists(src_path):
        return ""
    try:
        txt = open(src_path, "r", encoding="utf-8").read()
    except Exception:
        return ""

    # reuse the `tools` list declared above
    for m in re.finditer(r"def\s+(\w+)\s*\(([^)]*)\)\s*:\s*(?:\"\"\"([\s\S]*?)\"\"\"|)", txt):
        name = m.group(1)
        sig = m.group(2).strip()
        doc = (m.group(3) or "").strip().split("\n")[0] if m.group(3) else ""
        line = name
        if sig:
            line += f"({sig})"
        if doc:
            line += f": {doc[:80]}"
        tools.append(line)
    return "\n".join(tools[:40])


def get_mcp_runtime_summary() -> str:
    """Query a few status tools on the running MCP server and return a short summary.

    Attempts quick POSTs to a handful of tools and returns a multi-line summary.
    """
    MCP_BASE = os.environ.get("MCP_BASE", "http://127.0.0.1:8000")
    services = [
        ("PolyHaven", "get_polyhaven_status"),
        ("Sketchfab", "get_sketchfab_status"),
        ("Hyper3D", "get_hyper3d_status"),
    ]
    parts: list[str] = []
    for title, tool in services:
        try:
            resp = get_session().post(f"{MCP_BASE}/tools/{tool}", json={}, timeout=3)
            if resp.ok:
                j = resp.json()
                summary = j.get("summary") or str(j)
                parts.append(f"{title}: {summary}")
        except Exception:
            parts.append(f"{title}: unreachable")
    return " | ".join(parts)


def call_gemini_cli(user_request: str) -> ToolCommand:
    prompt = _prepare_prompt(user_request)
    cmd = shlex.split(GEMINI_CMD)
    out = _run_gemini_subprocess(cmd, prompt)

    top = _extract_first_json_from_string(out)
    if top and "tool" in top:
        return top
    if top:
        inner = find_inner_json(top)
        if isinstance(inner, dict):
            return cast(ToolCommand, inner)
        if inner is not None:
            return inner
    inner_raw = find_inner_json(out)
    if inner_raw is not None:
        if isinstance(inner_raw, dict):
            return cast(ToolCommand, inner_raw)
        return inner_raw
    print(
        "Could not find a tool JSON in Gemini CLI output. Raw output:\n",
        out,
        file=sys.stderr,
    )
    raise SystemExit(1)


def _prepare_prompt(user_request: str) -> str:
    tools_summary = get_local_tool_catalog()
    runtime = ""
    try:
        runtime = get_mcp_runtime_summary()
    except Exception:
        runtime = ""
    combined = tools_summary + ("\n\nLive status:\n" + runtime if runtime else "")
    return PROMPT_TEMPLATE.format(user_request=user_request, tools_summary=combined)


def _run_gemini_subprocess(cmd: list[str], prompt: str) -> str:
    exe = cmd[0]
    resolved = shutil.which(exe)
    if not resolved and os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidate = os.path.join(appdata, "npm", exe if exe.lower().endswith(".cmd") else exe + ".cmd")
            if os.path.exists(candidate):
                resolved = candidate
    if resolved:
        cmd[0] = resolved
    else:
        print(
            (
                f"Could not find executable for '{exe}'. "
                "Set GEMINI_CMD to the full path to your gemini binary or add it to PATH."
            )
        )
        raise SystemExit(1)

    try:
        proc = subprocess.run(
            cmd,
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as e:
        print(f"Failed to launch gemini command: {e}")
        raise
    return proc.stdout.decode("utf-8", errors="ignore").strip()


def _extract_text_from_genai_response(resp: Any) -> Any:
    """Normalize various response shapes from the google-genai client into text/dict."""
    if hasattr(resp, "text"):
        return resp.text
    try:
        d = dict(resp)
        for k in ("output", "content", "candidates", "response"):
            if k in d:
                return d[k]
    except Exception:
        return str(resp)
    return str(resp)


def _extract_tool_from_genai_response(resp: Any, text: Any) -> Optional[ToolCommand]:
    """Try to extract a tool JSON dict from various genai response shapes.

    Returns a Dict when a tool object is found, otherwise None.
    """
    # If the top-level text is already a mapping with a tool, prefer that.
    if isinstance(text, dict):
        if "tool" in text:
            return cast(ToolCommand, text)
        inner = find_inner_json(text)
        if isinstance(inner, dict):
            return cast(ToolCommand, inner)
        return None

    # If text is a string, try to find JSON inside it.
    if isinstance(text, str):
        inner = find_inner_json(text)
        if isinstance(inner, dict):
            return cast(ToolCommand, inner)
        return None

    # Some clients embed the useful text under resp.text
    raw = getattr(resp, "text", None)
    if raw and isinstance(raw, str):
        inner = find_inner_json(raw)
        if isinstance(inner, dict):
            return cast(ToolCommand, inner)
    return None


def call_gemini_api(user_request: str) -> ToolCommand:
    # Import google.genai dynamically and fail with a clear message if missing.
    try:
        import importlib

        genai = importlib.import_module("google.genai")
    except Exception:
        # Be explicit: this feature is optional and requires the google-genai SDK.
        raise RuntimeError("google-genai library not available. Install with: pip install google-genai")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set in environment.", file=sys.stderr)
        raise SystemExit(1)

    client = genai.Client()
    prompt = _prepare_prompt(user_request)
    model = GEMINI_MODEL

    resp = client.models.generate_content(model=model, contents=prompt)
    text = _extract_text_from_genai_response(resp)

    found = _extract_tool_from_genai_response(resp, text)
    if found is not None:
        return found
    print(
        "Could not extract tool JSON from Gemini API response. Response snapshot:",
        resp,
        file=sys.stderr,
    )
    raise SystemExit(1)
