from __future__ import annotations

from typing import Dict

from blender_mcp.dispatchers import policies


def test_allow_all_returns_none():
    assert policies.allow_all("any", {}) is None


def test_deny_all_returns_reason():
    msg = policies.deny_all("x", {}, reason="blocked")
    assert isinstance(msg, str)
    assert msg == "blocked"


def test_role_based_allows_and_denies():
    checker = policies.role_based(["admin", "dev"], role_getter=lambda p: p.get("role"))
    assert checker("cmd", {"role": "admin"}) is None
    assert checker("cmd", {"role": "dev"}) is None
    assert checker("cmd", {"role": "user"}) == "role not allowed"
    # missing role is denied
    assert checker("cmd", {}) == "role not allowed"


def test_and_or_composition():
    allow = policies.allow_all
    deny = lambda _t, _p: "nope"
    and_checker = policies.and_(allow, allow)
    assert and_checker("cmd", {}) is None
    and_checker2 = policies.and_(allow, deny)
    assert and_checker2("cmd", {}) == "nope"

    or_checker = policies.or_(deny, allow)
    assert or_checker("cmd", {}) is None
    or_checker2 = policies.or_(deny, deny)
    assert isinstance(or_checker2("cmd", {}), str)
