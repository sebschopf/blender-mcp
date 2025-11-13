"""Canonical exceptions and response shapes for blender_mcp.

This module defines typed exceptions for services and a small set of
TypedDict shapes used by adapters to produce stable, machine-readable
error codes while preserving backward-compatible human messages.
"""
from __future__ import annotations

from typing import Any, Literal, Optional, TypedDict


class BlenderMCPError(Exception):
    """Base class for all canonical errors in blender_mcp."""


class InvalidParamsError(BlenderMCPError):
    """Raised when provided params are invalid.

    Optionally contains a `fields` attribute describing invalid fields.
    """

    def __init__(self, message: str = "Invalid parameters", *, fields: Optional[Any] = None) -> None:
        super().__init__(message)
        self.fields = fields


class HandlerNotFoundError(BlenderMCPError):
    """Raised when a named handler was not found."""


class PolicyDeniedError(BlenderMCPError):
    """Raised when a policy prevents execution of a command."""


class ExecutionTimeoutError(BlenderMCPError):
    """Raised when a handler times out."""


class ExternalServiceError(BlenderMCPError):
    """Raised when an external dependency fails (network, remote API, etc.)."""


class HandlerError(BlenderMCPError):
    """Wrapper for exceptions raised by handlers.

    Keeps the original exception as `original` for diagnostics.
    """

    def __init__(self, name: str, original: Exception) -> None:
        super().__init__(f"Handler '{name}' raised: {original!r}")
        self.name = name
        self.original = original


# Response shapes used by adapters
class SuccessResult(TypedDict, total=True):
    status: str
    result: Any


class ErrorResult(TypedDict, total=True):
    status: str
    message: str
    # stable machine-readable error code (e.g. 'invalid_params')
    error_code: str


# Canonical set de codes d'erreur machine-readable.
ErrorCode = Literal[
    "invalid_command",
    "invalid_command_type",
    "policy_denied",
    "not_found",
    "invalid_params",
    "timeout",
    "handler_error",
    "external_error",
    "internal_error",
]


class ErrorInfo(TypedDict, total=True):
    message: str
    error_code: ErrorCode


def error_code_for_exception(exc: BlenderMCPError) -> ErrorCode:
    if isinstance(exc, InvalidParamsError):
        return "invalid_params"
    if isinstance(exc, HandlerNotFoundError):
        return "not_found"
    if isinstance(exc, PolicyDeniedError):
        return "policy_denied"
    if isinstance(exc, ExecutionTimeoutError):
        return "timeout"
    if isinstance(exc, HandlerError):
        return "handler_error"
    if isinstance(exc, ExternalServiceError):
        return "external_error"
    return "internal_error"


__all__ = [
    "BlenderMCPError",
    "InvalidParamsError",
    "HandlerNotFoundError",
    "PolicyDeniedError",
    "ExecutionTimeoutError",
    "ExternalServiceError",
    "HandlerError",
    "SuccessResult",
    "ErrorResult",
    "ErrorCode",
    "ErrorInfo",
    "error_code_for_exception",
]
