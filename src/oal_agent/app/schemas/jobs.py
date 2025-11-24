"""Job schemas."""

from typing import Optional, Self

from pydantic import BaseModel, Field, model_validator, ValidationError


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
    previous_status: Optional[str] = None

    @model_validator(mode="after")
    def validate_status_transition(self) -> Self:
        new_status = self.status
        previous_status = self.previous_status

        if previous_status is None:
            # Initial state, any status is allowed
            return self

        allowed_transitions = {
            "PENDING": ["RUNNING"],
            "RUNNING": ["COMPLETED", "FAILED"],
            "COMPLETED": [],
            "FAILED": [],
        }

        if new_status not in allowed_transitions.get(previous_status, []):
            raise ValueError(
                f"Invalid state transition from '{previous_status}' to '{new_status}'"
            )
        return self
