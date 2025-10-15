import pytest
from pathlib import Path
from src.oal_agent.utils.fs_utils import read_file_content

def test_read_file_content_success(tmp_path: Path):
    """
    Tests that read_file_content successfully reads the content of an existing file.
    """
    file_content = "Hello, this is a test file."
    test_file = tmp_path / "test.txt"
    test_file.write_text(file_content)

    result = read_file_content(test_file)
    assert result == file_content

def test_read_file_content_file_not_found(tmp_path: Path):
    """
    Tests that read_file_content returns None (default behavior) when the file does not exist.
    """
    non_existent_file = tmp_path / "non_existent.txt"
    result = read_file_content(non_existent_file)
    assert result is None

def test_read_file_content_with_default_value(tmp_path: Path):
    """
    Tests that read_file_content returns the specified default value when the file does not exist.
    """
    non_existent_file = tmp_path / "another_non_existent.txt"
    default_value = "Default content"
    result = read_file_content(non_existent_file, default_value=default_value)
    assert result == default_value

def test_read_file_content_empty_file(tmp_path: Path):
    """
    Tests that read_file_content correctly reads an empty file.
    """
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")

    result = read_file_content(empty_file)
    assert result == ""
