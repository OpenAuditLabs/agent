# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Main FastAPI application."""

from fastapi import FastAPI

from .routers import analysis

app = FastAPI(
    title="OAL Agent API",
    description="Smart Contract Security Analysis System",
    version="0.1.0"
)

app.include_router(analysis.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "OAL Agent API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    """Readiness check endpoint."""
    return {"status": "ready"}

@app.get("/metrics")
async def metrics():
    """Metrics endpoint."""
    return {"metrics": "Not implemented yet"}
