**Addon Layout**

This project provides two complementary artifacts related to the Blender add-on:

- **Top-level shim**: `addon.py` at the repository root. This is the minimal, import-safe entrypoint that Blender expects when installing the add-on directly from source or from a zip containing the repository root. `addon.py` is intentionally small and defers non-essential imports (Blender UI, operators) so it can be imported in non‑Blender environments (tests, CI).

- **Packaged implementation**: `src/blender_mcp/services/addon/`  the authoritative implementation lives here. This is the code base used by the packaged `blender_mcp` distribution and by the test suite. It contains modules such as `objects.py`, `polyhaven.py`, `scene.py`, `textures.py`, and `__init__.py` that provide the actual functionality.

Why both exist
- Blender commonly expects a top-level `addon.py` (or a folder containing it) when the add-on is installed directly. The project also adopted a `src/` layout so the Python package `blender_mcp` can be imported and packaged cleanly. The root shim keeps Blender compatibility while `src/` provides a clean packaging layout used by tests and distribution.

Developer guidance
- To run tests and avoid duplicate-import identity problems, always prefer the `src/` layout on the import path. This prevents the same package code from being importable under two different module names (which can break `isinstance` checks).

Local test commands (PowerShell):

```powershell
# Preferred: include the repo root after `src` so top-level shims like `addon.py` can be imported
$Env:PYTHONPATH='src;.'
pytest -q
Remove-Item Env:PYTHONPATH
```

Notes on packaging for Blender
- When creating a zip to install in Blender, include the top-level `addon.py` at the repository root (or a zip root containing it). The `addon.py` shim will lazily import the package implementation at runtime.

If you plan to produce a PyPI-style package, `src/blender_mcp` remains the canonical package source; `addon.py` can remain as a convenience shim for manual installs and Blender compatibility.

Troubleshooting
- If you see intermittent `isinstance` or identity mismatches in tests, verify that `src/` is first on `sys.path` and that no legacy top-level `blender_mcp/` package exists at the repo root. The test bootstrapping in `tests/conftest.py` enforces `src/` first by design.

If you are unsure which implementation is authoritative, prefer the files under `src/blender_mcp/services/addon/`.
