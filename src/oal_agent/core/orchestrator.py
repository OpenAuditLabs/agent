"""Orchestrator for coordinating analysis tasks."""

import logging

from oal_agent.core.errors import OrchestrationError
from oal_agent.agents.coordinator import CoordinatorAgent

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates the analysis workflow."""

    def __init__(self):
        """Initialize the orchestrator."""
        self.coordinator_agent = CoordinatorAgent()

    async def orchestrate(self, job_id: str, job_data: dict):
        """Orchestrate an analysis job."""
        logger.info("Starting orchestration for job_id: %s", job_id)
        try:
            # TODO: Implement actual orchestration logic here
            # For demonstration, let's simulate a potential error
            if job_id == "simulate_error":
                raise ValueError("Simulated orchestration error")
            # Call coordinator to route the task
            await self.coordinator_agent.route({"job_id": job_id, "job_data": job_data})
            logger.info("Orchestration completed for job_id: %s", job_id)
        except Exception as e:
            logger.error("Orchestration failed for job_id: %s: %s", job_id, e)
            raise OrchestrationError(f"Failed to orchestrate job {job_id}: {e}") from e
