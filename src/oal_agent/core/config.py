"""Configuration management."""

from typing import Union

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    def __init__(self, _env_file: Union[str, None] = None):
        """
        Initializes the Settings object.

        Args:
            _env_file: Optional path to an environment file.
        """
        super().__init__(_env_file=_env_file)

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database
    database_url: str = "sqlite:///./oal_agent.db"

    # Queue
    queue_url: str = "redis://localhost:6379"
    queue_max_size: int = 100

    # LLM
    llm_provider: str = "openai"
    llm_api_key: str = ""

    class Config:
        """Pydantic config."""

        env_file = ".env"


settings = Settings()
