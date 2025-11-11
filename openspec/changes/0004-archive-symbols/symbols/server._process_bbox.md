# Symbol: `_process_bbox` (src/blender_mcp/server.py)

Location: `src/blender_mcp/server.py`

Current status:
- Small validation/normalization helper used by the server façade for tests.

Proposal:
- Keep the helper but add a small spec that documents its expected input shapes and error cases. Consider moving to a `validators` module if reuse grows.

Acceptance criteria:
- Unit tests validate the six explicit behaviours: None -> None, wrong shape raises, negative values raise, zero max raises, scaling behaviour boundary checks.

Tasks:
- Reference existing `tests/test_bbox.py` and ensure coverage meets acceptance criteria.
