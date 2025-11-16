# Spec: Dépréciation des shims legacy (avertissements à l'import)

#### Summary
Introduire des DeprecationWarning à l'import pour les modules legacy conservés à des fins de compatibilité migratoire, et planifier leur retrait après deux cycles de release.

#### Motivation
- Réduire l'ambiguïté sur les chemins d'import « historiques » encore présents pendant la refactorisation.
- Guider explicitement les utilisateurs/tests vers les chemins canoniques sous `blender_mcp.dispatchers`, `blender_mcp.servers`, et `services/connection`.
- Permettre une suppression propre et anticipée des shims.

#### Scope
- Fichiers concernés:
  - `src/blender_mcp/simple_dispatcher.py` → use `blender_mcp.dispatchers`
  - `src/blender_mcp/command_dispatcher.py` → use `blender_mcp.dispatchers.command_dispatcher`
  - `src/blender_mcp/server_shim.py` → use `blender_mcp.servers.shim`
  - `src/blender_mcp/server.py` (façade) → use `blender_mcp.servers.server`
  - `src/blender_mcp/connection_core.py` → use `services/connection/network_core.py` et `connection.py`
  - `blender_mcp/server.py` (repo root shim) → temporaire, à retirer

#### Current Behavior
- Les modules legacy existent et sont importables silencieusement, ce qui entretient la confusion pendant la refonte.

#### Proposed Behavior
- Émettre `DeprecationWarning` à l'import sur chacun de ces modules, avec message de redirection clair vers les chemins cibles.
- Maintenir la fonctionnalité inchangée (compatibilité), les tests ne doivent pas échouer.

#### Backwards Compatibility
- Non-breaking: seuls des avertissements sont ajoutés. Les imports continuent de fonctionner.
- Les CI restent vertes; les tests peuvent afficher des warnings capturés par pytest.

#### Acceptance Criteria
1) Importer chaque module legacy déclenche un `DeprecationWarning` unique et informatif.
2) La suite de tests passe sans modification fonctionnelle.
3) La documentation (`ai_session_guide.md` et `CHANGELOG.md`) mentionne ces avertissements et la trajectoire de migration.

#### Removal Plan
- Retrait planifié après deux cycles de release à partir du 2025-11-13.
- Étapes:
  1. Cycle N, N+1: warnings à l'import + docs + CHANGELOG (présent changement).
  2. Cycle N+2: supprimer les shims; mettre à jour les imports dans les tests restants.

#### Scenarios
##### Scenario: import legacy
Given un code importe `from blender_mcp.simple_dispatcher import Dispatcher`
When le module est importé
Then un `DeprecationWarning` est émis avec une redirection vers `blender_mcp.dispatchers`

##### Scenario: import root server shim
Given un code importe `from blender_mcp.server import BlenderMCPServer`
When le module est importé
Then un `DeprecationWarning` indique d'utiliser `blender_mcp.servers.server` et que le shim sera retiré

#### Notes d'implémentation
- Utiliser `warnings.warn(msg, DeprecationWarning, stacklevel=2)` pour un pointage utile des appels.
- Ne pas modifier les signatures publiques ni le comportement runtime.
