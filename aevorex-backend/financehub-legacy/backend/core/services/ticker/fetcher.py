"""
This module is responsible for fetching and parsing raw data for the ticker tape
from various external API providers.
"""

import httpx
from typing import Any
import os
import asyncio

# Optional import of yfinance – only used if YF fallback is selected.
try:
    import yfinance as yf  # type: ignore
except ModuleNotFoundError:
    yf = None  # Will check at runtime

from backend.config import settings
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)
MODULE_PREFIX = "[TickerTape Fetcher]"

# --- API Response Parsers ---
# These functions are kept here as they are tightly coupled with the API endpoints defined in API_CONFIG.


def parse_fmp_quote_response(
    api_response_data: Any, symbol: str
) -> dict[str, Any] | None:
    log_prefix = f"{MODULE_PREFIX} [ParseFMP:{symbol}]"
    if not isinstance(api_response_data, list) or not api_response_data:
        logger.warning(
            f"{log_prefix} Unexpected API response format (expected non-empty list)."
        )
        return None
    quote_data = api_response_data[0]
    if not isinstance(quote_data, dict):
        return None
    current_price_str = quote_data.get("price")
    change_str = quote_data.get("change")
    change_percent_str = quote_data.get("changesPercentage")
    if current_price_str is None or change_str is None or change_percent_str is None:
        return None
    try:
        current_price = float(current_price_str)
        change = float(change_str)
        change_percent = float(change_percent_str)
    except (ValueError, TypeError):
        return None
    return {
        "symbol": symbol,
        "price": round(current_price, 4),
        "change": round(change, 4),
        "change_percent": round(change_percent, 2),
    }


def parse_alpha_vantage_quote_response(
    api_response_data: Any, symbol: str
) -> dict[str, Any] | None:
    log_prefix = f"{MODULE_PREFIX} [ParseAV:{symbol}]"
    if not isinstance(api_response_data, dict):
        return None
    quote_data = api_response_data.get("Global Quote")
    if not quote_data or not isinstance(quote_data, dict):
        return None
    symbol_api = quote_data.get("01. symbol")
    current_price_str = quote_data.get("05. price")
    change_str = quote_data.get("09. change")
    change_percent_str = quote_data.get("10. change percent")
    if symbol_api != symbol:
        logger.warning(
            f"{log_prefix} Mismatched symbol. Expected '{symbol}', got '{symbol_api}'."
        )
    if current_price_str is None or change_str is None or change_percent_str is None:
        return None
    try:
        current_price = float(current_price_str)
        change = float(change_str)
        change_percent = float(change_percent_str.rstrip("%"))
    except (ValueError, TypeError, AttributeError):
        return None
    return {
        "symbol": symbol,
        "price": round(current_price, 4),
        "change": round(change, 4),
        "change_percent": round(change_percent, 2),
    }


def parse_eodhd_realtime_response(
    api_response_data: Any, full_symbol: str
) -> dict[str, Any] | None:
    log_prefix = f"{MODULE_PREFIX} [ParseEODHD:{full_symbol}]"
    if isinstance(api_response_data, dict):
        try:
            current_price = float(api_response_data.get("close"))
            change = float(api_response_data.get("change"))
            change_percent = float(api_response_data.get("change_p"))
            return {
                "symbol": full_symbol,
                "price": round(current_price, 4),
                "change": round(change, 4),
                "change_percent": round(change_percent, 2),
            }
        except (ValueError, TypeError, KeyError):
            return None
    return None


# --- API Configuration ---
API_CONFIG = {
    "FMP": {
        "endpoint_template": "https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}",
        "api_key_getter": lambda: settings.API_KEYS.FMP.get_secret_value()
        if settings.API_KEYS.FMP
        else None,
        "response_parser": parse_fmp_quote_response,
    },
    "ALPHA_VANTAGE": {
        "endpoint_template": "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}",
        "api_key_getter": lambda: settings.API_KEYS.ALPHA_VANTAGE.get_secret_value()
        if settings.API_KEYS.ALPHA_VANTAGE
        else None,
        "response_parser": parse_alpha_vantage_quote_response,
    },
    "EODHD": {
        "endpoint_template": "https://eodhistoricaldata.com/api/real-time/{symbol}?api_token={api_key}&fmt=json",
        # Try nested env var first (double underscore), then flat, then Settings-based value
        "api_key_getter": lambda: (
            os.getenv("FINBOT_API_KEYS__EODHD")
            or os.getenv("FINBOT_API_KEYS_EODHD")
            or (
                settings.API_KEYS.EODHD.get_secret_value()
                if getattr(settings.API_KEYS, "EODHD", None)
                else None
            )
        ),
        "response_parser": parse_eodhd_realtime_response,
    },
    # ------------------------------------------------------------------
    # YF – Key-less Yahoo Finance fallback provider (read-only)
    # ------------------------------------------------------------------
    "YF": {
        # Local provider – no external endpoint template required. The fetcher
        # will invoke the yfinance Python package directly.
        "endpoint_template": None,
        "api_key_getter": lambda: "",  # Always available (no key)
        "response_parser": None,  # Will be handled inline
    },
}

# -----------------------------------------------------------------------
# Helper for YF key-less provider
# -----------------------------------------------------------------------


def _fetch_yf_quote_sync(symbol: str) -> dict[str, Any] | None:
    """Synchronous helper that fetches a single ticker quote via yfinance.

    Returns dict with symbol, price, change, change_percent or None on failure.
    """
    if yf is None:
        logger.error(
            f"{MODULE_PREFIX} yfinance package missing – cannot use YF provider."
        )
        return None
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info  # fast_info is lightweight (~<200ms)
        price = info.get("last_price") or info.get("regularMarketPrice")
        prev_close = info.get("previous_close") or info.get(
            "regularMarketPreviousClose"
        )
        if price is None or prev_close is None:
            return None
        price_f = float(price)
        prev_f = float(prev_close)
        change = price_f - prev_f
        change_percent = (change / prev_f) * 100 if prev_f else 0.0
        return {
            "symbol": symbol,
            "price": round(price_f, 4),
            "change": round(change, 4),
            "change_percent": round(change_percent, 2),
        }
    except Exception as exc:
        logger.warning(f"{MODULE_PREFIX} YF fetch failed for {symbol}: {exc}")
        return None


# --- Utility Functions ---
def normalize_symbol_for_provider(symbol: str, provider: str) -> str:
    """
    Normalize symbol for different providers to handle FX, crypto, commodities, and futures.
    """
    if provider == "EODHD":
        # Handle index symbols (^GSPC, etc.)
        if symbol.startswith("^"):
            return symbol

        # Handle futures (ES=F, NQ=F, etc.)
        if symbol.endswith("=F"):
            return symbol

        # Handle forex (EURUSD=X, USDJPY=X, etc.)
        if symbol.endswith("=X"):
            return symbol

        # Handle crypto (BTC-USD, ETH-USD, etc.)
        if "-USD" in symbol:
            return symbol

        # Handle regular stocks - add .US suffix if no exchange specified
        if (
            "." not in symbol
            and not symbol.startswith("^")
            and "=" not in symbol
            and "-" not in symbol
        ):
            return f"{symbol}.US"

        return symbol

    # For other providers, return as-is for now
    return symbol


def get_original_symbol(full_symbol: str, provider: str) -> str:
    if provider == "EODHD":
        if full_symbol.endswith(".US"):
            return full_symbol[:-3]
    return full_symbol


# --- Main Fetcher Function ---
async def fetch_single_ticker_quote(
    symbol: str, client: httpx.AsyncClient, provider_config: dict[str, Any]
) -> dict[str, Any] | None:
    """Unified fetcher that supports both HTTP-based and local providers."""
    log_prefix = f"{MODULE_PREFIX} [Fetch:{symbol}]"

    # Local YF provider – handled without HTTP request
    if provider_config is API_CONFIG.get("YF"):
        return await asyncio.to_thread(_fetch_yf_quote_sync, symbol)

    # HTTP-based providers (FMP, AV, EODHD)
    api_key_getter = provider_config.get("api_key_getter")
    api_key = api_key_getter() if api_key_getter else None
    if not api_key:
        logger.error(f"{log_prefix} API key is missing for provider.")
        return None

    endpoint_template = provider_config.get("endpoint_template")
    if not endpoint_template:
        logger.error(f"{log_prefix} No endpoint template defined for provider.")
        return None

    url = endpoint_template.format(symbol=symbol, api_key=api_key)
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        parser = provider_config.get("response_parser")
        if parser:
            parsed = parser(data, symbol)
            if parsed is None:
                logger.warning(
                    f"{log_prefix} Failed to parse response from provider – attempting YF fallback…"
                )
                # Symbol-level graceful degradation: Attempt Yahoo Finance as secondary source.
                if API_CONFIG.get("YF")["response_parser"] is None:
                    # yfinance path
                    return await asyncio.to_thread(_fetch_yf_quote_sync, symbol)
                return None
            return parsed
    except httpx.RequestError as req_err:
        logger.warning(f"{log_prefix} Request failed for {url}. Error: {req_err}")
        return None
    except Exception as exc:
        logger.error(
            f"{log_prefix} An unexpected error occurred. Error: {exc}. Attempting YF fallback…"
        )
        return await asyncio.to_thread(_fetch_yf_quote_sync, symbol)
