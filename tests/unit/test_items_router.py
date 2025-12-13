import pytest
from fastapi.testclient import TestClient

from src.oal_agent.app.main import app

# Import the items_db from the router to reset it for testing
from src.oal_agent.app.routers.items import items_db
from src.oal_agent.app.routers.items import _next_id as router_next_id # Import with alias


@pytest.fixture(scope="module", autouse=True)
def reset_items_db():
    """Resets the in-memory database before each test module to ensure isolation."""
    original_items = items_db.copy()
    original_next_id = router_next_id
    yield
    items_db.clear()
    items_db.update(original_items)
    global router_next_id
    router_next_id = original_next_id


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
        "At least one of 'name', 'description', or 'is_deleted' must be provided."
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
    assert response.json()["name"] == "Updated Item Name"


def test_update_item_with_description(client):
    """
    Test updating an item by providing only the description.
    """
    item_id = 2 # Use a different item to avoid conflicts with previous test
    update_payload = {"description": "Updated Item Description"}
    response = client.patch(f"/v1/items/{item_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json()["description"] == "Updated Item Description"


def test_update_item_with_both_fields(client):
    """
    Test updating an item by providing both name and description.
    """
    item_id = 3 # Use a different item
    update_payload = {"name": "New Name", "description": "New Description"}
    response = client.patch(f"/v1/items/{item_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["description"] == "New Description"


def test_soft_delete_item_success(client):
    """
    Test successful soft-deletion of an item.
    """
    # First, create a new item to ensure a clean state for soft-deletion
    create_response = client.post(
        "/v1/items/", json={"name": "Item to Soft Delete", "description": "Desc"}
    )
    assert create_response.status_code == 201
    item_id_to_delete = create_response.json()["id"]

    # Soft-delete the item
    delete_response = client.delete(f"/v1/items/{item_id_to_delete}/soft-delete")
    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": f"Item {item_id_to_delete} soft-deleted successfully"
    }

    # Verify the item is marked as deleted in the database
    # (Direct access to items_db for verification in test context)
    from src.oal_agent.app.routers.items import items_db

    assert items_db[item_id_to_delete].is_deleted is True

    # Verify it's not returned by get_all_items
    get_response = client.get("/v1/items/")
    assert get_response.status_code == 200
    returned_items = get_response.json()["items"]
    returned_ids = [item["id"] for item in returned_items]
    assert item_id_to_delete not in returned_ids


def test_soft_delete_item_not_found(client):
    """
    Test attempting to soft-delete a non-existent item.
    """
    non_existent_item_id = 99999
    response = client.delete(f"/v1/items/{non_existent_item_id}/soft-delete")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_get_all_items_after_soft_delete(client):
    """
    Verify that soft-deleted items are not returned by get_all_items.
    This test specifically checks the filtering behavior.
    """
    # Create an item and then soft-delete it
    create_response_1 = client.post(
        "/v1/items/", json={"name": "Item to Delete A", "description": "Desc A"}
    )
    item_id_a = create_response_1.json()["id"]
    client.delete(f"/v1/items/{item_id_a}/soft-delete")

    # Create another item that should still be visible
    create_response_2 = client.post(
        "/v1/items/", json={"name": "Item to Keep B", "description": "Desc B"}
    )
    item_id_b = create_response_2.json()["id"]

    # Fetch all items and ensure item_id_a is not present, but item_id_b is.
    get_response = client.get("/v1/items/")
    assert get_response.status_code == 200
    returned_items = get_response.json()["items"]
    returned_ids = {item["id"] for item in returned_items}

    assert item_id_a not in returned_ids
    assert item_id_b in returned_ids


def test_update_soft_deleted_item(client):
    """
    Test updating a soft-deleted item. It should still be possible to update it.
    """
    create_response = client.post(
        "/v1/items/", json={"name": "Updatable Soft-Delete", "description": "Desc"}
    )
    item_id = create_response.json()["id"]

    # Soft-delete the item
    client.delete(f"/v1/items/{item_id}/soft-delete")

    # Try to update the soft-deleted item
    update_payload = {"name": "Updated Soft-Deleted Name"}
    response = client.patch(f"/v1/items/{item_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Soft-Deleted Name"
    assert response.json()["is_deleted"] is True  # Should still be deleted

    # Verify it's still not in the default get_all_items list
    get_response = client.get("/v1/items/")
    returned_ids = {item["id"] for item in get_response.json()["items"]}
    assert item_id not in returned_ids


def test_restore_soft_deleted_item(client):
    """
    Test restoring a soft-deleted item by setting is_deleted to False via PATCH.
    """
    create_response = client.post(
        "/v1/items/", json={"name": "Restorable Item", "description": "Desc"}
    )
    item_id = create_response.json()["id"]

    # Soft-delete the item
    client.delete(f"/v1/items/{item_id}/soft-delete")

    # Verify it's not in the default get_all_items list
    get_response_before_restore = client.get("/v1/items/")
    returned_ids_before = {item["id"] for item in get_response_before_restore.json()["items"]}
    assert item_id not in returned_ids_before

    # Restore the item using PATCH
    restore_payload = {"is_deleted": False}
    restore_response = client.patch(f"/v1/items/{item_id}", json=restore_payload)
    assert restore_response.status_code == 200
    assert restore_response.json()["is_deleted"] is False

    # Verify it is now in the default get_all_items list
    get_response_after_restore = client.get("/v1/items/")
    returned_ids_after = {item["id"] for item in get_response_after_restore.json()["items"]}
    assert item_id in returned_ids_after
