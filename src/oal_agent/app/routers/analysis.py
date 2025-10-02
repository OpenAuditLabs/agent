"""Analysis router."""

from fastapi import APIRouter, HTTPException

from ..schemas.jobs import JobRequest, JobResponse
from ..schemas.results import AnalysisResult

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/", response_model=JobResponse)
async def submit_analysis(job: JobRequest):
    """Submit a smart contract for analysis."""
    # TODO: Implement job submission logic
    return JobResponse(job_id="placeholder", status="queued")


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """Get the status of an analysis job."""
    # TODO: Implement job status retrieval
    raise HTTPException(status_code=404, detail="Job not found")


@router.get("/{job_id}/results", response_model=AnalysisResult)
async def get_job_results(job_id: str):
    """Get the results of an analysis job."""
    # TODO: Implement results retrieval
    raise HTTPException(status_code=404, detail="Results not found")
