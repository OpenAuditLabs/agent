from fastapi import APIRouter, HTTPException, Response

from oal_agent.app.schemas.jobs import JobRequest, JobResponse
from oal_agent.app.schemas.results import AnalysisResult, AnalysisStatus
from oal_agent.services.results_sink import ResultsSink

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])

results_sink = ResultsSink()


@router.head("/")
async def readiness_check(response: Response):
    """Perform a readiness check for the analysis service."""
    response.status_code = 200
    return


@router.post("/", response_model=JobResponse)
async def submit_analysis(job: JobRequest):
    """Submit a smart contract for analysis."""
    # TODO: Implement actual job submission logic and use a real job_id
    job_id = str(uuid.uuid4())
    logger.info("Received analysis job: %s", job_id)
    initial_results = {
        "status": AnalysisStatus.QUEUED.value,  # Use enum value
        "contract_code": job.contract_code,
        "findings": [],
        "metadata": {"submitted_at": "2023-11-14T12:00:00Z"},  # Placeholder metadata
    }
    await results_sink.store(job_id, initial_results)
    return JobResponse(job_id=job_id, status=AnalysisStatus.QUEUED.value)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """Get the status of an analysis job."""
    # TODO: Implement job status retrieval
    results = await results_sink.retrieve(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(
        job_id=job_id,
        status=AnalysisStatus(results.get("status", AnalysisStatus.UNKNOWN.value)),
    )


@router.get("/{job_id}/results", response_model=AnalysisResult)
async def get_job_results(job_id: str):
    """Get the results of an analysis job."""
    results = await results_sink.retrieve(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    # Ensure status is a valid AnalysisStatus enum member
    status = AnalysisStatus(results.get("status", AnalysisStatus.UNKNOWN.value))

    return AnalysisResult(
        job_id=job_id,
        status=status,
        findings=results.get("findings", []),
        metadata=results.get("metadata", {}),
    )
