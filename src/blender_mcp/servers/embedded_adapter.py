"""Embedded server adapter moved into `servers` package.

This is a copy of the top-level `embedded_server_adapter.py` adjusted to
live under the `servers` package.
"""

from __future__ import annotations

import logging
import os
import platform
import subprocess
from typing import Any, Iterable, List, Optional

logger = logging.getLogger(__name__)


def _default_command() -> List[str]:
    # Use the repository PowerShell helper on Windows by default; otherwise
    # require the caller to pass an explicit command.
    if platform.system() == "Windows":
        repo_root = os.path.dirname(os.path.dirname(__file__))
        script = os.path.join(repo_root, "..", "scripts", "start-server.ps1")
        # Run PowerShell in a non-interactive mode to execute the script.
        return ["pwsh", "-NoProfile", "-NonInteractive", "-File", script]
    raise RuntimeError("No default server command for non-Windows platforms; pass `command` explicitly")


def start_server_process(command: Optional[Iterable[str]] = None, cwd: Optional[str] = None) -> subprocess.Popen[Any]:
    """Start an external server process and return the Popen object.

    The caller is responsible for keeping the returned Popen and calling
    :func:`stop_server_process` when appropriate.
    """
    if command is None:
        command = _default_command()
    cmd_list = list(command)
    logger.info("Starting external server: %s", cmd_list)
    # Start detached process group so child won't be killed when parent exits
    proc = subprocess.Popen(cmd_list, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def stop_server_process(proc: subprocess.Popen[Any], timeout: float = 5.0) -> None:
    """Terminate the given process, waiting up to `timeout` seconds.

    Best-effort cleanup: if the process doesn't exit gracefully it will be
    killed.
    """
    if proc.poll() is not None:
        return
    logger.info("Stopping external server (pid=%s)", getattr(proc, "pid", "?"))
    try:
        proc.terminate()
        proc.wait(timeout=timeout)
    except Exception:
        logger.exception("Graceful shutdown failed; killing process")
        try:
            proc.kill()
        except Exception:
            logger.exception("Failed to kill process")


def is_running(proc: subprocess.Popen[Any]) -> bool:
    return proc.poll() is None


__all__ = ["start_server_process", "stop_server_process", "is_running"]
