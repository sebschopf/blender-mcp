"""Top-level shim package used for tests during refactor.

This package shadows the src layout so unit tests that import
``blender_mcp.*`` can pick up refactored modules placed under
``src/blender_mcp`` while the migration is in progress.

Strategy:
	- If ``src/blender_mcp`` exists, add it to this package's
		``__path__`` so normal ``import blender_mcp.connection`` will
		resolve to the refactored module in ``src/``. This keeps tests
		and runtime imports working during the transition and is
		intentionally temporary.
"""

from pathlib import Path

# prefer any modules inside src/blender_mcp if present
_pkg_dir = Path(__file__).parent
_candidate = (_pkg_dir.parent / "src" / "blender_mcp").resolve()
if _candidate.is_dir():
		# insert at front so src/ takes precedence over the legacy files
		__path__.insert(0, str(_candidate))

__all__ = ["server"]
