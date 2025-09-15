"""
ECB Client Package
==================

Public API exports for all ECB fetchers.
"""

from .client import ECBSDMXClient
from .fetchers import (
    fetch_ecb_policy_rates,
    fetch_ecb_yield_curve,
    fetch_ecb_fx_rates,
    fetch_ecb_comprehensive_data,
    fetch_ecb_bop_data,
    fetch_ecb_sts_data,
)
from .config import ECB_DATAFLOWS, COMPREHENSIVE_ECB_SERIES
from .exceptions import ECBAPIError, ECBDataParsingError

# Import all standard fetchers from consolidated module
from .standard_fetchers import *  # noqa: F401, F403

# Import all special fetchers from specials package
from .specials import *  # noqa: F401, F403

__all__ = [
    "ECBSDMXClient",
    "fetch_ecb_policy_rates",
    "fetch_ecb_yield_curve",
    "fetch_ecb_fx_rates",
    "fetch_ecb_comprehensive_data",
    "fetch_ecb_bop_data",
    "fetch_ecb_sts_data",
    "ECB_DATAFLOWS",
    "COMPREHENSIVE_ECB_SERIES",
    "ECBAPIError",
    "ECBDataParsingError",
]

# All standard and special fetchers are now imported via wildcard imports
# and automatically included in __all__ via their respective modules

__version__ = "1.0.0"
