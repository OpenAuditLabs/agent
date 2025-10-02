"""Timing utilities."""

import time
from contextlib import contextmanager


@contextmanager
def timer(name: str):
    """Context manager for timing operations."""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        print(f"{name} took {duration:.2f} seconds")


def timestamp() -> float:
    """Get current timestamp."""
    return time.time()
