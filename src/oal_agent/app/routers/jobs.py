import logging

from fastapi import APIRouter, HTTPException, status, Depends

from oal_agent.app.schemas.jobs import JobResponse
from oal_agent.services.queue import QueueService
from oal_agent.app.dependencies import get_queue_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["jobs"])


@router.delete("/{job_id}", response_model=JobResponse)
async def cancel_job(job_id: str, queue_service: QueueService = Depends(get_queue_service)):
    """Cancel an analysis job by its ID."""
    logger.info("Received cancellation request for job: %s", job_id)
    was_cancelled = await queue_service.cancel_job(job_id)
    if was_cancelled:
        return JobResponse(
            job_id=job_id, status="cancelled", message="Job cancelled successfully."
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found or already completed/failed.")
