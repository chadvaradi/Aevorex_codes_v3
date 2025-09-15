"""
Ticker Tape Settings - EODHD Only
=================================

Simplified ticker tape configuration for EODHD-only provider.
No caching, no FMP fallback - direct EODHD integration.
"""

from typing import Any
from pydantic import field_validator, BaseModel, Field
from pydantic.types import PositiveInt

from ._core import _parse_env_list_str_utility


class TickerTapeSettings(BaseModel):
    """Ticker tape settings for EODHD-only provider."""

    # Provider settings
    provider: str = Field(default="EODHD", description="Data provider (EODHD only)")
    
    # Default symbols for ticker tape
    SYMBOLS: list[str] = Field(
        default_factory=lambda: [
            "AAPL",
            "MSFT", 
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "NFLX",
            "AMD",
            "INTC",
            "BTC-USD",
            "ETH-USD"
        ],
        description="Default ticker symbols for ticker tape"
    )
    
    # Request limits
    max_symbols: int = Field(default=50, description="Maximum number of symbols per request")
    default_limit: int = Field(default=20, description="Default number of symbols to return")
    
    # Update interval (for background tasks if needed)
    update_interval_seconds: PositiveInt = Field(default=60, description="Update interval for background tasks")

    @field_validator("SYMBOLS", mode="before")
    @classmethod
    def _parse_symbols_list(cls, v: Any) -> list[str]:
        return _parse_env_list_str_utility(v, "TICKER_TAPE_SYMBOLS")