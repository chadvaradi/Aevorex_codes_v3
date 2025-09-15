# backend/core.ppers/eodhd/__init__.py
# ==============================================================================
# Barrel file for the EODHD mappers package.
# This makes the individual, specialized mappers available under a single namespace.
# ==============================================================================

# --- Import public-facing mapper functions from sub-modules ---
from backend.core.mappers.eodhd.price import (
    map_eodhd_ohlcv_to_price_history_entries,
    map_eodhd_ohlcv_df_to_frontend_list,
    map_eodhd_data_to_chart_ready_format,
)
from backend.core.mappers.eodhd.splits import map_eodhd_splits_data_to_models
from backend.core.mappers.eodhd.dividends import map_eodhd_dividends_data_to_models
from backend.core.mappers.eodhd.news import map_eodhd_news_data_to_models
from backend.core.mappers.eodhd.financials import (
    map_eodhd_company_info_placeholder_to_overview,
    map_eodhd_financial_statements_placeholder_to_models,
)
from backend.core.mappers.mappers.eodhd.forex_mapper import map_eodhd_fx_quote_to_model
from backend.core.mappers.mappers.eodhd.helpers import (
    preprocess_ohlcv_dataframe,
)  # Expose helper if it's used externally

# --- Define the public API of the package ---
__all__ = [
    # OHLCV Mappers
    "map_eodhd_ohlcv_to_price_history_entries",
    "map_eodhd_ohlcv_df_to_frontend_list",
    # Corporate Events Mappers
    "map_eodhd_splits_data_to_models",
    "map_eodhd_dividends_data_to_models",
    # News Mapper
    "map_eodhd_news_data_to_models",
    # Fundamental Data Placeholder Mappers
    "map_eodhd_company_info_placeholder_to_overview",
    "map_eodhd_financial_statements_placeholder_to_models",
    # Forex Mapper
    "map_eodhd_fx_quote_to_model",
    # High-level Orchestrator
    "map_eodhd_data_to_chart_ready_format",
    # Shared Helpers (optional, if needed by other parts of the app)
    "preprocess_ohlcv_dataframe",
]
