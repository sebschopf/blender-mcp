## ADDED Requirements

### Requirement: AddonPreferences allow_ui_start_server
The add-on SHALL expose `AddonPreferences.allow_ui_start_server` as a boolean preference that defaults to `False` and can be toggled by the user to allow the UI to start an embedded server.

#### Scenario: Preference prevents auto-start
- **WHEN** the preference is `False` and the StartServer operator is triggered
- **THEN** the operator must not start the server and should return a clear message explaining how to enable the preference
