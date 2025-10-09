"""File system utilities."""

import os
from pathlib import Path

from oal_agent.utils.fs_utils import read_file_content


def ensure_dir(path: str):
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)


def read_file(path: str) -> str:
    """Read file contents."""
    return read_file_content(Path(path), default_value="")


def write_file(path: str, content: str):
    """Write content to file."""
    ensure_dir(os.path.dirname(path))
    with open(path, 'w') as f:
        f.write(content)
