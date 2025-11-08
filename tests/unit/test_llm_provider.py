import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from oal_agent.core.errors import LLMTimeoutError
from oal_agent.llm.provider import OpenAIProvider


@pytest.mark.asyncio
async def test_openai_provider_timeout():
    """Test that OpenAIProvider raises LLMTimeoutError on timeout."""
    provider = OpenAIProvider(api_key="test_key")

    with patch("oal_agent.llm.provider.OpenAIProvider._call_openai_api", side_effect=asyncio.TimeoutError) as mock_api_call:
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_backoff_sleep:
            with pytest.raises(LLMTimeoutError):
                await provider.generate(prompt="test prompt", retry_attempts=1)
            mock_api_call.assert_called_once()
            mock_backoff_sleep.assert_not_called()


@pytest.mark.asyncio
async def test_openai_provider_retries_on_timeout():
    """Test that OpenAIProvider retries on asyncio.TimeoutError."""
    provider = OpenAIProvider(api_key="test_key")
    # Simulate 2 timeouts then success
    side_effects = [asyncio.TimeoutError, asyncio.TimeoutError, "Generated text from OpenAI"]

    with patch("oal_agent.llm.provider.OpenAIProvider._call_openai_api", side_effect=side_effects) as mock_api_call:
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_backoff_sleep:
            result = await provider.generate(prompt="test prompt", retry_attempts=3)
            assert result == "Generated text from OpenAI"
            assert mock_api_call.call_count == 3
            assert mock_backoff_sleep.call_count == 2  # Two retries, so sleep is called twice


@pytest.mark.asyncio
async def test_openai_provider_invalid_retry_attempts():
    """Test that OpenAIProvider raises ValueError for invalid retry_attempts."""
    provider = OpenAIProvider(api_key="test_key")
    with pytest.raises(ValueError, match="Invalid retry_attempts"):
        await provider.generate(prompt="test prompt", retry_attempts=0)
    with pytest.raises(ValueError, match="Invalid retry_attempts"):
        await provider.generate(prompt="test prompt", retry_attempts=6)


@pytest.mark.asyncio
async def test_openai_provider_invalid_timeout():
    """Test that OpenAIProvider raises ValueError for invalid timeout."""
    provider = OpenAIProvider(api_key="test_key")
    with pytest.raises(ValueError, match="Invalid timeout"):
        await provider.generate(prompt="test prompt", timeout=9)
    with pytest.raises(ValueError, match="Invalid timeout"):
        await provider.generate(prompt="test prompt", timeout=121)
