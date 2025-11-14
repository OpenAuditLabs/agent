"""LLM provider interface."""

import asyncio
import random
from abc import ABC, abstractmethod

from oal_agent.core.errors import LLMTimeoutError
from oal_agent.llm.guards import LLMGuards


class LLMProvider(ABC):
    """Abstract base class for Large Language Model (LLM) providers.

    Defines the interface for interacting with different LLMs, ensuring a consistent
    way to generate text based on a given prompt.
    """

    @abstractmethod
    async def generate(
        self, prompt: str, retry_attempts: int = 3, timeout: int = 60, **kwargs
    ) -> str:
        """Generates text based on a provided prompt.

        This method must be implemented by concrete LLM provider classes to
        interact with their respective LLM APIs.

        Args:
            prompt: The input text prompt for the LLM.
            retry_attempts: The number of times to retry the LLM call if it fails.
            timeout: The maximum time in seconds to wait for the LLM call to complete.
            **kwargs: Additional keyword arguments specific to the LLM provider's API.

        Returns:
            The generated text as a string.
        """
        pass


class OpenAIProvider(LLMProvider):
    """Concrete implementation of an LLMProvider for OpenAI models.

    This class handles the interaction with the OpenAI API to generate text.
    """

    def __init__(self, api_key: str, llm_guard_cache_max_size: int = 128):
        """Initializes the OpenAIProvider with the necessary API key.

        Args:
            api_key: The API key required to authenticate with the OpenAI service.
            llm_guard_cache_max_size: The maximum size for the LRU cache used by LLMGuards.
        """
        self.api_key = api_key
        self.guards = LLMGuards(cache_max_size=llm_guard_cache_max_size)

    async def _call_openai_api(self, prompt: str, **kwargs) -> str:
        """Simulates the actual OpenAI API call.

        In a real scenario, this would integrate with the OpenAI API client.
        """
        await asyncio.sleep(0.1)  # Simulate network latency
        return "Generated text from OpenAI"

    async def generate(
        self, prompt: str, retry_attempts: int = 3, timeout: int = 60, **kwargs
    ) -> str:
        """Generates text using the OpenAI API.

        Args:
            prompt: The input text prompt for the OpenAI model.
            retry_attempts: The number of times to retry the LLM call if it fails.
            timeout: The maximum time in seconds to wait for the LLM call to complete.
            **kwargs: Additional keyword arguments to pass to the OpenAI API call
                      (e.g., `temperature`, `max_tokens`).

        Returns:
            The generated text from the OpenAI model.

        Raises:
            LLMTimeoutError: If the OpenAI API call times out after all retries.
            ValueError: If input validation fails for retry_attempts or timeout.
        """
        if not self.guards.validate_retry_attempts(retry_attempts):
            raise ValueError(f"Invalid retry_attempts: {retry_attempts}")
        if not self.guards.validate_timeout(timeout):
            raise ValueError(f"Invalid timeout: {timeout}")

        for attempt in range(retry_attempts):
            try:
                # TODO: Implement OpenAI integration using self.api_key and the prompt.
                # Example: response = await openai.Completion.acreate(prompt=prompt, **kwargs)
                # return response.choices[0].text.strip()
                result = await asyncio.wait_for(
                    self._call_openai_api(prompt, **kwargs), timeout=timeout
                )
                return result
            except asyncio.TimeoutError as e:
                if attempt < retry_attempts - 1:
                    backoff_time = 2**attempt + random.uniform(0, 1)
                    print(
                        f"OpenAI API call timed out. Retrying in {backoff_time:.2f} seconds..."
                    )
                    await asyncio.sleep(backoff_time)
                else:
                    raise LLMTimeoutError(
                        "OpenAI API call timed out after multiple retries."
                    ) from e
            except asyncio.CancelledError:
                raise
            except Exception as e:
                if attempt < retry_attempts - 1:
                    backoff_time = 2**attempt + random.uniform(0, 1)
                    print(
                        f"OpenAI API call failed: {e}. Retrying in {backoff_time:.2f} seconds..."
                    )
                    await asyncio.sleep(backoff_time)
                else:
                    raise
