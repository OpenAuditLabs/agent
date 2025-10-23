import logging
from pathlib import Path
from typing import Any, Union

logger = logging.getLogger(__name__)

def get_project_root() -> Path:


def safe_path_join(*parts: Union[str, Path]) -> Path:
    """
    Joins multiple path components intelligently, handling absolute paths and empty parts.
    If an absolute path is encountered, subsequent relative parts are joined to it.
    Empty parts are ignored.

    Args:
        *parts: Variable number of path components (str or Path).

    Returns:
        A Path object representing the joined path.
    """
    if not parts:
        return Path(".")

    # Filter out empty strings and convert all parts to Path objects
    path_objects = [Path(p) for p in parts if p is not None and str(p) != ""]

    if not path_objects:
        return Path(".")

    # Start with the first valid path object
    joined_path = path_objects[0]

    # Iterate through the rest of the path objects and join them
    for i in range(1, len(path_objects)):
        part = path_objects[i]
        if part.is_absolute():
            # If an absolute path is encountered, it resets the base for subsequent joins
            joined_path = part
        else:
            joined_path = joined_path / part

    return joined_path


def read_file_content(file_path: Path, default_value: Any = None) -> Any:
    """
    Reads the content of a file, logging any exceptions at debug level.

    Args:
        file_path: The path to the file.
        default_value: The value to return if an exception occurs during file reading.

    Returns:
        The content of the file, or the default_value if an error occurs.
    """
    try:
        return file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        logger.debug(f"Error reading file {file_path}: {e}")
        return default_value
