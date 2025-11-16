import importlib
import sys
from pathlib import Path

import yaml


def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_services_registry_covered_in_docs():
    # Ensure src is on path
    sys.path.insert(0, str(Path("src").resolve()))

    registry = importlib.import_module("blender_mcp.services.registry")

    services = set(registry.list_services())

    services_index = load_yaml("docs/IA_ASSISTANT/services_index.yaml") or {}
    index_names = {s["name"] for s in services_index.get("services", [])}

    missing_in_index = sorted(services - index_names)

    assert not missing_in_index, (
        "Missing services in docs/IA_ASSISTANT/services_index.yaml: " + ", ".join(missing_in_index)
    )


def test_services_metadata_covered():
    sys.path.insert(0, str(Path("src").resolve()))
    registry = importlib.import_module("blender_mcp.services.registry")
    services = set(registry.list_services())

    metadata = load_yaml("docs/IA_ASSISTANT/services_metadata.yaml") or {}
    metadata_names = {m.get("name") for m in metadata.get("services_metadata", [])}

    missing_meta = sorted(services - metadata_names)

    assert not missing_meta, (
        "Missing metadata entries in docs/IA_ASSISTANT/services_metadata.yaml for: " + ", ".join(missing_meta)
    )
