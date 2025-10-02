"""Job schemas."""

from typing import Optional

from pydantic import BaseModel


class JobRequest(BaseModel):
    """Analysis job request schema."""
    contract_code: str
    contract_address: Optional[str] = None
    chain_id: Optional[int] = None
    pipeline: str = "standard"


class JobResponse(BaseModel):
    """Analysis job response schema."""
    job_id: str
    status: str
    message: Optional[str] = None
