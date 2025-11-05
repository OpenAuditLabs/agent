from fastapi import APIRouter, Depends, HTTPException, status

from oal_agent.app.schemas.items import ItemCreate, ItemUpdate
from oal_agent.app.schemas.jobs import PaginationParams
from oal_agent.app.schemas.results import PaginatedItemsResponse

router = APIRouter()


@router.get(
    "/",
    summary="Get all items with pagination",
    response_description="Paginated list of all items",
    response_model=PaginatedItemsResponse,
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
        # Placeholder for actual item retrieval logic
        # In a real application, this would fetch data from a database
        # and apply limit/offset at the database level.
        all_items = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]
        total_items = len(all_items)

        # Apply pagination
        paginated_items = all_items[
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
)
async def create_item(item: ItemCreate):
    """Create a new item with the provided data.

    Args:
        item (ItemCreate): The item data to create.

    Returns:
        dict: The created item with a generated ID.
    """
    # Placeholder for actual item creation logic
    # In a real application, this would save the item to a database
    # and return the saved item with its generated ID.
    new_item_id = 101  # Simulate a new ID
    return {"id": new_item_id, **item.model_dump()}


@router.patch(
    "/{item_id}",
    summary="Update an existing item",
    response_description="The updated item",
)
async def update_item(item_id: int, item: ItemUpdate):
    """Update an existing item with the provided data.

    Args:
        item_id (int): The ID of the item to update.
        item (ItemUpdate): The item data to update.

    Returns:
        dict: The updated item.
    """
    # Placeholder for actual item update logic
    # In a real application, this would fetch the item, update it,
    # save it back to the database, and return the updated item.
    # For demonstration, we'll just return the item_id and the updated data.
    if not item.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided for update.",
        )
    return {"id": item_id, **item.model_dump(exclude_unset=True)}
