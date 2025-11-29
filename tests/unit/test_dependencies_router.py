from typing import Annotated

import pytest
from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient

from src.oal_agent.app.dependencies import RequestMetadata, get_request_metadata
from src.oal_agent.app.main import app

# Create a test router
test_router = APIRouter()


@test_router.get("/test-metadata")
async def get_metadata(
    metadata: Annotated[RequestMetadata, Depends(get_request_metadata)],
):
    return {
        "request_id": metadata.request_id,
        "user_agent": metadata.user_agent,
        "x_forwarded_for": metadata.x_forwarded_for,
        "client_ip": metadata.client_ip,
    }


# Include the test router in the main app for testing purposes
app.include_router(test_router, prefix="/test")


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient for the FastAPI application."""
    with TestClient(app) as c:
        yield c


def test_request_metadata_dependency(client):
    """
    Test that RequestMetadata dependency correctly extracts headers.
    """
    headers = {
        "X-Request-ID": "test-request-123",
        "User-Agent": "test-client/1.0",
        "X-Forwarded-For": "192.168.1.1, 10.0.0.1",
    }
    response = client.get("/test/test-metadata", headers=headers)

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["request_id"] == "test-request-123"
    assert response_data["user_agent"] == "test-client/1.0"
    assert response_data["x_forwarded_for"] == "192.168.1.1, 10.0.0.1"
    assert response_data["client_ip"] == "192.168.1.1"


def test_request_metadata_dependency_no_headers(client):
    """
    Test that RequestMetadata dependency handles missing headers gracefully.
    """
    response = client.get("/test/test-metadata")

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["request_id"] is None
    assert response_data["user_agent"] == "testclient"
    assert response_data["x_forwarded_for"] is None
    assert response_data["client_ip"] is None
