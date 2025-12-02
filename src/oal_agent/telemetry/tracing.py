"""Distributed tracing."""

import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.oal_agent.core.config import settings

logger = logging.getLogger(__name__)


class Tracer:
    """Distributed tracing implementation."""

    def __init__(self):
        """Initialize tracer."""
        self.tracer = None
        if settings.otlp_trace_endpoint:
            resource = Resource.create({SERVICE_NAME: "oal-agent"})
            provider = TracerProvider(resource=resource)
            processor = BatchSpanProcessor(
                OTLPSpanExporter(endpoint=settings.otlp_trace_endpoint)
            )
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
            self.tracer = trace.get_tracer(__name__)
            logger.info(
                f"OpenTelemetry tracing initialized with OTLP endpoint: {settings.otlp_trace_endpoint}"
            )
        else:
            logger.info("OpenTelemetry tracing not enabled.")

    def start_span(self, name: str, attributes: dict | None = None):
        """Start a new trace span."""
        if self.tracer:
            if attributes:
                return self.tracer.start_as_current_span(name, attributes=attributes)
            else:
                return self.tracer.start_as_current_span(name)
        return DummySpan()

    def end_span(self):
        """End current span."""
        # Spans created with start_as_current_span are ended automatically
        # when exiting the context manager.
        pass


class DummySpan:
    """A dummy span that does nothing."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def set_attribute(self, key, value):
        pass


tracer = Tracer()