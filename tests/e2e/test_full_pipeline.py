from unittest.mock import AsyncMock, patch

import pytest

from oal_agent.app.schemas.jobs import JobRequest
from oal_agent.core.orchestrator import Orchestrator

# Sample contract for testing
SAMPLE_CONTRACT_CODE = """
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint public storedData;

    function set(uint x) public {
        storedData = x;
    }

    function get() public view returns (uint) {
        return storedData;
    }
}
"""


@pytest.mark.asyncio
async def test_full_analysis_pipeline_e2e():
    """
    Test a minimal end-to-end analysis pipeline.

    This test currently mocks the CoordinatorAgent.route method as the full
    orchestration logic is not yet implemented. Once the orchestration logic
    is complete, this mock should be removed, and the test should assert
    on the actual results produced by the pipeline.
    """
    orchestrator = Orchestrator()
    job_id = "test-job-id-123"
    job_request_data = JobRequest(contract_code=SAMPLE_CONTRACT_CODE).model_dump()

    with patch(
        "oal_agent.agents.coordinator.CoordinatorAgent.route", new_callable=AsyncMock
    ) as mock_route:
        # Simulate successful routing by the coordinator
        mock_route.return_value = None

        await orchestrator.orchestrate(job_id, job_request_data)

        # Assert that the coordinator's route method was called
        mock_route.assert_awaited_once_with(
            {"job_id": job_id, "job_data": job_request_data}
        )

    # TODO: Once the full pipeline is implemented, assert on the actual analysis results.
    # For example:
    # results = await results_sink.retrieve(job_id)
    # assert results["status"] == AnalysisStatus.COMPLETED.value
    # assert any("finding_type" in f for f in results["findings"])
