import pytest
from fastapi.testclient import TestClient

from src.oal_agent.app.main import app


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient for the FastAPI application."""
    with TestClient(app) as c:
        yield c


def test_submit_analysis_success(client):
    """
    Test submitting a smart contract for analysis successfully.
    """
    job_request_payload = {
        "contract_code": "pragma solidity ^0.8.0; contract MyContract { function foo() public {} }",
        "contract_address": "0x1234567890123456789012345678901234567890",
        "chain_id": 1,
        "pipeline": "static",
    }
    response = client.post("/api/v1/analysis/", json=job_request_payload)

    assert response.status_code == 200
    response_data = response.json()
    assert "job_id" in response_data
    assert isinstance(response_data["job_id"], str)
    assert response_data["status"] == "queued"
    assert response_data["message"] is None


def test_get_job_status_not_found(client):
    """
    Test retrieving the status of a non-existent analysis job.
    """
    job_id = "non_existent_job_id"
    response = client.get(f"/api/v1/analysis/{job_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}


def test_get_job_results_not_found(client):
    """
    Test retrieving the results of a non-existent analysis job.
    """
    job_id = "non_existent_job_id"
    response = client.get(f"/api/v1/analysis/{job_id}/results")

    assert response.status_code == 404
    assert response.json() == {"detail": "Results not found"}


# TODO: Add tests for successful job status and results retrieval once the
#       corresponding logic is implemented in the analysis router.
#       These tests currently expect 404 as per the router's placeholder implementation.
