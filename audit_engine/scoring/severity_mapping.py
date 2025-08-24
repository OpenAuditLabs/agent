from enum import Enum

class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MEDIUM = "Medium"
    MINOR = "Minor"
    INFORMATIONAL = "Informational"

# Interim mapping from SWC IDs to severity levels
SWC_SEVERITY_MAP: dict[str, SeverityLevel] = {
    "SWC-101": SeverityLevel.CRITICAL,         # Reentrancy
    "SWC-110": SeverityLevel.MAJOR,            # Integer Overflow
    "SWC-114": SeverityLevel.MEDIUM,           # DoS with Block Gas Limit
    "SWC-116": SeverityLevel.MINOR,            # Authorization through tx.origin
    # … add additional SWC IDs as needed
}

def map_swc_to_severity(swc_id: str) -> SeverityLevel:
    """
    Return the associated SeverityLevel for a given SWC identifier.
    Defaults to INFORMATIONAL if not explicitly mapped.
    """
    return SWC_SEVERITY_MAP.get(swc_id, SeverityLevel.INFORMATIONAL)
