"""Job schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination parameters schema."""

    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of items to return. Defaults to 10, max 100.",
    )
    offset: int = Field(0, ge=0, description="Number of items to skip. Defaults to 0.")


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
