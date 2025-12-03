import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi_limiter import FastAPILimiter

from oal_agent.app.main import app
from oal_agent.core.config import reset_settings, settings


# Helper to manage the rate limit counter in tests
class MockRateLimiter:
    def __init__(self, limit: int):
        self.limit = limit
        self.counter = 0

    async def has_been_limited(self, key: str, rate: str) -> bool:
        if self.counter < self.limit:
            self.counter += 1
            return False
        return True


@pytest.mark.asyncio
@patch("oal_agent.app.main.FastAPILimiter")  # Patch the class in the target module
@patch("redis.asyncio.from_url")
async def test_rate_limiting_enabled(
    mock_from_url: AsyncMock,
    mock_fastapi_limiter_cls: MagicMock,  # This is the mocked class in main.py
):
    """Test that rate limiting is enabled and works correctly."""
    reset_settings()
    settings.rate_limit_enabled = True
    settings.rate_limit_per_minute = 2

    # Configure the mocked FastAPILimiter class methods
    mock_fastapi_limiter_cls.init = AsyncMock()
    mock_fastapi_limiter_cls.shutdown = AsyncMock()

    # Mock Redis connection
    mock_redis_connection = AsyncMock()
    mock_from_url.return_value = mock_redis_connection

    mock_fastapi_limiter_cls._rate_limit_func = lambda request: f"{settings.rate_limit_per_minute}/minute"
    mock_fastapi_limiter_cls._identifier_func = lambda request: "test-client"
    def mock_exceeded_handler(request, response, p):
        res = JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        res.headers["x-ratelimit-remaining"] = "0"
        return res
    mock_fastapi_limiter_cls._rate_limit_exceeded_handler = mock_exceeded_handler

    # Use our mock for Redis's evalsha to simulate rate limiting
    # The Lua script typically returns [remaining_requests, total_requests, ttl]
    # We want to simulate successful requests until the limit is reached, then 429.
    # The first two calls should return 1 (not limited), subsequent calls 0 (limited).
    mock_redis_connection.evalsha.side_effect = [
        [1, settings.rate_limit_per_minute, 60], # Not limited, 1 request remaining
        [0, settings.rate_limit_per_minute, 60], # Not limited, 0 requests remaining
        [0, settings.rate_limit_per_minute, 60], # Limited, 0 requests remaining
    ]

    with TestClient(app) as client:
        # FastAPILimiter.init should be called during app startup
        mock_fastapi_limiter_cls.init.assert_called_once_with(mock_redis_connection)

        # Make requests up to the limit
        response1 = client.get("/health")
        assert response1.status_code == 200

        response2 = client.get("/health")
        assert response2.status_code == 200

        # Exceed the limit
        response3 = client.get("/health")
        assert response3.status_code == 429
        assert "x-ratelimit-remaining" in response3.headers
        assert response3.headers["x-ratelimit-remaining"] == "0"

        # FastAPILimiter.shutdown should be called during app shutdown
        mock_fastapi_limiter_cls.shutdown.assert_called_once()


@pytest.mark.asyncio
@patch("oal_agent.app.main.FastAPILimiter")
@patch("redis.asyncio.from_url")
async def test_rate_limiting_disabled(
    mock_from_url: AsyncMock,
    mock_fastapi_limiter_cls: MagicMock,
):
    """Test that rate limiting is disabled and no limits are applied."""
    reset_settings()
    settings.rate_limit_enabled = False
    settings.rate_limit_per_minute = 2

    mock_fastapi_limiter_cls.init = AsyncMock()
    mock_fastapi_limiter_cls.shutdown = AsyncMock()

    with TestClient(app) as client:
        # FastAPILimiter.init should NOT be called when rate limiting is disabled
        mock_fastapi_limiter_cls.init.assert_not_called()

        # Make multiple requests, they should all pass
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200

    # FastAPILimiter.shutdown should NOT be called when rate limiting is disabled
    mock_fastapi_limiter_cls.shutdown.assert_not_called()


@pytest.mark.asyncio
@patch("oal_agent.app.main.FastAPILimiter")
@patch("redis.asyncio.from_url")
async def test_rate_limiting_multiple_endpoints(
    mock_from_url: AsyncMock,
    mock_fastapi_limiter_cls: MagicMock,
):
    """Test that rate limiting applies across multiple endpoints."""
    reset_settings()
    settings.rate_limit_enabled = True
    settings.rate_limit_per_minute = 1

    mock_fastapi_limiter_cls.init = AsyncMock()
    mock_fastapi_limiter_cls.shutdown = AsyncMock()

    mock_redis_connection = AsyncMock()
    mock_from_url.return_value = mock_redis_connection

    mock_fastapi_limiter_cls._rate_limit_func = lambda request: f"{settings.rate_limit_per_minute}/minute"
    mock_fastapi_limiter_cls._identifier_func = lambda request: "test-client"
    def mock_exceeded_handler(request, response, p):
        res = JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        res.headers["x-ratelimit-remaining"] = "0"
        return res
    mock_fastapi_limiter_cls._rate_limit_exceeded_handler = mock_exceeded_handler

    # Use our mock for Redis's evalsha to simulate rate limiting
    # The Lua script typically returns [remaining_requests, total_requests, ttl]
    # We want to simulate successful requests until the limit is reached, then 429.
    mock_redis_connection.evalsha.side_effect = [
        [0, settings.rate_limit_per_minute, 60], # Not limited, 0 requests remaining
        [0, settings.rate_limit_per_minute, 60], # Limited, 0 requests remaining
    ]
        with TestClient(app) as client:
            mock_fastapi_limiter_cls.init.assert_called_once_with(mock_redis_connection)

            response1 = client.get("/health")
            assert response1.status_code == 200

            # Second request to a different endpoint should also be rate-limited if the global limit is exceeded
            response2 = client.get("/")
            assert response2.status_code == 429

        mock_fastapi_limiter_cls.shutdown.assert_called_once()