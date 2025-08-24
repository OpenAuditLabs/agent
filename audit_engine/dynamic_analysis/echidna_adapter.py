import subprocess
import json
from typing import List, Dict
from ..static_analysis.base import AbstractAdapter

class EchidnaAdapter(AbstractAdapter):
    def run(self, contract_path: str, **kwargs) -> List[Dict]:
        cmd = [
            "echidna-test", contract_path,
            "--format", "json"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=kwargs.get("timeout", 180))
            return self.parse_output(result.stdout)
        except Exception as e:
            return [{"title": "Echidna Error", "description": str(e), "severity": "Low", "swc_id": "", "line_numbers": [], "confidence": "Low", "tool": "Echidna"}]

    def parse_output(self, output: str) -> List[Dict]:
        try:
            data = json.loads(output)
            findings = []
            for test in data.get("tests", []):
                if not test.get("pass", True):
                    finding = {
                        "title": f"Property Violation: {test.get('name', '')}",
                        "description": test.get("message", ""),
                        "severity": "High",
                        "swc_id": "",  # Could map based on property name
                        "line_numbers": test.get("locations", []),
                        "confidence": "High",
                        "tool": "Echidna"
                    }
                    findings.append(self.standardize_finding(finding))
            return findings
        except Exception:
            return []
