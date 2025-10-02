"""Environment utilities."""

import os


def get_env(key: str, default: str = None) -> str:
    """Get environment variable."""
    return os.getenv(key, default)


def require_env(key: str) -> str:
    """Get required environment variable."""
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value
