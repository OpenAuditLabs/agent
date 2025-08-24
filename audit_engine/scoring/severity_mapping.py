from enum import Enum

class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"

# Interim mapping from SWC IDs to severity levels
SWC_SEVERITY_MAP: dict[str, SeverityLevel] = {
    "SWC-107": SeverityLevel.CRITICAL,         # Reentrancy
    "SWC-101": SeverityLevel.HIGH,             # Integer Overflow and Underflow
    "SWC-110": SeverityLevel.MEDIUM,           # Assert Violation
    "SWC-114": SeverityLevel.MEDIUM,           # Transaction Order Dependence (front-running)
    "SWC-116": SeverityLevel.LOW,              # Block values as a proxy for time
    # … add additional SWC IDs as needed
}


def map_swc_to_severity(swc_id: str) -> SeverityLevel:
    """
    Return the associated SeverityLevel for a given SWC identifier.
    Defaults to INFORMATIONAL if not explicitly mapped.
    """
    return SWC_SEVERITY_MAP.get(swc_id, SeverityLevel.INFORMATIONAL)
