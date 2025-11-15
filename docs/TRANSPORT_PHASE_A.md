# Transport — Phase A

This document summarizes Phase A of the Transport refactor.

Goals
- Introduce a runtime `Transport` protocol that abstracts how commands are sent and responses received.
- Provide two concrete transports:
  - `RawSocketTransport`: plain TCP socket transport using a simple line-delimited JSON protocol.
  - `CoreTransport`: adapter around the legacy `BlenderConnection` when available.
- Provide `select_transport(...)` and `NetworkCore` to centralize transport selection and injection.

CoreTransport
- `CoreTransport` is an adapter around the legacy `connection_core.BlenderConnection` shim. It preserves the same `Transport` protocol surface and delegates connect/send/receive/disconnect to the core implementation when available.

Shim: `connection_core.py`
- The repository exposes a compatibility shim at `src/blender_mcp/connection_core.py` which provides `BlenderConnection` and `get_blender_connection()` for legacy consumers and for `CoreTransport` in environments where the native core implementation is desired.

Usage
- Prefer `NetworkCore(..., transport=your_transport)` to inject a transport in tests or special runtimes.

Testing
- Tests include `tests/test_transport_protocol.py` validating protocol runtime-check and injection.

Next steps
- Add `ResponseReceiver` improvements for partial-message reassembly (if needed).
- Add `RawSocketTransport` connection retry behavior and more robust error handling.

Configuration
- **`BLENDER_MCP_MAX_MESSAGE_SIZE`**: optional environment variable (bytes). When set,
  `ResponseReceiver` will use this value as the safety cap to avoid unbounded buffer
  growth when reassembling incoming messages. If not set, the default is `10485760` (10 MiB).
  We recommend keeping this value conservative for untrusted networks.
