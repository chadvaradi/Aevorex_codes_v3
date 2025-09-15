"""
ECB Special Fetchers Package
============================

Contains complex ECB fetchers that require custom business logic
beyond the standard generic fetcher approach.
"""

# Import all special fetchers for easy access
from .bubor_client import *
from .euribor_client import *
from .euribor_scraper import *
from .fed_yield_curve import *
from .fm_fetcher import *
from .fx_rates_fetcher import *
from .policy_rates_fetcher import *
from .yc_fetcher import *
from .dbnomics_client import *

# Export all special fetchers
__all__ = [
    # From bubor_client
    "fetch_bubor_curve",
    # From euribor_client
    "fetch_official_euribor_rates",
    "get_latest_euribor_rates",
    # From euribor_scraper
    # "get_euribor_from_website",  # Function not defined
    # From fed_yield_curve
    # "fetch_fed_yield_curve",  # Function not defined
    # "get_fed_rates",  # Function not defined
    # From fm_fetcher
    # "fetch_financial_markets_data",  # Function not defined
    # "get_policy_rates",  # Function not defined
    # From fx_rates_fetcher
    "fetch_fx_rates",
    "fetch_single_fx_rate",
    # "get_fx_rates",  # Function not defined
    # From policy_rates_fetcher
    "fetch_policy_rates",
    "fetch_single_policy_rate",
    # From yc_fetcher
    "fetch_yield_curve_rates",
    "fetch_single_yield_rate",
    # "get_yield_curve_data",  # Function not defined
    # From dbnomics_client
    # "fetch_dbnomics_data",  # Function not defined
    # "get_dbnomics_series",  # Function not defined
]
