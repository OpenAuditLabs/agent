"""Standardized logging configuration for human and machine readability."""

import logging
import os
import sys


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    log_format = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


logger = logging.getLogger("oal_agent")
