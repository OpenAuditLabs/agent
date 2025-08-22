from abc import ABC, abstractmethod
from typing import List, Dict

class AbstractAdapter(ABC):
    @abstractmethod
    def run(self, contract_path: str, **kwargs) -> List[Dict]:
        """Run analysis and return a list of standardized findings."""
        pass

    @abstractmethod
    def parse_output(self, output: str) -> List[Dict]:
        """Parse tool output into standardized findings."""
        pass

    def standardize_finding(self, finding: Dict) -> Dict:
        # Standardize keys and SWC/severity mapping
        return {
            "title": finding.get("title", ""),
            "description": finding.get("description", ""),
            "severity": self._map_severity(finding.get("severity", "Medium")),
            "swc_id": finding.get("swc_id", ""),
            "line_numbers": finding.get("line_numbers", []),
            "confidence": finding.get("confidence", "Medium"),
            "tool": finding.get("tool", self.__class__.__name__),
        }

    def _map_severity(self, severity: str) -> str:
        mapping = {"Critical": "High", "High": "High", "Medium": "Medium", "Low": "Low", "Informational": "Low"}
        return mapping.get(severity, "Medium")
