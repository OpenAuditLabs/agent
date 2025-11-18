# Telemetry

Telemetry in the OpenAuditLabs Agent provides insights into the application's behavior, performance, and health. This document outlines how to configure and integrate telemetry, focusing on logging and potential extensions for metrics and tracing.

## Configuration

The agent's telemetry can be configured primarily through environment variables, aligning with the existing configuration patterns. While direct telemetry-specific settings are not yet in `src/oal_agent/core/config.py`, the logging module already respects environment variables.

### Logging Configuration

The `src/oal_agent/telemetry/logging.py` module uses the following environment variables to configure the standard Python logging:

*   `LOG_LEVEL`: Sets the minimum level of messages to log (e.g., `INFO`, `DEBUG`, `WARNING`, `ERROR`). Defaults to `INFO`.
*   `LOG_FORMAT`: Defines the format string for log messages. Defaults to `%(asctime)s - %(levelname)s - %(name)s - %(message)s`.
*   `DATE_FORMAT`: Specifies the date and time format within log messages. Defaults to `%Y-%m-%dT%H:%M:%S%z`.

Example:
```bash
export LOG_LEVEL=DEBUG
export LOG_FORMAT="%(asctime)s [%(process)d] %(name)s - %(levelname)s: %(message)s"
```

### Extending for Metrics and Tracing

For more comprehensive telemetry including metrics and tracing, the OpenTelemetry Python SDK is recommended. Configuration for OpenTelemetry typically involves environment variables as well:

*   `OTEL_SERVICE_NAME`: A logical name for the service (e.g., `oal-agent`).
*   `OTEL_EXPORTER_OTLP_ENDPOINT`: The endpoint of the OTLP collector (e.g., `http://localhost:4317`).
*   `OTEL_RESOURCE_ATTRIBUTES`: Key-value pairs describing the service, e.g., `service.version=1.0.0,deployment.environment=production`.

These would be set in your deployment environment or `.env` file.

## Integration Points in `telemetry/logging.py`

The `src/oal_agent/telemetry/logging.py` module provides a standardized way to configure Python's built-in `logging` module. The `setup_logging()` function, intended to be called once at application startup, configures the root logger.

To integrate with a broader telemetry system like OpenTelemetry, you would typically add an OpenTelemetry `LoggingHandler` to the root logger *after* `setup_logging()` has been called. This allows existing log records to be processed and exported as OpenTelemetry logs.

Example of extending `setup_logging` (conceptual, requires OpenTelemetry SDK installation):

::: danger OpenTelemetry Logs API is Experimental
The OpenTelemetry Logs API and SDK are currently experimental and unstable. Imports from `opentelemetry.sdk._logs` (and other `_logs` submodules) may change in minor or patch releases and could require code updates.

For the latest status and to track breaking changes, please refer to the [official OpenTelemetry Python Logs API documentation](https://opentelemetry.io/docs/instrumentation/python/manual/#logs).
:::

```python
import logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import ConsoleLogExporter, SimpleLogRecordProcessor
from opentelemetry.sdk.resources import Resource

from oal_agent.telemetry.logging import setup_logging, get_logger

def setup_opentelemetry_logging():
    # Configure OpenTelemetry resource
    resource = Resource.create({
        "service.name": "oal-agent",
        "service.instance.id": "instance-1",
    })

    # Create a logger provider
    logger_provider = LoggerProvider(resource=resource)
    
    # Configure a simple console exporter for demonstration
    processor = SimpleLogRecordProcessor(ConsoleLogExporter())
    logger_provider.add_log_record_processor(processor)

    # Attach OpenTelemetry handler to the root Python logger
    handler = LoggingHandler(logger_provider=logger_provider)
    
    # Ensure standard logging is set up first
    setup_logging() 
    
    # Get the root logger and add the OpenTelemetry handler
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    # Set the root logger level to capture all logs for OpenTelemetry
    root_logger.setLevel(logging.DEBUG) 

# Call this function at application startup, e.g., in main.py
# setup_opentelemetry_logging()
```

## Sample Exporter Setup Commands

To set up a basic OpenTelemetry environment for exporting telemetry data, you'll typically need to install the OpenTelemetry SDK and configure an exporter.

### 1. Install OpenTelemetry Python SDK

First, install the necessary OpenTelemetry packages:

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-logging opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-uvicorn opentelemetry-instrumentation-requests
```

### 2. Console Exporter (for local development/debugging)

For quick local verification, you can configure OpenTelemetry to export logs, metrics, and traces to the console.

```bash
# For logs
export OTEL_LOGS_EXPORTER=console

# For traces
export OTEL_TRACES_EXPORTER=console

# For metrics
export OTEL_METRICS_EXPORTER=console

# Run your application
python -m uvicorn oal_agent.app.main:app --host 0.0.0.0 --port 8000
```

You will see telemetry data printed to your console.

### 3. OTLP Exporter (to a Collector like Jaeger or Prometheus)

For production or more robust development environments, you'll typically send telemetry data to an OpenTelemetry Collector using the OTLP (OpenTelemetry Protocol) exporter. The collector can then forward the data to various backends (e.g., Jaeger for traces, Prometheus for metrics, Loki for logs).

Assuming an OpenTelemetry Collector is running at `http://localhost:4317` (default OTLP/gRPC port) or `http://localhost:4318` (default OTLP/HTTP port):

```bash
# Set service name
export OTEL_SERVICE_NAME="oal-agent"

# Configure OTLP exporter endpoint (gRPC example)
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc" # or "http/protobuf" for HTTP

# Enable specific exporters
export OTEL_LOGS_EXPORTER="otlp"
export OTEL_TRACES_EXPORTER="otlp"
export OTEL_METRICS_EXPORTER="otlp"

# Run your application with OpenTelemetry instrumentation
# You might need to use opentelemetry-instrumentation to automatically instrument your application
opentelemetry-instrument python -m uvicorn oal_agent.app.main:app --host 0.0.0.0 --port 8000
```

### Running an OpenTelemetry Collector with Docker

You can easily run an OpenTelemetry Collector with Docker. Here's a `docker-compose.yaml` example that includes a collector and Jaeger for visualization:

```yaml
version: '3.8'
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317" # OTLP gRPC receiver
      - "4318:4318" # OTLP HTTP receiver
      - "8888:8888" # Prometheus metrics exporter
    depends_on:
      - jaeger-all-in-one

  jaeger-all-in-one:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686" # Jaeger UI
      - "14268:14268" # Jaeger gRPC collector
      - "14250:14250" # Jaeger gRPC collector
```

And an `otel-collector-config.yaml` for basic OTLP reception and Jaeger export:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:

exporters:
  jaeger:
    endpoint: jaeger-all-in-one:14250
    tls:
      insecure: true
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [jaeger, logging]
    metrics:
      receivers: [otlp]
      exporters: [logging] # Add prometheus or other metric exporters here
    logs:
      receivers: [otlp]
      exporters: [logging] # Add loki or other log exporters here
```

With these configurations, your agent will send telemetry data to the OpenTelemetry Collector, which then forwards traces to Jaeger for visualization.
