"""File system utilities."""

import os
from pathlib import Path


def ensure_dir(path: str):
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)


def read_file(path: str) -> str:
    """Read file contents."""
    with open(path, 'r') as f:
        return f.read()


def write_file(path: str, content: str):
    """Write content to file."""
    ensure_dir(os.path.dirname(path))
    with open(path, 'w') as f:
        f.write(content)
