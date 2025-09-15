# backend/core/mappers/__init__.py
# ==============================================================================
# Public Interface for the Data Mappers Package (v4.0 - Dynamic Import)
# Version: 4.0
# Last Modified: 2025-05-07
# Description:
#   This file constitutes the public API for the 'mappers' package.
#   It uses a dynamic, map-based approach to import and export all primary data mapping functions from
#   provider-specific sub-packages (e.g., yfinance, eodhd).
#
#   This centralized, dynamic system facilitates cleaner, more maintainable imports
#   across services like StockDataService and eliminates manual, error-prone
#   try-except blocks for each provider.
#
#   Key changes in v4.0:
#     - Maintained robust logger initialization and dynamic __all__ list generation.
#
#   Example Usage:
#     from ....core.mappers import map_yfinance_info_to_overview
# ==============================================================================

# --- Standard Library Imports ---
import logging
from typing import Any, Final
from collections.abc import Callable
import importlib

# --- Logger Setup ---
try:
    from ...utils.logger_config import get_logger

    logger = get_logger("aevorex_finbot.core.mappers")
except ImportError:
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger("aevorex_finbot.core.mappers.fallback")
    logger.warning("Using fallback logger for mappers package.")

# --- Dynamic Module and Function Mapping ---
# Defines which functions to import from which sub-module.
# Key: relative module path. Value: list of functions to import.
# Supports 'original_name as alias_name' syntax.
MODULE_MAP: Final[dict[str, list[str]]] = {
    ".alphavantage": [
        "map_alpha_vantage_earnings_to_model",
        "map_alphavantage_item_to_standard",
    ],
    ".eodhd": [
        "map_eodhd_company_info_placeholder_to_overview",
        "map_eodhd_data_to_chart_ready_format",
        "map_eodhd_dividends_data_to_models",
        "map_eodhd_financial_statements_placeholder_to_models",
        "map_eodhd_fx_quote_to_model",
        "map_eodhd_news_data_to_models",
        "map_eodhd_ohlcv_df_to_frontend_list",
        "map_eodhd_ohlcv_to_price_history_entries",
        "map_eodhd_splits_data_to_models",
        "preprocess_ohlcv_dataframe",
    ],
    ".fmp": ["map_fmp_item_to_standard", "map_fmp_raw_ratings_to_rating_points"],
    ".marketaux": ["_map_marketaux_item_to_standard"],
    ".newsapi": ["_map_newsapi_item_to_standard"],
    ".yfinance": [
        "get_latest_financial_values",
        "map_financial_dataframes_to_financials_model",
        "map_yfinance_financial_statement_to_earnings_periods",
        "map_yfinance_info_to_overview",
        "map_yfinance_news_to_standard_dicts",
        "map_yfinance_ohlcv_df_to_chart_list",
        "parse_ts_to_date_str",
    ],
    ".shared": ["map_raw_news_to_standard_dicts", "map_standard_dicts_to_newsitems"],
}

_available_mappers: dict[str, Callable[..., Any]] = {}

logger.info("Initializing mappers package (v4.0)...")

for module_path, func_list in MODULE_MAP.items():
    try:
        module = importlib.import_module(module_path, package=__package__)
        logger.debug(f"Successfully loaded mapper module: '{module_path}'")

        for func_spec in func_list:
            original_name, alias_name = (
                [s.strip() for s in func_spec.split(" as ")]
                if " as " in func_spec
                else (func_spec, func_spec)
            )

            try:
                mapper_func = getattr(module, original_name)
                if callable(mapper_func):
                    globals()[alias_name] = mapper_func
                    _available_mappers[alias_name] = mapper_func
                    logger.debug(f"  -> Exported '{alias_name}' from '{module_path}'")
                else:
                    logger.warning(
                        f"Attribute '{original_name}' in '{module_path}' is not callable."
                    )
            except AttributeError:
                logger.error(
                    f"Function '{original_name}' not found in module '{module_path}'."
                )

    except ImportError as e:
        logger.error(f"Failed to import mapper module '{module_path}': {e}")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred loading mappers from '{module_path}': {e}",
            exc_info=True,
        )


__all__ = sorted(list(_available_mappers.keys()))

logger.info(
    f"Mappers package initialized. Exposed mappers ({len(__all__)}): {', '.join(__all__) if __all__ else 'None'}."
)
