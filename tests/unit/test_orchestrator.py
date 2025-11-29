import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from oal_agent.core.config import reset_settings, settings
from oal_agent.core.errors import OrchestrationError
from oal_agent.core.orchestrator import Orchestrator


@pytest.fixture(autouse=True)
def reset_config_and_mocks():
    """Reset settings and mocks before each test."""
    reset_settings()
    yield


@pytest.mark.asyncio
async def test_orchestrator_concurrency_limit():
    """Test that the orchestrator respects the maximum concurrent pipelines limit."""
    settings.max_concurrent_pipelines = 2
    orchestrator = Orchestrator()

    # To track active tasks over time
    active_times = []
    active_times_lock = asyncio.Lock()

    # Mock the coordinator agent's route method to simulate work
    with patch.object(
        orchestrator.coordinator_agent, "route", new_callable=AsyncMock
    ) as mock_route:

        async def long_running_task(*args, **kwargs):
            start_time = time.monotonic()
            async with active_times_lock:
                active_times.append((start_time, "start"))
            await asyncio.sleep(0.1)  # Simulate work
            end_time = time.monotonic()
            async with active_times_lock:
                active_times.append((end_time, "end"))
            return {"result": "success"}

        mock_route.side_effect = long_running_task

        # Create more tasks than the allowed concurrency limit
        tasks = [
            orchestrator.orchestrate(f"job_{i}", {"data": f"job_{i}"}) for i in range(5)
        ]

        await asyncio.gather(*tasks)

        # Analyze active_times to verify concurrency
        active_times.sort()

        current_concurrent_tasks = 0
        max_concurrent_tasks_observed = 0

        for _, event_type in active_times:
            if event_type == "start":
                current_concurrent_tasks += 1
            else:
                current_concurrent_tasks -= 1
            max_concurrent_tasks_observed = max(
                max_concurrent_tasks_observed, current_concurrent_tasks
            )

        assert max_concurrent_tasks_observed == settings.max_concurrent_pipelines
        assert mock_route.call_count == 5  # All tasks should eventually run


@pytest.mark.asyncio
async def test_orchestrator_error_handling():
    """Test that the orchestrator handles errors during orchestration."""
    orchestrator = Orchestrator()
    with patch.object(
        orchestrator.coordinator_agent, "route", new_callable=AsyncMock
    ) as mock_route:
        mock_route.side_effect = ValueError("Simulated error during routing")

        with pytest.raises(
            OrchestrationError,
            match="Failed to orchestrate job test_job: Simulated error during routing",
        ):
            await orchestrator.orchestrate("test_job", {"data": "test"})

        mock_route.assert_called_once_with(
            {"job_id": "test_job", "job_data": {"data": "test"}}
        )


@pytest.mark.asyncio
async def test_orchestrator_timeout_handling():
    """Test that the orchestrator handles timeout during coordination."""
    settings.coordinator_timeout = 0.01  # Set a very short timeout
    orchestrator = Orchestrator()

    with patch.object(
        orchestrator.coordinator_agent, "route", new_callable=AsyncMock
    ) as mock_route:
        # Simulate a task that takes longer than the timeout
        async def slow_task(*args, **kwargs):
            await asyncio.sleep(0.1)
            return {"result": "success"}

        mock_route.side_effect = slow_task

        with pytest.raises(
            OrchestrationError, match="Coordinator routing timed out for job test_job"
        ):
            await orchestrator.orchestrate("test_job", {"data": "test"})

        mock_route.assert_called_once_with(
            {"job_id": "test_job", "job_data": {"data": "test"}}
        )
