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

Politique de mapping exceptions → codes
---------------------------------------
Cette politique définit comment chaque exception canonique est transformée en `error_code`.
Règles:

1. Ordre de spécificité: le helper `error_code_for_exception` vérifie les sous‑classes les plus spécifiques en premier (ex. `InvalidParamsError`) avant des classes plus générales. Ajoutez les nouveaux cas au bon endroit pour éviter qu'une exception soit capturée par un test précédent trop général.
2. Fallback stable: toute exception héritant de `BlenderMCPError` qui n'est pas reconnue retourne `internal_error`. Ne jamais exposer la classe brute aux consommateurs externes; l'`error_code` est la surface contractuelle.
3. Nommage: les codes sont snake_case, orientés domaine ("invalid_params") plutôt qu'implémentation (pas "value_error"). Choisir un nom reflétant l'intention métier et réutilisable indépendamment de la technologie interne.
4. Ajout d'un nouveau code: ajouter le Literal dans `ErrorCode`, étendre `error_code_for_exception`, créer/mettre à jour un test dédié (ex: `tests/test_errors_mapping.py`), et documenter dans cette section. Si le nouveau code est destiné à être consommé publiquement (changement de comportement observable), ouvrir une proposition sous `openspec/changes/<id>/` avant merge.
5. Pas de parsing des messages: les adapters ne dérivent jamais un `error_code` à partir du texte humain (`message`). Seule la classe d'exception décide du code. Cela garantit robustesse et évite les couplages fragiles.
6. Exceptions enrichies: les attributs additionnels (ex: `fields` dans `InvalidParamsError`) peuvent être utilisés pour construire des messages détaillés côté service, mais ne changent pas le `error_code`.
7. Stabilité: une fois publié, un `error_code` ne doit pas être renommé. Pour une nouvelle granularité, introduire un nouveau code et mapper l'ancien vers un comportement par défaut tant que les clients n'ont pas migré.
8. Sécurité: ne jamais inclure de détails sensibles (chemins système, tokens) dans les messages d'erreur. Le `error_code` suffit pour la logique machine; le `message` est destiné à l'observation humaine.

Table de correspondance actuelle:

| Exception                     | error_code       | Notes |
|-------------------------------|------------------|-------|
| InvalidParamsError            | invalid_params   | Paramètres manquants/invalides (peut contenir `fields`) |
| HandlerNotFoundError          | not_found        | Handler non enregistré ou nom inconnu |
| PolicyDeniedError             | policy_denied    | Rejet par une règle de sécurité/policy |
| ExecutionTimeoutError         | timeout          | Dépassement de temps configuré (ex: thread executor) |
| HandlerError                  | handler_error    | Exception levée dans le handler encapsulée |
| ExternalServiceError          | external_error   | Dépendance réseau/API tierce échouée |
| (toute autre BlenderMCPError) | internal_error   | Défaut de mapping explicite, scénario inattendu |

Scénario exemple (ajout d'une nouvelle exception):

1. Créer `class RateLimitExceededError(ExternalServiceError): pass` si spécifique à une intégration.
2. Décider si un nouveau code est nécessaire (ex: `rate_limited`). Si oui → ajouter à `ErrorCode`.
3. Étendre `error_code_for_exception` avant le bloc `ExternalServiceError` si on veut un code distinct.
4. Ajouter test: lever `RateLimitExceededError` et vérifier `error_code == 'rate_limited'`.
5. Mettre à jour cette section de politique + ouvrir spec si c'est une surface publique nouvelle.

Raisons de la politique:
- Prévisibilité pour les adapters (pas d'heuristiques).
- Simplicité d'extension (ajout = 3 modifications ciblées + test).
- Minimisation du couplage entre logique interne et protocole externe.

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
