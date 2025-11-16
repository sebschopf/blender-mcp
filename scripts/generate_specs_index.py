#!/usr/bin/env python3
"""
Generate a machine-readable index of OpenSpec changes under `openspec/changes/`.

Output: `docs/IA_ASSISTANT/specs_index.yaml`

Each entry contains:
 - id (folder name)
 - title (first heading or first line of spec.md)
 - has_spec (bool)
 - files (list of files in the change folder)
 - referenced_paths (list of file paths mentioned in the spec text)
"""
from pathlib import Path
import re
import yaml


ROOT = Path(__file__).resolve().parents[1]
OPENSPEC_DIR = ROOT / "openspec" / "changes"
OUT_PATH = ROOT / "docs" / "IA_ASSISTANT" / "specs_index.yaml"


def extract_title(text: str) -> str:
    # Try to find a Markdown H1/H2 or first non-empty line
    m = re.search(r'^#\s+(.+)', text, flags=re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r'^##\s+(.+)', text, flags=re.M)
    if m:
        return m.group(1).strip()
    # fallback: first non-empty line
    for line in text.splitlines():
        s = line.strip()
        if s:
            return s
    return ''


def find_referenced_paths(text: str):
    # crude: find backticked paths or 'src/' or 'docs/' occurrences
    refs = set()
    for m in re.finditer(r'`([^`]+)`', text):
        refs.add(m.group(1))
    for m in re.finditer(r'((?:src|docs|tests|openspec)[^\s,;\)\]]+)', text):
        refs.add(m.group(1).strip())
    return sorted(refs)


def gather():
    out = {"specs": []}
    if not OPENSPEC_DIR.exists():
        print("No openspec/changes directory found")
        return out

    for change_dir in sorted(OPENSPEC_DIR.iterdir()):
        if not change_dir.is_dir():
            continue
        entry = {"id": change_dir.name}
        files = []
        referenced = set()
        title = ''
        for p in sorted(change_dir.rglob('*')):
            rel = str(p.relative_to(ROOT))
            files.append(rel)
            if p.name.lower().endswith('.md'):
                try:
                    text = p.read_text(encoding='utf-8')
                except Exception:
                    text = ''
                if not title and 'spec.md' in p.name.lower():
                    title = extract_title(text)
                refs = find_referenced_paths(text)
                for r in refs:
                    referenced.add(r)
        entry['title'] = title
        entry['has_spec'] = any(p.name.lower() == 'spec.md' for p in change_dir.glob('**/*'))
        entry['files'] = files
        entry['referenced_paths'] = sorted(referenced)
        out['specs'].append(entry)
    return out


def main():
    out = gather()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open('w', encoding='utf-8') as f:
        yaml.safe_dump(out, f, sort_keys=False, allow_unicode=True)
    print(f'Wrote specs index to: {OUT_PATH}')


if __name__ == '__main__':
    main()
