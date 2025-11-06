from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.get("/", summary="Get all users", response_description="List of all users")
async def get_all_users(
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of users to return",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of users to skip",
    ),
):
    """Retrieve a list of all users with pagination.

    Args:
        limit (int): Maximum number of users to return. Defaults to 100, min 1, max 1000.
        offset (int): Number of users to skip. Defaults to 0, min 0.

    Returns:
        A dictionary with a placeholder message, including the applied limit and offset.
    """
    try:
        # Placeholder for actual user retrieval logic
        message = f"List of users with limit {limit}" f" and offset {offset}"
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {e}")
