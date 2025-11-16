#!/usr/bin/env python3
"""
Generate a draft `docs/IA_ASSISTANT/services_metadata_full_draft.yaml` from
`blender_mcp.services.registry.list_services()`.

This script is safe to run in PR CI: it emits a draft YAML that maintainers
can review and refine. It tries to preserve `tests` mappings from
`docs/IA_ASSISTANT/services_index.yaml` when available.
"""
from pathlib import Path
import sys
import argparse
import yaml
import importlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", default="docs/IA_ASSISTANT/services_metadata_full_draft.yaml")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    try:
        registry = importlib.import_module("blender_mcp.services.registry")
    except Exception as e:
        print("Failed to import registry:", e)
        sys.exit(2)

    services = registry.list_services()

    # Load existing services_index to copy tests if present
    services_index_path = repo_root / "docs" / "IA_ASSISTANT" / "services_index.yaml"
    services_index = {}
    if services_index_path.exists():
        with open(services_index_path, "r", encoding="utf-8") as f:
            try:
                services_index = yaml.safe_load(f) or {}
            except Exception:
                services_index = {}

    index_by_name = {s.get("name"): s for s in services_index.get("services", [])}

    out = {"services_metadata": []}
    for name in services:
        fn = registry.get_service(name)
        module = getattr(fn, "__module__", "src.blender_mcp.services")
        callable_name = getattr(fn, "__name__", name)
        entry = {
            "name": name,
            "module": module,
            "callable": callable_name,
            "description": "(draft) Auto-generated metadata entry. Please refine.",
            "params": {},
        }
        idx = index_by_name.get(name)
        if idx:
            if idx.get("tests"):
                entry["tests"] = idx.get("tests")
            if idx.get("description"):
                entry["description"] = idx.get("description")
        out["services_metadata"].append(entry)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, sort_keys=False, default_flow_style=False)

    print(f"Wrote draft metadata to: {out_path}")


if __name__ == "__main__":
    main()
