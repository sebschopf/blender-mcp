#!/usr/bin/env python3
"""
Outil diagnostique non-intrusif pour vérifier quel package 'blender_mcp' est résolu
selon la valeur de PYTHONPATH.

Usage (PowerShell) :
# sans PYTHONPATH
python tools/check_shim_imports.py

# avec PYTHONPATH pointant sur src (Windows PowerShell)
$env:PYTHONPATH = 'src'; python tools/check_shim_imports.py; Remove-Item Env:\PYTHONPATH
"""
from importlib import util, import_module, metadata
import importlib
import sys
import os
import types


def where_is_package(pkg_name: str):
    """
    Tentative non-invasive d'identifier le fichier __init__.py ou le package path
    sans exécuter le module plus que nécessaire.
    """
    try:
        # find_spec returns a ModuleSpec possibly with origin and submodule_search_locations
        spec = importlib.util.find_spec(pkg_name)
        if spec is None:
            return None
        origin = getattr(spec, "origin", None)
        loader = getattr(spec, "loader", None)
        sub_locations = getattr(spec, "submodule_search_locations", None)
        return {
            "name": pkg_name,
            "origin": origin,
            "loader": loader.__class__.__name__ if loader else None,
            "submodule_search_locations": list(sub_locations) if sub_locations else None,
        }
    except Exception as e:
        return {"error": repr(e)}


def main():
    pkg = "blender_mcp"
    print("Python executable:", sys.executable)
    print("sys.path (first 10):")
    for p in sys.path[:10]:
        print("  ", p)
    print("\nFinding spec for package:", pkg)
    info = where_is_package(pkg)
    if info is None:
        print("Package spec not found (find_spec returned None).")
    else:
        if "error" in info:
            print("Error while locating package:", info["error"])
        else:
            print("Spec info:")
            for k, v in info.items():
                print(f"  {k}: {v}")
    # Additionally attempt a very safe import of the package object but protect against heavy code:
    print("\nAttempting safe import (importlib.import_module) with guard — will avoid calling attributes.")
    try:
        mod = import_module(pkg)
        print("Imported module object:", mod)
        # show __file__ if available
        print("Module __file__:", getattr(mod, "__file__", None))
        # show whether it's a package
        print("Is package (has __path__):", hasattr(mod, "__path"))
    except Exception as e:
        print("Safe import raised exception (studio may be expected):", repr(e))
    print("\nRecommendation: run this script with and without PYTHONPATH=src to compare results.")


if __name__ == "__main__":
    main()
