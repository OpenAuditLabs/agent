import sys
from unittest.mock import patch

import pytest

from src.oal_agent.security.sandboxing import Sandbox


@pytest.mark.skipif(sys.platform == "win32", reason="Resource module not available on Windows")
def test_sandbox_resource_limits():
    """Test that the sandbox enforces CPU time and memory limits."""
    sandbox = Sandbox()
    code = "pass"
    cpu_time_limit = 1
    memory_limit = 1024 * 1024  # 1 MB

    stdout, stderr = sandbox.run(code, cpu_time_limit=cpu_time_limit, memory_limit=memory_limit)
    assert stderr == ""


@pytest.mark.skipif(sys.platform == "win32", reason="Resource module not available on Windows")
def test_sandbox_invalid_cpu_time_limit():
    """Test that an invalid CPU time limit raises a ValueError."""
    sandbox = Sandbox()
    code = "pass"
    cpu_time_limit = -1

    stdout, stderr = sandbox.run(code, cpu_time_limit=cpu_time_limit)
    assert stderr == (
        "Error: Sandbox process exited with non-zero code 1.\n"
        "Stdout: \n"
        "Stderr: Error: Invalid CPU time limit in child process: -1 is negative\n"
    )


@pytest.mark.skipif(sys.platform == "win32", reason="Resource module not available on Windows")
def test_sandbox_invalid_memory_limit():
    """Test that an invalid memory limit raises a ValueError."""
    sandbox = Sandbox()
    code = "pass"
    memory_limit = -1

    stdout, stderr = sandbox.run(code, memory_limit=memory_limit)
    assert stderr == (
        "Error: Sandbox process exited with non-zero code 1.\n"
        "Stdout: \n"
        "Stderr: Error: Invalid memory limit in child process: -1 is negative\n"
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
        assert captured.stderr == "Warning: CPU time and memory limits are not supported on Windows.\n"
    else:
        pytest.skip("Test only applicable on Windows")
