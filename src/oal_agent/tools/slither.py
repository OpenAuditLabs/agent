"""Slither tool integration."""

import json
import subprocess


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
                check=True  # Raise an exception for non-zero exit codes
            )
            return process.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Slither analysis failed: {e.stderr}") from e


def parse_slither_output(json_output: str) -> list[dict]:
    """
    Parses the JSON output from Slither and normalizes findings.
    """
    data = json.loads(json_output)
    findings = []
    if "results" in data and "detectors" in data["results"]:
        for detector_finding in data["results"]["detectors"]:
            finding = {
                "check": detector_finding.get("check"),
                "impact": detector_finding.get("impact"),
                "confidence": detector_finding.get("confidence"),
                "description": detector_finding.get("description"),
                "elements": detector_finding.get("elements", []),
            }
            findings.append(finding)
    return findings

