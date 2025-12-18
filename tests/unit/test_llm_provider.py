import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from oal_agent.core.errors import LLMProviderError
from oal_agent.llm.provider import FallbackLLMProvider, OpenAIProvider


@pytest.mark.asyncio
async def test_openai_provider_timeout():
    """Test that OpenAIProvider raises LLMProviderError on timeout."""
    provider = OpenAIProvider(api_key="test_key")

    with patch(
        "oal_agent.llm.provider.OpenAIProvider._call_openai_api",
        side_effect=asyncio.TimeoutError,
    ) as mock_api_call:
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_backoff_sleep:
            with pytest.raises(LLMProviderError):
                await provider.generate(prompt="test prompt", retry_attempts=1)
            mock_api_call.assert_called_once()
            mock_backoff_sleep.assert_not_called()


@pytest.mark.asyncio
async def test_openai_provider_retries_on_timeout():
    """Test that OpenAIProvider retries on asyncio.TimeoutError."""
    provider = OpenAIProvider(api_key="test_key")
    # Simulate 2 timeouts then success
    side_effects = [
        asyncio.TimeoutError,
        asyncio.TimeoutError,
        "Generated text from OpenAI",
    ]

    with patch(
        "oal_agent.llm.provider.OpenAIProvider._call_openai_api",
        side_effect=side_effects,
    ) as mock_api_call:
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_backoff_sleep:
            result = await provider.generate(prompt="test prompt", retry_attempts=3)
            assert result == "Generated text from OpenAI"
            assert mock_api_call.call_count == 3
            assert (
                mock_backoff_sleep.call_count == 2
            )  # Two retries, so sleep is called twice


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


@pytest.mark.asyncio
async def test_fallback_llm_provider_success():
    """Test that FallbackLLMProvider successfully falls back to a secondary provider."""
    # Mock the primary provider to always raise an error
    mock_primary_provider = AsyncMock(spec=OpenAIProvider)
    mock_primary_provider.generate.side_effect = LLMProviderError("Primary failed")

    # Mock the secondary provider to succeed
    mock_secondary_provider = AsyncMock(spec=OpenAIProvider)
    mock_secondary_provider.generate.return_value = "Response from fallback"

    fallback_provider = FallbackLLMProvider(
        providers=[mock_primary_provider, mock_secondary_provider]
    )

    result = await fallback_provider.generate(prompt="test prompt")

    assert result == "Response from fallback"
    mock_primary_provider.generate.assert_called_once_with(
        "test prompt", 3, 60
    )  # Default retry_attempts and timeout
    mock_secondary_provider.generate.assert_called_once_with(
        "test prompt", 3, 60
    )  # Default retry_attempts and timeout


@pytest.mark.asyncio
async def test_fallback_llm_provider_all_fail():
    """Test that FallbackLLMProvider raises an error if all providers fail."""
    mock_primary_provider = AsyncMock(spec=OpenAIProvider)
    mock_primary_provider.generate.side_effect = LLMProviderError("Primary failed")

    mock_secondary_provider = AsyncMock(spec=OpenAIProvider)
    mock_secondary_provider.generate.side_effect = LLMProviderError("Secondary failed")

    fallback_provider = FallbackLLMProvider(
        providers=[mock_primary_provider, mock_secondary_provider]
    )

    with pytest.raises(LLMProviderError, match="All LLM providers failed to generate a response."):
        await fallback_provider.generate(prompt="test prompt")

    mock_primary_provider.generate.assert_called_once()
    mock_secondary_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_fallback_llm_provider_empty_providers():
    """Test that FallbackLLMProvider raises ValueError if initialized with an empty list."""
    with pytest.raises(ValueError, match="At least one LLM provider must be provided for FallbackLLMProvider."):
        FallbackLLMProvider(providers=[])