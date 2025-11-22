"""Standardized logging configuration for human and machine readability."""

import logging
import os
import sys
import contextvars
import uuid

DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(request_id)s - %(correlation_id)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

request_id_ctx = contextvars.ContextVar("request_id", default=None)
correlation_id_ctx = contextvars.ContextVar("correlation_id", default=None)

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get() or "no-request-id"
        record.correlation_id = correlation_id_ctx.get() or "no-correlation-id"
        return True


def get_logger(name: str) -> logging.Logger:
    """Returns a module-scoped logger that propagates to the root logger. Call setup_logging() once at application startup to configure the root logger."""
    return logging.getLogger(name)


def setup_logging():
    """
    Configures the root logger with a single StreamHandler and Formatter.
    This function is idempotent and should be called once at application startup.
    """
    root = logging.getLogger()
    if getattr(setup_logging, "_configured", False):
        # Optionally update level if already configured
        root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIDFilter())
    formatter = logging.Formatter(
        os.getenv("LOG_FORMAT", DEFAULT_LOG_FORMAT),
        datefmt=os.getenv("DATE_FORMAT", DEFAULT_DATE_FORMAT),
    )
    handler.setFormatter(formatter)

    # Replace existing handlers to avoid duplicates
    # Remove existing StreamHandlers that write to sys.stdout to avoid duplicates
    for h in root.handlers[:]:
        if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout:
            root.removeHandler(h)

    root.addHandler(handler)
    root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    setup_logging._configured = True


logger = get_logger("oal_agent")
