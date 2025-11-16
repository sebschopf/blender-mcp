# 0007 - Secrets broker and runtime secret handling

Proposal: Do not inject long-lived secrets into execution runtimes. Instead provide a secrets broker service that performs privileged operations (e.g., API calls) on behalf of an execution when necessary and returns sanitized results.

Why: Prevents exfiltration of secrets from sandboxed runtimes and limits lateral movement if a runtime is compromised.

Scope:
- Design a secrets broker API and integrate callers (services that need API keys) so they call the broker rather than exposing keys to workers.
- Add tests that verify the broker never returns raw secrets to the runtime.

Acceptance criteria:
- No code path mounts raw API keys into child processes or into environments reachable by untrusted code.
- Secrets broker implements a narrow RPC with authentication and an audit trail.

Tasks:
1. Add an OpenSpec spec describing the broker API and threat model.
2. Port one service (e.g., Sketchfab) to use the broker as a proof of concept.
