"""Metrics collection."""

import logging

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from src.oal_agent.core.config import settings

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects application metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: dict[str, float] = {}
        self.high_water_marks: dict[str, float] = {}

    def increment(self, metric: str, value: int = 1):
        """Increment a metric."""
        if metric not in self.metrics:
            self.metrics[metric] = 0
        self.metrics[metric] += value

    def gauge(self, metric: str, value: float):
        """Set a gauge metric."""
        self.metrics[metric] = value
        if metric not in self.high_water_marks or value > self.high_water_marks[metric]:
            self.high_water_marks[metric] = value

    def get_metrics(self):
        """Get all metrics."""
        return self.metrics

    def get_high_water_mark(self, metric: str) -> float:
        """Get the high-water mark for a specific metric."""
        return self.high_water_marks.get(metric, 0.0)

    def push_metrics_to_prometheus(self):
        """Pushes collected metrics to Prometheus Pushgateway if enabled."""
        if (
            not settings.prometheus_pushgateway_enabled
            or not settings.prometheus_pushgateway_url
        ):
            return

        registry = CollectorRegistry()
        for metric_name, value in self.metrics.items():
            g = Gauge(
                metric_name, f"Application metric: {metric_name}", registry=registry
            )
            g.set(value)

        try:
            push_to_gateway(
                gateway=settings.prometheus_pushgateway_url,
                job=settings.prometheus_pushgateway_job,
                registry=registry,
            )
            logger.info(
                f"Metrics pushed to Prometheus Pushgateway at {settings.prometheus_pushgateway_url}"
            )
        except Exception:
            logger.exception("Failed to push metrics to Prometheus Pushgateway")


metrics = MetricsCollector()
