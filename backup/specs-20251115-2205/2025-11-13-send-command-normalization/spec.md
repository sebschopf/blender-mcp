# Spec: Normalisation `send_command` — retour toujours dict

#### Summary
Uniformiser le contrat de `send_command` côté client réseau pour toujours renvoyer un dictionnaire normalisé, plutôt que d’extraire le champ `result` en cas de succès. Aligne `services.connection` sur `connection_core` et simplifie les adapters/appels en amont.

#### Motivation
- Éviter la double sémantique actuelle: parfois `send_command` retourne directement la valeur, parfois un dict `{status, result}`.
- Stabiliser les appels et les tests; faciliter le mapping d’erreurs.

#### Current Behavior
- `services.connection.network_core.NetworkCore.send_command` renvoie `resp.get("result", resp)` et lève `RuntimeError` si `status == "error"`.
- `connection_core.BlenderConnection.send_command` renvoie un dict JSON complet.

#### Proposed Behavior
- `services.connection.network_core.NetworkCore.send_command` renvoie toujours l’objet JSON complet (dict) tel que reçu: `{status, result|message, error_code?}`.
- Ne pas extraire `result` dans cette couche; le formatage d’affichage reste du ressort des couches appelantes.

#### Scope
- Implémentation: `src/blender_mcp/services/connection/network_core.py`
- Tests: ajuster les tests qui attendaient une valeur "result" directe.

#### Backwards Compatibility
- Breaking change pour les appels qui s’attendaient à la valeur brute du champ `result`.
- Impact géré par mises à jour de tests et documentation.

#### Acceptance Criteria
1) `NetworkCore.send_command` renvoie toujours un dict.
2) Tests ciblés passent: `tests/test_connection_reassembly.py`, `tests/test_connection.py` (cas send_command).
3) Pas de régression sur `connection_core`.

#### Scenarios
##### Scenario: succès simple
Given un peer renvoie `{"status":"success","result":42}`
When `send_command("echo", {"value": 42})` est appelé
Then le retour est `{"status":"success","result":42}` (dict)

##### Scenario: erreur peer
Given un peer renvoie `{"status":"error","message":"boom","error_code":"handler_error"}`
When `send_command("any", {})`
Then la fonction retourne ce dict d’erreur sans lever `RuntimeError` dans cette couche

#### Notes d’implémentation
- Ne pas modifier `receive_full_response` (doit continuer à retourner le JSON parsé brut).
- Retirer l’extraction `r.get("result", resp)` et le `raise RuntimeError`.
