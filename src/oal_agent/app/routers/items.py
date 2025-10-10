from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from oal_agent.app.schemas.results import PaginatedItemsResponse

router = APIRouter()


@router.get(
    "/",
    summary="Get all items with pagination",
    response_description="Paginated list of all items",
    response_model=PaginatedItemsResponse,
)
async def get_all_items(
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
):
    """Retrieve a paginated list of all items.

    Args:
        limit (int): Maximum number of items to return. Defaults to 10, max 100.
        offset (int): Number of items to skip. Defaults to 0.

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
        paginated_items = all_items[offset : offset + limit]

        return PaginatedItemsResponse(
            items=paginated_items, total=total_items, limit=limit, offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve items: {e}")
