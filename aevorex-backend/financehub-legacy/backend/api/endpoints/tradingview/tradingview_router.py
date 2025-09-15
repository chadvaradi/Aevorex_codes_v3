 
from fastapi import APIRouter, Query
from backend.api.endpoints.tradingview.tradingview_logic import (
    get_symbols,
    get_symbol_config,
    get_tradingview_bars,
)

router = APIRouter()

@router.get("/symbols")
async def symbols():
    return await get_symbols()

@router.get("/symbols/{symbol}")
async def symbol_config(symbol: str):
    return await get_symbol_config(symbol)

@router.get("/bars")
async def bars(
    symbol: str = Query(...),
    resolution: str = Query(...),
    from_: int = Query(..., alias="from"),
    to: int = Query(...),
):
    return await get_tradingview_bars(symbol=symbol, resolution=resolution, from_ts=from_, to_ts=to)