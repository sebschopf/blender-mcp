#!/usr/bin/env python3
"""Bridge for Gemini -> local MCP HTTP adapter.

This script supports two modes:
- CLI mode (default): call a local gemini CLI command (GEMINI_CMD) and parse text output.
- API mode (--use-api or USE_GEMINI_API=1): call the official Google GenAI client
  (package name: google-genai) using the GEMINI_API_KEY environment variable.

Usage:
  # CLI mode (default)
  export GEMINI_CMD='gemini chat -o json --model=gemini-2.5-pro'
  python scripts/gemini_bridge.py "Donne-moi la scène et appelle get_scene_info"

  # API mode (recommended / cleaner): set GEMINI_API_KEY and model, then:
  export GEMINI_API_KEY='...'
  export GEMINI_MODEL='gemini-2.5-flash'
  python scripts/gemini_bridge.py --use-api "Donne-moi la scène et appelle get_scene_info"
"""

import json
import os
import re
import sys
from typing import Any, Optional

import requests

from blender_mcp.config import BridgeConfig

GEMINI_CMD = os.environ.get("GEMINI_CMD", "gemini chat -o json")

# Runtime guards: make the script import-safe for static analysis and CI.
# Define MCP_BASE as the base URL for the MCP HTTP API if present in env.
# Define a default empty mapping for local tool mappings to avoid NameErrors
# when the script is imported for static analysis.
from typing import Callable, Dict

MCP_BASE: str | None = os.environ.get("MCP_BASE")
# _TOOL_MAPPINGS is an optional local mapping of high-level intents to handlers.
# Fill at runtime (or keep empty) to avoid F821 during static checks.
# Use a flexible Callable[..., Any] so static analysis knows it's callable.
_TOOL_MAPPINGS: Dict[str, Callable[..., Any]] = {}


PROMPT_TEMPLATE = (
    "You are an assistant that controls a local Blender MCP server.\n"
    "When you want Blender to run a tool, reply with a single JSON object only, nothing else.\n"
    'Format exactly like this (JSON only): {{"tool": "<tool_name>", "params": {{ ... }} }}\n'
    'If you need user clarification, instead return JSON: {{"clarify": ["question 1", "question 2"] }}\n'
    "If you produce a plan that uses MCP tools, prefer these available tools (if helpful):\n{tools_summary}\n\n"
    "User request:\n{user_request}\n"
)


def get_local_tool_catalog() -> str:
    """Get a short textual summary of available tools.

    Prefer querying the running MCP server (/tools endpoint) to get a canonical list.
    If the server is not available, fall back to scanning the local source file.
    """
    # First try the running MCP server
    try:
        url = f"{MCP_BASE}/tools"
        resp = requests.get(url, timeout=3)
        if resp.ok:
            j = resp.json()
            tools = []
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
        # ignore and fall back to static scanning
        pass

    # Fallback: static scan of the local server.py
    src_path = os.path.join(os.getcwd(), "src", "blender_mcp", "server.py")
    if not os.path.exists(src_path):
        return ""
    try:
        txt = open(src_path, "r", encoding="utf-8").read()
    except Exception:
        return ""

    # Find occurrences of function definitions with optional docstrings
    tools = []
    import re as _re

    for m in _re.finditer(
        r"def\s+(\w+)\s*\(([^)]*)\)\s*:\s*(?:\"\"\"([\s\S]*?)\"\"\"|)", txt
    ):
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

    This function performs short POST requests to /tools/<name> and extracts a one-line
    summary for each service. If MCP is unreachable or a tool fails, it will return a
    short error note instead of blocking.
    """
    services = [
        ("PolyHaven", "get_polyhaven_status"),
        ("Sketchfab", "get_sketchfab_status"),
        ("Hyper3D", "get_hyper3d_status"),
    ]
    parts = []
    for label, tool in services:
        try:
            url = f"{MCP_BASE}/tools/{tool}"
            resp = requests.post(url, json={"params": {}}, timeout=4)
            if resp.ok:
                j = resp.json()
                # asgi adapter returns {status: 'ok', result: ...}
                res = j.get("result")
                if isinstance(res, str):
                    summary = res.splitlines()[0]
                elif isinstance(res, dict):
                    enabled = res.get("enabled")
                    msg = res.get("message") or ""
                    if enabled is not None:
                        summary = (
                            f"enabled={enabled}; {msg}" if msg else f"enabled={enabled}"
                        )
                    else:
                        # Fallback – stringify
                        summary = str(res)
                else:
                    summary = str(res)
            else:
                summary = f"HTTP {resp.status_code}"
        except Exception as e:
            summary = f"error: {str(e)}"
        parts.append(f"{label}: {summary}")
    return "\n".join(parts)


def find_inner_json(obj: Any) -> Optional[dict]:
    """Recursively search for a JSON object inside strings, lists or dicts.

    Returns the first parsed dict found, or None.
    """
    if isinstance(obj, str):
        mm = re.search(r"(\{[\s\S]*\})", obj)
        if mm:
            try:
                parsed = json.loads(mm.group(1))
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                return None
        return None
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


def call_gemini_cli(user_request: str) -> dict:
    """Proxy to the extracted Gemini CLI implementation.

    The heavy logic lives in `blender_mcp.gemini_client` for testability and
    smaller scripts. We import lazily so the script remains importable even if
    the package is not installed in Blender's Python.
    """
    try:
        from blender_mcp.gemini_client import call_gemini_cli as _call  # type: ignore

        return _call(user_request)
    except Exception:
        # If the extracted module is unavailable, surface a clear error.
        raise


def call_gemini_api(user_request: str) -> dict:
    """Proxy to the extracted Gemini API implementation.

    Delegates to `blender_mcp.gemini_client.call_gemini_api`.
    """
    try:
        from blender_mcp.gemini_client import call_gemini_api as _call  # type: ignore

        return _call(user_request)
    except Exception:
        raise


def call_mcp_tool(tool: str, params: dict):
    """Proxy to the MCP HTTP client wrapper in `blender_mcp.mcp_client`.

    Lazy-imported for testability and to keep this script small.
    """
    try:
        from blender_mcp.mcp_client import call_mcp_tool as _call  # type: ignore

        return _call(tool, params)
    except Exception:
        # If import fails, fall back to the inline implementation
        url = f"{MCP_BASE}/tools/{tool}"
        resp = requests.post(url, json={"params": params}, timeout=60)
        resp.raise_for_status()
        return resp.json()


# --- Mapping handlers: translate high-level intentions into bpy code and call execute_blender_code
def _make_ruby_material_code(mat_name: str = "M_Ruby", photoreal: bool = False) -> str:
    if photoreal:
        rough = 0.18
        spec = 0.7
        clearcoat = 0.1
    else:
        rough = 0.25
        spec = 0.5
        clearcoat = 0.0
    return f"""
import bpy
from mathutils import Color
mat = bpy.data.materials.new('{mat_name}')
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
principled = nodes.new('ShaderNodeBsdfPrincipled')
principled.inputs['Base Color'].default_value = (0.6, 0.03, 0.03, 1)  # deep ruby
principled.inputs['Metallic'].default_value = 0.0
principled.inputs['Roughness'].default_value = {rough}
principled.inputs['Specular'].default_value = {spec}
principled.inputs['Clearcoat'].default_value = {clearcoat}
links.new(principled.outputs['BSDF'], output.inputs['Surface'])
"""


def _make_gold_material_code(mat_name: str = "M_Gold", photoreal: bool = False) -> str:
    if photoreal:
        rough = 0.12
        spec = 0.8
        clearcoat = 0.0
    else:
        rough = 0.18
        spec = 0.5
        clearcoat = 0.0
    return f"""
import bpy
mat = bpy.data.materials.new('{mat_name}')
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
principled = nodes.new('ShaderNodeBsdfPrincipled')
principled.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1)
principled.inputs['Metallic'].default_value = 1.0
principled.inputs['Roughness'].default_value = {rough}
principled.inputs['Specular'].default_value = {spec}
principled.inputs['Clearcoat'].default_value = {clearcoat}
links.new(principled.outputs['BSDF'], output.inputs['Surface'])
"""


def _generate_d10_code(_: dict) -> str:
    """D10 generator removed.

    Historical note: an interactive D10 generator used for live testing was removed to
    reduce complexity. Use the standard primitive mapping in
    `handle_add_primitive_mapping` for simple primitives.
    """
    raise NotImplementedError("D10 generator has been removed; use primitive mapping")


def handle_add_primitive_mapping(params: dict, config):
    # Try to reuse an extracted, testable codegen module. If it's not present,
    # fall back to the inline primitive mapping implemented below.
    try:
        from blender_mcp.blender_codegen import append_save_blend, generate_primitive_code  # type: ignore

        code = generate_primitive_code(params or {})
    except Exception:
        # Generic add primitive -> we will fallback to execute_blender_code used to add simple primitives
        prim = ""
        if params:
            prim = (params.get("primitive_type") or params.get("type") or "").upper()

        # fallback: simple primitives using bpy.ops
        primitive_map = {
            "CYLINDER": "bpy.ops.mesh.primitive_cylinder_add(vertices={vertices}, radius={radius}, depth={depth})",
            "CUBE": "bpy.ops.mesh.primitive_cube_add(size={size})",
            "UV_SPHERE": "bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius={radius})",
        }
        if prim in primitive_map:
            template = primitive_map[prim]
            # Build formats safely
            fmt = {}
            for k in ("vertices", "radius", "depth", "size"):
                if params and params.get(k) is not None:
                    fmt[k] = params.get(k)
            code = "import bpy\n" + template.format(**fmt) + "\n"
        else:
            code = "import bpy\n# Unknown primitive requested, creating a default cube\nbpy.ops.mesh.primitive_cube_add(size=1)\n"

    # Optionally show generated code for debugging
    if getattr(config, "verbose", False):
        print("--- Generated Blender Python code ---")
        print(code)
        print("--- end generated code ---")

    # If requested, append a save step to the generated code so Blender saves the .blend
    if getattr(config, "save_blend", False):
        try:
            # Use the helper from the extracted module if available
            code = append_save_blend(code)  # type: ignore
        except Exception:
            import datetime

            save_dir = os.path.abspath(os.path.join(os.getcwd(), "output"))
            os.makedirs(save_dir, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"designed_scene_{ts}.blend"
            save_path = os.path.join(save_dir, filename)
            # Ensure Windows-friendly path escaping
            save_path_escaped = save_path.replace("\\", "\\\\")
            code += f"\n# Auto-save from bridge\nimport bpy\nbpy.ops.wm.save_mainfile(filepath=r'{save_path_escaped}')\n"

    # Call execute_blender_code via MCP
    print("Sending generated Blender code to MCP...")
    return call_mcp_tool("execute_blender_code", {"code": code})


# Mapping moved to `blender_mcp.dispatcher` to keep the script minimal.


def main():
    use_api = False
    argv = sys.argv[1:]
    if not argv:
        print(
            'Usage: python scripts/gemini_bridge.py [--use-api] [--verbose] [--save] [--photoreal] [--engraving=geometry|visual] "<user request>"'
        )
        sys.exit(1)

    # Parse flags (simple): --use-api, --verbose, --save, --photoreal, --engraving=geometry|visual
    verbose = False
    save_blend = False
    photoreal = False
    engraving_default = os.environ.get("GEMINI_BRIDGE_ENGRAVING", "geometry")
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--use-api":
            use_api = True
            argv.pop(i)
            continue
        if a == "--verbose":
            verbose = True
            argv.pop(i)
            continue
        if a == "--save":
            save_blend = True
            argv.pop(i)
            continue
        if a == "--photoreal":
            photoreal = True
            argv.pop(i)
            continue
        if a.startswith("--engraving="):
            _, val = a.split("=", 1)
            engraving_default = val
            argv.pop(i)
            continue
        i += 1

    # Alternatively enable via env var
    if os.environ.get("USE_GEMINI_API") in ("1", "true", "True"):
        use_api = True

    user_req = " ".join(argv)

    # Build runtime config from env and CLI flags
    config = BridgeConfig.from_env()
    config.verbose = verbose
    config.save_blend = save_blend
    config.photoreal = photoreal
    config.engraving_default = engraving_default

    # Support a simple clarification loop: Gemini can return {"clarify": ["q1", ...]}
    current_req = user_req
    while True:
        if use_api:
            gresp = call_gemini_api(current_req)
        else:
            gresp = call_gemini_cli(current_req)

        # If Gemini asks for clarification, interact with the user and resend
        if isinstance(gresp, dict) and "clarify" in gresp:
            questions = gresp.get("clarify") or []
            if not isinstance(questions, list):
                questions = [str(questions)]
            answers = []
            print("Gemini requests clarification:")
            for q in questions:
                a = input(str(q) + " \n> ")
                answers.append({"question": q, "answer": a})
            # Append clarifications to the prompt and retry
            clarification_text = "\n".join([f"Q: {x['question']} A: {x['answer']}" for x in answers])
            current_req = current_req + "\nClarifications:\n" + clarification_text
            continue

        tool = gresp.get("tool")
        params = gresp.get("params", {})
        print("Gemini suggested:", tool, params)

    # If we have a local mapping for high-level intents, use it
    if tool in _TOOL_MAPPINGS:
        try:
            mapped_result = _TOOL_MAPPINGS[tool](params, config)
            print(
                "Mapping handler result:",
                json.dumps(mapped_result, indent=2, ensure_ascii=False),
            )
        except Exception as e:
            print("Error while handling mapped tool:", str(e), file=sys.stderr)
            raise
    else:
        # Fallback: try to interpret common synonyms locally before calling MCP.
        try:
            t_lower = tool.lower() if isinstance(tool, str) else ""
        except Exception:
            t_lower = ""

        if any(x in t_lower for x in ("dice", "die", "d10")):
            try:
                print(
                    "Tool name looks like a dice/die intent — using local mapping to generate Blender code..."
                )
                mapped_result = handle_add_primitive_mapping(params or {})
                print(
                    "Fallback mapping handler result:",
                    json.dumps(mapped_result, indent=2, ensure_ascii=False),
                )
                # done
                return
            except Exception as e:
                print("Fallback mapping handler failed:", str(e), file=sys.stderr)

        # Directly call MCP tool by name; if it doesn't exist, give a clearer message
        try:
            result = call_mcp_tool(tool, params)
            print("MCP result:", json.dumps(result, indent=2, ensure_ascii=False))
        except requests.exceptions.HTTPError as e:
            print(
                f"MCP endpoint returned error when calling tool '{tool}': {e}",
                file=sys.stderr,
            )
            print(
                "Il semble que le serveur MCP n'expose pas un outil nommé '"
                + str(tool)
                + "'.",
                file=sys.stderr,
            )
            print(
                "Solution rapide: je peux mapper 'create_dice' ou 'create_die' vers le générateur local D10. Réessaie après correction ou demande-moi de l'ajouter.",
                file=sys.stderr,
            )
            raise


if __name__ == "__main__":
    # The CLI script is now a thin wrapper that builds the BridgeConfig and
    # delegates orchestration to the package-level dispatcher. This keeps the
    # script import-light and the orchestration testable.
    from blender_mcp.dispatcher import run_bridge

    # Parse flags in main() earlier and build config; reuse existing logic
    use_api = False
    argv = sys.argv[1:]
    if not argv:
        print(
            'Usage: python scripts/gemini_bridge.py [--use-api] [--verbose] [--save] [--photoreal] [--engraving=geometry|visual] "<user request>"'
        )
        sys.exit(1)

    verbose = False
    save_blend = False
    photoreal = False
    engraving_default = os.environ.get("GEMINI_BRIDGE_ENGRAVING", "geometry")
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--use-api":
            use_api = True
            argv.pop(i)
            continue
        if a == "--verbose":
            verbose = True
            argv.pop(i)
            continue
        if a == "--save":
            save_blend = True
            argv.pop(i)
            continue
        if a == "--photoreal":
            photoreal = True
            argv.pop(i)
            continue
        if a.startswith("--engraving="):
            _, val = a.split("=", 1)
            engraving_default = val
            argv.pop(i)
            continue
        i += 1

    user_req = " ".join(argv)
    cfg = BridgeConfig.from_env()
    cfg.verbose = verbose
    cfg.save_blend = save_blend
    cfg.photoreal = photoreal
    cfg.engraving_default = engraving_default

    run_bridge(user_req, cfg, use_api=use_api)
