import json
import subprocess
from unittest.mock import patch

import pytest

from oal_agent.app.schemas.results import Severity
from src.oal_agent.tools.slither import SlitherTool, _map_severity, parse_slither_output


@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_run:
        yield mock_run


@pytest.fixture
def sample_slither_json_output():
    return {
        "results": {
            "detectors": [
                {
                    "check": "uninitialized-state-variables",
                    "impact": "High",
                    "confidence": "High",
                    "description": "State variables are not initialized.",
                    "elements": [
                        {"type": "variable", "name": "myVar", "source_mapping": {}},
                    ],
                }
            ]
        }
    }


@pytest.mark.asyncio
async def test_slither_tool_analyze_json_output(
    mock_subprocess_run, sample_slither_json_output
):
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["slither", "contract.sol", "--json", "-"],
        returncode=0,
        stdout=json.dumps(sample_slither_json_output),
        stderr="",
    )
    tool = SlitherTool()
    output = await tool.analyze("contract.sol", json_output=True)

    mock_subprocess_run.assert_called_once_with(
        ["slither", "contract.sol", "--json", "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert output == json.dumps(sample_slither_json_output)


@pytest.mark.asyncio
async def test_slither_tool_analyze_text_output(mock_subprocess_run):
    mock_subprocess_run.return_value = subprocess.CompletedProcess(
        args=["slither", "contract.sol"],
        returncode=0,
        stdout="Slither analysis text output",
        stderr="",
    )
    tool = SlitherTool()
    output = await tool.analyze("contract.sol", json_output=False)

    mock_subprocess_run.assert_called_once_with(
        ["slither", "contract.sol"], capture_output=True, text=True, check=True
    )
    assert output == "Slither analysis text output"


@pytest.mark.asyncio
async def test_slither_tool_analyze_failure(mock_subprocess_run):
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["slither", "contract.sol"], stderr="Error running slither"
    )
    tool = SlitherTool()
    with pytest.raises(
        Exception, match="Slither analysis failed: Error running slither"
    ):
        await tool.analyze("contract.sol")


def test_parse_slither_output(sample_slither_json_output):
    json_string = json.dumps(sample_slither_json_output)
    parsed_findings = parse_slither_output(json_string)

    expected_findings = [
        {
            "check": "uninitialized-state-variables",
            "severity": Severity.HIGH.value,
            "confidence": "High",
            "description": "State variables are not initialized.",
            "elements": [
                {"type": "variable", "name": "myVar", "source_mapping": {}},
            ],
        }
    ]
    assert parsed_findings == expected_findings


def test_parse_slither_output_empty_results():
    empty_output = {"results": {"detectors": []}}
    json_string = json.dumps(empty_output)
    parsed_findings = parse_slither_output(json_string)
    assert parsed_findings == []


def test_parse_slither_output_no_detectors_key():
    no_detectors_output = {"results": {}}
    json_string = json.dumps(no_detectors_output)
    parsed_findings = parse_slither_output(json_string)
    assert parsed_findings == []


def test_parse_slither_output_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        parse_slither_output("invalid json")


def test_map_severity():
    assert _map_severity("Critical") == Severity.CRITICAL
    assert _map_severity("High") == Severity.HIGH
    assert _map_severity("Medium") == Severity.MEDIUM
    assert _map_severity("Low") == Severity.LOW
    assert _map_severity("Informational") == Severity.INFORMATIONAL
    assert _map_severity("high") == Severity.HIGH
    assert _map_severity("medium") == Severity.MEDIUM
    assert _map_severity("low") == Severity.LOW
    assert _map_severity("informational") == Severity.INFORMATIONAL
    assert _map_severity("Unknown Impact") == Severity.LOW
    assert _map_severity(None) == Severity.LOW
