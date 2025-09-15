"""
Ticker Tape Service - EODHD Only (Simplified)
============================================

Simplified ticker tape service using only EODHD API.
No caching, no FMP fallback - direct EODHD integration for MVP.
"""

import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.config.eodhd import settings as eodhd_settings
from backend.utils.logger_config import get_logger
from .services.trading_hours_service import TradingHoursService

logger = get_logger(__name__)
MODULE_PREFIX = "[TickerTape Service]"

# Default ticker symbols for ticker tape
DEFAULT_TICKER_SYMBOLS = [
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
]

def _get_exchange_from_symbol(symbol: str) -> str:
    """Determine exchange from symbol format."""
    if symbol.endswith('.US') or symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA']:
        return 'US'
    elif symbol.endswith('.L') or symbol.endswith('.LSE'):
        return 'LSE'
    elif symbol.endswith('.TO') or symbol.endswith('.TSE'):
        return 'TO'
    elif 'BTC' in symbol.upper() or 'ETH' in symbol.upper() or 'USD' in symbol.upper():
        return 'CRYPTO'
    else:
        return 'US'

def _enhance_ticker_with_trading_hours(ticker_data: dict) -> dict:
    """Enhance ticker data with trading hours information."""
    if not ticker_data or not isinstance(ticker_data, dict):
        return ticker_data
    
    symbol = ticker_data.get('symbol', '')
    exchange = _get_exchange_from_symbol(symbol)
    
    # Skip crypto symbols
    if exchange == 'CRYPTO':
        ticker_data['market_status'] = {
            'is_open': True,
            'session_type': 'crypto',
            'exchange': 'CRYPTO',
            'timezone': 'UTC'
        }
        return ticker_data
    
    try:
        market_status = TradingHoursService.get_market_status(exchange)
        ticker_data['market_status'] = market_status
    except Exception as e:
        logger.warning(f"{MODULE_PREFIX} Failed to get trading hours for {symbol}: {e}")
        ticker_data['market_status'] = {
            'is_open': None,
            'session_type': 'unknown',
            'exchange': exchange,
            'error': str(e)
        }
    
    return ticker_data

async def fetch_single_ticker_from_eodhd(
    symbol: str, 
    client: httpx.AsyncClient
) -> Optional[Dict[str, Any]]:
    """Fetch single ticker data from EODHD API."""
    try:
        # EODHD real-time endpoint
        url = f"https://eodhd.com/api/real-time/{symbol}"
        params = {
            "api_token": eodhd_settings.API_KEY,
            "fmt": "json"
        }
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or not isinstance(data, dict):
            logger.warning(f"{MODULE_PREFIX} No data returned for {symbol}")
            return None
            
        # Extract relevant fields
        ticker_data = {
            "symbol": symbol,
            "price": data.get("close"),
            "change": data.get("change"),
            "change_percent": data.get("change_percent"),
            "volume": data.get("volume"),
            "high": data.get("high"),
            "low": data.get("low"),
            "open": data.get("open"),
            "previous_close": data.get("previous_close"),
            "timestamp": data.get("timestamp"),
            "currency": data.get("currency", "USD")
        }
        
        # Enhance with trading hours
        enhanced_data = _enhance_ticker_with_trading_hours(ticker_data)
        
        logger.info(f"{MODULE_PREFIX} Successfully fetched {symbol} from EODHD")
        return enhanced_data
        
    except Exception as e:
        logger.error(f"{MODULE_PREFIX} Failed to fetch {symbol} from EODHD: {e}")
        return None

async def get_ticker_tape_data(
    symbols: List[str],
    client: httpx.AsyncClient
) -> List[Dict[str, Any]]:
    """
    Get ticker tape data from EODHD API.
    
    Args:
        symbols: List of symbols to fetch
        client: HTTP client for making requests
        
    Returns:
        List of ticker data dictionaries
    """
    logger.info(f"{MODULE_PREFIX} Fetching ticker tape data for {len(symbols)} symbols from EODHD")
    
    # Create tasks for concurrent fetching
    tasks = [
        fetch_single_ticker_from_eodhd(symbol, client) 
        for symbol in symbols
    ]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    ticker_data = []
    for symbol, result in zip(symbols, results):
        if isinstance(result, dict):
            ticker_data.append(result)
        elif isinstance(result, Exception):
            logger.error(f"{MODULE_PREFIX} Exception fetching {symbol}: {result}")
        # None results are already logged in fetch_single_ticker_from_eodhd
    
    logger.info(f"{MODULE_PREFIX} Successfully fetched {len(ticker_data)} tickers from EODHD")
    return ticker_data

async def get_single_ticker_data(
    symbol: str,
    client: httpx.AsyncClient
) -> Optional[Dict[str, Any]]:
    """
    Get single ticker data from EODHD API.
    
    Args:
        symbol: Ticker symbol to fetch
        client: HTTP client for making requests
        
    Returns:
        Ticker data dictionary or None if failed
    """
    logger.info(f"{MODULE_PREFIX} Fetching single ticker data for {symbol} from EODHD")
    return await fetch_single_ticker_from_eodhd(symbol, client)

# Module loaded indicator
logger.info(f"{MODULE_PREFIX} EODHD-only service module loaded successfully")