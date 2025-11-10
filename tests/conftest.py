import os
import sys


def _add_repo_root_to_path():
    # Ensure the repository root is on sys.path so top-level modules like
    # `addon.py` can be imported by tests running from the tests/ directory.
    here = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(here, os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


_add_repo_root_to_path()
