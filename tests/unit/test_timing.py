import logging
from unittest.mock import patch

from src.oal_agent.utils.timing import timer


def test_timer_logs_duration_at_info_level():
    with patch("src.oal_agent.utils.timing.logger") as mock_logger:
        with timer("test_operation"):
            pass
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.INFO
        assert "test_operation took" in args[1]
        assert "seconds" in args[1]


def test_timer_logs_duration_at_debug_level():
    with patch("src.oal_agent.utils.timing.logger") as mock_logger:
        with timer("debug_operation", level=logging.DEBUG):
            pass
        mock_logger.log.assert_called_once()
        args, kwargs = mock_logger.log.call_args
        assert args[0] == logging.DEBUG
        assert "debug_operation took" in args[1]
        assert "seconds" in args[1]


def test_timer_measures_time_correctly():
    with patch("src.oal_agent.utils.timing.time") as mock_time:
        with patch("src.oal_agent.utils.timing.logger") as mock_logger:

            mock_time.perf_counter.side_effect = [0, 1.234]

            with timer("measured_operation"):
                pass

            mock_logger.log.assert_called_once()
            args, kwargs = mock_logger.log.call_args
            assert args[0] == logging.INFO
            assert "measured_operation took 1.2340 seconds" in args[1]
