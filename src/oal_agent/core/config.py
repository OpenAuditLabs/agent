"""Configuration management."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    def __init__(self, _env_file: str | None = None, **kwargs: dict[str, any]):
        """
        Initializes the Settings object.

        Args:
            _env_file: Optional path to an environment file.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(_env_file=_env_file, **kwargs)

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
