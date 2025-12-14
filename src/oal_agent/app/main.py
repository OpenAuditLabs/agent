# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Main FastAPI application."""

import asyncio
import os
import signal
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send, Message
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import PlainTextResponse
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.brotli import BrotliMiddleware

from prometheus_client import CONTENT_TYPE_LATEST

from oal_agent import __version__
from oal_agent.core.config import settings
from oal_agent.services.queue import QueueService
from oal_agent.services.storage import StorageService
from oal_agent.telemetry.logging import get_logger, setup_logging
from oal_agent.telemetry.metrics import metrics

from .routers import analysis, items, users, jobs

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





    global queue_service
    dependencies._queue_service = queue_service

    try:
        # Ensure storage directory exists
        os.makedirs(settings.storage_path, exist_ok=True)
        await queue_service.start()

    yield



    logger.info("Shutting down...")
    try:
        await queue_service.stop()
    except Exception as e:
        logger.exception("Failed to stop services during shutdown: %s", e)
        # Do not re-raise to allow remaining shutdown tasks to run



external_docs = {
    "description": "OpenAuditLabs Agent Documentation",
    "url": "https://docs.openauditlabs.com/agent",
}

tags_metadata = [
    {
        "name": "analysis",
        "description": "Operations related to smart contract analysis.",
    },
    {
        "name": "items",
        "description": "Manage audit items and their lifecycle.",
    },
    {
        "name": "jobs",
        "description": "Manage analysis jobs and their status.",
    },
    {
        "name": "users",
        "description": "User management operations.",
    },
    {
        "name": "monitoring",
        "description": "Health checks, metrics, and application status.",
        "externalDocs": external_docs,
    },
    {
        "name": "internal",
        "description": "Internal endpoints for system information and debugging.",
    },
]

app = FastAPI(
    title="OAL Agent API",
    description="Smart Contract Security Analysis System",
    version=__version__,
    openapi_tags=tags_metadata,
    openapi_external_docs=external_docs,
    docs_url="/documentation",
    redoc_url=None,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BrotliMiddleware, minimum_size=settings.compression_minimum_size)
app.add_middleware(GZipMiddleware, minimum_size=settings.compression_minimum_size)

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


app.include_router(analysis.router, prefix="/v1/analysis")
app.include_router(items.router, prefix="/v1/items")
app.include_router(users.router, prefix="/v1/users")
app.include_router(jobs.router, prefix="/v1/jobs")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "OAL Agent API"}


@app.get("/health", tags=["monitoring"])
async def health():
    """Health check endpoint."""
    return {"message": "OK"}


@app.get("/livez", tags=["monitoring"])
async def livez():
    """Liveness check endpoint."""
    return {"status": "alive"}


@app.get("/readyz", tags=["monitoring"])
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


@app.get("/metrics", tags=["monitoring"])
async def metrics_endpoint():
    """Metrics endpoint serving Prometheus-format metrics."""
    return Response(content=metrics.generate_prometheus_metrics(), media_type=CONTENT_TYPE_LATEST)


@app.get("/build-info", tags=["internal"])
async def build_info():
    """Returns build information from environment variables."""
    return {
        "git_commit_sha": os.getenv("GIT_COMMIT_SHA", "N/A"),
        "git_branch": os.getenv("GIT_BRANCH", "N/A"),
        "git_tag": os.getenv("GIT_TAG", "N/A"),
        "build_date": os.getenv("BUILD_DATE", "N/A"),
    }
