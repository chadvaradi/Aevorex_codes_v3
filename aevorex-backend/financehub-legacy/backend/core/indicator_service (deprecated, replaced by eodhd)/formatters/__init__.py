"""
Indicator Formatters Module

This package contains modularized formatting functions for various technical indicators.
The `__all__` variable ensures that these functions are easily importable
from the `core.indicator_service.formatters` namespace.
"""

from .simple import format_simple_series
from .volume import format_volume_series
from .macd import format_macd_hist_series
from .stoch import format_stoch_series

__all__ = [
    "format_simple_series",
    "format_volume_series",
    "format_macd_hist_series",
    "format_stoch_series",
]
