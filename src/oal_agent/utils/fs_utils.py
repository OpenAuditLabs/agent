import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

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
        return file_path.read_text()
    except Exception as e:
        logger.debug(f"Error reading file {file_path}: {e}")
        return default_value
