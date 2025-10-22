from pathlib import Path
from src.oal_agent.utils.fs_utils import read_file_content, safe_path_join

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


def test_safe_path_join_basic_relative_paths():
    """
    Tests basic joining of relative path components.
    """
    assert safe_path_join("dir1", "dir2", "file.txt") == Path("dir1/dir2/file.txt")

def test_safe_path_join_with_absolute_path_at_start():
    """
    Tests joining with an absolute path at the beginning.
    """
    assert safe_path_join("/a/b", "c", "d") == Path("/a/b/c/d")

def test_safe_path_join_with_absolute_path_in_middle():
    """
    Tests joining with an absolute path in the middle, which should reset the base.
    """
    assert safe_path_join("a", "b", "/c/d", "e") == Path("/c/d/e")

def test_safe_path_join_with_empty_parts():
    """
    Tests joining with empty string components.
    """
    assert safe_path_join("dir1", "", "dir2", "file.txt") == Path("dir1/dir2/file.txt")
    assert safe_path_join("", "dir1", "dir2") == Path("dir1/dir2")
    assert safe_path_join("dir1", "dir2", "") == Path("dir1/dir2")

def test_safe_path_join_single_part():
    """
    Tests joining with a single path component.
    """
    assert safe_path_join("single_file.txt") == Path("single_file.txt")
    assert safe_path_join("/single_abs_file.txt") == Path("/single_abs_file.txt")

def test_safe_path_join_no_parts():
    """
    Tests joining with no path components.
    """
    assert safe_path_join() == Path(".")

def test_safe_path_join_only_empty_parts():
    """
    Tests joining with only empty string components.
    """
    assert safe_path_join("", "", "") == Path(".")

def test_safe_path_join_with_path_objects():
    """
    Tests joining with Path objects as components.
    """
    assert safe_path_join(Path("dir1"), Path("dir2"), "file.txt") == Path("dir1/dir2/file.txt")
    assert safe_path_join("/a/b", Path("c"), Path("d")) == Path("/a/b/c/d")

def test_safe_path_join_complex_scenario():
    """
    Tests a more complex scenario with mixed absolute, relative, and empty parts.
    """
    assert safe_path_join("start", "", "/absolute", "relative", Path("another"), "") == Path("/absolute/relative/another")

def test_safe_path_join_trailing_slash():
    """
    Tests that trailing slashes are handled correctly (Pathlib normalizes them).
    """
    assert safe_path_join("dir1/", "dir2/") == Path("dir1/dir2")
    assert safe_path_join("/dir1/", "dir2/") == Path("/dir1/dir2")

def test_safe_path_join_leading_slash_relative_part():
    """
    Tests that a leading slash on a relative part is handled correctly (Pathlib treats it as relative to the current part).
    """
    assert safe_path_join("dir1", "/dir2") == Path("/dir2")
    assert safe_path_join("dir1", "./dir2") == Path("dir1/dir2")

def test_safe_path_join_none_parts():
    """
    Tests joining with None as path components.
    """
    assert safe_path_join("dir1", None, "dir2") == Path("dir1/dir2")
    assert safe_path_join(None, "dir1", None, "dir2") == Path("dir1/dir2")
    assert safe_path_join(None, None) == Path(".")