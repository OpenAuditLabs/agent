import asyncio
import pytest
from unittest.mock import patch, AsyncMock

from oal_agent.llm.provider import OpenAIProvider
from oal_agent.core.errors import LLMTimeoutError


@pytest.mark.asyncio
async def test_openai_provider_timeout():
    """Test that OpenAIProvider raises LLMTimeoutError on timeout."""
    provider = OpenAIProvider(api_key="test_key")

    with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError) as mock_wait_for:
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            with pytest.raises(LLMTimeoutError):
                await provider.generate(prompt="test prompt")
            mock_wait_for.assert_called_once()
            mock_sleep.assert_called_once_with(0.1)
