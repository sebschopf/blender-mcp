import os
import sys


def _add_repo_root_to_path():
    # Ensure the repository root is on sys.path so top-level modules like
    # `addon.py` can be imported by tests running from the tests/ directory.
    here = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(here, os.pardir))
    # Prefer the `src/` package layout when available to avoid importing the
    # top-level shim package accidentally. Insert `src` first so `import
    # blender_mcp...` resolves to `src/blender_mcp` during tests.
    src_dir = os.path.join(repo_root, "src")
    if os.path.isdir(src_dir) and src_dir not in sys.path:
        # Only add `src` to sys.path so imports resolve to the refactored
        # package under `src/blender_mcp`. Do not insert the repo root to
        # avoid accidental double-imports of the package under different
        # paths which can break `isinstance` checks in tests.
        sys.path.insert(0, src_dir)


_add_repo_root_to_path()


# Fail-fast check: ensure the `blender_mcp` package resolves to the `src/` layout
# to prevent duplicate imports (which break runtime identity checks).
try:
    import importlib

    mod = importlib.import_module("blender_mcp")
    mod_file = getattr(mod, "__file__", None)
    # If the resolved module file is not under the src/ directory, fail early
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    src_dir = os.path.join(repo_root, "src")
    if (
        not mod_file
        or os.path.commonpath([
            os.path.abspath(mod_file),
            os.path.abspath(src_dir),
        ])
        != os.path.abspath(src_dir)
    ):
        msg = (
            "blender_mcp import did not resolve to 'src/blender_mcp'.\n"
            f"Resolved module: {getattr(mod, '__name__', None)!r} at {mod_file!r}\n"
            "Tests require the refactored package under `src/` to be first on sys.path.\n"
            "If you have a legacy top-level `blender_mcp/` directory, move it out of the "
            "repo root or ensure `src/` is ahead of it on `sys.path`."
        )
        print(msg)
        raise RuntimeError(msg)
except Exception:
    # Re-raise to fail tests early; this keeps CI deterministic and surfaces
    # import-resolution issues immediately rather than producing intermittent
    # `isinstance` failures later in the run.
    raise


# Check for duplicate module objects pointing to the same source file.
# Duplicate entries in `sys.modules` that reference the same file but under
# different module names can cause `isinstance` to fail because classes are
# distinct objects from different module objects. Detect and fail fast.
import sys as _sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
src_dir = os.path.abspath(os.path.join(repo_root, "src"))
file_map: dict[str, list[str]] = {}
for name, mod in list(_sys.modules.items()):
    mf = getattr(mod, "__file__", None)
    if not mf:
        continue
    try:
        mf_abs = os.path.abspath(mf)
    except Exception:
        continue
    if not mf_abs.startswith(src_dir):
        continue
    file_map.setdefault(mf_abs, []).append(name)

duplicates = {f: names for f, names in file_map.items() if len(names) > 1}
if duplicates:
    # Report the first duplicate for clarity and fail early.
    dup_file, names = next(iter(duplicates.items()))
    msg = (
        "Duplicate module entries detected for the same source file, which can\n"
        "cause runtime identity mismatches (e.g. `isinstance` failing).\n"
        f"File: {dup_file}\n"
        f"Module names: {names!r}\n"
        "Ensure `src/` is first on sys.path and remove any legacy top-level shims."
    )
    print(msg)
    raise RuntimeError(msg)


# Monkeypatch builtins.__import__ to deduplicate modules as they are imported.
# This ensures that if a module file from `src/` is loaded under multiple
# names, later imports are normalized to the canonical module object.
try:
    import builtins as _builtins
    _orig_import = _builtins.__import__

    def _patched_import(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: C901
        mod = _orig_import(name, globals, locals, fromlist, level)
        try:
            # use the module-level `sys` to avoid re-triggering imports
            _sys = sys
            # build file -> module names map for modules under src_dir
            file_map_local: dict[str, list[str]] = {}
            for n, m in list(_sys.modules.items()):
                mf = getattr(m, "__file__", None)
                if not mf:
                    continue
                try:
                    mf_abs = os.path.abspath(mf)
                except Exception:
                    continue
                if not mf_abs.startswith(src_dir):
                    continue
                file_map_local.setdefault(mf_abs, []).append(n)
            for mf, names in file_map_local.items():
                if len(names) <= 1:
                    continue
                canonical = names[0]
                canonical_mod = _sys.modules.get(canonical)
                if canonical_mod is None:
                    continue
                for other in names[1:]:
                    if _sys.modules.get(other) is not canonical_mod:
                        # Replace the duplicate module object with the canonical one
                        _sys.modules[other] = canonical_mod
        except Exception:
            # Best-effort deduplication; ignore errors to avoid breaking imports during test startup.
            pass
        return mod

    _builtins.__import__ = _patched_import
except Exception:
    # Best-effort; don't fail test startup if monkeypatching import fails.
    pass
