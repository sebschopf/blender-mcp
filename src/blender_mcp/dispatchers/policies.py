"""Policy helpers for command dispatching.

This module provides a small, well-documented set of policy helpers
and the canonical `PolicyChecker` type used by the dispatcher/adapter.

Contract: a PolicyChecker accepts (cmd_type: str, params: Dict[str, Any])
and returns None when the command is allowed, or a string message when
the policy disallows the action. Returning a non-empty string is
treated by the adapter as a denial reason.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Sequence

# PolicyChecker returns None when allowed, or a string message when denied.
PolicyChecker = Callable[[str, Dict[str, Any]], Optional[str]]


class PolicyDeniedError(Exception):
    """Raised when a policy denies a command with a message."""


def allow_all(_: str, __: Dict[str, Any]) -> Optional[str]:
    """Policy that always allows the command."""
    return None


def deny_all(_: str, __: Dict[str, Any], *, reason: str = "denied by policy") -> Optional[str]:
    """Policy that always denies the command with an optional reason."""
    return reason


def role_based(allowed_roles: Sequence[str], role_getter: Callable[[Dict[str, Any]], Optional[str]] = lambda p: p.get("role")) -> PolicyChecker:
    """Factory that returns a PolicyChecker allowing commands only for given roles.

    role_getter: extracts a role string from params. If no role is found
    the policy denies the request.
    """

    allowed_set = set(allowed_roles)

    def _checker(_: str, params: Dict[str, Any]) -> Optional[str]:
        role = role_getter(params)
        if role in allowed_set:
            return None
        return "role not allowed"

    return _checker


def and_(*policies: PolicyChecker) -> PolicyChecker:
    """Compose multiple policies with logical AND semantics.

    Returns the first denial message encountered, or None if all allow.
    """

    def _checker(cmd_type: str, params: Dict[str, Any]) -> Optional[str]:
        for p in policies:
            msg = p(cmd_type, params)
            if isinstance(msg, str) and msg:
                return msg
        return None

    return _checker


def or_(*policies: PolicyChecker) -> PolicyChecker:
    """Compose policies with logical OR: allow if any policy allows.

    If none allow, returns the last denial message.
    """

    def _checker(cmd_type: str, params: Dict[str, Any]) -> Optional[str]:
        last_msg: Optional[str] = None
        for p in policies:
            msg = p(cmd_type, params)
            if msg is None:
                return None
            last_msg = msg
        return last_msg

    return _checker
