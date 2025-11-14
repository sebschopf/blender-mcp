# Transport — Phase A

This document summarizes Phase A of the Transport refactor.

Goals
- Introduce a runtime `Transport` protocol that abstracts how commands are sent and responses received.
- Provide two concrete transports:
  - `RawSocketTransport`: plain TCP socket transport using a simple line-delimited JSON protocol.
  - `CoreTransport`: adapter around the legacy `BlenderConnection` when available.
- Provide `select_transport(...)` and `NetworkCore` to centralize transport selection and injection.

Usage
- Prefer `NetworkCore(..., transport=your_transport)` to inject a transport in tests or special runtimes.

Testing
- Tests include `tests/test_transport_protocol.py` validating protocol runtime-check and injection.

Next steps
- Add `ResponseReceiver` improvements for partial-message reassembly (if needed).
- Add `RawSocketTransport` connection retry behavior and more robust error handling.
