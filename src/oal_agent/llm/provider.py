"""LLM provider interface."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for Large Language Model (LLM) providers.

    Defines the interface for interacting with different LLMs, ensuring a consistent
    way to generate text based on a given prompt.
    """

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generates text based on a provided prompt.

        This method must be implemented by concrete LLM provider classes to
        interact with their respective LLM APIs.

        Args:
            prompt: The input text prompt for the LLM.
            **kwargs: Additional keyword arguments specific to the LLM provider's API.

        Returns:
            The generated text as a string.
        """
        pass


class OpenAIProvider(LLMProvider):
    """Concrete implementation of an LLMProvider for OpenAI models.

    This class handles the interaction with the OpenAI API to generate text.
    """

    def __init__(self, api_key: str):
        """Initializes the OpenAIProvider with the necessary API key.

        Args:
            api_key: The API key required to authenticate with the OpenAI service.
        """
        self.api_key = api_key

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generates text using the OpenAI API.

        Args:
            prompt: The input text prompt for the OpenAI model.
            **kwargs: Additional keyword arguments to pass to the OpenAI API call
                      (e.g., `temperature`, `max_tokens`).

        Returns:
            The generated text from the OpenAI model.

        Raises:
            NotImplementedError: If the OpenAI API integration is not yet implemented.
        """
        # TODO: Implement OpenAI integration using self.api_key and the prompt.
        # Example: response = await openai.Completion.acreate(prompt=prompt, **kwargs)
        # return response.choices[0].text.strip()
        raise NotImplementedError("OpenAI integration is not yet implemented.")
