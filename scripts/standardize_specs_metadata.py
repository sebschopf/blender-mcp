#!/usr/bin/env python3
"""
Standardize spec metadata for IA assistant folders.

Reads `docs/IA_ASSISTANT/specs/<id>/index.yaml` (created by
`scripts/sync_specs_to_ia_assistant.py`) and emits a normalized
`metadata.yaml` in the same folder following `docs/IA_ASSISTANT/specs_schema.yaml`.

Fields produced: id, title, summary, status, owner, files, referenced_paths,
acceptance_tests, missing_refs, spec_files
"""
from pathlib import Path
import yaml
import sys

ROOT = Path(__file__).resolve().parents[1]
IA_SPECS = ROOT / "docs" / "IA_ASSISTANT" / "specs"


def read_index(path: Path):
    idx = path / "index.yaml"
    if not idx.exists():
        return None
    try:
        return yaml.safe_load(idx.read_text(encoding="utf-8")) or {}
    except Exception:
        return None


def read_text_first_paragraph(path: Path):
    if not path.exists():
        return ""
    txt = path.read_text(encoding="utf-8")
    # strip fences and markdown markers
    lines = [l.rstrip() for l in txt.splitlines()]
    para = []
    for l in lines:
        if l.strip() == "":
            if para:
                break
            else:
                continue
        para.append(l)
    return " ".join(para).strip()


def main():
    if not IA_SPECS.exists():
        print("No specs directory found under docs/IA_ASSISTANT/specs/")
        return

    for spec_dir in sorted(IA_SPECS.iterdir()):
        if not spec_dir.is_dir():
            continue
        idx = read_index(spec_dir)
        if idx is None:
            print(f"Skipping {spec_dir.name}: no index.yaml")
            continue

        # Base metadata
        meta = {}
        meta["id"] = idx.get("id", spec_dir.name)

        # Try to populate title/summary from any available files
        title = None
        summary = None
        owner = None

        # prefer existing metadata copied in spec_dir
        existing_meta = spec_dir / "metadata.yaml"
        if existing_meta.exists():
            try:
                em = yaml.safe_load(existing_meta.read_text(encoding="utf-8")) or {}
                title = em.get("title") or em.get("id")
                summary = em.get("summary")
                owner = em.get("owner")
                # keep files list if present
                files_from_em = em.get("files") or []
            except Exception:
                files_from_em = []
        else:
            files_from_em = []

        # if no title, probe README/proposal
        if not title:
            title = read_text_first_paragraph(spec_dir / "README.md")
            if title:
                # take first line as title if contains colon or is short
                title = title.splitlines()[0][:120]
        if not summary:
            summary = read_text_first_paragraph(spec_dir / "proposal.md") or read_text_first_paragraph(spec_dir / "README.md")

        meta["title"] = title or spec_dir.name
        meta["summary"] = summary or ""

        # owner: try to infer from existing metadata or leave empty
        meta["owner"] = owner or (em.get("owner") if 'em' in locals() and isinstance(em, dict) else None) or ""

        # files / refs
        meta["files"] = list(dict.fromkeys(idx.get("files_present", []) + files_from_em))
        meta["referenced_paths"] = sorted(set(idx.get("referenced_paths", [])))
        meta["acceptance_tests"] = []
        meta["missing_refs"] = idx.get("missing_refs", [])
        meta["spec_files"] = idx.get("spec_files", [])

        # status: if missing_refs present -> draft, else ready
        meta["status"] = "draft" if meta["missing_refs"] else "ready"

        # write normalized metadata.yaml
        out = spec_dir / "metadata.yaml"
        with out.open("w", encoding="utf-8") as f:
            yaml.safe_dump(meta, f, sort_keys=False, allow_unicode=True)

        print(f"Wrote standardized metadata for {spec_dir.name}")


if __name__ == "__main__":
    main()
