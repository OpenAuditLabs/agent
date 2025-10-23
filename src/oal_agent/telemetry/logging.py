"""Standardized logging configuration for human and machine readability."""

import logging
import os
import sys

DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def get_logger(name: str) -> logging.Logger:
    """
    Returns a module-scoped logger with a consistent format.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Prevent adding multiple handlers if the logger is retrieved multiple times
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            os.getenv("LOG_FORMAT", DEFAULT_LOG_FORMAT),
            datefmt=DEFAULT_DATE_FORMAT,
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    return logger


def setup_logging(level: str = "INFO"):
    """
    Configures the root logger with a basic setup.
    This is primarily for compatibility or simple scripts.
    For module-specific logging, use `get_logger(__name__)`.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=os.getenv("LOG_FORMAT", DEFAULT_LOG_FORMAT),
        datefmt=DEFAULT_DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )


logger = get_logger("oal_agent")
