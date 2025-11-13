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

Canonical source
----------------
Les codes ci‑dessus sont définis comme `Literal` dans `src/blender_mcp/errors.py`:

```python
ErrorCode = Literal[
		"invalid_command",
		"invalid_command_type",
		"policy_denied",
		"not_found",
		"invalid_params",
		"timeout",
		"handler_error",
		"external_error",
		"internal_error",
]
```

Utilisez toujours `error_code_for_exception(exc)` pour convertir une exception canonique
en code machine‑readable. Cela évite la duplication du mapping dans les services/adapters.

Wrapper / services convention
-----------------------------
- Les services lèvent des exceptions (`InvalidParamsError`, `ExternalServiceError`, etc.).
- Les adapters (CommandAdapter, ASGI, MCP tool decorators) transforment ces exceptions en
	payloads `{status:"error", message:<str>, error_code:<ErrorCode>}`.
- Ne retournez pas vous‑même des dicts d'erreur dans les services — utilisez les exceptions.
- Pour des validations complexes de paramètres, inclure un détail via `InvalidParamsError(fields=...)`.

TypedDicts exportés
-------------------
- `SuccessResult`: `{status: str, result: Any}` (chemin succès).
- `ErrorResult`: `{status: str, message: str, error_code: str}` (chemin erreur normalisé).
- `ErrorInfo`: `{message: str, error_code: ErrorCode}` shape compacte pour log/audit interne.

Mise à jour future
------------------
Ajouter un nouveau code = ajouter le Literal dans `errors.py` + tests de mapping dans
`tests/test_command_adapter_errors.py`. Si le contrat public change (suppression d'un
champ ou renommage), créer une spec sous `openspec/changes/<id>/` avant merge.

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
Les wrappers MCP doivent vérifier uniquement `status` et `error_code` (pas d'heuristiques
sur le contenu du message) pour éviter les couplages fragiles.
