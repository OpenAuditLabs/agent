import logging
import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from src.oal_agent.telemetry.logging import get_logger, setup_logging


@pytest.fixture(autouse=True)
def reset_logging_config():
    """Resets logging configuration before each test to ensure isolation."""
    logging.shutdown()
    # Clear the _configured flag if it exists
    if hasattr(setup_logging, "_configured"):
        del setup_logging._configured
    yield
    logging.shutdown()
    if hasattr(setup_logging, "_configured"):
        del setup_logging._configured


def test_setup_logging_configures_root_logger():
    """Test that setup_logging configures the root logger correctly."""
    with patch.object(sys, "stdout", new_callable=StringIO) as mock_stdout:
        # Ensure a clean slate for handlers before setup_logging
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging()

        assert len(root_logger.handlers) == 1
        handler = root_logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream == mock_stdout
        assert root_logger.level == logging.INFO  # Default level


def test_setup_logging_idempotence():
    """Test that calling setup_logging multiple times does not add duplicate handlers."""
    with patch.object(sys, "stdout", new_callable=StringIO):
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging()
        setup_logging()
        assert len(root_logger.handlers) == 1


def test_get_logger_propagates_to_root(caplog):
    """Test that module loggers propagate messages to the root logger."""
    setup_logging()
    module_logger = get_logger("test_module")

    with caplog.at_level(logging.INFO):
        module_logger.info("Test message")
        assert len(caplog.records) == 1
        assert "Test message" in caplog.text


def test_log_messages_not_duplicated(caplog):
    """Test that log messages are not duplicated when using module and root loggers."""
    setup_logging()
    module_logger = get_logger("test_module")

    with caplog.at_level(logging.INFO):
        module_logger.info("This is a test message.")
        assert len(caplog.records) == 1
        assert "This is a test message." in caplog.text


def test_log_level_updates_from_env_var():
    """Test that LOG_LEVEL environment variable correctly sets the log level."""
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
        setup_logging()
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}):
        # Re-configure to test level update
        if hasattr(setup_logging, "_configured"):
            del setup_logging._configured
        setup_logging()
        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING


def test_get_logger_level_after_setup():
    """Test that a logger retrieved after setup_logging has the correct effective level."""
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
        setup_logging()
        module_logger = get_logger("another_module")
        assert module_logger.getEffectiveLevel() == logging.DEBUG


def test_log_format_from_env_var(caplog):
    """Test that LOG_FORMAT environment variable is respected."""
    custom_format = "CUSTOM: %(message)s"
    with patch.dict(os.environ, {"LOG_FORMAT": custom_format}):
        with patch.object(sys, "stdout", new_callable=StringIO) as mock_stdout:
            # Ensure root logger has no extra handlers from previous tests
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            setup_logging()
            module_logger = get_logger("format_test")

            # Emit a log and assert the StreamHandler output
            module_logger.info("Formatted message")
            output = mock_stdout.getvalue()
            assert "Formatted message" in output
            assert "CUSTOM:" in output


def test_date_format_from_env_var(caplog):
    """Test that DATE_FORMAT environment variable is respected."""
    custom_date_format = "%H:%M:%S"
    with patch.dict(os.environ, {"DATE_FORMAT": custom_date_format}):
        with patch.object(sys, "stdout", new_callable=StringIO) as mock_stdout:
            # Ensure root logger has no extra handlers from previous tests
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            setup_logging()
            module_logger = get_logger("date_format_test")

            # Emit a log and assert the StreamHandler output
            module_logger.info("Date message")
            output = mock_stdout.getvalue()
            assert "Date message" in output
            assert ":" in output  # Check for time separators
            assert "T" not in output  # Ensure default ISO format 'T' is not present
