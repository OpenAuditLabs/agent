# New tests for is_system_path and is_read_only_path

def test_is_system_path():
    """
    Tests the is_system_path function with various system and non-system paths.
    """
    # Test with known system paths
    for p in READ_ONLY_PATHS:
        assert is_system_path(Path(p)), f"Expected {p} to be a system path"

    # Test with subdirectories of known system paths
    assert is_system_path(Path("/usr/local/bin"))
    assert is_system_path(Path("/etc/nginx/nginx.conf"))

    # Test with non-system paths
    assert not is_system_path(Path("/home/user/my_document.txt"))
    assert not is_system_path(Path("relative/path/to/file.py"))
    assert not is_system_path(Path("/tmp/test_file.txt"))
    assert not is_system_path(Path("/var/log/my_app/events.log")) # /var/log is generally writable

    # Test with a path that doesn't exist but matches a system path prefix
    assert is_system_path(Path("/usr/non_existent_dir/file.txt"))


def test_is_read_only_path(tmp_path: Path):
    """
    Tests the is_read_only_path function with various scenarios.
    """
    # Test with known system paths (should be read-only by definition)
    for p_str in READ_ONLY_PATHS:
        p = Path(p_str)
        assert is_read_only_path(p), f"Expected system path {p} to be read-only"

    # Test with a path within a system path that doesn't exist
    assert is_read_only_path(Path("/bin/non_existent_tool"))

    # Test with an existing, writable file in a non-system directory
    writable_file = tmp_path / "writable.txt"
    writable_file.write_text("test")
    os.chmod(writable_file, 0o644)  # Ensure it's writable
    assert not is_read_only_path(writable_file), "Expected writable_file to not be read-only"

    # Test with an existing, read-only file in a non-system directory
    read_only_file = tmp_path / "read_only.txt"
    read_only_file.write_text("test")
    os.chmod(read_only_file, 0o444)  # Make it read-only
    assert is_read_only_path(read_only_file), "Expected read_only_file to be read-only"

    # Test with a non-existent path that is not a system path
    non_existent_non_system_path = tmp_path / "non_existent_dir" / "file.txt"
    assert not is_read_only_path(non_existent_non_system_path), "Expected non-existent non-system path to not be read-only"

    # Test with an existing writable directory
    writable_dir = tmp_path / "writable_dir"
    writable_dir.mkdir()
    os.chmod(writable_dir, 0o755) # Ensure it's writable
    assert not is_read_only_path(writable_dir), "Expected writable_dir to not be read-only"

    # Test with an existing read-only directory
    read_only_dir = tmp_path / "read_only_dir"
    read_only_dir.mkdir()
    os.chmod(read_only_dir, 0o555) # Make it read-only (executable but not writable)
    assert is_read_only_path(read_only_dir), "Expected read_only_dir to be read-only"