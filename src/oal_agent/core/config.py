"""Configuration management."""

from typing import Dict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Settings are loaded in the following order of precedence (highest to lowest):
    1.  Arguments passed directly to the Settings constructor.
    2.  Environment variables (e.g., `API_HOST`).
    3.  Variables loaded from a `.env` file in the project root.
    4.  Default values defined in the Settings class.

    Attributes:
        api_host: The host for the API server. Defaults to "127.0.0.1".
        api_port: The port for the API server. Defaults to 8000.
        database_url: The URL for the database connection. Defaults to "sqlite:///./oal_agent.db".
        queue_url: The URL for the message queue. Defaults to "redis://localhost:6379".
        queue_max_size: The maximum size of the message queue. Defaults to 100.
        llm_provider: The provider for the Large Language Model. Defaults to "openai".
        llm_api_key: The API key for the LLM provider. Defaults to an empty string.
        coordinator_timeout: The timeout in seconds for the coordinator agent's routing. Defaults to 5.
        request_timeout: The timeout in seconds for API requests. Defaults to 15.
        storage_encryption_enabled: Whether to enable at-rest encryption for stored data. Defaults to False.
        evaluation_mode: A boolean indicating whether the agent is running in evaluation mode. Defaults to False.
        max_concurrent_pipelines: The maximum number of analysis pipelines that can run concurrently. Defaults to 10.
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
    coordinator_timeout: int = 5
    request_timeout: int = 15
    storage_encryption_enabled: bool = False
    prometheus_pushgateway_url: str | None = None
    prometheus_pushgateway_job: str = "oal_agent"
    prometheus_pushgateway_enabled: bool = False
    evaluation_mode: bool = False
    max_concurrent_pipelines: int = Field(10, gt=0)

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
