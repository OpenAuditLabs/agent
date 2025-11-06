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
        # TODO: Integrate with a user store/service/DB for real paginated retrieval.
        # This PR should be marked as DRAFT until this is implemented.
        # For now, returning a placeholder to avoid misleading success.
        users = []  # Replace with actual user data from the service
        total_count = 0  # Replace with actual total count from the service

        return {
            "users": users,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        # TODO: Catch more specific exceptions from the user service/DB.
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {e}") from e
