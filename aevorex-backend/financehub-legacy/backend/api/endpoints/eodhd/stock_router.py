
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
        return JSONResponse(content=data)
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/intraday")
async def get_intraday(
    symbol: str = Query(..., description="Ticker symbol"),
    interval: str = Query("5m", description="Interval, e.g. 1m, 5m, 15m, 1h"),
    from_: Optional[str] = Query(None, alias="from", description="Start datetime (YYYY-MM-DD HH:MM)"),
    to: Optional[str] = Query(None, description="End datetime (YYYY-MM-DD HH:MM)"),
    api_key: str = Depends(get_api_key),
    base_url: str = Depends(get_base_url),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Get intraday OHLCV stock data.
    """
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
    try:
        logger.info(f"Requesting intraday data for {symbol} from EODHD API")
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()
        return JSONResponse(content=data)
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
        return JSONResponse(content=data)
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
        return JSONResponse(content=data)
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
        return JSONResponse(content=data)
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
        return JSONResponse(content=ticker_dicts)
    except httpx.HTTPStatusError as e:
        logger.error(f"EODHD API error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


__all__ = ["router"]