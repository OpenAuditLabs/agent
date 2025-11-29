import contextlib
import logging
import shutil
import tempfile
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


@contextlib.contextmanager
def safe_temp_dir(suffix: str = "", prefix: str = "tmp_") -> Path:
    """
    Context manager for creating a secure temporary directory.

    The directory is created with 0o700 permissions (owner read/write/execute only)
    and is automatically cleaned up when the context is exited.

    Args:
        suffix: If not empty, the file name will end with that suffix.
        prefix: If not empty, the file name will begin with that prefix.

    Yields:
        Path: The path to the created temporary directory.
    """
    temp_dir: Union[Path, None] = None
    try:
        temp_dir = Path(tempfile.mkdtemp(suffix=suffix, prefix=prefix))
        temp_dir.chmod(0o700)  # Owner read/write/execute only
        yield temp_dir
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)
