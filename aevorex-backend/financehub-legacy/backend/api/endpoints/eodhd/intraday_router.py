


from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from httpx import AsyncClient
from datetime import datetime
from backend.api.deps import get_http_client
from backend.config import settings
from backend.config.eodhd import settings as eodhd_settings
from backend.api.endpoints.shared.response_builder import (
    create_eodhd_success_response,
    create_eodhd_error_response,
    CacheStatus
)

router = APIRouter()

@router.get("/")
async def get_intraday_data(
    symbol: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    interval: str = Query("5m", description="Supported: 1m, 5m, 1h"),
    from_date: Optional[str] = Query(None, alias="from", description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, alias="to", description="To date (YYYY-MM-DD)"),
    client: AsyncClient = Depends(get_http_client)
):
    url = f"https://eodhd.com/api/intraday/{symbol}"
    params = {
        "api_token": eodhd_settings.API_KEY,
        "interval": interval,
    }
    if from_date:
        try:
            # Convert date string to timestamp
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            params["from"] = int(from_dt.timestamp())
        except ValueError:
            return JSONResponse(
                content=create_eodhd_error_response(
                    message="Invalid from_date format. Use YYYY-MM-DD",
                    error_code="INVALID_DATE_FORMAT",
                    symbol=symbol,
                    data_type="intraday"
                ),
                status_code=400
            )
    
    if to_date:
        try:
            # Convert date string to timestamp
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            params["to"] = int(to_dt.timestamp())
        except ValueError:
            return JSONResponse(
                content=create_eodhd_error_response(
                    message="Invalid to_date format. Use YYYY-MM-DD",
                    error_code="INVALID_DATE_FORMAT",
                    symbol=symbol,
                    data_type="intraday"
                ),
                status_code=400
            )
    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        
        # EODHD intraday API returns CSV format, not JSON
        csv_content = resp.text
        if not csv_content.strip():
            return JSONResponse(
                content=create_eodhd_error_response(
                    message="No intraday data available for this symbol",
                    error_code="NO_DATA_AVAILABLE",
                    symbol=symbol,
                    data_type="intraday"
                ),
                status_code=404
            )
        
        # Parse CSV and convert to JSON
        lines = csv_content.strip().split('\n')
        if len(lines) < 2:
            return JSONResponse(
                content=create_eodhd_error_response(
                    message="No intraday data available for this symbol",
                    error_code="NO_DATA_AVAILABLE",
                    symbol=symbol,
                    data_type="intraday"
                ),
                status_code=404
            )
        
        headers = lines[0].split(',')
        data_points = []
        
        for line in lines[1:]:
            values = line.split(',')
            if len(values) >= len(headers):
                data_point = {}
                for i, header in enumerate(headers):
                    header = header.strip('"')
                    value = values[i].strip('"')
                    
                    # Convert numeric fields
                    if header in ['Open', 'High', 'Low', 'Close', 'Volume']:
                        try:
                            data_point[header.lower()] = float(value)
                        except ValueError:
                            data_point[header.lower()] = value
                    elif header == 'Timestamp':
                        try:
                            data_point['timestamp'] = int(value)
                        except ValueError:
                            data_point['timestamp'] = value
                    else:
                        data_point[header.lower()] = value
                
                data_points.append(data_point)
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data_points,
                data_type="intraday",
                symbol=symbol,
                frequency="intraday",
                cache_status=CacheStatus.FRESH,
                provider_meta={"interval": interval, "from": from_date, "to": to_date, "count": len(data_points)}
            ),
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD Intraday API error: {str(e)}",
                error_code="EODHD_INTRADAY_ERROR",
                symbol=symbol,
                data_type="intraday"
            ),
            status_code=500
        )
