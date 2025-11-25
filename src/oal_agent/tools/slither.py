"""Slither tool integration."""

import json
import subprocess

from oal_agent.app.schemas.results import Severity


class SlitherTool:
    """Integration with Slither static analyzer."""

    def __init__(self):
        """Initialize Slither tool."""
        pass

    async def analyze(self, contract_path: str, json_output: bool = False) -> str:
        """
        Run Slither analysis.
        """
        command = ["slither", contract_path]
        if json_output:
            command.extend(["--json", "-"])  # Output JSON to stdout

        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,  # Raise an exception for non-zero exit codes
            )
            return process.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Slither analysis failed: {e.stderr}") from e


def _map_severity(impact: str) -> Severity:
    """Maps Slither's impact string to internal Severity enum."""
    impact_lower = (impact or "").lower()
    if "critical" in impact_lower:
        return Severity.CRITICAL
    if "high" in impact_lower:
        return Severity.HIGH
    if "medium" in impact_lower:
        return Severity.MEDIUM
    if "low" in impact_lower:
        return Severity.LOW
    if "informational" in impact_lower:
        return Severity.INFORMATIONAL
    return Severity.LOW  # Default or unknown impact


def parse_slither_output(json_output: str) -> list[dict]:
    """
    Parses the JSON output from Slither and normalizes findings.
    """
    data = json.loads(json_output)
    findings = []
    if "results" in data and "detectors" in data["results"]:
        for detector_finding in data["results"]["detectors"]:
            severity = _map_severity(detector_finding.get("impact", "Low"))
            finding = {
                "check": detector_finding.get("check"),
                "severity": severity.value,  # Use the mapped severity
                "confidence": detector_finding.get("confidence"),
                "description": detector_finding.get("description"),
                "elements": detector_finding.get("elements", []),
            }
            findings.append(finding)
    return findings
