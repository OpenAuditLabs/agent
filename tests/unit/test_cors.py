# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Unit tests for CORS middleware."""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient


def create_app(allow_origins: list[str] = None) -> FastAPI:
    app = FastAPI()
    if allow_origins is None:
        allow_origins = []

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


def test_cors_middleware_disabled_by_default():
    """Test that CORS middleware is disabled by default (empty origins)."""
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert "access-control-allow-origin" not in response.headers.keys()


def test_cors_middleware_with_allowed_origin():
    """Test that CORS headers are present with an allowed origin."""
    app = create_app(allow_origins=["http://localhost:3000"])
    client = TestClient(app)
    response = client.get("/health", headers={"origin": "http://localhost:3000"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-credentials" in response.headers.keys()
    assert "access-control-allow-methods" in response.headers.keys()
    assert "access-control-allow-headers" in response.headers.keys()


def test_cors_middleware_with_multiple_allowed_origins():
    """Test that CORS headers work with multiple allowed origins."""
    app = create_app(allow_origins=["http://localhost:3000", "http://example.com"])
    client = TestClient(app)
    response = client.get("/health", headers={"origin": "http://example.com"})
    assert response.headers["access-control-allow-origin"] == "http://example.com"


def test_cors_middleware_with_not_allowed_origin():
    """Test that CORS headers are not present with a non-allowed origin."""
    app = create_app(allow_origins=["http://localhost:3000"])
    client = TestClient(app)
    response = client.get("/health", headers={"origin": "http://malicious.com"})
    assert "access-control-allow-origin" not in response.headers.keys()


def test_cors_middleware_options_request():
    """Test that CORS handles OPTIONS preflight requests."""
    app = create_app(allow_origins=["http://localhost:3000"])
    client = TestClient(app)
    response = client.options(
        "/health",
        headers={
            "origin": "http://localhost:3000",
            "access-control-request-method": "GET",
            "access-control-request-headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-methods" in response.headers.keys()
    assert "access-control-allow-headers" in response.headers.keys()