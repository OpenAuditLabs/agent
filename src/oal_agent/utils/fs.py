"""File system utilities."""

import os

from pathlib import Path

from typing import cast



from oal_agent.utils.fs_utils import read_file_content



# Common read-only system directories (case-insensitive for some OS, but typically exact match on Linux)

READ_ONLY_PATHS = {

    "/etc", "/usr", "/bin", "/sbin", "/lib", "/boot", "/dev", "/proc", "/sys", "/run",

    "/var/lock", "/var/run" # Specific common read-only subdirectories

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

        # Path does not exist, but we can still check its string representation

        abs_path = path.absolute()



    for ro_path in READ_ONLY_PATHS:

        if str(abs_path) == ro_path or str(abs_path).startswith(f"{ro_path}/"):

            return True

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

    ensure_dir(os.path.dirname(path))

    with open(path, "w") as f:

        f.write(content)
