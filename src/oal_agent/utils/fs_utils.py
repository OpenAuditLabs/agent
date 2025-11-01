import logging
from pathlib import Path
from typing import Any, Union

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Get the project root directory by searching for 'pyproject.toml'."""
    current_path = Path.cwd()
    while current_path != current_path.parent:
        if (current_path / "pyproject.toml").exists():
            return current_path
        current_path = current_path.parent
    # Fallback if pyproject.toml is not found
    return Path.cwd()


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
    joined_path = Path(".")
    for part in parts:
        if part is None or str(part) == "":
            continue
        current_part = Path(part)
        if current_part.is_absolute():
            joined_path = current_part
        else:
            joined_path = joined_path / current_part
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
