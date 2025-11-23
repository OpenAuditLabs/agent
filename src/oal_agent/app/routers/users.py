from typing import Any, Dict, List, Optional
import logging

from fastapi import APIRouter, HTTPException, Query

from oal_agent.app.schemas.users import UserRole, UserStatus

router = APIRouter()

logger = logging.getLogger(__name__)


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
    role: Optional[UserRole] = Query(
        None,
        description="Filter users by role",
        examples=["admin"],
    ),
    status: Optional[UserStatus] = Query(
        None,
        description="Filter users by status",
        examples=["active"],
    ),
):
    """Retrieve a list of all users with pagination and optional filtering.

    Args:
        limit (int): Maximum number of users to return. Defaults to 100, min 1, max 1000.
        offset (int): Number of users to skip. Defaults to 0, min 0.
        role (Optional[UserRole]): Filter users by role.
        status (Optional[UserStatus]): Filter users by status.

    Returns:
        dict: (WIP) A dictionary containing:
            - "users" (list[dict]): A list of user objects, each with 'id', 'name', and 'email'.
            - "total_count" (int): The total number of users available.
            - "limit" (int): The maximum number of users requested.
            - "offset" (int): The number of users skipped.
    """
    try:
        # TODO: Integrate with a user store/service/DB for real paginated retrieval.
        # This PR should be marked as DRAFT until this is implemented.
        # For now, returning a placeholder to avoid misleading success.
        users: List[Dict[str, Any]] = (
            []
        )  # Replace with actual user data from the service
        total_count = 0  # Replace with actual total count from the service

        # Apply role filter if provided
        if role:
            # In a real implementation, this would filter the user collection/queryset
            logger.debug("Filtering by role: %s", role.value)

        # Apply status filter if provided
        if status:
            # In a real implementation, this would filter the user collection/queryset
            logger.debug("Filtering by status: %s", status.value)

        return {
            "users": users,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        # TODO: Catch more specific exceptions from the user service/DB.
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve users: {e}"
        ) from e
