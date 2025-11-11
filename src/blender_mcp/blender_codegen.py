"""Thin compatibility façade for the relocated codegen package.

The implementation now lives in ``blender_mcp.codegen.blender_codegen``.
This module keeps the old import path working while the refactor is in
progress.
"""

from .codegen.blender_codegen import append_save_blend, generate_primitive_code  # noqa: F401

__all__ = ["generate_primitive_code", "append_save_blend"]
