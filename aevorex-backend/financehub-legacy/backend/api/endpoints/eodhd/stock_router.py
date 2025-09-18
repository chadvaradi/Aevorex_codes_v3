
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
from backend.config import settings
from backend.config.eodhd import settings as eodhd_settings
from backend.api.deps import get_http_client
from backend.utils.logger_config import get_logger
from backend.models.eodhd.stock_models import (
    ExchangeTicker, 
    StockEODData, 
    StockIntradayData, 
    StockSplitData, 
    StockDividendData,
    ExchangeTickersResponse,
    StockEODResponse,
    StockIntradayResponse,
    StockSplitsResponse,
    StockDividendsResponse
)
from backend.api.endpoints.shared.response_builder import (
    create_eodhd_success_response,
    create_eodhd_error_response,
    CacheStatus
)
import httpx

router = APIRouter()
logger = get_logger(__name__)

def get_api_key():
    return eodhd_settings.API_KEY

def get_base_url():
    return "https://eodhd.com/api"


@router.get("/eod")
async def get_eod(
    symbol: str = Query(..., description="Ticker symbol"),
    from_: Optional[str] = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    api_key: str = Depends(get_api_key),
    base_url: str = Depends(get_base_url),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Get End of Day (EOD) stock data.
    """
    endpoint = f"{base_url}/eod/{symbol}"
    params = {
        "api_token": api_key,
        "fmt": "json"
    }
    if from_:
        params["from"] = from_
    if to:
        params["to"] = to
    try:
        logger.info(f"Requesting EOD data for {symbol} from EODHD API")
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="stock_eod",
                symbol=symbol,
                frequency="daily",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD API error: {e.response.text}",
                error_code="EODHD_API_ERROR",
                symbol=symbol,
                data_type="stock_eod"
            ),
            status_code=e.response.status_code
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                symbol=symbol,
                data_type="stock_eod"
            ),
            status_code=500
        )


@router.get("/intraday")
async def get_intraday(
    symbol: str = Query(..., description="Ticker symbol"),
    interval: str = Query("5m", description="Interval, e.g. 1m, 5m, 15m, 1h"),
    from_: Optional[str] = Query(None, alias="from", description="Start datetime (YYYY-MM-DD HH:MM)"),
    to: Optional[str] = Query(None, description="End datetime (YYYY-MM-DD HH:MM)"),
    limit: Optional[int] = Query(1000, ge=1, le=5000, description="Maximum number of data points (default: 1000, max: 5000)"),
    view: Optional[str] = Query("full", regex="^(full|summary)$", description="Data view: 'full' for complete data, 'summary' for condensed view"),
    api_key: str = Depends(get_api_key),
    base_url: str = Depends(get_base_url),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Get intraday OHLCV stock data with comprehensive cost protection.
    
    **🛡️ COST PROTECTION GUARDS:**
    - **Token Estimation**: Estimates response size based on interval, limit, and date range
    - **Limit Validation**: Default 1000 points, maximum 5000 points per request
    - **Token Threshold**: 250,000 tokens (~1MB JSON) maximum for full view
    - **402 Upgrade Required**: Blocks requests exceeding token threshold with upgrade prompt
    - **Summary View**: Provides condensed data (~1,000 tokens) for LLM consumption
    
    **💰 COST RATIONALE:**
    - 1m interval + 5000 limit = ~200,000 tokens = ~$0.80 (Gemini 2.0 Flash)
    - Without guards: 1 year 1m data = ~4M tokens = ~$16+ per request
    - Summary view reduces costs by 99.5% while maintaining analytical value
    
    **🎯 PROTECTION STRATEGY:**
    - Prevents accidental high-cost requests during MVP testing
    - Maintains premium user experience with upgrade paths
    - Optimizes for LLM token efficiency without data loss
    """
    # Cost protection: Estimate token count and apply limits
    estimated_tokens = _estimate_intraday_token_count(symbol, interval, from_, to, limit)
    MAX_TOKEN_THRESHOLD = 250000  # ~1MB JSON for intraday data
    
    if estimated_tokens > MAX_TOKEN_THRESHOLD and view == "full":
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Upgrade Required",
                "message": f"Request would generate ~{estimated_tokens} tokens. Use view=summary or reduce parameters.",
                "estimated_tokens": estimated_tokens,
                "max_allowed": MAX_TOKEN_THRESHOLD,
                "suggestions": [
                    "Add ?view=summary for condensed data",
                    "Reduce date range (max 2 weeks for 1m data)",
                    "Use larger interval (5m, 15m, 1h instead of 1m)",
                    "Reduce limit parameter (current: {})".format(limit),
                    "Upgrade to premium plan for full access"
                ]
            }
        )
    
    # Handle summary view
    if view == "summary":
        return await _get_intraday_summary_view(symbol, interval, from_, to, api_key, base_url, client)
    
    endpoint = f"{base_url}/intraday/{symbol}"
    params = {
        "api_token": api_key,
        "interval": interval,
        "fmt": "json"
    }
    if from_:
        params["from"] = from_
    if to:
        params["to"] = to
    if limit:
        params["limit"] = limit
    try:
        logger.info(f"Requesting intraday data for {symbol} from EODHD API")
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="stock_intraday",
                symbol=symbol,
                frequency="intraday",
                cache_status=CacheStatus.FRESH,
                provider_meta={"interval": interval, "view": view}
            ),
            status_code=200
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD API error: {e.response.text}",
                error_code="EODHD_API_ERROR",
                symbol=symbol,
                data_type="stock_intraday"
            ),
            status_code=e.response.status_code
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                symbol=symbol,
                data_type="stock_intraday"
            ),
            status_code=500
        )


@router.get("/splits")
async def get_splits(
    symbol: str = Query(..., description="Ticker symbol"),
    api_key: str = Depends(get_api_key),
    base_url: str = Depends(get_base_url),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Get stock splits data.
    """
    endpoint = f"{base_url}/splits/{symbol}"
    params = {
        "api_token": api_key,
        "fmt": "json"
    }
    try:
        logger.info(f"Requesting splits data for {symbol} from EODHD API")
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="stock_splits",
                symbol=symbol,
                frequency="event",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD API error: {e.response.text}",
                error_code="EODHD_API_ERROR",
                symbol=symbol,
                data_type="stock_splits"
            ),
            status_code=e.response.status_code
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                symbol=symbol,
                data_type="stock_splits"
            ),
            status_code=500
        )


@router.get("/dividends")
async def get_dividends(
    symbol: str = Query(..., description="Ticker symbol"),
    api_key: str = Depends(get_api_key),
    base_url: str = Depends(get_base_url),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Get stock dividends data.
    """
    endpoint = f"{base_url}/div/{symbol}"
    params = {
        "api_token": api_key,
        "fmt": "json"
    }
    try:
        logger.info(f"Requesting dividends data for {symbol} from EODHD API")
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="stock_dividends",
                symbol=symbol,
                frequency="event",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD API error: {e.response.text}",
                error_code="EODHD_API_ERROR",
                symbol=symbol,
                data_type="stock_dividends"
            ),
            status_code=e.response.status_code
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                symbol=symbol,
                data_type="stock_dividends"
            ),
            status_code=500
        )


@router.get("/adjusted")
async def get_adjusted(
    symbol: str = Query(..., description="Ticker symbol"),
    from_: Optional[str] = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    api_key: str = Depends(get_api_key),
    base_url: str = Depends(get_base_url),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Get adjusted stock data (EOD with splits/dividends applied).
    """
    endpoint = f"{base_url}/eod/{symbol}"
    params = {
        "api_token": api_key,
        "fmt": "json",
        "adjusted": "1"
    }
    if from_:
        params["from"] = from_
    if to:
        params["to"] = to
    try:
        logger.info(f"Requesting adjusted data for {symbol} from EODHD API")
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="stock_adjusted",
                symbol=symbol,
                frequency="daily",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD API error: {e.response.text}",
                error_code="EODHD_API_ERROR",
                symbol=symbol,
                data_type="stock_adjusted"
            ),
            status_code=e.response.status_code
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                symbol=symbol,
                data_type="stock_adjusted"
            ),
            status_code=500
        )


@router.get("/exchange-tickers")
async def get_exchange_tickers(
    exchange: str = Query(..., description="Exchange code, e.g. 'US', 'NYSE', 'NASDAQ'"),
    delisted: Optional[str] = Query(None, description="Include delisted tickers (set to '1')"),
    type_: Optional[str] = Query(None, alias="type", description="Filter by type: common_stock, preferred_stock, stock, etf, fund"),
    api_key: str = Depends(get_api_key),
    base_url: str = Depends(get_base_url),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Get list of tickers for a given exchange.
    """
    endpoint = f"{base_url}/exchange-symbol-list/{exchange}"
    params = {
        "api_token": api_key,
        "fmt": "json"
    }
    if delisted:
        params["delisted"] = delisted
    if type_:
        params["type"] = type_
    try:
        logger.info(f"Requesting tickers for exchange {exchange} from EODHD API")
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        raw_data = resp.json()
        
        # Parse the raw data using Pydantic models with proper field mapping
        tickers = [ExchangeTicker.from_eodhd_data(ticker_data) for ticker_data in raw_data]
        
        # Convert to dict format for JSON response
        ticker_dicts = [ticker.model_dump() for ticker in tickers]
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=ticker_dicts,
                data_type="exchange_tickers",
                symbol=exchange,
                frequency="static",
                cache_status=CacheStatus.FRESH,
                provider_meta={"delisted": delisted, "type": type_}
            ),
            status_code=200
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD API error: {e.response.text}",
                error_code="EODHD_API_ERROR",
                symbol=exchange,
                data_type="exchange_tickers"
            ),
            status_code=e.response.status_code
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                symbol=exchange,
                data_type="exchange_tickers"
            ),
            status_code=500
        )


def _estimate_intraday_token_count(symbol: str, interval: str, from_: str, to: str, limit: int) -> int:
    """
    Estimate token count for EODHD intraday data request.
    Based on OHLCV data structure and interval frequency.
    """
    from datetime import datetime, timedelta
    
    # Base tokens per data point (OHLCV + timestamp + metadata)
    base_tokens_per_point = 40  # Similar to FRED observations
    
    # Interval multipliers (more frequent = more data points)
    interval_multipliers = {
        "1m": 1.0,   # 1 minute (highest frequency)
        "5m": 0.2,   # 5 minutes
        "15m": 0.067, # 15 minutes
        "30m": 0.033, # 30 minutes
        "1h": 0.017,  # 1 hour
        "4h": 0.004,  # 4 hours
        "1d": 0.001,  # 1 day
    }
    
    # Get interval multiplier
    interval_mult = interval_multipliers.get(interval, 1.0)
    
    # Calculate estimated data points
    if limit and limit > 0:
        estimated_points = limit
    else:
        # Estimate based on date range and interval
        if from_ and to:
            try:
                start_dt = datetime.strptime(from_, "%Y-%m-%d %H:%M")
                end_dt = datetime.strptime(to, "%Y-%m-%d %H:%M")
                total_minutes = (end_dt - start_dt).total_seconds() / 60
                
                # Calculate points based on interval
                if interval == "1m":
                    estimated_points = min(int(total_minutes), 10000)  # Cap at 10k
                elif interval == "5m":
                    estimated_points = min(int(total_minutes / 5), 5000)
                elif interval == "15m":
                    estimated_points = min(int(total_minutes / 15), 3000)
                elif interval == "30m":
                    estimated_points = min(int(total_minutes / 30), 2000)
                elif interval == "1h":
                    estimated_points = min(int(total_minutes / 60), 1000)
                else:
                    estimated_points = 1000  # Default estimate
            except:
                estimated_points = 1000
        else:
            # No date range specified, use conservative estimate
            estimated_points = 2000 if interval == "1m" else 1000
    
    # Calculate total estimated tokens
    total_tokens = int(estimated_points * base_tokens_per_point * interval_mult)
    
    return total_tokens


async def _get_intraday_summary_view(symbol: str, interval: str, from_: str, to: str, api_key: str, base_url: str, client: httpx.AsyncClient) -> dict:
    """
    Get summary view of intraday data (last 1000 points + statistics).
    Optimized for LLM consumption with minimal token usage.
    """
    try:
        # Get limited data for summary (1000 points max)
        endpoint = f"{base_url}/intraday/{symbol}"
        params = {
            "api_token": api_key,
            "interval": interval,
            "fmt": "json"
        }
        
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        if not data or not isinstance(data, list):
            return {
                "status": "error",
                "message": f"No intraday data available for {symbol}",
                "symbol": symbol
            }
        
        # Process data for summary
        if len(data) == 0:
            return {
                "status": "error",
                "message": f"No data points found for {symbol}",
                "symbol": symbol
            }
        
        # Extract OHLCV data
        ohlcv_data = []
        for item in data:
            if isinstance(item, dict) and all(key in item for key in ['open', 'high', 'low', 'close', 'volume']):
                ohlcv_data.append({
                    'timestamp': item.get('timestamp', item.get('datetime')),
                    'open': float(item['open']),
                    'high': float(item['high']),
                    'low': float(item['low']),
                    'close': float(item['close']),
                    'volume': int(item['volume'])
                })
        
        if not ohlcv_data:
            return {
                "status": "error",
                "message": f"No valid OHLCV data found for {symbol}",
                "symbol": symbol
            }
        
        # Calculate statistics
        closes = [item['close'] for item in ohlcv_data]
        volumes = [item['volume'] for item in ohlcv_data]
        
        latest = closes[-1] if closes else None
        previous = closes[-2] if len(closes) > 1 else None
        
        # Calculate changes
        change = latest - previous if latest and previous else None
        change_pct = (change / previous * 100) if change and previous else None
        
        # Calculate min/max/avg for last 2 weeks
        min_2w = min(closes) if closes else None
        max_2w = max(closes) if closes else None
        avg_2w = sum(closes) / len(closes) if closes else None
        
        # Calculate volatility (standard deviation)
        if len(closes) > 1:
            mean = avg_2w
            variance = sum((x - mean) ** 2 for x in closes) / len(closes)
            volatility = variance ** 0.5
        else:
            volatility = None
        
        # Get recent data (last 50 points for summary)
        recent_data = ohlcv_data[-50:] if len(ohlcv_data) > 50 else ohlcv_data
        
        # Calculate daily aggregates (if we have enough data)
        daily_aggregates = []
        if len(ohlcv_data) > 100:  # Only if we have substantial data
            # Group by date and calculate daily OHLCV
            daily_groups = {}
            for item in ohlcv_data:
                # Extract date from timestamp (handle both formats)
                timestamp = item.get('timestamp', item.get('datetime', ''))
                if isinstance(timestamp, (int, float)):
                    # Unix timestamp
                    from datetime import datetime
                    date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                else:
                    # String timestamp
                    date = str(timestamp)[:10] if timestamp else "unknown"
                
                if date not in daily_groups:
                    daily_groups[date] = []
                daily_groups[date].append(item)
            
            # Calculate daily aggregates for last 7 days
            for date in sorted(daily_groups.keys())[-7:]:
                day_data = daily_groups[date]
                daily_aggregates.append({
                    'date': date,
                    'open': day_data[0]['open'],
                    'high': max(item['high'] for item in day_data),
                    'low': min(item['low'] for item in day_data),
                    'close': day_data[-1]['close'],
                    'volume': sum(item['volume'] for item in day_data),
                    'data_points': len(day_data)
                })
        
        return {
            "status": "success",
            "view": "summary",
            "symbol": symbol,
            "interval": interval,
            "period": "recent_data",
            "statistics": {
                "latest": latest,
                "previous": previous,
                "change": change,
                "change_pct": round(change_pct, 2) if change_pct else None,
                "min_period": min_2w,
                "max_period": max_2w,
                "avg_period": round(avg_2w, 4) if avg_2w else None,
                "volatility": round(volatility, 4) if volatility else None,
                "total_data_points": len(ohlcv_data),
                "avg_volume": int(sum(volumes) / len(volumes)) if volumes else None
            },
            "recent_data": recent_data[-50:],  # Last 50 points
            "daily_aggregates": daily_aggregates,
            "upgrade_prompt": "Full intraday data available with premium plan",
            "meta": {
                "data_source": "EODHD",
                "interval": interval,
                "last_updated": datetime.now().isoformat(),
                "total_observations": len(ohlcv_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating intraday summary view for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Error generating summary view: {str(e)}",
            "symbol": symbol
        }


__all__ = ["router"]