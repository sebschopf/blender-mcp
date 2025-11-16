#!/usr/bin/env python3
"""
Export missing referenced paths from the specs index into a machine-readable YAML file.

Usage: python scripts/export_missing_spec_refs.py
Writes: docs/IA_ASSISTANT/missing_spec_refs.yaml
"""
from pathlib import Path
import yaml
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "docs" / "IA_ASSISTANT" / "specs_index.yaml"
OUT_PATH = ROOT / "docs" / "IA_ASSISTANT" / "missing_spec_refs.yaml"


def load_index():
    if not INDEX_PATH.exists():
        print("specs_index.yaml not found. Run scripts/generate_specs_index.py first.")
        sys.exit(2)
    with INDEX_PATH.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return data


def find_missing(data):
    missing = {}
    for spec in data.get('specs', []):
        sid = spec.get('id') or spec.get('title')
        refs = spec.get('referenced_paths') or []
        miss = []
        for ref in refs:
            p = ROOT / ref
            if not p.exists():
                miss.append(ref)
        if miss:
            missing[sid] = miss
    return missing


def main():
    data = load_index()
    missing = find_missing(data)
    out = {
        'generated_from': str(INDEX_PATH.relative_to(ROOT)),
        'missing_count': sum(len(v) for v in missing.values()),
        'specs': [{'id': k, 'missing_paths': v} for k, v in missing.items()],
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open('w', encoding='utf-8') as f:
        yaml.safe_dump(out, f, sort_keys=False, allow_unicode=True)

    print(f"Wrote missing refs report to: {OUT_PATH}")


if __name__ == '__main__':
    main()
