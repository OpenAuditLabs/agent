from fastapi import APIRouter, Depends, HTTPException

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
