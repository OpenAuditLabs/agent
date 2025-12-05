# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Main FastAPI application."""

import asyncio
import os
import signal
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send, Message
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import PlainTextResponse



from oal_agent import __version__
from oal_agent.core.config import settings
from oal_agent.services.queue import QueueService
from oal_agent.services.storage import StorageService
from oal_agent.telemetry.logging import get_logger, setup_logging

from .routers import analysis, items, users

setup_logging()

logger = get_logger(__name__)


class ContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type")
            if not content_type or not content_type.startswith("application/json"):
                logger.warning(
                    "Rejected request with invalid Content-Type: %s from %s",
                    content_type,
                    request.client.host if request.client else "unknown",
                )
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={"detail": "Unsupported Media Type. Only application/json is supported."},
                )
        response = await call_next(request)
        return response


queue_service = QueueService(queue_url=settings.queue_url)
storage_service = StorageService(
    storage_path=settings.storage_path,
    encryption_key=(
        settings.storage_encryption_key.encode("utf-8")
        if settings.storage_encryption_key
        else None
    ),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")





    try:
        # Ensure storage directory exists
        os.makedirs(settings.storage_path, exist_ok=True)
        await queue_service.start()
    except Exception as e:
        logger.exception("Failed to start services during startup: %s", e)
        sys.exit(1)  # Exit to prevent running with a partially-initialized app

    yield



    logger.info("Shutting down...")
    try:
        await queue_service.stop()
    except Exception as e:
        logger.exception("Failed to stop services during shutdown: %s", e)
        # Do not re-raise to allow remaining shutdown tasks to run


app = FastAPI(
    title="OAL Agent API",
    description="Smart Contract Security Analysis System",
    version=__version__,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ContentTypeMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Handles all unhandled exceptions, logs them, and returns a consistent JSON error response.
    """
    logger.exception("Unhandled exception occurred: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "An internal server error occurred",
            "code": "internal_error",
        },
    )


app.include_router(analysis.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1/items")
app.include_router(users.router, prefix="/api/v1/users")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "OAL Agent API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"message": "OK"}


@app.get("/livez")
async def livez():
    """Liveness check endpoint."""
    return {"status": "alive"}


@app.get("/readyz")
def readyz():
    """Readiness check endpoint that verifies downstream dependencies."""
    try:
        queue_healthy = queue_service.check_health()
    except Exception as exc:
        logger.exception('Queue health check failed unexpectedly: %s', exc)
        queue_healthy = False

    try:
        storage_healthy = storage_service.check_health()
    except Exception as exc:
        logger.exception('Storage health check failed unexpectedly: %s', exc)
        storage_healthy = False

    if queue_healthy and storage_healthy:
        return {"status": "ready"}
    else:
        content = {}
        if not queue_healthy:
            content["queue"] = "unhealthy"
        if not storage_healthy:
            content["storage"] = "unhealthy"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not ready",
                "dependencies": content,
            },
        )


@app.get("/metrics")
async def metrics():
    """Metrics endpoint."""
    return {"metrics": "Not implemented yet"}


@app.get("/build-info")
async def build_info():
    """Returns build information from environment variables."""
    return {
        "git_commit_sha": os.getenv("GIT_COMMIT_SHA", "N/A"),
        "git_branch": os.getenv("GIT_BRANCH", "N/A"),
        "git_tag": os.getenv("GIT_TAG", "N/A"),
        "build_date": os.getenv("BUILD_DATE", "N/A"),
    }
