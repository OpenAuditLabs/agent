import pytest
from fastapi.testclient import TestClient

from oal_agent.app.main import app


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient for the FastAPI application."""
    with TestClient(app) as c:
        yield c


def test_get_all_users_default_pagination(client):
    """
    Test retrieving all users with default pagination parameters.
    """
    response = client.get("/api/v1/users/")

    assert response.status_code == 200
    response_data = response.json()
    assert "users" in response_data
    assert isinstance(response_data["users"], list)
    assert (
        response_data["total_count"] == 0
    )  # As per current placeholder implementation
    assert response_data["limit"] == 100
    assert response_data["offset"] == 0


def test_get_all_users_custom_pagination(client):
    """
    Test retrieving all users with custom pagination parameters.
    """
    limit = 50
    offset = 10
    response = client.get(f"/api/v1/users/?limit={limit}&offset={offset}")

    assert response.status_code == 200
    response_data = response.json()
    assert "users" in response_data
    assert isinstance(response_data["users"], list)
    assert response_data["total_count"] == 0
    assert response_data["limit"] == limit
    assert response_data["offset"] == offset


@pytest.mark.parametrize(
    "limit, expected_status_code",
    [
        (1, 200),
        (1000, 200),
        (0, 422),  # limit must be >= 1
        (1001, 422),  # limit must be <= 1000
    ],
)
def test_get_all_users_pagination_limits(client, limit, expected_status_code):
    """
    Test retrieving all users with limit parameter at its boundaries and beyond.
    """
    response = client.get(f"/api/v1/users/?limit={limit}")

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.json()["limit"] == limit
    else:
        assert "detail" in response.json()


@pytest.mark.parametrize(
    "offset, expected_status_code",
    [
        (0, 200),
        (10, 200),
        (-1, 422),  # offset must be >= 0
    ],
)
def test_get_all_users_pagination_offset(client, offset, expected_status_code):
    """
    Test retrieving all users with offset parameter at its boundaries and beyond.
    """
    response = client.get(f"/api/v1/users/?offset={offset}")

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.json()["offset"] == offset
    else:
        assert "detail" in response.json()
