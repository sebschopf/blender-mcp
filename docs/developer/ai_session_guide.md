# Guide Session AI — blender-mcp

Ce fichier est conçu pour (re)donner rapidement à un assistant AI (ChatGPT / GitHub Copilot / autre) le contexte nécessaire pour continuer le travail sans perte d'information. Il résume l'architecture, l'état des tâches, les conventions, le workflow CI, et fournit des prompts prêts à l'emploi.

---
## 1. TL;DR (Résumé immédiat)
Architecture en refactorisation: séparation claire entre core (erreurs, dispatcher, connexion), services (logique métier), adapters (ASGI / embedded), UI Blender, clients (LLM/MCP). Objectif: éliminer les duplications (dispatchers multiples, server shims, services racine vs services/), uniformiser contrat de réponse (`status`, `result`, `error_code`). Registre unique en place; normalisation `send_command` implémentée (PR #22). Prochain focus: refactor SOLID du dispatcher, dépréciation des shims.

---
## 2. Couches d'Architecture (Modèle cible)
| Couche | Contenu | Rôle | Import recommandé |
|--------|---------|------|-------------------|
| Core | `errors.py`, `types.py`, `logging_utils.py` | Contrats & base stable | `from blender_mcp.errors import ...` |
| Dispatcher | `dispatchers/dispatcher.py` + façade `dispatcher.py` | Orchestration handlers | `from blender_mcp.dispatcher import Dispatcher` |
| Connexion | `services/connection/*` + shim `connection.py` | Transport + reassembly | `from blender_mcp.connection import BlenderConnection` |
| Services | `services/*.py` | Logique métier testable | `from blender_mcp.services.scene import get_scene_info` |
| Adapters | `asgi.py`, `servers/embedded_adapter.py` | Intégration HTTP / processus embarqué | `from blender_mcp.servers import start_server_process` |
| UI | `blender_ui/*`, `codegen/*` | Addon Blender (panel, opérateurs) | Blender runtime seulement |
| Clients | `gemini_client.py`, `mcp_client.py`, `http.py` | Accès LLM / MCP / HTTP | Tools externes |
| Legacy/Shims | `simple_dispatcher.py`, `server_shim.py`, `connection_core.py` | Compatibilité migratoire | À déprécier |

---
## 3. État Actuel (Phase et Avancement)
Branche active: `feature/errors-dispatcher-standardisation`.

Roadmap courante: Issue #19 — Registry & Endpoint Porting
https://github.com/sebschopf/blender-mcp/issues/19

Terminés:
- Standardisation erreurs (`ErrorCode`, `ErrorInfo`, mapping centralisé).
- Façade dispatcher unifiée + tests concurrency/timeout.
- Connexion: shim + injection `socket_factory` + tests fragments/timeout.
- Documentation politique mapping exceptions.
- Registre unique services/tools (`src/blender_mcp/services/registry.py`) + fallback dans le Dispatcher.
- Premiers endpoints portés dans `services/` et enregistrés: `scene`, `object`, `screenshot`, `execute`, `polyhaven.*`, `sketchfab.*`, `hyper3d.*`.
 - Normalisation `send_command` (services.connection) → retour dict complet; spec OpenSpec ajoutée; tests adaptés (PR #22).

Partiellement faits / À finaliser:
- Séparation façade connexion multi-mode en classes SRP (optionnel).
- Dépréciation modules dupliqués (simple_dispatcher, server shims, services racine). 

À venir (phases):
1. Refactor SOLID du dispatcher (isoler stratégies/executor/adapters) sans rupture publique.
2. Deprecation warnings systématiques + plan de retrait des shims (suppression après 2 cycles).
3. Migration résiduelle des services racine vers `services/` si restant.
4. Refactor connexion (classes séparées) si nécessaire stricte SRP.
5. Injection strategies (policy / parser / framing) dans dispatcher.

---
## 4. Workflow Local (PowerShell / Windows)
```powershell
# Activer venv (si pas déjà)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Installer dépendances de dev (si Poetry non utilisé)
pip install -e . --config-settings editable_mode=strict
pip install ruff==0.12.4 mypy==1.11.0 pytest==7.4.2 fastapi==0.95 starlette==0.28 httpx==0.24 pytest-asyncio==0.21 types-requests types-urllib3

# Tests rapides
$Env:PYTHONPATH='src'
pytest -q
Remove-Item Env:PYTHONPATH

# Lint ciblé
ruff check src tests

# Typecheck ciblé
mypy src --exclude "src/blender_mcp/archive/.*"

# Test spécifique (ex: connexion)
$Env:PYTHONPATH='src'
pytest -q tests/test_connection_reassembly.py
Remove-Item Env:PYTHONPATH
```

CI (GitHub Actions): matrice Python 3.11 + 3.12; jobs: ruff, mypy, pytest; option job `integration` pour tests ASGI si FastAPI installé.

---
## 5. Conventions de Réponse & Erreurs
- Services lèvent exceptions (`InvalidParamsError`, `ExternalServiceError`, etc.).
- Adapters formatent:
  - Succès: `{"status":"success","result":<valeur>}`
  - Erreur: `{"status":"error","message":<str>,"error_code":<ErrorCode>}`
- Aucune logique ne doit inférer `error_code` depuis `message`.
- Ajout de code erreur → modifier `ErrorCode`, `error_code_for_exception`, ajouter test mapping.

---
## 6. SOLID Compliance (Checklist exécutable)
| Principe | État | Action | Priorité |
|----------|------|--------|----------|
| SRP | Façade connexion multi-mode mélange 3 rôles | Scinder en `SocketConnection`, `NetworkConnection`, `JSONReassembler` | Medium |
| OCP | Ajout service modifie endpoints/tools divers | Utiliser `services/registry.py` et centraliser | High |
| LSP | `send_command` output variable (dict vs result) | Normaliser pour toujours renvoyer dict | High |
| ISP | OK sur `SocketLike` | Maintenir interfaces petites | Low |
| DIP | Parser/framing/policy non injectés | Introduire `strategies/` + injection dispatcher | Medium |

Audit rapide par fichier modifié (PR):
1. Décrire responsabilité unique en 1 phrase.
2. Si >1 responsabilité → proposer extraction.
3. Vérifier ajout fonctionnalité = ajout module (pas modif heavy du core).
4. Confirmer exceptions utilisées (pas dict d’erreur brut).
5. Vérifier absence de parsing heuristique de messages.

---
## 7. Registre Services / Tools (Implémenté)
Fichier: `src/blender_mcp/services/registry.py`
```python
_SERVICES: dict[str, Any] = {}
def register_service(name: str, fn: Any) -> None: _SERVICES[name] = fn
def get_service(name: str) -> Any: return _SERVICES.get(name)
def list_services() -> list[str]: return sorted(_SERVICES.keys())
def has_service(name: str) -> bool: return name in _SERVICES
```
- Dispatcher: tente d'abord ses handlers; à défaut, fallback sur le registre (`has_service`/`get_service`) et invoque la fonction via introspection (voir `dispatchers/dispatcher.py::_invoke_service`).
- Enregistrés à date: `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `execute_blender_code`, `polyhaven.*`, `sketchfab.*`, `hyper3d.*`.
- ASGI/tools: exposer la liste via `list_services()` (ou registre spécifique tools si nécessaire).

---
## 8. Dépréciation (Stratégie)
| Module legacy | Remplacement | Phase retrait | Avertissement |
|---------------|-------------|---------------|--------------|
| `simple_dispatcher.py` | `dispatcher.py` | Phase 2 | DeprecationWarning import |
| `command_dispatcher.py` (racine) | `dispatchers/dispatcher.py` | Phase 2 | idem |
| `connection_core.py` | `services/connection/network_core.py` | Phase 4 | idem |
| Services racine (`polyhaven.py`, etc.) | `services/*.py` | Phase 3 | stub + warning |
| `server_shim.py` | `servers/shim.py` | Phase 2 | warning + doc |
| `blender_codegen.py` racine | `codegen/blender_codegen.py` | Phase 5 | stub + warning |

Après 2 cycles de release: suppression stubs.

---
## 9. Phases de Migration (Résumé pour AI)
1. Ajouter warnings legacy + spec OpenSpec (non-breaking).
2. Créer registre services/tools + adapter dispatcher & ASGI.
3. Migrer services racine vers dossier `services/` (PRs petites).
4. Refactor connexion multi-mode si nécessaire.
5. Structurer intégrations (dossier), déplacer fichiers réseau.
6. Injection stratégies (policy/parser/framing) + docs.
7. Retirer stubs & mettre à jour CHANGELOG.

---
## 10. Prompts Modèles (Réutilisables)
Re-engagement (état général):
```
Tu es assistant sur blender-mcp. Branche active: feature/errors-dispatcher-standardisation.
Objectif actuel: normaliser send_command + refactor SOLID du dispatcher + déprécier les shims. Tâches: spec si breaking, implémentation non‑rupture, warnings de dépréciation, MAJ docs/tests.
Contraintes: contrat réponse (status/result/error_code), SOLID, petits PR (<3 fichiers).
Commence par un plan de tâches, puis implémente par petits incréments, ajoute tests, mets à jour journal.
```

Demande ciblée (ajout service):
```
Porter le service get_scene_info vers services/scene.py avec exceptions canoniques.
Ajouter tests: succès, absence bpy, invalid params.
Mettre à jour PROJECT_JOURNAL + mapping error.
```

Audit rapide module:
```
Audit SOLID du fichier X: donner SRP, suggestions extraction, risques OCP/LSP.
```

---
## 11. Checklist PR (Copier/Coller)
1. Fichiers modifiés <= 3 (hors tests/doc).
2. Responsabilité décrite dans PROJECT_JOURNAL.md.
3. Tests locaux: `pytest -q` + ciblés.
4. Lint & type: `ruff check` / `mypy src` OK.
5. Pas de dict d’erreur retourné par service (exceptions uniquement).
6. Contrat réponse stable (status/result). 
7. Si surface publique changée → spec OpenSpec créée.

---
## 12. Zones de Risque / Attention
- Variation actuelle `send_command` (retour `result` direct). À harmoniser avant extension.
- Multiples serveurs / dispatchers → risque confusion import. Documenter et ajouter warnings.
- Services en double (racine + services/). Priorité à migrer pour éviter divergence.
- Codegen duplicata: clarifier unique source.

---
## 13. Glossaire Rapide
- Dispatcher: centralise routage de commandes (handlers enregistrés).
- Service: fonction métier pure, lève exceptions, retourne données.
- Adapter: couche protocole (HTTP, embedded process, CLI) convertit service → payload.
- Registry: table dynamique des services ou tools exposés.
- Shim: fichier transitoire conservant chemin d’import legacy avec warning.

---
## 14. Ouverture pour l’Assistant AI
Lorsque tu reprends une session AI:
1. Consulter la roadmap courante: Issue #19 (https://github.com/sebschopf/blender-mcp/issues/19).
2. Lire ce fichier + `docs/developer/error_handling.md`.
3. Résumer la phase cible et tâches actives.
4. Créer/mettre à jour une TODO list: GitHub Issues/Projects (recommandé) ou `docs/TODO.md` si hors-ligne.
5. Exécuter les tests ciblés avant commit.
6. Éviter modifications massives hors périmètre (stick to plan).

Outils recommandés pour le suivi:
- GitHub Issues: 1 tâche = 1 issue (labels: `phase-2`, `service`, `infra`).
- GitHub Projects (Kanban): tableau "Refactor MCP" pour prioriser (To do / In progress / Done).
- PR task-lists: cases à cocher dans la description de PR pour sous-tâches.
- Fallback local: fichier `docs/TODO.md` avec checkboxes si GitHub Projects non utilisé.

Audit rapide GitHub (sans ajouter de fichiers):
```powershell
# Vérifier fonctions activées et branche par défaut
gh repo view --json hasIssues,hasProjects,nameWithOwner,defaultBranchRef -q "{nameWithOwner: .nameWithOwner, branch: .defaultBranchRef.name, issues: .hasIssues, projects: .hasProjects}"

# Lister labels existants
gh label list

# Lister issues récentes (toutes)
gh issue list --state all --limit 20

# Lister milestones
gh api repos/$(git config --get remote.origin.url | %% { $_ -replace '.*github.com[:/]|\.git$','' })/milestones | ConvertFrom-Json | Select-Object title,state,open_issues,closed_issues

# Lister Projects de l'owner (optionnel)
gh project list --owner $(git config --get remote.origin.url | %% { $_ -replace '.*github.com[:/].*?/(.+)$','$1' })
```

Note: Si tu préfères ne pas créer d'autres fichiers, conserve ces commandes dans ce guide et utilise Issues/Projects directement dans l'UI GitHub. 

---
## 15. Prochaine Action Recommandée (si aucune autre instruction)
Phase suivante: refactor SOLID du dispatcher + dépréciations.
- Extraire/clarifier stratégies d’exécution/policy dans le dispatcher (itération 1, sans rupture publique).
- Ajouter warnings de dépréciation pour les shims encore chargés; planifier suppression après 2 cycles.
- Poursuivre/terminer la migration des services restants; maintenir à jour `docs/endpoint_mapping_detailed.md`.

---
## 15b. Référence Endpoints / Portage
Source canonique de la liste des endpoints à porter: `docs/endpoint_mapping_detailed.md`.

Règles de portage d’un endpoint `@tool`:
1. Créer/ouvrir fichier cible sous `src/blender_mcp/services/<domaine>.py` (ex: `scene.py`, `objects.py`, `polyhaven.py`).
2. Transformer la fonction décorée en service pur (retourne des données ou lève une exception; pas de sérialisation JSON ici).
3. Remplacer paramètres contextuels implicites (`ctx`) par paramètres explicites si nécessaire; sinon garder `ctx` pour accès Blender isolé.
4. Ne jamais retourner un dict d’erreur : lever une exception (`InvalidParamsError`, `ExternalServiceError`, etc.) et laisser l’adapter formater.
5. Ajouter tests dédiés: succès nominal, erreurs de paramètres, environnement Blender absent (mock `bpy`).
6. Mettre à jour le registre (`services/registry.py`) via `register_service("get_scene_info", get_scene_info)`.
7. Ajouter entrée dans `PROJECT_JOURNAL.md` (section Phase 2) + si la surface publique change (signature différente) créer une spec sous `openspec/changes/phase-2-endpoint-porting/`.
8. Vérifier mapping d’erreurs si nouvelles exceptions introduites.

Format de documentation interne ajouté à la spec pour chaque endpoint:
```markdown
### Endpoint: get_scene_info
- Ancien décorateur: @tool get_scene_info(ctx)
- Nouveau service: services/scene.py:get_scene_info(ctx) -> dict
- Exceptions possibles: BlenderNotAvailableError, ExternalServiceError
- Tests: test_scene_service_success, test_scene_service_no_bpy, test_scene_service_invalid
- Registre: register_service("get_scene_info", get_scene_info)
```

Checklist avant de marquer "porté":
- Service créé et importable.
- Test(s) verts.
- Registre mis à jour.
- Journal mis à jour.
- Aucune dépendance legacy (pas d’appel à copy_server.py).

Statuts de la table `endpoint_mapping_detailed.md` à convertir de `pending` → `ported` une fois la checklist validée.

Note: Les endpoints Hyper3D/Sketchfab impliquent I/O réseau; mocker les appels externes dans les tests pour rapidité et isolation.

Stratégie d’ordre de portage recommandée:
1. Scène & objets (base locale).
2. Screenshot (interaction Blender simple).
3. Execute code (plus sensible – définir limites de sécurité).
4. PolyHaven (catégories → search → download → set_texture → status).
5. Sketchfab (status → search → download).
6. Hyper3D (status → generate text/images → poll → import).
7. Prompt `asset_creation_strategy` (convertir en configuration statique ou service de suggestion).

Impact sur registre: chaque domaine peut proposer un sous-espace (`polyhaven.search`, `hyper3d.generate_text`). Décider de la granularité dans la spec avant implémentation pour cohérence.

Sécurité pour `execute_blender_code`: ajouter couche de validation (liste fonctions autorisées ou sandbox limité) – à spécifier dans une spec séparée avant portage.

Note: Spec de sécurité créée — voir `openspec/changes/2025-11-13-execute-security/spec.md`. Phase 2 = baseline (audit + limitations documentées). Phase 3 introduira un mode restreint (builtins réduits/AST allowlist) sous drapeau de config.

---
## 16. Validation Rapide Avant Merge
```powershell
$Env:PYTHONPATH='src'
pytest -q tests/test_dispatcher.py tests/test_connection_reassembly.py tests/test_errors_mapping.py
Remove-Item Env:PYTHONPATH
ruff check src tests
mypy src
```

Tout vert + journal mis à jour = PR prête.

---
## 17. Notes Finales
Ce guide doit rester court, concret et mis à jour après chaque phase majeure. Ajouter un changelog interne ici si de nouvelles conventions apparaissent.

---
## 18. Changelog interne du guide
- 2025-11-13: MAJ normalisation `send_command` (implémentée, PR #22). Focus déplacé vers refactor dispatcher + dépréciation shims.
- 2025-11-13: MAJ Phase 2 fusionnée (registre services/tools opérationnel, fallback Dispatcher). Prochain focus: `send_command` + refactor dispatcher + dépréciation shims.
- 2025-11-13: Version initiale (standardisation erreurs, dispatcher, connexion shim).