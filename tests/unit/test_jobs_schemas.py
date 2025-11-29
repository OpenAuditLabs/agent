import pytest
from pydantic import ValidationError

from src.oal_agent.app.schemas.jobs import JobResponse


def test_job_response_initial_status():
    """Test that a JobResponse can be created with an initial status."""
    job = JobResponse(job_id="123", status="PENDING")
    assert job.status == "PENDING"


def test_job_response_valid_transition():
    """Test valid state transitions."""
    job = JobResponse(job_id="123", status="PENDING")
    updated_job = JobResponse(
        job_id="123", status="RUNNING", previous_status=job.status
    )
    assert updated_job.status == "RUNNING"

    job = updated_job
    updated_job = JobResponse(
        job_id="123", status="COMPLETED", previous_status=job.status
    )
    assert updated_job.status == "COMPLETED"

    job = JobResponse(job_id="123", status="RUNNING")
    updated_job = JobResponse(job_id="123", status="FAILED", previous_status=job.status)
    assert updated_job.status == "FAILED"


def test_job_response_invalid_transition():
    """Test invalid state transitions raise ValidationError."""
    job = JobResponse(job_id="123", status="PENDING")
    with pytest.raises(ValidationError) as exc_info:
        JobResponse(job_id="123", status="COMPLETED", previous_status=job.status)
    assert "Invalid state transition from 'PENDING' to 'COMPLETED'" in str(
        exc_info.value
    )

    job = JobResponse(job_id="123", status="COMPLETED")
    with pytest.raises(ValidationError) as exc_info:
        JobResponse(job_id="123", status="RUNNING", previous_status=job.status)
    assert "Invalid state transition from 'COMPLETED' to 'RUNNING'" in str(
        exc_info.value
    )

    job = JobResponse(job_id="123", status="FAILED")
    with pytest.raises(ValidationError) as exc_info:
        JobResponse(job_id="123", status="RUNNING", previous_status=job.status)
    assert "Invalid state transition from 'FAILED' to 'RUNNING'" in str(exc_info.value)


def test_job_response_no_previous_status_any_status_allowed():
    """Test that if previous_status is not provided, any status is allowed (initial creation)."""
    job = JobResponse(job_id="123", status="COMPLETED")
    assert job.status == "COMPLETED"

    job = JobResponse(job_id="123", status="FAILED")
    assert job.status == "FAILED"

    job = JobResponse(job_id="123", status="RUNNING")
    assert job.status == "RUNNING"

    job = JobResponse(job_id="123", status="PENDING")
    assert job.status == "PENDING"
