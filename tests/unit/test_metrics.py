from unittest.mock import patch

import pytest

from src.oal_agent.core.config import reset_settings, settings
from src.oal_agent.telemetry.metrics import MetricsCollector


@pytest.fixture(autouse=True)
def run_around_tests():
    """Resets settings before and after each test to ensure isolation."""
    reset_settings()
    yield
    reset_settings()


def test_metrics_collector_increment():
    collector = MetricsCollector()
    collector.increment("test_metric")
    assert collector.get_metrics() == {"test_metric": 1}
    collector.increment("test_metric", 5)
    assert collector.get_metrics() == {"test_metric": 6}


def test_metrics_collector_gauge():
    collector = MetricsCollector()
    collector.gauge("test_gauge", 10.5)
    assert collector.get_metrics() == {"test_gauge": 10.5}
    collector.gauge("test_gauge", 5.2)
    assert collector.get_metrics() == {"test_gauge": 5.2}


def test_metrics_collector_high_water_mark():
    collector = MetricsCollector()
    collector.gauge("test_hwm", 10.0)
    assert collector.get_high_water_mark("test_hwm") == 10.0
    collector.gauge("test_hwm", 20.0)
    assert collector.get_high_water_mark("test_hwm") == 20.0
    collector.gauge("test_hwm", 15.0)
    assert collector.get_high_water_mark("test_hwm") == 20.0


@patch("src.oal_agent.telemetry.metrics.push_to_gateway")
def test_push_metrics_to_prometheus_enabled(mock_push_to_gateway):
    settings.prometheus_pushgateway_enabled = True
    settings.prometheus_pushgateway_url = "http://localhost:9091"
    settings.prometheus_pushgateway_job = "test_job"

    collector = MetricsCollector()
    collector.increment("test_counter", 3)
    collector.gauge("test_gauge", 15.0)

    collector.push_metrics_to_prometheus()

    mock_push_to_gateway.assert_called_once()
    args, kwargs = mock_push_to_gateway.call_args
    assert kwargs["gateway"] == "http://localhost:9091"
    assert kwargs["job"] == "test_job"
    assert "registry" in kwargs


@patch("src.oal_agent.telemetry.metrics.push_to_gateway")
def test_push_metrics_to_prometheus_disabled(mock_push_to_gateway):
    settings.prometheus_pushgateway_enabled = False
    settings.prometheus_pushgateway_url = "http://localhost:9091"

    collector = MetricsCollector()
    collector.increment("test_counter", 3)

    collector.push_metrics_to_prometheus()

    mock_push_to_gateway.assert_not_called()


@patch("src.oal_agent.telemetry.metrics.push_to_gateway")
def test_push_metrics_to_prometheus_no_url(mock_push_to_gateway):
    settings.prometheus_pushgateway_enabled = True
    settings.prometheus_pushgateway_url = None

    collector = MetricsCollector()
    collector.increment("test_counter", 3)

    collector.push_metrics_to_prometheus()

    mock_push_to_gateway.assert_not_called()
