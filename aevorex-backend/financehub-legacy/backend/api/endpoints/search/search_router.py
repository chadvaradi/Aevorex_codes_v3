

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from backend.api.dependencies.eodhd_client import get_eodhd_client
from backend.api.dependencies.tier import get_current_tier

router = APIRouter()

@router.get("/")
async def search_ticker(
    query: str = Query(..., description="Ticker search query"),
    eodhd_client = Depends(get_eodhd_client),
    tier: str = Depends(get_current_tier)
):
    if tier not in ("pro", "enterprise"):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="This endpoint is available for pro and enterprise tiers only."
        )
    try:
        # EODHD search endpoint: /search/{query}
        result = await eodhd_client.get(f"/search/{query}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EODHD search error: {e}")
    return JSONResponse(content=result)


__all__ = ["router"]