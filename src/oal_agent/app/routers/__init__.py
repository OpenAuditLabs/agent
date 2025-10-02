"""Routers module."""

from fastapi import APIRouter
from .health import router as health_router
from .items import router as items_router
from .users import router as users_router
from .auth import router as auth_router
from .files import router as files_router
from .models import router as models_router
from .predictions import router as predictions_router
from .deployments import router as deployments_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(items_router, prefix="/items", tags=["items"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(models_router, prefix="/models", tags=["models"])
api_router.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
api_router.include_router(deployments_router, prefix="/deployments", tags=["deployments"])

