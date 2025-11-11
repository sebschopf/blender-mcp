"""Small download helpers to centralize network IO and safe zip extraction.

These helpers are intentionally small and raise on HTTP errors so callers
can handle/report them. They make it easier to mock network calls in tests.
"""

from __future__ import annotations

import io
import logging
import os
import time
import zipfile
from typing import Any, Mapping, Optional

import requests
from requests.exceptions import HTTPError, RequestException

logger = logging.getLogger(__name__)


def download_bytes(
    url: str,
    timeout: Optional[float] = 60.0,
    headers: Optional[Mapping[str, Any]] = None,
    *,
    max_retries: int = 3,
    backoff_factor: float = 0.5,
    session: Optional[requests.sessions.Session] = None,
) -> bytes:
    """Download raw bytes from a URL with simple retry/backoff.

    Retries on network errors and 5xx HTTP responses. Does not retry on
    client errors (4xx). Parameters `max_retries` and `backoff_factor`
    control retry behaviour; sleeps between retries using exponential
    backoff: backoff_factor * (2 ** attempt).

    Raises the underlying exception on final failure.
    """
    attempt = 0
    last_exc: Exception | None = None
    while attempt <= max_retries:
        try:
            if session is not None:
                resp = session.get(url, timeout=timeout, headers=headers)
            else:
                resp = requests.get(url, timeout=timeout, headers=headers)
            # raise_for_status will raise HTTPError for 4xx/5xx
            resp.raise_for_status()
            return resp.content
        except HTTPError as he:
            status = None
            try:
                status = he.response.status_code  # type: ignore[attr-defined]
            except Exception:
                status = None
            # Do not retry on client errors (4xx)
            if status is not None and 400 <= status < 500:
                raise
            last_exc = he
        except RequestException as re:
            # network-level error (Timeout, ConnectionError, etc.) — retry
            last_exc = re

        # If we are here, we encountered an error. If exhausted, raise.
        if attempt == max_retries:
            if last_exc:
                raise last_exc
            raise RuntimeError("download failed")

        # Sleep with exponential backoff before retrying
        sleep_for = backoff_factor * (2**attempt)
        logger.debug(
            "download_bytes: attempt %s failed, sleeping %s seconds before retry (%s)",
            attempt,
            sleep_for,
            last_exc,
        )
        try:
            time.sleep(sleep_for)
        except Exception:
            # In test environments time.sleep may be patched; ignore errors
            pass

        attempt += 1
    # Should not be reachable, but satisfy type checkers
    raise RuntimeError("download failed")


def secure_extract_zip_bytes(zip_bytes: bytes, target_dir: str | None = None) -> str:
    """Extract zip bytes safely.

    If `target_dir` is provided, extract into it and return the path. If
    `target_dir` is None, a temporary directory is created, extraction is
    performed there and the path to that directory is returned.

    Raises ValueError on suspicious zip entries (path traversal).
    """
    # Lazy import to keep this module import-friendly in tests
    import tempfile

    created_temp = False
    if target_dir is None:
        target_dir = tempfile.mkdtemp(prefix="blender_mcp_zip_")
        created_temp = True

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_ref:
        for file_info in zip_ref.infolist():
            file_path = file_info.filename

            # Normalize and compute absolute paths
            target_path = os.path.join(target_dir, os.path.normpath(file_path))
            abs_temp_dir = os.path.abspath(target_dir)
            abs_target_path = os.path.abspath(target_path)

            if not abs_target_path.startswith(abs_temp_dir):
                # If we created the temp dir for this extraction, attempt cleanup
                if created_temp:
                    try:
                        import shutil

                        shutil.rmtree(target_dir)
                    except Exception:
                        pass
                raise ValueError("Zip contains path traversal entries")

            # Also reject explicit '..' segments
            if ".." in file_path.split(os.path.sep):
                if created_temp:
                    try:
                        import shutil

                        shutil.rmtree(target_dir)
                    except Exception:
                        pass
                raise ValueError("Zip contains directory traversal sequence")

        # If all checks pass, extract
        zip_ref.extractall(target_dir)

    return target_dir


def download_to_tempfile(
    url: str,
    prefix: str = "",
    suffix: str = "",
    timeout: Optional[float] = 120.0,
    headers: Optional[Mapping[str, Any]] = None,
    session: Optional[requests.sessions.Session] = None,
) -> str:
    """Download a URL and write it to a NamedTemporaryFile, returning the path.

    This uses download_bytes (which raises on HTTP errors) and is a small
    convenience wrapper so callers don't duplicate tempfile management.
    """
    import os
    import tempfile

    # Forward optional session to download_bytes for connection reuse/testability.
    if session is None:
        data = download_bytes(url, timeout=timeout, headers=headers)
    else:
        data = download_bytes(url, timeout=timeout, headers=headers, session=session)
    tf = tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix)
    try:
        tf.write(data)
        tf.close()
        return tf.name
    except Exception:
        try:
            tf.close()
        except Exception:
            pass
        try:
            os.unlink(tf.name)
        except Exception:
            pass
        raise
