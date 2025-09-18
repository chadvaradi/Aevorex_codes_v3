from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from datetime import datetime, timedelta

from backend.api.deps import get_http_client
from backend.config import settings
from backend.config.eodhd import settings as eodhd_settings
from backend.utils.logger_config import get_logger
from backend.models.eodhd.stock_models import CryptoTicker
from backend.api.endpoints.shared.response_builder import (
    create_eodhd_success_response,
    create_eodhd_error_response,
    CacheStatus
)

logger = get_logger(__name__)
router = APIRouter()

BASE_URL = "https://eodhd.com/api"

def get_default_date_range():
    """Get default date range (last 30 days) for crypto endpoints."""
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    return thirty_days_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

@router.get("/list")
async def list_cryptocurrencies(
    http_client: AsyncClient = Depends(get_http_client),
    api_token: str = Query(default=eodhd_settings.API_KEY, description="EODHD API token"),
):
    """
    List all supported cryptocurrencies from EODHD.
    """
    url = f"{BASE_URL}/exchange-symbol-list/CC"
    try:
        resp = await http_client.get(url, params={"api_token": api_token, "fmt": "json"})
        resp.raise_for_status()
        raw_data = resp.json()
        
        # Parse the raw data using Pydantic models with proper field mapping
        tickers = [CryptoTicker.from_eodhd_data(ticker_data) for ticker_data in raw_data]
        
        # Convert to dict format for JSON response
        ticker_dicts = [ticker.model_dump() for ticker in tickers]
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=ticker_dicts,
                data_type="crypto_list",
                frequency="static",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error fetching crypto list: {e}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch crypto list: {str(e)}",
                error_code="CRYPTO_LIST_ERROR",
                data_type="crypto_list"
            ),
            status_code=500
        )

@router.get("/{symbol}/quote")
async def get_crypto_quote(
    symbol: str,
    http_client: AsyncClient = Depends(get_http_client),
    api_token: str = Query(default=eodhd_settings.API_KEY, description="EODHD API token"),
):
    """
    Get real-time or delayed quote for a given cryptocurrency.
    """
    url = f"{BASE_URL}/real-time/{symbol}.CC"
    params = {"api_token": api_token, "fmt": "json"}
    try:
        resp = await http_client.get(url, params=params)
        resp.raise_for_status()
        raw_data = resp.json()
        
        # Real-time endpoint returns a single object, not a list
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=raw_data,
                data_type="crypto_quote",
                symbol=symbol,
                frequency="realtime",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error fetching crypto quote for {symbol}: {e}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch crypto quote: {str(e)}",
                error_code="CRYPTO_QUOTE_ERROR",
                symbol=symbol,
                data_type="crypto_quote"
            ),
            status_code=500
        )

@router.get("/{symbol}/eod")
async def get_crypto_eod(
    symbol: str,
    from_date: str | None = Query(None, description="Start date YYYY-MM-DD"),
    to_date: str | None = Query(None, description="End date YYYY-MM-DD"),
    http_client: AsyncClient = Depends(get_http_client),
    api_token: str = Query(default=eodhd_settings.API_KEY, description="EODHD API token"),
):
    """
    Get End Of Day (historical) data for a given cryptocurrency.
    Defaults to last 30 days if no date range specified.
    """
    url = f"{BASE_URL}/eod/{symbol}.CC"
    params = {"api_token": api_token, "fmt": "json"}
    
    # Use default date range if not specified
    if not from_date or not to_date:
        default_from, default_to = get_default_date_range()
        params["from"] = from_date or default_from
        params["to"] = to_date or default_to
    else:
        params["from"] = from_date
        params["to"] = to_date

    try:
        resp = await http_client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        provider_meta = {}
        if not from_date or not to_date:
            provider_meta["note"] = "Showing last 30 days by default. Use ?from=YYYY-MM-DD&to=YYYY-MM-DD for custom range."
            provider_meta["date_range"] = f"{params['from']} to {params['to']}"
        
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="crypto_eod",
                symbol=symbol,
                frequency="daily",
                cache_status=CacheStatus.FRESH,
                provider_meta=provider_meta
            ),
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error fetching EOD crypto data for {symbol}: {e}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch crypto EOD data: {str(e)}",
                error_code="CRYPTO_EOD_ERROR",
                symbol=symbol,
                data_type="crypto_eod"
            ),
            status_code=500
        )

@router.get("/{symbol}/intraday")
async def get_crypto_intraday(
    symbol: str,
    interval: str = Query("5m", description="Intraday interval (e.g. 1m, 5m, 1h)"),
    http_client: AsyncClient = Depends(get_http_client),
    api_token: str = Query(default=eodhd_settings.API_KEY, description="EODHD API token"),
):
    """
    Get intraday data for a given cryptocurrency.
    """
    url = f"{BASE_URL}/intraday/{symbol}.CC"
    params = {"api_token": api_token, "interval": interval, "fmt": "json"}

    try:
        resp = await http_client.get(url, params=params)
        resp.raise_for_status()
        raw_data = resp.json()
        
        # Intraday endpoint returns a list of data points
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=raw_data,
                data_type="crypto_intraday",
                symbol=symbol,
                frequency="intraday",
                cache_status=CacheStatus.FRESH,
                provider_meta={"interval": interval}
            ),
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error fetching intraday crypto data for {symbol}: {e}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch crypto intraday data: {str(e)}",
                error_code="CRYPTO_INTRADAY_ERROR",
                symbol=symbol,
                data_type="crypto_intraday"
            ),
            status_code=500
        )

@router.get("/{symbol}/history")
async def get_crypto_history(
    symbol: str,
    from_date: str | None = Query(None, description="Start date YYYY-MM-DD"),
    to_date: str | None = Query(None, description="End date YYYY-MM-DD"),
    http_client: AsyncClient = Depends(get_http_client),
    api_token: str = Query(default=eodhd_settings.API_KEY, description="EODHD API token"),
):
    """
    Get historical data for a given cryptocurrency.
    Defaults to last 30 days if no date range specified.
    """
    url = f"{BASE_URL}/eod/{symbol}.CC"
    params = {"api_token": api_token, "fmt": "json"}
    
    # Use default date range if not specified
    if not from_date or not to_date:
        default_from, default_to = get_default_date_range()
        params["from"] = from_date or default_from
        params["to"] = to_date or default_to
    else:
        params["from"] = from_date
        params["to"] = to_date

    try:
        resp = await http_client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        provider_meta = {}
        if not from_date or not to_date:
            provider_meta["note"] = "Showing last 30 days by default. Use ?from=YYYY-MM-DD&to=YYYY-MM-DD for custom range."
            provider_meta["date_range"] = f"{params['from']} to {params['to']}"
        
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="crypto_history",
                symbol=symbol,
                frequency="daily",
                cache_status=CacheStatus.FRESH,
                provider_meta=provider_meta
            ),
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error fetching history crypto data for {symbol}: {e}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch crypto history data: {str(e)}",
                error_code="CRYPTO_HISTORY_ERROR",
                symbol=symbol,
                data_type="crypto_history"
            ),
            status_code=500
        )

@router.get("/{symbol}/splits")
async def get_crypto_splits(
    symbol: str,
):
    """
    Splits data is not supported for cryptocurrencies.
    """
    logger.error(f"Splits endpoint not supported for crypto symbol {symbol}")
    return JSONResponse(
        content=create_eodhd_error_response(
            message="Splits data not supported for cryptocurrencies",
            error_code="CRYPTO_SPLITS_NOT_SUPPORTED",
            symbol=symbol,
            data_type="crypto_splits"
        ),
        status_code=400
    )

@router.get("/{symbol}/dividends")
async def get_crypto_dividends(
    symbol: str,
):
    """
    Dividends data is not supported for cryptocurrencies.
    """
    logger.error(f"Dividends endpoint not supported for crypto symbol {symbol}")
    return JSONResponse(
        content=create_eodhd_error_response(
            message="Dividends data not supported for cryptocurrencies",
            error_code="CRYPTO_DIVIDENDS_NOT_SUPPORTED",
            symbol=symbol,
            data_type="crypto_dividends"
        ),
        status_code=400
    )

@router.get("/{symbol}/adjusted")
async def get_crypto_adjusted(
    symbol: str,
    from_date: str | None = Query(None, description="Start date YYYY-MM-DD"),
    to_date: str | None = Query(None, description="End date YYYY-MM-DD"),
    http_client: AsyncClient = Depends(get_http_client),
    api_token: str = Query(default=eodhd_settings.API_KEY, description="EODHD API token"),
):
    """
    Get adjusted price data for a given cryptocurrency.
    Defaults to last 30 days if no date range specified.
    """
    url = f"{BASE_URL}/eod/{symbol}.CC"
    params = {"api_token": api_token, "fmt": "json"}
    
    # Use default date range if not specified
    if not from_date or not to_date:
        default_from, default_to = get_default_date_range()
        params["from"] = from_date or default_from
        params["to"] = to_date or default_to
    else:
        params["from"] = from_date
        params["to"] = to_date

    try:
        resp = await http_client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        provider_meta = {}
        if not from_date or not to_date:
            provider_meta["note"] = "Showing last 30 days by default. Use ?from=YYYY-MM-DD&to=YYYY-MM-DD for custom range."
            provider_meta["date_range"] = f"{params['from']} to {params['to']}"
        
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="crypto_adjusted",
                symbol=symbol,
                frequency="daily",
                cache_status=CacheStatus.FRESH,
                provider_meta=provider_meta
            ),
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error fetching adjusted crypto data for {symbol}: {e}")
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch crypto adjusted data: {str(e)}",
                error_code="CRYPTO_ADJUSTED_ERROR",
                symbol=symbol,
                data_type="crypto_adjusted"
            ),
            status_code=500
        )


__all__ = ["router"]