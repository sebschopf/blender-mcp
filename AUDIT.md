# Audit rapide et actions réalisées

Date: 2025-11-06

Résumé
------
Ce document résume les actions réalisées au titre d'un audit rapide orienté qualité, testabilité et sécurité pour le projet `blender-mcp`.

Actions effectuées
------------------
- Extraction de fonctions purement logiques dans `src/blender_mcp/` pour améliorer la testabilité (ex: `blender_codegen`, `materials`, `polyhaven`, `downloaders`, `node_helpers`, `texture_helpers`).
- Suppression d'un générateur D10 expérimental et réduction de la complexité du script `scripts/gemini_bridge.py` (remplacé par un module testable).
- Ajout de tests unitaires couvrant les nouveaux modules et exécution locale : actuellement la suite passe (24 tests verts localement).
- Mise en place d'un workflow CI GitHub Actions (`.github/workflows/ci.yml`) qui lance ruff, black, isort, mypy et pytest sur chaque push/PR.

Principes et recommandations d'audit (exécutés / en attente)
---------------------------------------------------------
1. Isolation des dépendances et testabilité
   - Ce qui a été fait : extractions des helpers hors de `addon.py` pour éviter d'importer `bpy` en environnement CI.
   - Recommande : continuer à extraire les gros composants (`gemini_client`, `mcp_client`, dispatcher) et remplacer les variables globales par un objet de configuration injectable.

2. Sécurité des entrées et chaîne d'exécution
   - Observations : le code génère du Python source et l'envoie à un outil MCP `execute_blender_code` — c'est un pattern puissant mais à risque si on accepte des prompts non fiables.
   - Recommande :
     - ajouter une validation stricte des intents et des paramètres avant génération/exécution;
     - journaliser (audit log) toutes les actions qui déclenchent `execute_blender_code`;
     - restreindre l'accès au serveur MCP (auth/tokens) en production.

3. Qualité du code et CI
   - Ce qui a été fait : ruff/black/isort/mypy/pytest dans CI pour prévenir les régressions.
   - Recommande : fixer `tool.mypy.strict = true` et corriger progressivement les erreurs, ou configurer une baseline si certaines importations tierces sont problématiques.

4. Tests et couverture
   - Ce qui a été fait : ajout de tests unitaires ciblés.
   - Recommande : ajouter tests d'intégration en environnement contrôlé (mock MCP server) pour valider l'envoi de commandes.

5. Documentation opérationnelle
   - Ce qui a été fait : ajout d'instructions et README déjà présents.
   - Recommande : ajouter un `SECURITY.md` et des instructions pour déployer le MCP en production (auth, CORS, contrôle d'accès).

Prochaines étapes pratiques (priorisées)
--------------------------------------
1. Extraire `gemini_client.py` et `mcp_client.py` (tests, mocks).
2. Remplacer globals CLI par `BridgeConfig` injectable et écrire tests unitaires autour des différents flags.
3. Ajouter audit logging pour toute exécution d'outil MCP qui modifie l'état (POST/execute).
4. Mettre en place un job CI additionnel (optionnel) qui construit et publie une distribution (packaging) et un autre job pour la sécurité (snyk/semgrep) si souhaité.

---

Décisions de refactorisation récentes (résumé)
----------------------------------------------

- `addon.py` a été réduit à un shim minimal, désormais importable hors-Blender.
- Les imports de `bpy` sont paresseux (lazy imports) pour rendre le code testable
   et éviter d'avoir à charger Blender dans CI.
- `types-requests` a été ajouté dans les dev-deps pour corriger les warnings
   `mypy` venant de `requests`.
- `google-genai` est optionnel : le module `gemini_client` charge
   `google.genai` dynamiquement et lève une erreur claire si l'option n'est pas
   installée. Cela évite d'imposer cette dépendance sur tous les environnements.

Notes rapides pour reviewers
---------------------------

- Tests : la suite unitaire locale est verte. Un test d'import (`tests/test_addon_import.py`)
   garantit que `addon.py` est importable sans `bpy`.
- Typing : `mypy` passe localement après installation des stubs.
- Lint : `ruff --fix` a été exécuté et n'a signalé aucune erreur restante pour `src`.

Si vous voulez que je prépare un commit/PR (branche) je peux le faire —
actuellement j'ai préparé un brouillon de PR dans `PR_DRAFT.md`.

