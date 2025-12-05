import pytest
from fastapi.testclient import TestClient

from src.oal_agent.app.main import app


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient for the FastAPI application."""
    with TestClient(app) as c:
        yield c


def test_update_item_no_fields_provided(client):
    """
    Test updating an item with no fields provided (both name and description are None).
    Should result in a 422 Unprocessable Entity error due to the ItemUpdate validator.
    """
    item_id = 1
    response = client.patch(f"/v1/items/{item_id}", json={})

    assert response.status_code == 422
    assert (
        "At least one of 'name' or 'description' must be provided."
        in response.json()["detail"][0]["msg"]
    )


def test_update_item_with_name(client):
    """
    Test updating an item by providing only the name.
    """
    item_id = 1
    update_payload = {"name": "Updated Item Name"}
    response = client.patch(f"/v1/items/{item_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json() == {"id": item_id, "name": "Updated Item Name"}


def test_update_item_with_description(client):
    """
    Test updating an item by providing only the description.
    """
    item_id = 1
    update_payload = {"description": "Updated Item Description"}
    response = client.patch(f"/v1/items/{item_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json() == {"id": item_id, "description": "Updated Item Description"}


def test_update_item_with_both_fields(client):
    """
    Test updating an item by providing both name and description.
    """
    item_id = 1
    update_payload = {"name": "New Name", "description": "New Description"}
    response = client.patch(f"/v1/items/{item_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json() == {
        "id": item_id,
        "name": "New Name",
        "description": "New Description",
    }
