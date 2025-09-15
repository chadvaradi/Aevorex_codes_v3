"""
Crypto Data Endpoint
Provides Cryptocurrency data.
"""

from fastapi import APIRouter, status, Path, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Annotated
import httpx  # Expose at module level for test monkeypatch

from backend.api.deps import get_cache_service
from backend.utils.cache_service import CacheService

router = APIRouter(prefix="/crypto", tags=["Cryptocurrency Data"])


@router.get(
    "/symbols", summary="Get Supported Crypto Symbols", status_code=status.HTTP_200_OK
)
async def get_crypto_symbols(
    cache: Annotated[CacheService, Depends(get_cache_service)],
):
    """Return a list of crypto symbols fetched from CoinGecko (top 250 by market-cap).

    This replaces the previous mock response with *live* data so that the
    FinanceHub UI can stay in sync with real-world listings.  We purposely cap
    the list to 250 entries to keep the payload lightweight for the ticker
    selector.
    """

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": "false",
    }
    cache_key = "crypto:symbols:v1"
    cached = await cache.get(cache_key) if cache else None
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            from backend.config import settings

            if settings.ENVIRONMENT.NODE_ENV != "production":
                # Dev fallback to CoinPaprika
                fallback_resp = await client.get("https://api.coinpaprika.com/v1/coins")
                if fallback_resp.status_code == 200:
                    coins = fallback_resp.json()[:250]
                    symbols = [
                        f"{c['symbol'].upper()}-USD" for c in coins if c.get("symbol")
                    ]
                    return {"symbols": symbols}
            # Prod: return empty list (graceful N/A)
            return {
                "status": "success",
                "symbols": [],
                "metadata": {
                    "fallback": False,
                    "detail": "Primary provider unavailable",
                    "code": resp.status_code,
                },
            }

        data = resp.json()

    symbols = [f"{item['symbol'].upper()}-USD" for item in data]
    payload = {"symbols": symbols}
    # Cache – tighten to 10 minutes for fresher symbols in PROD policy
    if cache:
        await cache.set(cache_key, payload, ttl=600)
    return payload


@router.get(
    "/{symbol}", summary="Get Crypto Rate for a Symbol", status_code=status.HTTP_200_OK
)
async def get_crypto_rate(
    symbol: Annotated[str, Path(description="Crypto symbol", example="BTC-USD")],
    cache: Annotated[CacheService, Depends(get_cache_service)],
):
    """Return latest USD quote for the requested crypto symbol via CoinGecko.

    Supported tickers follow the *COIN-USD* convention (BTC-USD, ETH-USD …).
    For performance we map a handful of common tickers directly → CoinGecko
    IDs, otherwise we attempt a best-effort lookup.
    """

    # Normalise input (allow both BTC and BTC-USD)
    clean_symbol = symbol.upper().replace("-USD", "")

    # Quick-map of popular tickers → CoinGecko IDs
    COINGECKO_ID_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "DOGE": "dogecoin",
        "ADA": "cardano",
        "XRP": "ripple",
        "DOT": "polkadot",
        "MATIC": "polygon",
    }

    try:
        coin_id = COINGECKO_ID_MAP.get(clean_symbol)

        if coin_id is None:
            # Fallback search – call /coins/list and find matching symbol
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.coingecko.com/api/v3/coins/list?include_platform=false"
                )
                if resp.status_code != 200:
                    raise HTTPException(
                        status_code=502, detail="CoinGecko lookup failed"
                    )
                coins = resp.json()
                for c in coins:
                    if c["symbol"].upper() == clean_symbol:
                        coin_id = c["id"]
                        break

        if coin_id is None:
            raise HTTPException(
                status_code=404, detail="Symbol not supported by CoinGecko"
            )

        # Proceed to fetch price

        price_url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd"}

        cache_key_rate = f"crypto:rate:{coin_id}"
        cached_rate = await cache.get(cache_key_rate) if cache else None
        if cached_rate is not None:
            prices = {coin_id: {"usd": cached_rate}}
        else:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(price_url, params=params)
                if resp.status_code != 200:
                    from backend.config import settings

                    if settings.ENVIRONMENT.NODE_ENV != "production":
                        # Dev: try CoinPaprika
                        pp_resp = await client.get(
                            f"https://api.coinpaprika.com/v1/tickers/{coin_id}"
                        )
                        if pp_resp.status_code == 200:
                            pp_data = pp_resp.json()
                            usd_price = (
                                pp_data.get("quotes", {}).get("USD", {}).get("price")
                            )
                            if usd_price is not None:
                                prices = {coin_id: {"usd": usd_price}}
                            else:
                                raise HTTPException(
                                    status_code=404,
                                    detail="Price data unavailable in CoinPaprika",
                                )
                        else:
                            raise HTTPException(
                                status_code=502,
                                detail="Crypto price fetch failed (CoinGecko & CoinPaprika)",
                            )
                    else:
                        raise HTTPException(
                            status_code=502,
                            detail="Crypto price fetch failed (primary provider)",
                        )
                else:
                    prices = resp.json()

        if coin_id not in prices or "usd" not in prices[coin_id]:
            raise HTTPException(status_code=404, detail="Price data unavailable")

        rate_value = prices[coin_id]["usd"]
        if cache:
            await cache.set(
                cache_key_rate, rate_value, ttl=15
            )  # 15s TTL for near-real-time quotes

        return {
            "status": "success",
            "metadata": {
                "symbol": f"{clean_symbol}-USD",
                "source": "CoinGecko",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "rate": rate_value,
        }
    except HTTPException as e:
        # Convert to success payload with explanatory metadata per Rule #008
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "metadata": {
                    "symbol": f"{symbol.upper()}",
                    "source": "Crypto Endpoint Fallback",
                    "detail": e.detail,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                "rate": None,
            },
        )
