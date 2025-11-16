#!/usr/bin/env python3
"""
Synchronize OpenSpec change directories into `docs/IA_ASSISTANT/specs/<id>/`.

For each `openspec/changes/<id>/` this script will create/refresh a folder
under `docs/IA_ASSISTANT/specs/<id>/` containing:
 - copy of `proposal.md`, `README.md`, `tasks.md` (if present)
 - copy of `specs/` listing (not copying spec files themselves)
 - `metadata.yaml` if present in change dir
 - `index.yaml` summarizing files present, referenced_paths, and missing refs

This makes it fast for IA and humans to find the spec + related artifacts.
"""
from pathlib import Path
import yaml
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
CHANGES_DIR = ROOT / "openspec" / "changes"
OUT_ROOT = ROOT / "docs" / "IA_ASSISTANT" / "specs"
MISSING_PATH = ROOT / "docs" / "IA_ASSISTANT" / "missing_spec_refs.yaml"


def load_missing_refs():
    if not MISSING_PATH.exists():
        return {}
    with MISSING_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    out = {}
    for s in data.get("specs", []):
        out[s.get("id")] = s.get("missing_paths", [])
    return out


def copy_if(src: Path, dst: Path):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def list_spec_files(specs_dir: Path):
    if not specs_dir.exists():
        return []
    files = []
    for p in sorted(specs_dir.rglob("*")):
        if p.is_file():
            files.append(str(p.relative_to(ROOT).as_posix()))
    return files


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    missing = load_missing_refs()
    for change in sorted(CHANGES_DIR.iterdir()):
        if not change.is_dir():
            continue
        cid = change.name
        out_dir = OUT_ROOT / cid
        # clear existing index files but keep full copy behavior idempotent
        out_dir.mkdir(parents=True, exist_ok=True)

        # copy common files
        for name in ("proposal.md", "README.md", "tasks.md", "metadata.yaml"):
            src = change / name
            dst = out_dir / name
            copy_if(src, dst)

        # summarize specs subdir
        specs_sub = change / "specs"
        specs_list = list_spec_files(specs_sub)
        # build index
        index = {
            "id": cid,
            "path": str(change.relative_to(ROOT).as_posix()),
            "files_present": [],
            "referenced_paths": [],
            "missing_refs": missing.get(cid, []),
        }

        # gather referenced_paths heuristically from proposal/tasks/README
        refs = set()
        for txtfile in (change / "proposal.md", change / "tasks.md", change / "README.md"):
            if txtfile.exists():
                try:
                    txt = txtfile.read_text(encoding="utf-8")
                except Exception:
                    txt = ""
                # lines that look like paths (basic heuristic)
                for line in txt.splitlines():
                    line = line.strip()
                    if line.startswith("src/") or line.startswith("tests/") or line.startswith("scripts/") or "openspec/changes/" in line:
                        refs.add(line.strip("`"))
        index["referenced_paths"] = sorted(refs)

        # files present: list important files in the change dir
        # also add any explicit files listed in metadata.yaml
        meta = change / "metadata.yaml"
        if meta.exists():
            try:
                md = yaml.safe_load(meta.read_text(encoding="utf-8")) or {}
                for f in md.get("files", []):
                    index["files_present"].append(f)
                for f in md.get("referenced_paths", []):
                    if f not in index["referenced_paths"]:
                        index["referenced_paths"].append(f)
            except Exception:
                pass

        index["spec_files"] = specs_list

        # write index.yaml
        with (out_dir / "index.yaml").open("w", encoding="utf-8") as f:
            yaml.safe_dump(index, f, sort_keys=False, allow_unicode=True)

        print(f"Wrote spec summary for: {cid} -> {out_dir}")


if __name__ == "__main__":
    main()
