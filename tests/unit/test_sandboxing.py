import sys
from unittest.mock import patch

import pytest

from src.oal_agent.security.sandboxing import Sandbox


@pytest.mark.asyncio
@pytest.mark.skipif(sys.platform == "win32", reason="Resource module not available on Windows")
@patch("src.oal_agent.security.sandboxing.resource")
async def test_sandbox_resource_limits(mock_resource):
    """Test that the sandbox enforces CPU time and memory limits."""
    sandbox = Sandbox()
    code = "pass"
    cpu_time_limit = 1
    memory_limit = 1024 * 1024  # 1 MB

    await sandbox.run(code, cpu_time_limit=cpu_time_limit, memory_limit=memory_limit)

    mock_resource.setrlimit.assert_any_call(
        mock_resource.RLIMIT_CPU, (cpu_time_limit, cpu_time_limit)
    )
    mock_resource.setrlimit.assert_any_call(
        mock_resource.RLIMIT_AS, (memory_limit, memory_limit)
    )


@pytest.mark.asyncio
@pytest.mark.skipif(sys.platform == "win32", reason="Resource module not available on Windows")
@patch("src.oal_agent.security.sandboxing.resource")
async def test_sandbox_invalid_cpu_time_limit(mock_resource):
    """Test that an invalid CPU time limit raises a ValueError."""
    mock_resource.setrlimit.side_effect = ValueError("Invalid argument")
    sandbox = Sandbox()
    code = "pass"
    cpu_time_limit = -1

    with pytest.raises(ValueError, match="Invalid CPU time limit"):
        await sandbox.run(code, cpu_time_limit=cpu_time_limit)


@pytest.mark.asyncio
@pytest.mark.skipif(sys.platform == "win32", reason="Resource module not available on Windows")
@patch("src.oal_agent.security.sandboxing.resource")
async def test_sandbox_invalid_memory_limit(mock_resource):
    """Test that an invalid memory limit raises a ValueError."""
    mock_resource.setrlimit.side_effect = ValueError("Invalid argument")
    sandbox = Sandbox()
    code = "pass"
    memory_limit = -1

    with pytest.raises(ValueError, match="Invalid memory limit"):
        await sandbox.run(code, memory_limit=memory_limit)


@pytest.mark.asyncio
async def test_sandbox_windows_no_limits():
    """Test that resource limits are not applied on Windows and a warning is printed."""
    if sys.platform == "win32":
        sandbox = Sandbox()
        code = "pass"
        cpu_time_limit = 1
        memory_limit = 1024

        with patch("sys.stderr") as mock_stderr:
            await sandbox.run(code, cpu_time_limit=cpu_time_limit, memory_limit=memory_limit)
            mock_stderr.write.assert_called_with(
                "Warning: CPU time and memory limits are not supported on Windows.\n"
            )
    else:
        pytest.skip("Test only applicable on Windows")
