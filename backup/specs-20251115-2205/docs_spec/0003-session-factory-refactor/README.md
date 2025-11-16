# 0003 - Central session factory and conservative session-injection

Résumé
------
Ce changement introduit une usine centralisée de sessions HTTP et une
approche conservatrice de migration des helpers réseau afin de faciliter
le partage de connexions et l'injection de `requests.Session` pour les
tests et les usages embarqués.

Principaux points
- Ajout de `src/blender_mcp/http.py` fournissant `get_session()` et
  `reset_session()`.
- Migration conservative : les helpers réseau acceptent désormais un
  paramètre optionnel `session: Optional[requests.sessions.Session]`. Si
  `session` est fourni, il est utilisé ; sinon on retombe sur
  `requests.get/post` (comportement backward-compatible) ou sur
  `get_session()` selon le module.

Fichiers modifiés/ajoutés (résumé)
- `src/blender_mcp/http.py` (nouveau)
- `src/blender_mcp/downloaders.py` (acceptation de `session`)
- `src/blender_mcp/polyhaven.py` / `src/blender_mcp/services/addon/polyhaven.py`
- `src/blender_mcp/sketchfab.py`
- `src/blender_mcp/hyper3d.py`
- Tests ajoutés: `tests/test_session_injection_*.py` couvrant les chemins
  injectés.

Raisons et implications
- Facilite la réutilisation des connexions, le contrôle des en-têtes
  par défaut et la configuration centralisée des retries/proxies.
- Permet d'injecter des sessions factices/faites sur-mesure dans les
  tests sans casser les tests existants qui patchent `requests.get`.

Validation
- La suite de tests unitaire a été exécutée localement et est verte
  (pytest : 157 passed, 0 failed).

Migration future
- On peut envisager de remplacer progressivement le fallback `requests.*`
  par `get_session()` global lorsque tous les call-sites accepteront la
  session injectée.

Notes de PR
- Valider openspec : `openspec validate --strict`.
- Avant merge : exécuter `python -m pytest` et relire `PR_NOTES_SESSION_REFACTOR.md`.
