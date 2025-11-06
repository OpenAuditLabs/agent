"""FastAPI dependencies."""

import time
from typing import Generator

from oal_agent.telemetry.logging import logger


def get_db() -> Generator:
    """Database dependency."""
    # TODO: Implement database session
    pass


def get_queue() -> Generator:
    """Queue dependency."""
    # TODO: Implement queue connection
    pass


async def get_request_duration() -> Generator[float, None, None]:
    """
    Dependency that records the duration of a request.
    Yields the duration in seconds.
    """
    start_time = time.monotonic()
    try:
        yield
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info("Request duration: %.4f seconds", duration)
