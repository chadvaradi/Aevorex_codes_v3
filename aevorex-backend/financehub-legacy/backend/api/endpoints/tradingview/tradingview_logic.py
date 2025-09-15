

import datetime
from typing import Optional, Tuple, List, Dict, Any
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

# Helper: Resolution to timedelta
def resolution_to_timedelta(resolution: str) -> datetime.timedelta:
    if resolution.endswith('D'):
        return datetime.timedelta(days=int(resolution[:-1]))
    elif resolution.endswith('W'):
        return datetime.timedelta(weeks=int(resolution[:-1]))
    elif resolution.endswith('M'):
        return datetime.timedelta(days=30*int(resolution[:-1]))
    elif resolution.endswith('Y'):
        return datetime.timedelta(days=365*int(resolution[:-1]))
    else:
        # Minutes
        return datetime.timedelta(minutes=int(resolution))

# Helper: Convert TradingView resolution to Pandas frequency string
def resolution_to_pandas_freq(resolution: str) -> str:
    if resolution.endswith('D'):
        return f"{resolution[:-1]}D"
    elif resolution.endswith('W'):
        return f"{resolution[:-1]}W"
    elif resolution.endswith('M'):
        return f"{resolution[:-1]}M"
    elif resolution.endswith('Y'):
        return f"{resolution[:-1]}A"
    else:
        return f"{resolution}T"

# Helper: Parse symbol
def parse_symbol(symbol: str) -> Tuple[str, str]:
    if ':' in symbol:
        exchange, base = symbol.split(':', 1)
        return exchange, base
    return "BINANCE", symbol


# TODO: Implement EODHD fetcher
# from backend.core.fetchers.eodhd.eodhd_fetcher import EODHDFetcher

async def fetch_ohlcv(symbol: str, from_ts: int, to_ts: int, resolution: str) -> List[Dict[str, Any]]:
    """
    Fetch OHLCV data from EODHD API and return as a list of dictionaries.
    """
    import httpx
    from datetime import datetime
    
    logger.info(f"Fetching OHLCV data for {symbol}, resolution: {resolution}, from: {from_ts}, to: {to_ts}")
    
    # Convert timestamps to date strings for EODHD API
    from_date = datetime.fromtimestamp(from_ts).strftime('%Y-%m-%d')
    to_date = datetime.fromtimestamp(to_ts).strftime('%Y-%m-%d')
    
    logger.info(f"Date range: {from_date} to {to_date}")
    
    # Map TradingView resolution to EODHD interval
    interval_map = {
        "1": "1m",      # 1 minute
        "5": "5m",      # 5 minutes
        "15": "15m",    # 15 minutes
        "30": "30m",    # 30 minutes
        "60": "1h",     # 1 hour
        "1D": "1d",     # 1 day
    }
    
    interval = interval_map.get(resolution)
    if not interval:
        logger.error(f"Unsupported resolution: {resolution}")
        return []
    
    # Determine which EODHD endpoint to use
    if resolution == "1D":
        # Use end-of-day data for daily resolution
        url = f"https://eodhd.com/api/eod/{symbol}"
        params = {
            "api_token": "6819f415c58868.65742188",
            "from": from_date,
            "to": to_date,
            "fmt": "json"
        }
        logger.info(f"Using EOD endpoint for daily data")
    else:
        # Use intraday data for intraday resolutions
        url = f"https://eodhd.com/api/intraday/{symbol}"
        params = {
            "api_token": "6819f415c58868.65742188",
            "interval": interval,
            "from": from_ts,  # Intraday API expects timestamps
            "to": to_ts,
            "fmt": "json"
        }
        logger.info(f"Using intraday endpoint for {interval} data")
    
    logger.info(f"EODHD URL: {url}")
    logger.info(f"EODHD params: {params}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            logger.info(f"EODHD response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            logger.info(f"EODHD response data type: {type(data)}")
            logger.info(f"EODHD response data length: {len(data) if isinstance(data, list) else 'not a list'}")
            
            # EODHD EOD API returns a list directly
            if isinstance(data, list):
                ohlcv_list = data
            else:
                logger.error(f"Unexpected data format: {data}")
                return []
            
            # Transform EODHD data to our format
            ohlcv_data = []
            for item in ohlcv_list:
                # Convert date to timestamp
                if 'date' in item:
                    date_str = item['date']
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                    timestamp = int(dt.timestamp())
                else:
                    logger.warning(f"No date field in item: {item}")
                    continue
                
                ohlcv_data.append({
                    "time": timestamp,
                    "open": float(item.get('open', 0)),
                    "high": float(item.get('high', 0)),
                    "low": float(item.get('low', 0)),
                    "close": float(item.get('close', 0)),
                    "volume": int(item.get('volume', 0))
                })
            
            logger.info(f"Transformed {len(ohlcv_data)} OHLCV data points")
            return ohlcv_data
            
    except Exception as e:
        logger.error(f"Error fetching OHLCV data from EODHD for {symbol}: {e}")
        return []

# Main TradingView UDF bars endpoint logic
async def get_tradingview_bars(
    symbol: str,
    resolution: str,
    from_ts: int,
    to_ts: int,
    countback: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Returns a dictionary with TradingView UDF bars response:
    {
        "s": "ok" or "no_data",
        "t": [...],  # Timestamps
        "o": [...],  # Opens
        "h": [...],  # Highs
        "l": [...],  # Lows
        "c": [...],  # Closes
        "v": [...],  # Volumes
        "nextTime": <int> (optional)
    }
    """
    exchange, base = parse_symbol(symbol)
    ohlcv_data = await fetch_ohlcv(symbol, from_ts, to_ts, resolution)
    if not ohlcv_data:
        return {"s": "no_data"}
    
    # Filter by time range
    filtered_data = [item for item in ohlcv_data if from_ts <= item['time'] <= to_ts]
    if countback is not None:
        filtered_data = filtered_data[-countback:]
    if not filtered_data:
        return {"s": "no_data"}
    
    result = {
        "s": "ok",
        "t": [item['time'] for item in filtered_data],
        "o": [item['open'] for item in filtered_data],
        "h": [item['high'] for item in filtered_data],
        "l": [item['low'] for item in filtered_data],
        "c": [item['close'] for item in filtered_data],
        "v": [item['volume'] for item in filtered_data],
    }
    return result


# TradingView symbols configuration
OFFICIAL_SYMBOLS = {
    # Sample symbols for TradingView integration
    "AAPL": {
        "symbol": "AAPL",
        "full_name": "Apple Inc.",
        "description": "Apple Inc. stock",
        "type": "stock",
        "session": "0930-1600",
        "timezone": "America/New_York",
        "minmov": 1,
        "pricescale": 100,
        "has_intraday": True,
        "supported_resolutions": ["1", "5", "15", "30", "60", "1D"],
        "data_source": "EODHD",
        "license": "Commercial",
    },
    "EURUSD": {
        "symbol": "EURUSD",
        "full_name": "Euro / US Dollar",
        "description": "EUR/USD currency pair",
        "type": "forex",
        "session": "0000-2359",
        "timezone": "UTC",
        "minmov": 1,
        "pricescale": 100000,
        "has_intraday": True,
        "supported_resolutions": ["1", "5", "15", "30", "60", "1D"],
        "data_source": "EODHD",
        "license": "Commercial",
    },
}


async def get_symbols() -> List[Dict[str, Any]]:
    """
    Get all available financial symbols for TradingView Advanced Chart.
    Returns symbol configuration for available data sources.
    """
    logger.info("Fetching available TradingView symbols")

    symbols_list = []

    for symbol_id, config in OFFICIAL_SYMBOLS.items():
        symbols_list.append(
            {
                "symbol": config["symbol"],
                "full_name": config["full_name"],
                "description": config["description"],
                "type": config["type"],
                "session": config["session"],
                "timezone": config["timezone"],
                "minmov": config["minmov"],
                "pricescale": config["pricescale"],
                "has_intraday": config["has_intraday"],
                "supported_resolutions": config["supported_resolutions"],
                "data_source": config["data_source"],
                "license": config["license"],
            }
        )

    logger.info(f"Returning {len(symbols_list)} symbols")
    return symbols_list


async def get_symbol_config(symbol: str) -> Dict[str, Any]:
    """Get configuration for a specific symbol."""
    
    if symbol not in OFFICIAL_SYMBOLS:
        return {
            "error": f"Symbol {symbol} not found",
            "available_symbols": list(OFFICIAL_SYMBOLS.keys()),
        }
    
    config = OFFICIAL_SYMBOLS[symbol]
    return {
        "symbol": config["symbol"],
        "full_name": config["full_name"],
        "description": config["description"],
        "type": config["type"],
        "session": config["session"],
        "timezone": config["timezone"],
        "minmov": config["minmov"],
        "pricescale": config["pricescale"],
        "has_intraday": config["has_intraday"],
        "supported_resolutions": config["supported_resolutions"],
        "data_source": config["data_source"],
        "license": config["license"],
    }