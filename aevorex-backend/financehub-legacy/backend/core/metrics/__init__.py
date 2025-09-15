# Import the prometheus exporter components
from .prometheus_exporter import get_metrics_router, PrometheusExporter

# Global instance of the exporter to be used across the application
METRICS_EXPORTER = PrometheusExporter()

# Export the main components
__all__ = ["METRICS_EXPORTER", "get_metrics_router", "PrometheusExporter"]
