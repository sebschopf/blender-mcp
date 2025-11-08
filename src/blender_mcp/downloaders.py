"""Small download helpers to centralize network IO and safe zip extraction.

These helpers are intentionally small and raise on HTTP errors so callers
can handle/report them. They make it easier to mock network calls in tests.
"""
from __future__ import annotations

import io
import os
import zipfile
from typing import Any, Mapping, Optional

import requests


def download_bytes(url: str, timeout: Optional[float] = 60.0, headers: Optional[Mapping[str, Any]] = None) -> bytes:
    """Download raw bytes from a URL. Raises an exception on HTTP error."""
    resp = requests.get(url, timeout=timeout, headers=headers)
    resp.raise_for_status()
    return resp.content


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
    headers: Optional[dict] = None,
) -> str:
    """Download a URL and write it to a NamedTemporaryFile, returning the path.

    This uses download_bytes (which raises on HTTP errors) and is a small
    convenience wrapper so callers don't duplicate tempfile management.
    """
    import os
    import tempfile

    data = download_bytes(url, timeout=timeout, headers=headers)
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
