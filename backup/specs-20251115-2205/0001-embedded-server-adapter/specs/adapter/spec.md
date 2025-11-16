## ADDED Requirements

### Requirement: Embedded server adapter API
The project SHALL provide an embedded server adapter exposing `start_server_process(command, cwd)` and `stop_server_process(proc)` and SHALL provide `is_running(proc)`. The adapter SHALL be import-safe for the Blender add-on.

#### Scenario: Start and stop via UI operator
- **WHEN** the UI StartServer operator is triggered
- **THEN** it lazy-imports `blender_mcp.servers.embedded_adapter` and calls `start_server_process`, receiving a process handle; the UI updates status and later calls `stop_server_process` to terminate the helper process. The UI MAY call `is_running` to check process state.
