import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from slowapi.errors import RateLimitExceeded


from oal_agent.app.main import app
from oal_agent.core.config import reset_settings, settings


@pytest.mark.asyncio
@patch("fastapi_limiter.depends.RateLimiter") # Patch the dependency directly
@patch("redis.asyncio.from_url") # Mock redis.asyncio.from_url
async def test_rate_limiting_enabled(
    mock_from_url: AsyncMock, # Mock for redis.asyncio.from_url
    mock_rate_limiter_dep: MagicMock, # Mock for RateLimiter dependency
):
    """Test that rate limiting is enabled and works correctly."""
    reset_settings()
    settings.rate_limit_enabled = True
    settings.rate_limit_per_minute = 2

    # Mock Redis connection object and its methods
    mock_redis_connection = MagicMock()
    mock_redis_connection.script_load = AsyncMock(return_value="sha1_script") # Mock script_load
    mock_redis_connection.close = AsyncMock() # Mock close method

    # Configure the mock for redis.asyncio.from_url to return our mock connection
    # It needs to return a coroutine that, when awaited, gives mock_redis_connection
    mock_from_url.return_value = mock_redis_connection

    # Simulate the RateLimiter dependency directly
    # We will use side_effect to raise RateLimitExceeded after a certain number of calls
    call_count = 0
    async def mock_rate_limiter_callable(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count > settings.rate_limit_per_minute:
            raise RateLimitExceeded("Too Many Requests") # Simulate rate limit exceeded
        return None # Allow the request to proceed otherwise

    mock_rate_limiter_dep.side_effect = mock_rate_limiter_callable


    with TestClient(app) as client:
        # FastAPILimiter.init should be called during app startup with the mock_redis_connection
        # We need to patch FastAPILimiter.init in main.py to assert it's called
        with patch("oal_agent.app.main.FastAPILimiter.init", new=AsyncMock()) as mock_fastapilimiter_init:
            # The actual FastAPILimiter.init will be called by the app's lifespan
            # We just need to assert that our mock was called with the correct redis_connection
            pass # No direct call here, it's triggered by TestClient(app) context

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
    with patch("oal_agent.app.main.FastAPILimiter.shutdown", new=AsyncMock()) as mock_fastapilimiter_shutdown:
        pass # No direct call here, it's triggered by TestClient(app) context

    mock_fastapilimiter_init.assert_called_once_with(mock_redis_connection)
    mock_fastapilimiter_shutdown.assert_called_once()
    mock_redis_connection.close.assert_called_once()


@pytest.mark.asyncio
@patch("oal_agent.app.main.FastAPILimiter") # Keep this patch for test_rate_limiting_disabled
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
@patch("fastapi_limiter.depends.RateLimiter")
@patch("redis.asyncio.from_url")
async def test_rate_limiting_multiple_endpoints(
    mock_from_url: AsyncMock,
    mock_rate_limiter_dep: MagicMock,
):
    """Test that rate limiting applies across multiple endpoints."""
    reset_settings()
    settings.rate_limit_enabled = True
    settings.rate_limit_per_minute = 1

    # Mock Redis connection object and its methods
    mock_redis_connection = MagicMock()
    mock_redis_connection.script_load = AsyncMock(return_value="sha1_script")
    mock_redis_connection.close = AsyncMock()

    mock_from_url.return_value = mock_redis_connection

    call_count = 0
    async def mock_rate_limiter_callable(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count > settings.rate_limit_per_minute:
            raise RateLimitExceeded("Too Many Requests")
        return None

    mock_rate_limiter_dep.side_effect = mock_rate_limiter_callable

    with TestClient(app) as client:
        with patch("oal_agent.app.main.FastAPILimiter.init", new=AsyncMock()) as mock_fastapilimiter_init:
            pass

        response1 = client.get("/health")
        assert response1.status_code == 200

        # Second request to a different endpoint should also be rate-limited if the global limit is exceeded
        response2 = client.get("/")
        assert response2.status_code == 429

    with patch("oal_agent.app.main.FastAPILimiter.shutdown", new=AsyncMock()) as mock_fastapilimiter_shutdown:
        pass

    mock_fastapilimiter_init.assert_called_once_with(mock_redis_connection)
    mock_fastapilimiter_shutdown.assert_called_once()
    mock_redis_connection.close.assert_called_once()
