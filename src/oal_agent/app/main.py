# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Main FastAPI application."""

from contextlib import asynccontextmanager

import os
import sys

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware

from oal_agent import __version__
from oal_agent.core.config import settings
from oal_agent.services.queue import QueueService
from oal_agent.telemetry.logging import get_logger, setup_logging

from .routers import analysis, items, users

setup_logging()

logger = get_logger(__name__)

queue_service = QueueService(queue_url=settings.queue_url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    try:
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
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/ready")
async def ready():
    """Readiness check endpoint."""
    return {"status": "ready"}


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
