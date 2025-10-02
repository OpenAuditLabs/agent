"""Results schemas."""

from typing import Any, Dict, List

from pydantic import BaseModel


class Finding(BaseModel):
    """Security finding schema."""
    severity: str
    title: str
    description: str
    location: Dict[str, Any]
    recommendation: str


class AnalysisResult(BaseModel):
    """Analysis result schema."""
    job_id: str
    status: str
    findings: List[Finding]
    metadata: Dict[str, Any]
