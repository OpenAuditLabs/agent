"""Metrics collection."""


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


metrics = MetricsCollector()
