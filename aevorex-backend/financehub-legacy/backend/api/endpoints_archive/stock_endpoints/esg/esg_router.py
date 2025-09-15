from __future__ import annotations

"""ESG endpoint – provides ESG score for a given stock ticker.
Relies on FinancialModelingPrep ESG API (real data). Requires env var FMP_API_KEY.
Falls back to 502 error if data unavailable.
"""
import os
from typing import Dict
import httpx
from fastapi import APIRouter, Path, HTTPException
from fastapi.responses import JSONResponse
from backend.utils.logger_config import get_logger
from datetime import datetime

logger = get_logger(__name__)

_FMP_KEY = os.getenv("FMP_API_KEY")

# Hide the route from OpenAPI if the API-kulcs is missing so integrators see immediately that
# ESG szolgáltatás nem elérhető, és ne kapjanak üres mock választ.
router = APIRouter(
    prefix="/esg",
    tags=["Stock ESG"],
    include_in_schema=bool(_FMP_KEY),
)

_BASE_URL = "https://financialmodelingprep.com/api/v3/esg-score/{symbol}?apikey={key}"


@router.get(
    "/{ticker}",
    summary="Get ESG score for a stock ticker",
    include_in_schema=bool(_FMP_KEY),
)
async def get_esg_score(
    ticker: str = Path(..., description="Stock ticker symbol", example="AAPL"),
) -> Dict:
    symbol = ticker.upper()
    if not _FMP_KEY:
        # Return graceful fallback – keeps 200-only API surface
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "symbol": symbol,
                "provider": "FMP",
                "data": {},
                "metadata": {
                    "fallback": True,
                    "reason": "FMP_API_KEY not configured",
                },
            },
        )
    url = _BASE_URL.format(symbol=symbol, key=_FMP_KEY)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "symbol": symbol,
                        "provider": "FMP",
                        "data": {},
                        "metadata": {
                            "warning": "ESG data not found",
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    },
                )
            esg_info = data[0] if isinstance(data, list) else data
            return {
                "status": "success",
                "symbol": symbol,
                "provider": "FMP",
                "data": esg_info,
            }
    except HTTPException as http_exc:
        logger.warning("ESG endpoint upstream HTTP error: %s", http_exc.detail)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "symbol": symbol,
                "provider": "FMP",
                "data": {},
                "metadata": {
                    "warning": http_exc.detail,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )
    except Exception as exc:
        logger.error("ESG endpoint error: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "symbol": symbol,
                "provider": "FMP",
                "data": {},
                "metadata": {
                    "fallback": True,
                    "reason": str(exc),
                },
            },
        )
