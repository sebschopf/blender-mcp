from __future__ import annotations

from typing import List, Tuple

from blender_mcp.errors import (
    BlenderMCPError,
    ExecutionTimeoutError,
    ExternalServiceError,
    HandlerError,
    HandlerNotFoundError,
    InvalidParamsError,
    PolicyDeniedError,
    error_code_for_exception,
)


def test_error_code_for_each_canonical_exception() -> None:
    cases: List[Tuple[BlenderMCPError, str]] = [
        (InvalidParamsError("bad"), "invalid_params"),
        (HandlerNotFoundError("missing"), "not_found"),
        (PolicyDeniedError("denied"), "policy_denied"),
        (ExecutionTimeoutError("t"), "timeout"),
        (HandlerError("h", ValueError("boom")), "handler_error"),
        (ExternalServiceError("ext"), "external_error"),
    ]
    for exc, expected in cases:
        assert error_code_for_exception(exc) == expected


def test_error_code_fallback_internal_error() -> None:
    class CustomError(BlenderMCPError):
        pass

    exc: CustomError = CustomError("x")
    assert error_code_for_exception(exc) == "internal_error"
