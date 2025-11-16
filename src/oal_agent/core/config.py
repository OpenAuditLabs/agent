"""Configuration management."""

from typing import Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Attributes:
        api_host: The host for the API server. Defaults to "127.0.0.1".
        api_port: The port for the API server. Defaults to 8000.
        database_url: The URL for the database connection. Defaults to "sqlite:///./oal_agent.db".
        queue_url: The URL for the message queue. Defaults to "redis://localhost:6379".
        queue_max_size: The maximum size of the message queue. Defaults to 100.
        llm_provider: The provider for the Large Language Model. Defaults to "openai".
        llm_api_key: The API key for the LLM provider. Defaults to an empty string.
    """

    api_host: str = (
        "127.0.0.1"  # Bind to 0.0.0.0 for external access, e.g., via environment variable or config file
    )
    api_port: int = 8000

    database_url: str = "sqlite:///./oal_agent.db"

    queue_url: str = "redis://localhost:6379"
    queue_max_size: int = 100

    llm_provider: str = "openai"
    llm_api_key: str = ""

    @classmethod
    def from_dict(cls, env_vars: Dict[str, str]) -> "Settings":
        """
        Constructs a Settings instance from a dictionary of environment variables.

        Args:
            env_vars: A dictionary where keys are setting names (e.g., "API_HOST")
                      and values are their corresponding string values.

        Returns:
            A Settings instance configured with the provided values.
        """
        return cls(**env_vars)  # type: ignore[arg-type]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore

def reset_settings():
    """Resets the global settings object to its default values, primarily for test isolation."""
    global settings
    settings = Settings()
