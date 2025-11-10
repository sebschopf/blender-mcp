## ADDED Requirements

### Requirement: Embedded server adapter API
The project SHALL provide an embedded server adapter exposing `start_server_process(cmd, timeout_sec, workdir)` and `stop_server_process(handle)` and SHALL be import-safe for the Blender add-on.

#### Scenario: Start and stop via UI operator
- **WHEN** the UI StartServer operator is triggered
- **THEN** it lazy-imports the adapter and calls `start_server_process`, returning a handle and updating UI status
