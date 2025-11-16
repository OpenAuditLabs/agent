import os
import sys

import pytest

from src.oal_agent.security.sandboxing import Sandbox, sanitize_path


@pytest.fixture
def temp_paths(tmp_path):
    """Fixture to create temporary paths and symlinks for testing."""
    base = tmp_path / "base"
    base.mkdir()

    # Create a file inside base
    (base / "file.txt").write_text("content")

    # Create a directory inside base
    (base / "subdir").mkdir()
    (base / "subdir" / "nested_file.txt").write_text("nested content")

    # Create a directory outside base
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret content")

    # Create a symlink inside base pointing outside
    (base / "link_to_outside").symlink_to(outside)

    # Create a symlink inside base pointing inside
    (base / "link_to_subdir").symlink_to(base / "subdir")

    return {"base": base, "outside": outside}


def test_sanitize_path_valid_path(temp_paths):
    """Test sanitizing a valid path within the base directory."""
    base = str(temp_paths["base"])
    target = "file.txt"
    sanitized = sanitize_path(base, target)
    assert sanitized == os.path.realpath(os.path.join(base, target))


def test_sanitize_path_subdir_valid_path(temp_paths):
    """Test sanitizing a valid path within a subdirectory."""
    base = str(temp_paths["base"])
    target = "subdir/nested_file.txt"
    sanitized = sanitize_path(base, target)
    assert sanitized == os.path.realpath(os.path.join(base, target))


def test_sanitize_path_path_traversal_escape(temp_paths):
    """Test sanitizing a path that attempts to escape using '..'."""
    base = str(temp_paths["base"])
    target = "../outside/secret.txt"
    with pytest.raises(
        ValueError, match=f"Path {target} attempts to escape base path {base}"
    ):
        sanitize_path(base, target)


def test_sanitize_path_symlink_escape(temp_paths):
    """Test sanitizing a path that attempts to escape using a symlink."""
    base = str(temp_paths["base"])
    target = "link_to_outside/secret.txt"
    with pytest.raises(
        ValueError, match=f"Path {target} attempts to escape base path {base}"
    ):
        sanitize_path(base, target)


def test_sanitize_path_symlink_within_base(temp_paths):
    """Test sanitizing a path that uses a symlink pointing within the base directory."""
    base = str(temp_paths["base"])
    target = "link_to_subdir/nested_file.txt"
    sanitized = sanitize_path(base, target)
    expected_path = os.path.realpath(os.path.join(base, "subdir", "nested_file.txt"))
    assert sanitized == expected_path


def test_sanitize_path_prefix_directory_escape(temp_paths, tmp_path):
    """Test sanitizing a path where a sibling directory has the base path as a prefix."""
    base = str(temp_paths["base"])
    
    # Create a sibling directory named like "<base>_evil"
    evil_sibling_dir = tmp_path / f"{os.path.basename(base)}_evil"
    evil_sibling_dir.mkdir()
    (evil_sibling_dir / "evil_file.txt").write_text("evil content")

    target = f"../{os.path.basename(evil_sibling_dir)}/evil_file.txt"
    with pytest.raises(
        ValueError, match=f"Path {target} attempts to escape base path {base}"
    ):
        sanitize_path(base, target)


@pytest.mark.skipif(
    sys.platform == "win32", reason="Resource module not available on Windows"
)
def test_sandbox_resource_limits():
    """Test that the sandbox enforces CPU time and memory limits."""
    sandbox = Sandbox()
    code = "pass"
    cpu_time_limit = 1
    memory_limit = 1024 * 1024  # 1 MB

    _, stderr = sandbox.run(
        code, cpu_time_limit=cpu_time_limit, memory_limit=memory_limit
    )
    assert stderr == ""


@pytest.mark.skipif(
    sys.platform == "win32", reason="Resource module not available on Windows"
)
def test_sandbox_invalid_cpu_time_limit():
    """Test that an invalid CPU time limit raises a ValueError."""
    sandbox = Sandbox()
    code = "pass"
    cpu_time_limit = -1

    _, stderr = sandbox.run(code, cpu_time_limit=cpu_time_limit)
    assert stderr == (
        "Error: Sandbox process exited with non-zero code 1.\n"
        "Stdout: \n"
        "Stderr: Error: Invalid CPU time limit in child process: -1 must be positive\n"
    )


@pytest.mark.skipif(
    sys.platform == "win32", reason="Resource module not available on Windows"
)
def test_sandbox_invalid_memory_limit():
    """Test that an invalid memory limit raises a ValueError."""
    sandbox = Sandbox()
    code = "pass"
    memory_limit = -1

    _, stderr = sandbox.run(code, memory_limit=memory_limit)
    assert stderr == (
        "Error: Sandbox process exited with non-zero code 1.\n"
        "Stdout: \n"
        "Stderr: Error: Invalid memory limit in child process: -1 must be positive\n"
    )


def test_sandbox_windows_no_limits(capsys):
    """Test that resource limits are not applied on Windows and a warning is printed."""
    if sys.platform == "win32":
        sandbox = Sandbox()
        code = "pass"
        cpu_time_limit = 1
        memory_limit = 1024

        sandbox.run(code, cpu_time_limit=cpu_time_limit, memory_limit=memory_limit)
        captured = capsys.readouterr()
        assert (
            captured.stderr
            == "Warning: CPU time and memory limits are not supported on Windows.\n"
        )
    else:
        pytest.skip("Test only applicable on Windows")
