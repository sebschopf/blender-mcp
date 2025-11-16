#!/usr/bin/env python3
"""
Validate IA assistant YAML files against lightweight JSON Schemas.

Requires: pyyaml, jsonschema

Usage:
  python scripts/validate_ia_yaml.py

Exits with 0 on success, non-zero on validation error.
"""
import json
import sys
from pathlib import Path

try:
    import yaml
    import jsonschema
except Exception as e:
    print("Missing runtime dependency:", e)
    print("Install with: pip install pyyaml jsonschema")
    sys.exit(2)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "docs" / "IA_ASSISTANT" / "schemas"
FILES_TO_VALIDATE = [
    (ROOT / "docs" / "IA_ASSISTANT" / "services_index.yaml", SCHEMA_DIR / "services_index.schema.json"),
    (ROOT / "docs" / "IA_ASSISTANT" / "services_metadata.yaml", SCHEMA_DIR / "services_metadata.schema.json"),
    (ROOT / "docs" / "IA_ASSISTANT" / "endpoints.yaml", SCHEMA_DIR / "endpoints.schema.json"),
]


def load_yaml(path: Path):
    text = path.read_text(encoding="utf-8")
    # If the file contains a fenced code block (```yaml ... ```), strip it.
    if text.lstrip().startswith("```"):
        lines = text.splitlines()
        # remove first fence line
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        # remove trailing fence if present
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return yaml.safe_load(text)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    errors = []
    recommendations = []

    for yaml_path, schema_path in FILES_TO_VALIDATE:
        if not yaml_path.exists():
            errors.append(f"Missing file: {yaml_path}")
            continue
        if not schema_path.exists():
            errors.append(f"Missing schema: {schema_path}")
            continue

        data = load_yaml(yaml_path)
        schema = load_json(schema_path)

        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as ve:
            # Keep validation lenient: record errors but also provide non-blocking recommendations
            errors.append(f"Validation error for {yaml_path}: {ve.message}")
            recommendations.append(f"Consider relaxing or aligning data for {yaml_path}: {ve.message}")

    if errors:
        print("IA YAML validation failed:")
        for e in errors:
            print(" -", e)
        if recommendations:
            print('\nRecommendations (non-blocking):')
            for r in recommendations:
                print(' -', r)
        return 1

    print("IA YAML validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
