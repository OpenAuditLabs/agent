"""FastAPI dependencies."""

import time
from typing import AsyncGenerator, Generator

from oal_agent.telemetry.logging import logger


def get_db() -> Generator:
    """Database dependency."""
    # TODO: Implement database session
    pass


def get_queue() -> Generator:
    """Queue dependency."""
    # TODO: Implement queue connection
    pass


async def get_request_duration() -> AsyncGenerator[None, None]:
    """
    Dependency that records the duration of a request.
    Yields control (None) and logs the request duration as a side effect.
    """
    start_time = time.monotonic()
    try:
        yield
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info("Request duration: %.4f seconds", duration)
