"""Macro service subpackage – holds base_service and fetch_mixins."""

__all__ = [
    "BaseMacroService",
    "ECBStandardMixin",
]

from .base_service import BaseMacroService
from .fetch_mixins import ECBStandardMixin

# Special services for complex ECB endpoints
from .specials import *

__all__.extend(
    [
        # Special services (imported from specials/__init__.py)
        "build_bop_response",
        "build_comprehensive_response",
        "build_fx_response",
        "build_rates_response",
        "build_rates_extended_response",
        "build_sts_response",
        "build_yield_curve_response",
    ]
)
