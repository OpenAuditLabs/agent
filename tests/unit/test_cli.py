import pytest
from click.testing import CliRunner
import requests
from unittest.mock import patch

from src.oal_agent.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_status_command_timeout(runner):
    """
    Test that the status command handles a timeout correctly.
    """
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out.")
        result = runner.invoke(cli, ["status", "test_job_id"])

        assert "Error: The request timed out: Connection timed out." in result.output
        assert result.exit_code == 0 # CLI commands usually exit with 0 even on handled errors
