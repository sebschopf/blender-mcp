## ADDED Requirements

### Requirement: Secrets broker RPC
The system SHALL provide a secrets broker API that performs privileged operations (e.g., external API calls requiring keys) on behalf of untrusted runtimes and SHALL NOT return raw secret material in responses.

#### Scenario: Broker performs Sketchfab metadata fetch
- **WHEN** a runtime requests `service=sketchfab operation=download_metadata` with `uid` param
- **THEN** the broker performs the privileged call using stored credentials and returns sanitized metadata without exposing the API key
