# Issue Proposal: Phase A Transport Abstraction

## Résumé
Introduire une abstraction de transport claire (non-breaking) pour préparer la décomposition SRP du sous-système connexion: isoler sélection du transport, boucle réception/réassemblage et framing.

## Contexte
Le journal SRP (voir `docs/PROJECT_JOURNAL.refactor_connection.md`) identifie un mélange de responsabilités dans `network_core.py` et `facade.py` (`BlenderConnection`). La logique: sélection socket vs core + framing + reassembly + gestion erreurs est condensée.

## Objectifs
- Créer un protocole `Transport` minimal: `connect() -> bool`, `close() -> None`, `send(bytes) -> None`, `recv() -> bytes` (ou itérateur).
- Implémentations initiales:
  - `RawSocketTransport`: encapsule socket direct (connect/timeout, lecture jusqu'à newline ou taille).
  - `CoreTransport`: enveloppe la logique existante de `NetworkCore` sans modifier comportements.
- Adapter `NetworkCore` pour consommer un objet `Transport` injecté plutôt qu'accéder directement au socket.
- Préserver l'API publique: `from blender_mcp.connection import BlenderConnection` inchangé.

## Portée
Fichiers (ajouts/modifs minimes, ≤3 code hors tests):
- `src/blender_mcp/services/connection/transport.py` (protocole + classes).
- `src/blender_mcp/services/connection/network_core.py` (injection optionnelle `transport` + fallback legacy).
- Tests ciblés: `tests/test_connection_transport_phase_a.py` (nouveau) validant substitution.

## Non-Objectifs (Phase A)
- Pas de refactor complet du framing length-prefix (gardé tel quel).
- Pas de modification du format de réponse ou mapping erreurs.
- Pas encore d'instrumentation connexion (prévu Phase D du plan général).

## Conception
```python
class Transport(Protocol):
    def connect(self) -> bool: ...
    def close(self) -> None: ...
    def send(self, payload: bytes) -> None: ...
    def recv(self, bufsize: int = 8192) -> bytes: ...  # blocage ou timeout
```
`RawSocketTransport` gère création, timeout et retourne chunk brute; la réassemblage JSON reste dans `NetworkCore`.

`CoreTransport` wrappe l'implémentation actuelle pour isoler transition — peut déléguer à méthodes existantes, assurant tests existants verts.

Injection: `NetworkCore(transport: Optional[Transport] = None, ...)`. Si `transport` est `None`, comportement legacy: création socket interne.

## Migration & Back-compat
- Aucune dépréciation immédiate; un warning pourra être ajouté plus tard à l'usage direct de méthodes socket dans `BlenderConnection`.
- Tests existants ne changent pas; nouveau test prouve substitution.

## Scénarios
### Scenario: Raw transport substitué
Given un `RawSocketTransport` mock
When instancié dans `NetworkCore(transport=mock)`
Then les appels `send_command` utilisent le mock sans ouvrir de vrai socket.

### Scenario: Legacy fallback
Given instantiation sans param
When `NetworkCore()` est utilisé
Then comportement identique (tests verts) sans warnings supplémentaires.

## Tâches
1. Ajouter `transport.py` (protocol + classes).
2. Modifier constructeur `NetworkCore` pour accepter `transport`.
3. Ajouter test substitution mock (simulate `recv` renvoyant message JSON newline).
4. Documenter dans journal + mettre entrée CHANGELOG.

## Acceptation
- Tests existants verts + nouveau test transport.
- Pas de rupture d'import ou signature publique.
- Lint & mypy OK.

## Risques
- Sur-abstraction overhead: limité au passage d'un param optionnel.
- Couverture tests insuffisante: mitigé par test mock substitution + maintien suite complète.

## Commandes Vérif
```powershell
$Env:PYTHONPATH='src'
ruff check src tests
mypy src --exclude "src/blender_mcp/archive/.*"
pytest -q tests/test_connection_transport_phase_a.py
pytest -q
Remove-Item Env:PYTHONPATH
```

## Suivi
Prochaine phase (B/C/D): séparation `TransportSelector`, instrumentation connexion, dépréciation façade monolithique.
