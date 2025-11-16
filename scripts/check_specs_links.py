#!/usr/bin/env python3
"""
Check that referenced file paths in OpenSpec changes exist in the repository.

Usage: python scripts/check_specs_links.py
Exits 0 if all referenced paths exist, 1 otherwise and prints missing references.
"""
from pathlib import Path
import yaml
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "docs" / "IA_ASSISTANT" / "specs_index.yaml"


def load_index():
    if not INDEX_PATH.exists():
        print("specs_index.yaml not found. Run scripts/generate_specs_index.py first.")
        sys.exit(2)
    with INDEX_PATH.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return data


def main():
    data = load_index()
    missing = []
    for spec in data.get('specs', []):
        for ref in spec.get('referenced_paths', []):
            p = ROOT / ref
            if not p.exists():
                missing.append({'spec': spec.get('id'), 'path': ref})

    if missing:
        print('Missing referenced files found:')
        for m in missing:
            print(f"- spec: {m['spec']}; missing: {m['path']}")
        sys.exit(1)

    print('All referenced spec paths exist (or no references).')
    sys.exit(0)


if __name__ == '__main__':
    main()
