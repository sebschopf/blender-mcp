# Guide Session AI — blender-mcp

Ce fichier est conçu pour (re)donner rapidement à un assistant AI (ChatGPT / GitHub Copilot / autre) le contexte nécessaire pour continuer le travail sans perte d'information. Il résume l'architecture, l'état des tâches, les conventions, le workflow CI, et fournit des prompts prêts à l'emploi.

---
## 1. TL;DR (Résumé immédiat)
Architecture structurée en couches: core (erreurs, types, logging), dispatcher (stratégies + instrumentation), connexion (services/connection), services métier (testables), adapters (ASGI / embedded), UI Blender, clients (LLM/MCP). État courant: registre unique opérationnel, normalisation `send_command` effective, instrumentation du dispatcher en place, imports normalisés; PR #28 fusionnée. Transport Phase A démarrée (abstraction de transport + SRP côté connexion), poursuite des dépréciations contrôlées. Note: le module racine `command_dispatcher.py` a été retiré (2025-11-14); utiliser `blender_mcp.dispatcher` (façade) ou `blender_mcp.dispatchers.dispatcher`.

---
## 2. Couches d'Architecture (Modèle cible)
| Couche | Contenu | Rôle | Import recommandé |
|--------|---------|------|-------------------|
| Core | `errors.py`, `types.py`, `logging_utils.py` | Contrats & base stable | `from blender_mcp.errors import ...` |
| Dispatcher | `dispatchers/dispatcher.py` + façade `dispatcher.py` | Orchestration handlers | `from blender_mcp.dispatcher import Dispatcher` |
| Connexion | `services/connection/*` + shim `connection.py` | Transport + reassembly | `from blender_mcp.connection import BlenderConnection` |
| Transport | `services/connection/transport.py` | Sélection/impl (Core/Raw), DI | `from blender_mcp.services.connection import Transport` |
| Services | `services/*.py` | Logique métier testable | `from blender_mcp.services.scene import get_scene_info` |
| Adapters | `asgi.py`, `servers/embedded_adapter.py` | Intégration HTTP / processus embarqué | `from blender_mcp.servers.embedded_adapter import start_server_process` |
| UI | `blender_ui/*`, `codegen/*` | Addon Blender (panel, opérateurs) | Blender runtime seulement |
| Clients | `gemini_client.py`, `mcp_client.py`, `http.py` | Accès LLM / MCP / HTTP | Tools externes |
| Legacy/Shims | `simple_dispatcher.py`, `server_shim.py`, `connection_core.py` | Compatibilité migratoire | À déprécier |

---
## 3. État Actuel (Phase et Avancement)
Branche de base: `main` (PR #28 fusionnée). Prochaine branche: `feature/transport-phase-a`.

Roadmap courante: Issue #19 — Registry & Endpoint Porting
https://github.com/sebschopf/blender-mcp/issues/19

Terminés:
- Standardisation erreurs (`ErrorCode`, `ErrorInfo`), mapping centralisé.
- Dispatcher: unification + instrumentation (hooks start/success/error, adapter invoke), réduction de complexité.
- Retrait du module racine `command_dispatcher.py`; dispatcher canonique = `blender_mcp.dispatchers.dispatcher` (façade `blender_mcp.dispatcher`).
- Connexion: normalisation `send_command` → retour dict complet (PR #22), tests fragments/timeout.
- Registre unique services/tools (`services/registry.py`) avec fallback dans le Dispatcher.
- Endpoints portés et enregistrés: `scene`, `object`, `screenshot`, `execute`, `polyhaven.*`, `sketchfab.*`, `hyper3d.*`.
- CI: Ruff/Mypy/Pytest verts; import ordering normalisé.

Partiellement faits / À finaliser:
- Transport Phase A: abstraction de transport (Protocol), séparation stratégie/receiver, injection instrumentation connexion (non‑breaking).
- Dépréciations: modules legacy (simple_dispatcher, server shims, services racine) encore présents avec warnings; plan de retrait après 2 cycles.

À venir (phases):
1. Transport Phase A (connexion): `Transport` Protocol + `RawSocketTransport`/`CoreTransport`, `select_transport` (sélection), `ResponseReceiver` (SRP). Injection optionnelle: `BlenderConnectionNetwork(..., transport=...)`.
2. Dépréciations: maintenir warnings, documenter calendrier de retrait (2 cycles), préparer suppression progressive.
3. Services: finaliser migrations résiduelles si existantes; maintenir `endpoint_mapping_detailed.md`.
4. Dispatcher: itération légère si besoin (stratégies additionnelles) sans rupture.

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

Transport — tests ciblés (local):
```powershell
$Env:PYTHONPATH='src'
pytest -q tests/test_transport_phase_a.py
Remove-Item Env:PYTHONPATH
```

---
## 5. Conventions de Réponse & Erreurs
- Services lèvent exceptions (`InvalidParamsError`, `ExternalServiceError`, etc.).
- Adapters formatent:
  - Succès: `{"status":"success","result":<valeur>}`
  - Erreur: `{"status":"error","message":<str>,"error_code":<ErrorCode>}`
- Aucune logique ne doit inférer `error_code` depuis `message`.
- Ajout de code erreur → modifier `ErrorCode`, `error_code_for_exception`, ajouter test mapping.
Sous‑section: Politiques (PolicyChecker)
- Contrat `PolicyChecker`: `(cmd_type: str, params: Dict[str, Any]) -> Optional[str]`.
  - Retourne `None` pour autoriser, une chaîne non vide pour refuser.
  - Lever `PolicyDeniedError` est également supporté (mappé en `policy_denied`).
- Priorité: la policy passée per‑call à `Dispatcher.dispatch_command(..., policy_check=...)` PRIME sur celle fournie au constructeur `Dispatcher(policy_check=...)`.
- Mapping des refus: `{"status":"error","message":"Blocked by policy: <raison>","error_code":"policy_denied"}` (ou message de l’exception si `PolicyDeniedError`).
- Helpers dispo: `allow_all`, `deny_all`, `and_`, `or_`, `role_based` (voir `blender_mcp.dispatchers.policies`).
- Référence: Issue #23 — Refactor SOLID du dispatcher (injection PolicyChecker) https://github.com/sebschopf/blender-mcp/issues/23

Sous-section: ASGI `/tools` et registre de services
- Par défaut, `/tools` liste les fonctions module-level exposées par `blender_mcp.server` (tests actuels).
- Enrichissement optionnel (non-breaking): pour inclure les services du registre dans `/tools`, définir la variable d’environnement `BLENDER_MCP_EXPOSE_REGISTRY_TOOLS=1`.
  - Implémentation: concatène `services.registry.list_services()` au listing (`source: "services_registry"`).
  - Motivation: garder le comportement historique par défaut, tout en permettant d’exposer dynamiquement les services quand souhaité.
  - Tests: `tests/test_asgi_tools.py` reste vert sans flag; pas d’assertion stricte sur le contenu complet du listing.
Sous-section: Stratégies Dispatcher (injection non-breaking)
- But: ouvrir le dispatcher à l’extension (OCP) sans modifier sa surface publique.
- Package: `blender_mcp.dispatchers.strategies` fournit deux interfaces et leurs implémentations par défaut:
  - `HandlerResolutionStrategy`: résout un nom → callable (défaut = registre puis fallback services via `_resolve_handler_or_service`).
  - `PolicyStrategy`: applique la policy avant d’invoquer le `CommandAdapter` (défaut = exécuter le `PolicyChecker`).
- Construction: `Dispatcher(handler_resolution_strategy=..., policy_strategy=...)` (paramètres optionnels; si omis → comportements historiques inchangés).
- Effet: `dispatch` et `dispatch_strict` délèguent la résolution; `dispatch_command` exécute la stratégie de policy (retour immédiat `policy_denied` si blocage).
- Exemple minimal:
```python
from blender_mcp.dispatchers.dispatcher import Dispatcher
from blender_mcp.dispatchers.strategies import HandlerResolutionStrategy

class DemoResolution(HandlerResolutionStrategy):
    def resolve(self, dispatcher, name):  # type: ignore[override]
        if name.startswith("demo_"):
            return lambda p: {"status": "success", "result": p.get("x", 0)}
        return dispatcher._resolve_handler_or_service(name)

d = Dispatcher(handler_resolution_strategy=DemoResolution())
print(d.dispatch("demo_test", {"x": 5}))  # {'status': 'success', 'result': 5}
```
- Tests: `tests/test_dispatcher_strategies.py` (résolution synthétique + blocage policy custom) verts.
- Avantage futur: instrumentation, framing, parsing pourront s’ajouter via nouvelles stratégies dédiées sans refactor lourd ni duplication.
Sous-section: Stratégie d'Instrumentation (ajout non-breaking)
- Objectif: offrir un point d'extension pour observer le cycle de vie des dispatch (start/success/error) et des appels d'adapter sans mêler la logique métier.
- Interface: `InstrumentationStrategy` avec méthodes `on_dispatch_start(name, params)`, `on_dispatch_success(name, result, elapsed_s)`, `on_dispatch_error(name, error, elapsed_s)`, `on_adapter_invoke(adapter_name, cmd_type, params)`.
- Injection: `Dispatcher(instrumentation_strategy=...)` (paramètre optionnel; absence = aucun surcoût sauf tests de branche).
- Comportement: exceptions levées par la stratégie sont ignorées (swallow + log éventuel futur) pour préserver la robustesse.
- Usage minimal:
```python
from blender_mcp.dispatchers.dispatcher import Dispatcher
from blender_mcp.dispatchers.strategies import InstrumentationStrategy

class Rec(InstrumentationStrategy):
  def __init__(self): self.events = []
  def on_dispatch_start(self, n, p): self.events.append(("start", n))
  def on_dispatch_success(self, n, r, e): self.events.append(("success", e))
  def on_dispatch_error(self, n, err, e): self.events.append(("error", str(err)))
  def on_adapter_invoke(self, a, t, p): self.events.append(("adapter", t))

d = Dispatcher(instrumentation_strategy=Rec())
```
- Tests: `tests/test_dispatcher_instrumentation.py` vérifie succès, erreur, invocation adapter.
- Évolution Phase 3: agrégation métriques + export (Prometheus/OpenTelemetry) via implémentation dédiée.
---
## 6. SOLID Compliance (Checklist exécutable)
| Principe | État | Action | Priorité |
|----------|------|--------|----------|
| SRP | Façade connexion multi‑mode mélange 3 rôles | Scinder en `SocketConnection`, `NetworkConnection`, `JSONReassembler` | Medium |
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
Note (2025-11-13): les modules legacy listés ci-dessous émettent désormais un `DeprecationWarning` à l'import pour guider la migration. Voir la spec OpenSpec: `openspec/changes/2025-11-13-deprecations-legacy-shims/spec.md`.
| Module legacy | Remplacement | Phase retrait | Avertissement |
|---------------|-------------|---------------|--------------|
| `simple_dispatcher.py` | `dispatcher.py` | Phase 2 | DeprecationWarning import |
| `command_dispatcher.py` (racine) | `dispatchers/dispatcher.py` | Retiré (2025-11-14) | — |
| `connection_core.py` | `services/connection/network_core.py` | Phase 4 | idem |
| Services racine (`polyhaven.py`, `sketchfab.py`, `hyper3d.py`) | `services/*.py` | Phase 3 | stub + warning (actif) |
| `server_shim.py` | `servers/shim.py` | Phase 2 | warning + doc |
| `blender_codegen.py` racine | `codegen/blender_codegen.py` | Phase 5 | stub + warning |

Note additionnelle (2025-11-14): `command_dispatcher.py` au niveau racine a été supprimé. Compatibilité: importer via `blender_mcp.dispatcher` (façade) ou `blender_mcp.dispatchers.dispatcher`.

Note additionnelle (2025-11-13, post‑migration): les modules racine `polyhaven.py`, `sketchfab.py` et `hyper3d.py` déclenchent désormais un `DeprecationWarning` à l'import afin d'encourager l'utilisation des services validés sous `blender_mcp.services.*`. Leur suppression est planifiée après deux cycles de release une fois que les appels externes ont été migrés.

Après 2 cycles de release: suppression stubs.

---
## 9. Phases de Migration (Résumé pour AI)
1. Ajouter warnings legacy + spec OpenSpec (non-breaking).
2. Créer registre services/tools + adapter dispatcher & ASGI. (FAIT)
3. Migrer services racine vers dossier `services/` (PRs petites). (EN GRANDE PARTIE FAIT)
4. Refactor connexion multi-mode (Transport Phase A) si nécessaire.
5. Structurer intégrations (dossier), déplacer fichiers réseau.
6. Injection stratégies (policy/parser/framing) + docs.
7. Retirer stubs & mettre à jour CHANGELOG.

---
## 10. Prompts Modèles (Réutilisables)
Re-engagement (état général):
```
Tu es assistant sur blender-mcp. Branche: main (PR #28 fusionnée). Prochaine branche: feature/transport-phase-a.
Objectif: lancer Transport Phase A (abstraction de transport + séparation SRP), poursuivre dépréciations contrôlées, maintenir docs/tests. Contraintes: contrat réponse (status/result/error_code), SOLID, petits PR (<3 fichiers).
Commence par un plan concis, implémente par incréments, ajoute tests, mets à jour PROJECT_JOURNAL et endpoint_mapping_detailed.
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
Phase suivante: Transport Phase A (connexion) + dépréciations.
- Introduire `Transport` Protocol + classes concrètes (RawSocket/Core).
- Séparer sélection de transport et réception/réassemblage (SRP), conserver façade compat.
- Maintenir warnings de dépréciation, préparer calendrier de retrait (2 cycles).

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
- 2025-11-13: Version initiale (standardisation erreurs, dispatcher, connexion shim).
- 2025-11-13: Ajout de la note sur la priorité per‑call du `policy_check` et le mapping `policy_denied` (réf. Issue #23).

---
## AI Session — Changements récents et actions (2025-11-14)
Résumé des modifications appliquées pendant une session d'intégration LLM/bridge et actions recommandées pour finaliser l'E2E Gemini → Bridge → MCP → Blender.

- **Fichiers modifiés clé**:
  - `src/blender_mcp/asgi.py` : protection de `_ensure_mcp_thread` pour éviter une AttributeError si le shim racine n'expose pas `main`.
  - `src/blender_mcp/gemini_client.py` : correction du formatage du prompt (échappement des accolades et construction sûre du prompt) pour éviter `KeyError`.
  - `scripts/gemini_bridge.py` : le script crée désormais un `Dispatcher()`, injecte les callables `call_gemini_cli` / `call_mcp_tool` dans `dispatchers.bridge` et supporte `use_api`.
  - Documents: mise à jour de guides et journaux pour refléter les correctifs (voir `docs/AI_SESSION_CHANGES.md`).

- **Bugs résolus**:
  - Guard startup ASGI pour absence de `server.main` (évite crash au démarrage).
  - Injection du `Dispatcher` manquant pour `run_bridge` (TypeError résolu).
  - Remplacement des stubs NotImplemented par wiring des callables du script (NotImplementedError résolu).
  - Signature `call_gemini_cli(use_api=...)` acceptée et routage vers `call_gemini_api` si nécessaire.
  - Dépendance `google-genai` détectée et signalée (installer via `pip install google-genai`).
  - Correction du `PROMPT_TEMPLATE` pour éviter `KeyError` lors du formatage contenant du JSON.
  - Validation de présence de `MCP_BASE` (ex: `http://127.0.0.1:8000`) pour éviter `MissingSchema` lors des POST HTTP.

- **Etat actuel et points d'attention**:
  - FastAPI app (`blender_mcp.asgi:app`) importe correctement.
  - Bridge interactif fonctionne et pose les questions de clarification.
  - Blender détecté écoutant sur `127.0.0.1:9876`.
  - `/health` peut encore retourner un message sur l'absence de `get_blender_connection` — envisager d'aligner le shim racine ou d'ajuster l'endpoint health.

- **Actions recommandées immédiates**:
  1. Définir `MCP_BASE` dans l'environnement PowerShell: `$Env:MCP_BASE='http://127.0.0.1:8000'`.
  2. Redémarrer l'ASGI (ou lancer via `.\\scripts\\uvicorn_start.ps1`) puis relancer `scripts/gemini_bridge.py` pour finaliser le flux.
  3. Si Gemini retourne un nom d'outil non standard, mapper ce nom à `execute_blender_code` dans `scripts/gemini_bridge.py` ou ajouter un handler dispatcher.

- **Tests à ajouter** (prioritaires):
  - Test d'intégration simuler POST du bridge → `/tools/<toolname>` et vérifier que `execute_blender_code` est invoqué (mock `bpy`).
  - Unit tests pour `src/blender_mcp/gemini_client.py` (format prompt, parsing JSON tools).
  - Tests non-interactifs pour `scripts/gemini_bridge.py` (simulateur de réponse LLM).

Consulter `docs/AI_SESSION_CHANGES.md` pour le détail complet, commandes et exemples de reproductions.
