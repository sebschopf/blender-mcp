"""Transport package (SOLID-ready)

Provide the canonical `Transport` abstraction for the project.
This package is intentionally under `services` (not `services.connection`) to
make it a first-class service-level abstraction that other parts of the
codebase can depend on without triggering connection-layer import cycles.
"""
from .protocol import Transport

__all__ = ["Transport"]
