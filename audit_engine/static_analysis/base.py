from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, TypedDict

class StandardFinding(TypedDict, total=False):
    title: str
    description: str
    severity: Literal["High", "Medium", "Low"]
    confidence: Literal["High", "Medium", "Low"]
    swc_id: str
    line_numbers: List[int]
    tool: str
    # Optional extras that help with traceability without breaking consumers:
    original_severity: Any
    file: str
    raw: Dict[str, Any]

class AbstractAdapter(ABC):
    @abstractmethod
    def run(self, contract_path: str, **kwargs) -> List[StandardFinding]:
        """Run analysis and return a list of standardized findings."""
        pass

    @abstractmethod
    def parse_output(self, output: str) -> List[StandardFinding]:
        """Parse tool output into standardized findings."""
        pass

    def standardize_finding(self, finding: Dict) -> Dict:
        # Standardize keys and SWC/severity mapping
        severity_raw = finding.get("severity")
        # Normalize line_numbers to a list[int]
        ln = finding.get("line_numbers", [])
        if isinstance(ln, int):
            line_numbers = [ln]
        elif isinstance(ln, str):
            parts = [p.strip() for p in ln.split(",")]
            line_numbers = [int(p) for p in parts if p.isdigit()]
        else:
            line_numbers = ln or []

        return {
            "title": str(finding.get("title", "")),
            "description": str(finding.get("description", "")),
            "severity": self._map_severity(severity_raw),
            "swc_id": str(finding.get("swc_id", "")),
            "line_numbers": line_numbers,
            "confidence": str(finding.get("confidence", "Medium")),
            "tool": finding.get("tool", getattr(self, "tool_name", self.__class__.__name__)),
            # Extras that do not break consumers but preserve fidelity
            "original_severity": severity_raw,
        }

    def _map_severity(self, severity) -> str:
        if severity is None:
            return "Medium"
        key = str(severity).strip().lower()
        mapping = {
            "critical": "High",
            "high": "High",
            "medium": "Medium",
            "moderate": "Medium",
            "low": "Low",
            "info": "Low",
            "informational": "Low",
        }
        return mapping.get(key, "Medium")
