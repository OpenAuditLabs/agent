"""Configuration management."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database
    database_url: str = "sqlite:///./oal_agent.db"

    # Queue
    queue_url: str = "redis://localhost:6379"

    # LLM
    llm_provider: str = "openai"
    llm_api_key: str = ""

    class Config:
        """Pydantic config."""
        env_file = ".env"


settings = Settings()
