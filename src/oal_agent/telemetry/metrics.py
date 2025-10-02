"""Metrics collection."""


class MetricsCollector:
    """Collects application metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {}

    def increment(self, metric: str, value: int = 1):
        """Increment a metric."""
        if metric not in self.metrics:
            self.metrics[metric] = 0
        self.metrics[metric] += value

    def gauge(self, metric: str, value: float):
        """Set a gauge metric."""
        self.metrics[metric] = value

    def get_metrics(self):
        """Get all metrics."""
        return self.metrics


metrics = MetricsCollector()
