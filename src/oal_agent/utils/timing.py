"""Timing utilities."""

import logging
import time
from contextlib import contextmanager

from src.oal_agent.utils.logging_utils import setup_logger

logger = setup_logger(__name__)


@contextmanager
def timer(name: str, level: int = logging.INFO):
    """Context manager for timing operations.

    Args:
        name: The name of the operation being timed.
        level: The logging level to use for the duration message (e.g., logging.INFO, logging.DEBUG).
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        logger.log(level, f"{name} took {duration:.4f} seconds")


def timestamp() -> float:
    """Get current timestamp."""
    return time.time()
