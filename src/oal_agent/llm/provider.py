"""LLM provider interface."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs):
        """Generate text from prompt."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: str):
        """Initialize OpenAI provider."""
        self.api_key = api_key

    async def generate(self, prompt: str, **kwargs):
        """Generate text using OpenAI."""
        # TODO: Implement OpenAI integration
        pass
