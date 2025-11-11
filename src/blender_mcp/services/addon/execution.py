"""Code execution helpers extracted from addon handlers."""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from typing import Any, Dict


def execute_code(code: str) -> Dict[str, Any]:
    try:
        import bpy

        namespace = {"bpy": bpy}
        capture_buffer = io.StringIO()
        with redirect_stdout(capture_buffer):
            exec(code, namespace)
        captured_output = capture_buffer.getvalue()
        return {"executed": True, "result": captured_output}
    except Exception as e:
        raise Exception(f"Code execution error: {str(e)}")


__all__ = ["execute_code"]
