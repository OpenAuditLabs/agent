"""Results schemas."""

from enum import Enum
from typing import Any, ClassVar, Dict, List

from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    """Enumeration for analysis job statuses."""

    QUEUED = "queued"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    """Enumeration for the severity of a security finding."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"


class Finding(BaseModel):
    """Security finding schema."""

    severity: Severity = Field(..., description="The severity of the finding.")
    title: str = Field(..., min_length=1, description="The title of the finding.")
    description: str = Field(
        ..., min_length=1, description="A detailed description of the finding."
    )
    location: Dict[str, Any] = Field(
        ..., description="The location of the finding within the code."
    )
    recommendation: str = Field(
        ..., min_length=1, description="Recommended actions to remediate the finding."
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "severity": "High",
                "title": "Reentrancy Vulnerability",
                "description": "The contract is vulnerable to reentrancy attacks.",
                "location": {"file": "contract.sol", "line": 10, "column": 5},
                "recommendation": "Implement checks-effects-interactions pattern.",
            }
        }


class AnalysisResult(BaseModel):
    """Analysis result schema."""

    job_id: str = Field(..., min_length=1, pattern=r"^[a-zA-Z0-9_-]{1,128}$")
    status: AnalysisStatus
    findings: List[Finding]
    metadata: Dict[str, Any]

    class Config:
        """Pydantic model configuration."""

        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "job_id": "654a1b2c3d4e5f6a7b8c9d0e",
                "status": "completed",
                "findings": [
                    {
                        "severity": "High",
                        "title": "Reentrancy Vulnerability",
                        "description": (
                            "The contract is vulnerable to reentrancy attacks."
                        ),
                        "location": {"file": "contract.sol", "line": 10, "column": 5},
                        "recommendation": (
                            "Implement checks-effects-interactions pattern."
                        ),
                    }
                ],
                "metadata": {
                    "tool_version": "1.0.0",
                    "timestamp": "2023-10-27T10:00:00Z",
                },
            }
        }


class PaginatedItemsResponse(BaseModel):
    """Schema for paginated list of items."""

    items: List[Any]
    total: int
    limit: int
    offset: int
