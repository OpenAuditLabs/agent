import asyncio
from unittest.mock import AsyncMock, patch

import pytest


from oal_agent.core.config import settings
from oal_agent.core.errors import OrchestrationError
from oal_agent.core.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_orchestrator_happy_path():
    """Test orchestrator with a happy-path scenario for coordinator."""
    orchestrator = Orchestrator()

    with patch(
        "oal_agent.agents.coordinator.CoordinatorAgent.route", new_callable=AsyncMock
    ) as mock_route:
        job_id = "test_job_123"
        job_data = {"contract": "0x123...", "analysis_type": "security"}

        await orchestrator.orchestrate(job_id, job_data)

        mock_route.assert_called_once_with({"job_id": job_id, "job_data": job_data})


@pytest.mark.asyncio
async def test_orchestrator_coordinator_timeout():
    """Test orchestrator when coordinator routing times out."""
    orchestrator = Orchestrator()

    async def long_running_route(*args, **kwargs):
        await asyncio.sleep(2)  # Simulate a long-running operation

    with (
        patch(
            "oal_agent.agents.coordinator.CoordinatorAgent.route",
            new_callable=AsyncMock,
        ) as mock_route,
        patch.object(settings, "coordinator_timeout", 0.1),
    ):
        mock_route.side_effect = long_running_route

        job_id = "timeout_job_456"
        job_data = {"contract": "0x456...", "analysis_type": "performance"}

        with pytest.raises(
            OrchestrationError,
            match="Coordinator routing timed out for job timeout_job_456",
        ):
            await orchestrator.orchestrate(job_id, job_data)

        mock_route.assert_called_once()


@pytest.mark.asyncio
async def test_orchestrator_simulated_error():
    """Test orchestrator with a simulated error from within orchestrate."""
    orchestrator = Orchestrator()

    job_id = "simulate_error"
    job_data = {"contract": "0x789...", "analysis_type": "liveness"}

    with pytest.raises(
        OrchestrationError, match="Failed to orchestrate job simulate_error"
    ):
        await orchestrator.orchestrate(job_id, job_data)
