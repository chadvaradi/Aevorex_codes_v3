# backend/core.ppers/eodhd/forex_mapper.py
# ==============================================================================
# Mappers for EODHD Forex (FX) data.
# ==============================================================================
from typing import TYPE_CHECKING
import logging

from backend.models.stock import ForexQuote

if TYPE_CHECKING:
    pass


def map_eodhd_fx_quote_to_model(api_response: dict) -> "ForexQuote | None":
    """Convert raw EODHD FX quote JSON to ForexQuote model."""
    try:
        symbol = api_response.get("code") or api_response.get("symbol")
        if not symbol or len(symbol) != 6:
            return None

        price_val = api_response.get("close") or api_response.get("price")
        if price_val is None:
            return None
        price = float(price_val)

        prev_close_val = api_response.get("previousClose")
        if prev_close_val is None:
            prev_close = price
        else:
            prev_close = float(prev_close_val)

        change = price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close else 0.0

        return ForexQuote(
            symbol=symbol.upper(),
            price=price,
            change=change,
            change_percent=change_percent,
        )
    except Exception as exc:
        logging.getLogger(__name__).warning("Failed to map FX quote: %s", exc)
        return None
