"""Policy strategy abstraction.

Wraps the existing PolicyChecker pattern so injection is uniform when
extending dispatcher behavior. The default simply calls the checker if set.
"""
from __future__ import annotations

# isort: skip_file

from typing import Any, Dict, Optional

from ..policies import PolicyChecker


class PolicyStrategy:
    def check(
        self,
        checker: Optional[PolicyChecker],
        command: Dict[str, Any],
    ) -> Optional[str]:  # pragma: no cover - interface
        raise NotImplementedError


class DefaultPolicyStrategy(PolicyStrategy):
    def check(self, checker: Optional[PolicyChecker], command: Dict[str, Any]) -> Optional[str]:
        if checker is None:
            return None
        try:
            return checker(command.get("type", ""), command.get("params", {}) or {})
        except Exception as exc:
            # Surface exception message as denial reason; higher layer will map to error_code
            return str(exc)
