# Spec: Dispatcher Instrumentation Strategy (Non-Breaking Extension Point)

Status: proposed
Date: 2025-11-13
Author: automation
Scope: `dispatchers/dispatcher.py` (new optional strategy injection)
Phase: 2 (introduce interface + no-op default), Phase 3 (possible richer aggregation/export)

## Summary
Introduce an optional `InstrumentationStrategy` injected into `Dispatcher` to observe lifecycle events (start, success, error) of dispatch operations and command adapter invocations without modifying core logic or public API contracts. This enables lightweight logging/metrics/tracing and future performance telemetry while keeping existing behavior unchanged when absent.

## Motivation
The current dispatcher executes handlers/services and applies policies but offers no structured hook for instrumentation. Adding logging inline would mix concerns and complicate future refactors. A dedicated strategy aligns with the existing extensibility pattern (resolution/policy strategies), preserves Open/Closed Principle, and avoids repeated ad-hoc wrappers in tests or adapters.

## Non-Goals
- Providing a full metrics backend integration (Prometheus/OpenTelemetry) in this change.
- Altering the success/error payload contract already standardized (`status`, `result`, `message`, `error_code`).
- Collecting per-param sensitive data; instrumentation will receive params but implementers are responsible for redaction.

## Design
Add optional constructor argument: `Dispatcher(..., instrumentation_strategy: Optional[InstrumentationStrategy] = None)`.

Interface (initial draft):
```python
class InstrumentationStrategy(Protocol):
    def on_dispatch_start(self, name: str, params: dict[str, Any]) -> None: ...
    def on_dispatch_success(self, name: str, result: Any, elapsed_s: float) -> None: ...
    def on_dispatch_error(self, name: str, error: Exception, elapsed_s: float) -> None: ...
    def on_adapter_invoke(self, adapter_name: str, cmd_type: str, params: dict[str, Any]) -> None: ...
```

The dispatcher will:
1. Capture monotonic start time before resolution.
2. Invoke `on_dispatch_start` if strategy present.
3. After success/error, compute elapsed duration and call respective method.
4. `dispatch_command` will call `on_adapter_invoke` just before invoking the adapter (after policy pass).

Default behavior when no strategy is provided: no overhead beyond the `if strategy` checks.

Performance: single monotonic time capture + conditional calls. Strategy implementations should remain fast; any blocking I/O must be async-compatible or offloaded by the implementer.

Thread-safety: The dispatcher may be used concurrently; strategy implementations must be responsible for their own synchronization (documented caveat). The interface itself imposes no shared mutable state.

## API Contract Impact
No change to existing public methods; argument added is optional with default `None`. Type checkers see a new parameter—backwards-compatible for call sites using positional args. Named call sites ignoring the new kw continue to work.

## Error Handling
Instrumentation callbacks must not raise or alter dispatch results. Any exception raised by a strategy will be caught and logged at DEBUG (or ignored) to prevent side effects. (Implementation note: wrap each callback in a `try/except Exception:` block.)

## Security / Privacy Considerations
Strategy receives raw `params`; implementers must avoid logging secrets (e.g. API keys). Phase 3 may introduce a redaction helper or allow specifying a param allowlist. No new external surface exposed.

## Acceptance Scenarios

### Scenario: No strategy provided
Given a Dispatcher created without `instrumentation_strategy`
When calling `dispatch("echo", {"x":1})`
Then behavior matches current implementation and no instrumentation callbacks fire.

### Scenario: Strategy captures success
Given a `RecordingStrategy` storing events
When a handler returns successfully
Then `on_dispatch_start` and `on_dispatch_success` entries are recorded with non-negative elapsed time.

### Scenario: Strategy captures error
Given a handler that raises `InvalidParamsError`
When dispatched
Then `on_dispatch_start` and `on_dispatch_error` are recorded; elapsed time >= 0; original error propagates normally.

### Scenario: Adapter invocation instrumentation
Given a call to `dispatch_command` with a command adapter
When policy allows
Then `on_adapter_invoke` is recorded before adapter execution.

### Scenario: Strategy exception resilience
Given a strategy whose `on_dispatch_success` raises an exception
When a handler succeeds
Then dispatch result is still returned; strategy exception is swallowed (optionally logged).

## Backward Compatibility
All existing tests pass unchanged. New tests focus on instrumentation presence. No environment variable or config change required. API usage without the new kw remains valid.

## Rollout Plan
1. Land this spec file.
2. Implement interface + no-op default (Phase 2).
3. Add tests under `tests/test_dispatcher_instrumentation.py`.
4. Update `CHANGELOG.md` (Unreleased) and `docs/developer/ai_session_guide.md` with instrumentation section.
5. Future Phase 3: optional built-in implementation aggregating counts and latencies, with exporter hook.

## Alternatives Considered
- Inline logging inside dispatcher methods (rejected: mixes concerns, harder to evolve).
- Observer pattern via global signals (rejected: implicit coupling, less explicit injection point).
- Decorator wrapping dispatcher public methods externally (possible but less ergonomic for layered strategies; chosen approach integrates with existing strategy pattern).

## Open Questions
- Should we include a callback for policy denial? (Deferred; can be added in Phase 3 if needed.)
- Provide an async variant? (Current dispatcher is sync; revisit if async path added.)

## Tasks
- [ ] Add `InstrumentationStrategy` protocol + default no-op implementation.
- [ ] Extend Dispatcher constructor and internal calls.
- [ ] Implement safe callback wrapper (`_safe_call(strategy, method_name, ...)`).
- [ ] Add unit tests for success, error, adapter invoke, resilience.
- [ ] Documentation & changelog updates.

