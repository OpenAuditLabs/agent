"""File system utilities."""

import os
from pathlib import Path
from typing import cast

from oal_agent.utils.fs_utils import read_file_content

# Common read-only system directories (case-insensitive for some OS, but typically exact match on Linux)

# Common read-only system directories (case-insensitive on Windows, exact match on Linux/macOS)

# Consumers of this set should normalize paths and perform case-insensitive comparisons on Windows.

READ_ONLY_PATHS = {
    "/etc",
    "/usr",
    "/bin",
    "/sbin",
    "/lib",
    "/boot",
    "/dev",
    "/proc",
    "/sys",
    "/run",
    "/root",
    "/System",
    "/Library",
    "/private/var/db",  # macOS system paths
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",  # Windows system paths
}


def ensure_dir(path: str):
    """Ensure directory exists."""

    Path(path).mkdir(parents=True, exist_ok=True)


def read_file(path: str) -> str:
    """Read file contents."""

    return cast(str, read_file_content(Path(path), default_value=""))


def is_system_path(path: Path) -> bool:
    """



    Checks if the given path is a system-critical path that should generally be read-only.



    This is a heuristic and might not cover all cases or all operating systems.



    """

    # Normalize path for consistent checking

    try:

        abs_path = path.resolve()

    except OSError:

        # Path does not exist, but we can still check its absolute string representation

        abs_path = path.absolute()

    for ro_path_str in READ_ONLY_PATHS:

        ro_path = Path(ro_path_str)

        # On Windows, paths are case-insensitive. Normalize to lower case for comparison.

        # This is a heuristic; a more robust solution might use platform-specific Path methods

        # or a library like `pathvalidate` if available.

        if os.name == "nt":

            if abs_path.as_posix().lower() == ro_path.as_posix().lower():

                return True

            try:

                # Check if abs_path is a subpath of ro_path, case-insensitively

                # This involves converting to string and comparing prefixes for simplicity,\

                # as relative_to might be too strict with case or drive letters.

                abs_path_str = str(abs_path).lower()

                ro_path_str = str(ro_path).lower()

                if abs_path_str.startswith(ro_path_str):

                    # Ensure the match is at a path boundary

                    if len(abs_path_str) == len(ro_path_str) or abs_path_str[
                        len(ro_path_str)
                    ] in ("/", "\\"):

                        return True

            except TypeError:

                # Handle cases where path components might be non-string (unlikely with Path)

                pass

        else:

            if abs_path == ro_path:

                return True

            try:

                # Check if abs_path is a subpath of ro_path

                abs_path.relative_to(ro_path)

                return True

            except ValueError:

                # path is not a subpath of ro_path

                pass

    return False


def is_read_only_path(path: str | Path) -> bool:
    """

    Determines if a given path is considered read-only based on system conventions

    or explicit file permissions if the path exists.

    """

    p = Path(path)

    if is_system_path(p):

        return True

    # If path exists, check actual file system permissions

    if p.exists():

        return not os.access(p, os.W_OK)

    # If path doesn't exist and it's not a known system path, assume it's writable

    # (or rather, not explicitly read-only by convention)

    return False


def write_file(path: str, content: str):
    """Write content to file."""

    if is_read_only_path(path):

        raise PermissionError(f"Attempt to write to a read-only path: {path}")

    parent_dir = os.path.dirname(path)
    if parent_dir and is_read_only_path(parent_dir):
        raise PermissionError(
            f"Attempt to write to a file in a read-only directory: {parent_dir}"
        )
    ensure_dir(parent_dir)

    with open(path, "w") as f:

        f.write(content)
