from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status

from oal_agent.app.schemas.items import Item, ItemCreate, ItemUpdate
from oal_agent.app.schemas.jobs import PaginationParams
from oal_agent.app.schemas.results import PaginatedItemsResponse

router = APIRouter()


# In-memory "database" for demonstration purposes
# In a real application, this would be a proper database connection
items_db: Dict[int, Item] = {}

# Initialize with some dummy data
_next_id = 1
for i in range(1, 101):
    items_db[i] = Item(
        id=i,
        name=f"Item {i}",
        description=f"Description for item {i}",
        is_deleted=False,
    )
    _next_id = i + 1


@router.get(
    "/",
    summary="Get all items with pagination",
    response_description="Paginated list of all items",
    response_model=PaginatedItemsResponse[Item],
)
async def get_all_items(
    pagination: PaginationParams = Depends(),
):
    """Retrieve a paginated list of all items.

    Args:
        pagination (PaginationParams): Pagination parameters including limit and offset.

    Returns:
        PaginatedItemsResponse: A paginated list of items.
    """
    try:
        # Filter out soft-deleted items
        available_items = [
            item for item in items_db.values() if not item.is_deleted
        ]
        total_items = len(available_items)

        # Apply pagination
        paginated_items = available_items[
            pagination.offset : pagination.offset + pagination.limit
        ]

        return PaginatedItemsResponse(
            items=paginated_items,
            total=total_items,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve items: {e}")


@router.post(
    "/",
    summary="Create a new item",
    response_description="The newly created item",
    status_code=status.HTTP_201_CREATED,
    response_model=Item,
)
async def create_item(item: ItemCreate):
    """Create a new item with the provided data.

    Args:
        item (ItemCreate): The item data to create.

    Returns:
        Item: The created item with a generated ID.
    """
    global _next_id
    new_item = Item(id=_next_id, **item.model_dump(), is_deleted=False)
    items_db[_next_id] = new_item
    _next_id += 1
    return new_item


@router.patch(
    "/{item_id}",
    summary="Update an existing item",
    response_description="The updated item",
    response_model=Item,
)
async def update_item(item_id: int, item_update: ItemUpdate):
    """Update an existing item with the provided data.

    Args:
        item_id (int): The ID of the item to update.
        item_update (ItemUpdate): The item data to update.

    Returns:
        Item: The updated item.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_item = items_db[item_id]
    update_data = item_update.model_dump(exclude_unset=True)
    updated_item = existing_item.model_copy(update=update_data)
    items_db[item_id] = updated_item
    return updated_item


@router.delete(
    "/{item_id}/soft-delete",
    summary="Soft-delete an item",
    response_description="Message confirming soft-deletion",
    response_model=dict,
)
async def soft_delete_item(item_id: int):
    """Soft-delete an item by marking its 'is_deleted' flag as True.

    Args:
        item_id (int): The ID of the item to soft-delete.

    Returns:
        dict: A confirmation message.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    item = items_db[item_id]
    item.is_deleted = True
    return {"message": f"Item {item_id} soft-deleted successfully"}
