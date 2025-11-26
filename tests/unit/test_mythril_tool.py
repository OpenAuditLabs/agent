import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest

from oal_agent.tools.mythril import MythrilTool
from oal_agent.tools.sandbox import SandboxResult


@pytest.fixture
def mythril_tool(mocker):
    mocker.patch("oal_agent.tools.mythril.MythrilTool._check_mythril_version")
    return MythrilTool()


@pytest.mark.asyncio
async def test_analyze_uses_temp_file_and_cleans_up(mythril_tool):
    contract_code = (
        "pragma solidity ^0.8.0; contract MyContract { function foo() public {} }"
    )

    with patch(
        "oal_agent.tools.mythril.execute_external_command", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = SandboxResult(stdout="Mythril analysis result", stderr="", exit_code=0)

        result = await mythril_tool.analyze(contract_code)

        assert result.stdout == "Mythril analysis result"
        mock_execute.assert_called_once()

        args = mock_execute.call_args[0]
        assert args[0] == "myth"
        assert args[1] == "analyze"
        temp_file_path = args[2]
        assert temp_file_path.endswith(".sol")

        assert not os.path.exists(temp_file_path), "Temporary file was not cleaned up"


@pytest.mark.asyncio
async def test_analyze_returns_result_despite_cleanup_error(mythril_tool, tmp_path):
    contract_code = (
        "pragma solidity ^0.8.0; contract MyContract { function bar() public {} }"
    )
    mock_result = SandboxResult(stdout="Analysis result despite cleanup error", stderr="", exit_code=0)

    with patch(
        "oal_agent.tools.mythril.execute_external_command", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = mock_result
        with patch("os.unlink") as mock_unlink:
            mock_unlink.side_effect = OSError("Cleanup failed")

            with patch("oal_agent.tools.mythril.logger") as mock_logger:
                result = await mythril_tool.analyze(contract_code)

                assert result.stdout == mock_result.stdout
                mock_unlink.assert_called_once()
                # Ensure the logger.warning was called
                mock_logger.warning.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_temp_file_content(mythril_tool, tmp_path):
    contract_code = "pragma solidity ^0.8.0; contract MyContract { function baz() public {} }\n// Additional line"
    temp_file_path = None

    async def mock_execute_external_command(*args, **kwargs):
        nonlocal temp_file_path
        temp_file_path = args[2]
        # Read the content of the temporary file before it's "processed" by the external command
        with open(temp_file_path, "r") as f:
            content = f.read()
            assert content == contract_code
        return SandboxResult(stdout="Content verified result", stderr="", exit_code=0)

    original_named_temp_file = tempfile.NamedTemporaryFile

    def mock_named_temp_file(*args, **kwargs):
        # Ensure the file is created within tmp_path
        kwargs["dir"] = tmp_path
        f = original_named_temp_file(*args, **kwargs)
        return f

    with patch(
        "oal_agent.tools.mythril.execute_external_command",
        new_callable=AsyncMock,
        side_effect=mock_execute_external_command,
    ):
        with patch("tempfile.NamedTemporaryFile", side_effect=mock_named_temp_file):
            result = await mythril_tool.analyze(contract_code)

            assert result.stdout == "Content verified result"
            assert temp_file_path is not None
            assert not os.path.exists(
                temp_file_path
            ), "Temporary file was not cleaned up after content check"


@pytest.mark.asyncio
async def test_analyze_propagates_mythril_errors(mythril_tool):
    contract_code = "invalid solidity code"

    with patch(
        "oal_agent.tools.mythril.execute_external_command", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.side_effect = RuntimeError("Mythril command failed")

        with pytest.raises(RuntimeError, match="Mythril analysis failed"):
            await mythril_tool.analyze(contract_code)

        mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_file_creation_error(mythril_tool):
    contract_code = (
        "pragma solidity ^0.8.0; contract MyContract { function foo() public {} }"
    )

    with patch("tempfile.NamedTemporaryFile") as mock_named_temp_file:
        mock_named_temp_file.side_effect = IOError("Disk full")

        with pytest.raises(RuntimeError, match="Mythril analysis failed"):
            await mythril_tool.analyze(contract_code)

        mock_named_temp_file.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_file_write_error(mythril_tool):
    contract_code = (
        "pragma solidity ^0.8.0; contract MyContract { function foo() public {} }"
    )

    with patch("asyncio.to_thread") as mock_to_thread:
        mock_to_thread.side_effect = IOError("Write error")

        with pytest.raises(RuntimeError, match="Mythril analysis failed"):
            await mythril_tool.analyze(contract_code)

        mock_to_thread.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_file_permission_error(mythril_tool):
    contract_code = (
        "pragma solidity ^0.8.0; contract MyContract { function foo() public {} }"
    )

    with patch("os.chmod") as mock_chmod:
        mock_chmod.side_effect = OSError("Permission denied")

        with pytest.raises(RuntimeError, match="Mythril analysis failed"):
            await mythril_tool.analyze(contract_code)

        mock_chmod.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_file_permissions_set(mythril_tool, tmp_path):
    contract_code = (
        "pragma solidity ^0.8.0; contract MyContract { function baz() public {} }"
    )

    with patch(
        "oal_agent.tools.mythril.execute_external_command", new_callable=AsyncMock
    ) as mock_execute:
        with patch("os.chmod") as mock_chmod:
            mock_execute.return_value = SandboxResult(stdout="Permission check result", stderr="", exit_code=0)

            # To ensure tempfile.NamedTemporaryFile creates a file in tmp_path
            original_named_temp_file = tempfile.NamedTemporaryFile
            temp_file_path = None

            def mock_named_temp_file(*args, **kwargs):
                nonlocal temp_file_path
                # Ensure the file is created within tmp_path
                kwargs["dir"] = tmp_path
                f = original_named_temp_file(*args, **kwargs)
                temp_file_path = f.name
                return f

            with patch("tempfile.NamedTemporaryFile", side_effect=mock_named_temp_file):
                result = await mythril_tool.analyze(contract_code)

                assert result.stdout == "Permission check result"
                mock_chmod.assert_called_once_with(temp_file_path, 0o600)


@pytest.mark.asyncio
async def test_analyze_temp_file_closed_before_command(mythril_tool, tmp_path):
    contract_code = (
        "pragma solidity ^0.8.0; contract MyContract { function qux() public {} }"
    )

    mock_close = Mock()

    class MockNamedTemporaryFile:
        def __init__(self, *args, **kwargs):
            self.name = str(tmp_path / "mock_temp_file.sol")
            self.closed = False
            # Create a dummy file to simulate its existence for chmod
            tmp_path.joinpath("mock_temp_file.sol").write_text("dummy content")

        def write(self, content):
            pass

        def close(self):
            self.closed = True
            mock_close()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch(
        "oal_agent.tools.mythril.execute_external_command", new_callable=AsyncMock
    ) as mock_execute:
        with patch("tempfile.NamedTemporaryFile", side_effect=MockNamedTemporaryFile):

            mock_execute.return_value = SandboxResult(stdout="Closed file check result", stderr="", exit_code=0)

            result = await mythril_tool.analyze(contract_code)

            assert result.stdout == "Closed file check result"
            mock_close.assert_called_once()
            mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_check_mythril_version_supported(mocker):
    mocker.patch("shutil.which", return_value="/usr/bin/myth")
    mocker.patch(
        "oal_agent.tools.mythril.subprocess.run",
        return_value=Mock(stdout="Mythril version 0.24.12\n", stderr="", returncode=0),
    )
    with patch("oal_agent.tools.mythril.logger") as mock_logger:
        tool = MythrilTool()
        mock_logger.info.assert_called_with(
            "Mythril version %s detected (supported).", "0.24.12"
        )
        mock_logger.warning.assert_not_called()


@pytest.mark.asyncio
async def test_check_mythril_version_unsupported(mocker):
    mocker.patch("shutil.which", return_value="/usr/bin/myth")
    mocker.patch(
        "oal_agent.tools.mythril.subprocess.run",
        return_value=Mock(stdout="Mythril version 0.23.0\n", stderr="", returncode=0),
    )
    with patch("oal_agent.tools.mythril.logger") as mock_logger:
        tool = MythrilTool()
        mock_logger.warning.assert_called_with(
            "Unsupported Mythril version detected: %s. Expected version starting with %s.",
            "0.23.0",
            "0.24",
        )
        mock_logger.info.assert_not_called()


@pytest.mark.asyncio
async def test_check_mythril_version_not_found(mocker):
    mocker.patch("shutil.which", return_value=None)
    with patch("oal_agent.tools.mythril.logger") as mock_logger:
        with pytest.raises(RuntimeError, match="Mythril executable not found."):
            MythrilTool()
        mock_logger.error.assert_called_with(
            "Mythril command not found. Please ensure Mythril is installed and in your PATH."
        )


@pytest.mark.asyncio
async def test_check_mythril_version_parse_error(mocker):
    mocker.patch("shutil.which", return_value="/usr/bin/myth")
    mocker.patch(
        "oal_agent.tools.mythril.subprocess.run",
        return_value=Mock(stdout="Some unexpected output\n", stderr="", returncode=0),
    )
    with patch("oal_agent.tools.mythril.logger") as mock_logger:
        tool = MythrilTool()
        mock_logger.warning.assert_called_with(
            "Could not parse Mythril version from output: %s",
            "Some unexpected output",
        )


@pytest.mark.asyncio
async def test_analyze_captures_stderr(mythril_tool):
    contract_code = "pragma solidity ^0.8.0; contract MyContract { function test() public {} }"
    mock_stderr = "Mythril warning: This is a test warning."

    with patch(
        "oal_agent.tools.mythril.execute_external_command", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = SandboxResult(stdout="Analysis output", stderr=mock_stderr, exit_code=0)

        result = await mythril_tool.analyze(contract_code)

        assert result.stderr == mock_stderr
        mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_raises_on_non_zero_exit_code(mythril_tool):
    contract_code = "pragma solidity ^0.8.0; contract MyContract { function fail() public {} }"
    mock_stderr = "Mythril error: Something went wrong."

    with patch(
        "oal_agent.tools.mythril.execute_external_command", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = SandboxResult(stdout="", stderr=mock_stderr, exit_code=1)

        with pytest.raises(RuntimeError) as excinfo:
            await mythril_tool.analyze(contract_code)

        assert f"Mythril analysis failed with exit code 1: {mock_stderr}" in str(excinfo.value)
        mock_execute.assert_called_once()