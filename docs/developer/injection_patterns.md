## Injection patterns for dispatcher: `policy_check` and `executor_factory`

This short developer note explains how to inject `policy_check` and `executor_factory` into the dispatcher/command flow so you can control authorization and execution strategies during runtime and testing.

### Contracts

- policy_check: Callable[[str, dict], Optional[str]]
  - Inputs: command type (string), params (dict)
  - Returns: None to allow; non-empty string to deny (reason)

- executor_factory: Callable[[], concurrent.futures.Executor]
  - Returns a `concurrent.futures.Executor` used by `HandlerExecutor` for timeouts or concurrent execution.

### Where to wire

- `CommandAdapter` accepts an optional `policy_check` argument. It calls the policy before delegating to handlers. If the policy returns a denial string, the command is short-circuited.

- `Dispatcher` exposes a `dispatch_with_timeout` API that uses `HandlerExecutor`. The `HandlerExecutor` can accept an `executor_factory` to change execution behavior (e.g., use ThreadPoolExecutor with specific max_workers).

### Examples

1) Simple allow-all policy (tests or local runs)

```python
from blender_mcp.dispatchers.policies import allow_all

# pass allow_all to the adapter
adapter = CommandAdapter(..., policy_check=allow_all)
```

2) Role-based policy example

```python
from blender_mcp.dispatchers.policies import role_based

# policy that checks params['user_role'] for required roles
policy = role_based(allowed_roles={'admin', 'operator'})
adapter = CommandAdapter(..., policy_check=policy)
```

3) Custom executor factory (limit threads for long-running handlers)

```python
import concurrent.futures

def small_pool_factory():
    return concurrent.futures.ThreadPoolExecutor(max_workers=2)

# pass factory to the dispatcher or HandlerExecutor
dispatcher = Dispatcher(handler_registry, executor_factory=small_pool_factory)

# then use dispatch_with_timeout
result = dispatcher.dispatch_with_timeout('do_thing', params, timeout=5.0)
```

### Tests

- In tests you can easily inject a synchronous `executor_factory` that runs inline (use `concurrent.futures.ThreadPoolExecutor(max_workers=1)` or a simple stub) to keep deterministic behavior.

- Use `policy_check` stubs to assert allowed/denied branches without mocking handlers.

### Notes

- Keep policies simple and side-effect free; prefer returning a denial reason string rather than raising.
- The `executor_factory` should return a short-lived executor or a pool that's safe to shut down after use. The `HandlerExecutor` will typically manage lifetimes for per-call executors.

If you want, I can also add a short example test file under `tests/` demonstrating a role-based policy and an executor factory used in `dispatch_with_timeout`.
