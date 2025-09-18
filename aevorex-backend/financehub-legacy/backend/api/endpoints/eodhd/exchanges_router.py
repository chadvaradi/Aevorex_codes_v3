

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx
from datetime import datetime
from typing import Dict, Any

from backend.config import settings
from backend.config.eodhd import settings as eodhd_settings
from backend.models.eodhd.exchange_models import (
    ExchangeHoursResponse,
    TradingHours,
    TradingSession,
    Holiday
)
from backend.api.deps import get_http_client
from backend.core.services.trading_hours_service import TradingHoursService
from backend.api.endpoints.shared.response_builder import (
    create_eodhd_success_response,
    create_eodhd_error_response,
    CacheStatus
)

router = APIRouter()

EODHD_BASE_URL = "https://eodhd.com/api"

# Hardcoded trading hours data for major exchanges
EXCHANGE_TRADING_HOURS: Dict[str, Dict[str, Any]] = {
    "US": {
        "exchange": "US",
        "trading_hours": {
            "regular": {
                "open": "09:30",
                "close": "16:00",
                "timezone": "America/New_York",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            },
            "pre_market": {
                "open": "04:00",
                "close": "09:30",
                "timezone": "America/New_York",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            },
            "after_hours": {
                "open": "16:00",
                "close": "20:00",
                "timezone": "America/New_York",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            }
        },
        "holidays": [
            {"date": "2024-01-01", "name": "New Year's Day", "type": "full_day"},
            {"date": "2024-01-15", "name": "Martin Luther King Jr. Day", "type": "full_day"},
            {"date": "2024-02-19", "name": "Presidents' Day", "type": "full_day"},
            {"date": "2024-03-29", "name": "Good Friday", "type": "full_day"},
            {"date": "2024-05-27", "name": "Memorial Day", "type": "full_day"},
            {"date": "2024-06-19", "name": "Juneteenth", "type": "full_day"},
            {"date": "2024-07-04", "name": "Independence Day", "type": "full_day"},
            {"date": "2024-09-02", "name": "Labor Day", "type": "full_day"},
            {"date": "2024-11-28", "name": "Thanksgiving Day", "type": "full_day"},
            {"date": "2024-12-25", "name": "Christmas Day", "type": "full_day"}
        ]
    },
    "LSE": {
        "exchange": "LSE",
        "trading_hours": {
            "regular": {
                "open": "08:00",
                "close": "16:30",
                "timezone": "Europe/London",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            },
            "pre_market": {
                "open": "07:00",
                "close": "08:00",
                "timezone": "Europe/London",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            },
            "after_hours": {
                "open": "16:30",
                "close": "17:00",
                "timezone": "Europe/London",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            }
        },
        "holidays": [
            {"date": "2024-01-01", "name": "New Year's Day", "type": "full_day"},
            {"date": "2024-03-29", "name": "Good Friday", "type": "full_day"},
            {"date": "2024-04-01", "name": "Easter Monday", "type": "full_day"},
            {"date": "2024-05-06", "name": "Early May Bank Holiday", "type": "full_day"},
            {"date": "2024-05-27", "name": "Spring Bank Holiday", "type": "full_day"},
            {"date": "2024-08-26", "name": "Summer Bank Holiday", "type": "full_day"},
            {"date": "2024-12-25", "name": "Christmas Day", "type": "full_day"},
            {"date": "2024-12-26", "name": "Boxing Day", "type": "full_day"}
        ]
    },
    "TO": {
        "exchange": "TO",
        "trading_hours": {
            "regular": {
                "open": "09:30",
                "close": "16:00",
                "timezone": "America/Toronto",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            },
            "pre_market": {
                "open": "07:00",
                "close": "09:30",
                "timezone": "America/Toronto",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            },
            "after_hours": {
                "open": "16:00",
                "close": "17:00",
                "timezone": "America/Toronto",
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            }
        },
        "holidays": [
            {"date": "2024-01-01", "name": "New Year's Day", "type": "full_day"},
            {"date": "2024-03-29", "name": "Good Friday", "type": "full_day"},
            {"date": "2024-05-20", "name": "Victoria Day", "type": "full_day"},
            {"date": "2024-07-01", "name": "Canada Day", "type": "full_day"},
            {"date": "2024-09-02", "name": "Labour Day", "type": "full_day"},
            {"date": "2024-10-14", "name": "Thanksgiving Day", "type": "full_day"},
            {"date": "2024-12-25", "name": "Christmas Day", "type": "full_day"},
            {"date": "2024-12-26", "name": "Boxing Day", "type": "full_day"}
        ]
    }
}

@router.get("/list")
async def list_exchanges(http_client: httpx.AsyncClient = Depends(get_http_client)):
    """List all available exchanges."""
    url = f"{EODHD_BASE_URL}/exchanges-list/"
    params = {"api_token": eodhd_settings.API_KEY, "fmt": "json"}
    try:
        resp = await http_client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="exchanges_list",
                frequency="static",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD API error: {e.response.text}",
                error_code="EODHD_API_ERROR",
                data_type="exchanges_list"
            ),
            status_code=e.response.status_code
        )
    except Exception as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                data_type="exchanges_list"
            ),
            status_code=500
        )

@router.get("/{exchange}/tickers")
async def list_exchange_tickers(
    exchange: str, 
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    """List all tickers for a specific exchange."""
    url = f"{EODHD_BASE_URL}/exchange-symbol-list/{exchange}"
    params = {"api_token": eodhd_settings.API_KEY, "fmt": "json"}
    try:
        resp = await http_client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="exchange_tickers",
                symbol=exchange,
                frequency="static",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except httpx.HTTPStatusError as e:
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
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                symbol=exchange,
                data_type="exchange_tickers"
            ),
            status_code=500
        )

@router.get("/{exchange}/hours")
async def exchange_hours(exchange: str):
    """Get trading hours and holidays for a specific exchange using EODHD API."""
    exchange_upper = exchange.upper()
    
    try:
        # Try to fetch from EODHD API first
        eodhd_data = await TradingHoursService.fetch_exchange_details(exchange_upper)
        
        if eodhd_data:
            # Use EODHD data
            parsed_data = TradingHoursService.parse_eodhd_trading_hours(eodhd_data)
            if parsed_data:
                response_data = {
                    "exchange": parsed_data["exchange"],
                    "trading_hours": parsed_data["trading_hours"],
                    "holidays": parsed_data["holidays"],
                    "metadata": {
                        "exchange": parsed_data["exchange"],
                        "last_updated": datetime.utcnow().isoformat() + "Z",
                        "timezone": parsed_data["timezone"],
                        "source": "eodhd_api"
                    }
                }
                
                # MCP-ready response with standardized format
                return JSONResponse(
                    content=create_eodhd_success_response(
                        data=response_data,
                        data_type="exchange_hours",
                        symbol=exchange_upper,
                        frequency="static",
                        cache_status=CacheStatus.FRESH,
                        provider_meta={"source": "eodhd_api"}
                    ),
                    status_code=200
                )
        
        # Fallback to hardcoded data
        if exchange_upper not in EXCHANGE_TRADING_HOURS:
            return JSONResponse(
                content=create_eodhd_error_response(
                    message=f"Exchange '{exchange}' not found. Supported exchanges: {list(EXCHANGE_TRADING_HOURS.keys())}",
                    error_code="EXCHANGE_NOT_FOUND",
                    symbol=exchange,
                    data_type="exchange_hours"
                ),
                status_code=404
            )
        
        exchange_data = EXCHANGE_TRADING_HOURS[exchange_upper]
        
        # Build response with proper structure
        response_data = {
            "exchange": exchange_data["exchange"],
            "trading_hours": exchange_data["trading_hours"],
            "holidays": exchange_data["holidays"],
            "metadata": {
                "exchange": exchange_data["exchange"],
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "timezone": exchange_data["trading_hours"]["regular"]["timezone"],
                "source": "fallback_data"
            }
        }
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=response_data,
                data_type="exchange_hours",
                symbol=exchange_upper,
                frequency="static",
                cache_status=CacheStatus.FRESH,
                provider_meta={"source": "fallback_data"}
            ),
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Error getting trading hours for exchange '{exchange}': {str(e)}",
                error_code="INTERNAL_ERROR",
                symbol=exchange,
                data_type="exchange_hours"
            ),
            status_code=500
        )

@router.get("/{exchange}/status")
async def exchange_status(exchange: str):
    """Get current market status for a specific exchange using EODHD API."""
    try:
        market_status = await TradingHoursService.get_market_status(exchange)
        return market_status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting market status for exchange '{exchange}': {str(e)}"
        )