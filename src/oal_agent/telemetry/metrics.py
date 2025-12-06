"""Metrics collection."""

import logging

from opentelemetry import metrics as otel_metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway, generate_latest

from src.oal_agent.core.config import settings

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects application metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: dict[str, float] = {}
        self.high_water_marks: dict[str, float] = {}

        self.meter = None
        if settings.otlp_metrics_endpoint:
            resource = Resource.create({SERVICE_NAME: "oal-agent"})
            reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=settings.otlp_metrics_endpoint)
            )
            provider = MeterProvider(resource=resource, metric_readers=[reader])
            otel_metrics.set_meter_provider(provider)
            self.meter = otel_metrics.get_meter(__name__)
            logger.info(
                f"OpenTelemetry metrics initialized with OTLP endpoint: {settings.otlp_metrics_endpoint}"
            )
        else:
            logger.info("OpenTelemetry metrics not enabled.")

        if self.meter:
            self.otlp_gauge_metrics = {}
            self.otlp_counter_metrics = {}

    def increment(self, metric: str, value: int = 1):
        """Increment a metric."""
        if metric not in self.metrics:
            self.metrics[metric] = 0
        self.metrics[metric] += value

        if self.meter:
            if metric not in self.otlp_counter_metrics:
                self.otlp_counter_metrics[metric] = self.meter.create_counter(
                    metric,
                    description=f"Application counter metric: {metric}",
                )
            self.otlp_counter_metrics[metric].add(value)

    def gauge(self, metric: str, value: float):
        """Set a gauge metric."""
        self.metrics[metric] = value
        if metric not in self.high_water_marks or value > self.high_water_marks[metric]:
            self.high_water_marks[metric] = value

        if self.meter:
            if metric not in self.otlp_gauge_metrics:
                self.otlp_gauge_metrics[metric] = self.meter.create_up_down_counter(
                    metric,
                    description=f"Application gauge metric: {metric}",
                )
            # Calculate the delta since the last recorded value
            previous_value = self.metrics.get(metric, 0.0)
            delta = value - previous_value
            self.otlp_gauge_metrics[metric].add(delta)
            self.metrics[metric] = value

    def get_metrics(self):
        """Get all metrics."""
        return self.metrics

    def get_high_water_mark(self, metric: str) -> float:
        """Get the high-water mark for a specific metric."""
        return self.high_water_marks.get(metric, 0.0)

    def _build_metrics_registry(self) -> CollectorRegistry:
        """Builds and populates a Prometheus CollectorRegistry with current metrics."""
        registry = CollectorRegistry()
        for metric_name, value in self.metrics.items():
            g = Gauge(
                metric_name, f"Application metric: {metric_name}", registry=registry
            )
            g.set(value)
        return registry

    def push_metrics_to_prometheus(self):
        """Pushes collected metrics to Prometheus Pushgateway if enabled."""
        if (
            not settings.prometheus_pushgateway_enabled
            or not settings.prometheus_pushgateway_url
        ):
            return

        registry = self._build_metrics_registry()

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

    def generate_prometheus_metrics(self) -> bytes:
        """Generates Prometheus-format metrics.

        Returns:
            bytes: The metrics in Prometheus text format.
        """
        registry = self._build_metrics_registry()
        return generate_latest(registry)


metrics = MetricsCollector()
