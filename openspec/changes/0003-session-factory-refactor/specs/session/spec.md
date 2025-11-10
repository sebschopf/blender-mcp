## ADDED Requirements

### Requirement: Central session factory
The system SHALL provide a central HTTP session factory `get_session()` that returns a configured `requests.Session` with project-standard headers and that can be reset by `reset_session()` for tests.

#### Scenario: Inject fake session
- **WHEN** a `requests.Session` fake is passed to a downloader helper
- **THEN** the helper uses the provided session's `get`/`post` methods instead of `requests.get`/`post`
