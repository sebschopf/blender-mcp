<!-- Use this template when creating a new openspec change under openspec/changes/<id>/ -->

# <id>-short-title

## Title

Short, imperative title of the change (one line).

## Summary

A 1–3 sentence summary describing what the spec introduces or changes.

## Motivation

Why this change is needed, with links to related issues or PRs.

## Files

List of files this change introduces or intends to modify (relative paths):

- `src/...`
- `tests/...`
- `openspec/changes/<id>/spec.md`

## Referenced Paths

Machine‑readable list of repository paths, tests, commands, or symbols that the spec references.
These should be valid paths or single-line symbols (e.g. `src/blender_mcp/server.py`, `tests/test_foo.py`, `scripts/start-server.ps1`).

- `src/...`

## Acceptance Criteria / Tests

Minimum tests and behaviors required for this change to be accepted. Prefer specific test filenames or commands.

- `python -m pytest tests/test_xyz.py -q`

## Status

- `draft` | `ready` | `in-progress` | `done`

## Owner

Who is responsible for this change (GitHub handle or team).

## Notes

Any additional notes, example usage, or migration guidance.
