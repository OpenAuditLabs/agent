"""Orchestrator for coordinating analysis tasks."""

import asyncio
import logging

from oal_agent.agents.coordinator import CoordinatorAgent
from oal_agent.core.config import settings
from oal_agent.core.errors import OrchestrationError

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates the analysis workflow."""

    def __init__(self):
        """Initialize the orchestrator."""
        self.coordinator_agent = CoordinatorAgent()
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_pipelines)

    async def orchestrate(self, job_id: str, job_data: dict):
        """Orchestrate an analysis job."""
        logger.info("Job %s: Waiting to acquire pipeline slot.", job_id)
        async with self.semaphore:
            logger.info("Job %s: Acquired pipeline slot. Starting orchestration.", job_id)
            try:
                # TODO: Implement actual orchestration logic here
                # For demonstration, let's simulate a potential error
                if job_id == "simulate_error":
                    raise ValueError("Simulated orchestration error")
                # Call coordinator to route the task with a timeout
                await asyncio.wait_for(
                    self.coordinator_agent.route({"job_id": job_id, "job_data": job_data}),
                    timeout=settings.coordinator_timeout,
                )
                logger.info("Job %s: Orchestration completed.", job_id)
            except asyncio.TimeoutError as e:
                logger.error("Job %s: Coordinator routing timed out.", job_id)
                raise OrchestrationError(
                    f"Coordinator routing timed out for job {job_id}"
                ) from e
            except Exception as e:
                logger.error("Job %s: Orchestration failed: %s", job_id, e)
                raise OrchestrationError(f"Failed to orchestrate job {job_id}: {e}") from e
            finally:
                logger.info("Job %s: Released pipeline slot.", job_id)
