from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/", summary="Health check", response_description="Health check successful")
async def health_check():
    """Perform a health check.

    Returns:
        A dictionary indicating the health status.
    """
    try:
        # Placeholder for actual health check logic (e.g., database connection, external service status)
        status = {"status": "ok", "message": "Service is healthy"}
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")
