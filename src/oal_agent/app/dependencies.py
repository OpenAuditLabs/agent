"""FastAPI dependencies."""

from typing import Generator


def get_db() -> Generator:
    """Database dependency."""
    # TODO: Implement database session
    pass


def get_queue() -> Generator:
    """Queue dependency."""
    # TODO: Implement queue connection
    pass
