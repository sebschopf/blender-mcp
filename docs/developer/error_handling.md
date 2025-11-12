# Error handling strategy (developer notes)

Résumé court
---------------
Cette page décrit la stratégie de normalisation des erreurs dans `blender_mcp`.
L'objectif est d'avoir :

- Exceptions typées pour la logique applicative.
- Mapping centralisé exceptions → réponses normalisées (stable `error_code`).
- Audit/logging minimal pour tracer décisions (policy deny / handler error / timeouts).

Contrat (pour `CommandAdapter.dispatch_command`)
------------------------------------------------
- Input: mapping JSON-like {"type": str, "params": dict}
- Output success: {"status":"success", "result": Any}
- Output error (backwards-compatible + enhanced): {"status":"error", "message": str, "error_code": str}

Error codes (stable)
---------------------
- invalid_command: input not a dict
- invalid_command_type: missing/invalid "type"
- invalid_params: handler raised InvalidParamsError
- not_found: handler missing
- policy_denied: policy check rejected
- timeout: handler timed out
- handler_error: handler raised an error wrapped in HandlerError
- external_error: downstream service failed
- internal_error: unexpected error

Where to extend
-----------------
- Add new exception types in `src/blender_mcp/errors.py`.
- Extend `CommandAdapter._map_exception` to map them to `error_code`.

Logging / audit
----------------
Use `blender_mcp.logging_utils.log_action(source, action, params, result)` to
emit a concise INFO event for successful flows and WARN/ERROR for failures.

Example
-------
Handler raises `InvalidParamsError("missing field X")` → `CommandAdapter` returns:

```
{"status": "error", "message": "missing field X", "error_code": "invalid_params"}
```

PR checklist for reviewers
-------------------------
- Small, focused commits
- Tests for each new exception mapping
- Ruff/black/isort formatting OK
- Mypy: no new blocking errors
- If API is changed (removing keys), add an `openspec/changes/<id>/` proposal

Notes
-----
This is intentionally conservative: we add a machine-friendly `error_code` while
keeping existing `status` and `message` keys for backward compatibility.
