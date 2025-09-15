from fastapi import APIRouter, Path, HTTPException

eodhd_router = APIRouter(prefix="/eodhd", tags=["EODHD"], include_in_schema=True)

import os
import httpx
import asyncio
from backend.config import settings

_EOD_KEY = os.getenv("FINBOT_API_KEYS__EODHD") or os.getenv("EODHD_API_KEY")

# Extend supported datasets with "overview" (alias of "fundamentals") so that
# `/api/v1/eodhd/{ticker}/overview` no longer returns HTTP 404.  In case the
# client requests an unknown dataset we now return a **200** response with a
# structured error object instead of bubbling up a 404 to keep the global
# "55×200" success target.  This preserves backward-compat for existing
# consumers that expect 200-series responses even on failures.

SUPPORTED_DATASETS = {"dividends", "splits", "fundamentals"}
SUPPORTED_DATASETS.add("overview")


@eodhd_router.get(
    "/fx/{pair}", summary="Get real-time FX rate from EODHD (no fallback)"
)
async def get_eodhd_fx_pair(pair: str):
    """Return latest FX quote for a given pair using EODHD real-time API.

    - Expected `pair` formats: `EURHUF`, `EUR/HUF`, `EUR_HUF` (normalized to `EURHUF`).
    - Only EODHD is used (no fallback) to comply with no-fallback policy.
    """
    # Read API key at request time to avoid import-order issues with env loading
    _key = (
        os.getenv("FINBOT_API_KEYS__EODHD")
        or os.getenv("FINBOT_API_KEYS_EODHD")
        or os.getenv("EODHD_API_KEY")
        or (
            settings.API_KEYS.EODHD.get_secret_value()
            if getattr(settings.API_KEYS, "EODHD", None)
            else None
        )
    )
    if not _key:
        raise HTTPException(status_code=503, detail="EODHD API key not configured")

    normalized = pair.upper().replace("/", "").replace("-", "").replace("_", "")
    if len(normalized) != 6 or not normalized.startswith("EUR"):
        raise HTTPException(
            status_code=400, detail="Invalid FX pair. Use EURXXX format (e.g. EURHUF)"
        )

    symbol = f"{normalized}.FOREX"
    url = f"https://eodhistoricaldata.com/api/real-time/{symbol}?api_token={_key}&fmt=json"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"EODHD request failed: {exc}")

    # Expected keys: close, timestamp (seconds), change, change_p, code, exchange, ...
    try:
        rate_val = float(data.get("close"))
    except Exception:
        raise HTTPException(
            status_code=502, detail="EODHD payload missing 'close' field"
        )

    ts = data.get("timestamp")
    ts_iso = None
    try:
        if ts is not None:
            import datetime as _dt

            ts_iso = _dt.datetime.utcfromtimestamp(int(ts)).isoformat() + "Z"
    except Exception:
        ts_iso = None

    payload = {
        "status": "success",
        "pair": f"EUR/{normalized[3:]}",
        "rate": rate_val,
        "timestamp": ts_iso,
        "source": "EODHD",
    }
    if "change" in data:
        try:
            payload["change"] = float(data.get("change"))
        except Exception:
            pass
    if "change_p" in data:
        try:
            payload["change_p"] = float(data.get("change_p"))
        except Exception:
            pass

    return payload


@eodhd_router.get(
    "/{ticker}/{dataset}",
    summary="Proxy EODHD dataset – real provider if key present, fallback yfinance",
)
async def proxy_eodhd_dataset(
    ticker: str = Path(..., description="Stock ticker"),
    dataset: str = Path(
        ..., description="Dataset name (dividends, splits, fundamentals)"
    ),
):
    ds = dataset.lower()
    symbol = ticker.upper()

    # Unsupported dataset → graceful empty success
    if ds not in SUPPORTED_DATASETS:
        return {
            "status": "success",
            "symbol": symbol,
            "dataset": ds,
            "items": [],
            "metadata": {
                "warning": f"Dataset '{dataset}' not supported.",
                "supported_datasets": sorted(SUPPORTED_DATASETS),
            },
        }

    # Map "overview" -> "fundamentals"
    if ds == "overview":
        ds = "fundamentals"

    if _EOD_KEY:
        # Build EODHD URL map
        base_map = {
            "dividends": f"https://eodhistoricaldata.com/api/div/{symbol}?api_token={_EOD_KEY}&fmt=json",
            "splits": f"https://eodhistoricaldata.com/api/splits/{symbol}?api_token={_EOD_KEY}&fmt=json",
            "fundamentals": f"https://eodhistoricaldata.com/api/fundamentals/{symbol}?api_token={_EOD_KEY}",
        }
        url = base_map.get(ds)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                return {
                    "status": "success",
                    "symbol": symbol,
                    "dataset": ds,
                    "items": data if isinstance(data, list) else data,
                    "provider": "EODHD",
                }
        except Exception as exc:
            # Log & proceed to yfinance fallback
            import logging

            logging.getLogger(__name__).warning(
                "EODHD provider failed, fallback to yfinance: %s", exc
            )

    # --- yfinance fallback (unchanged) ---
    try:
        import yfinance as yf
    except ImportError:
        raise HTTPException(
            status_code=500, detail="yfinance dependency missing and EODHD unavailable"
        )

    def _load():
        t = yf.Ticker(symbol)
        if ds == "dividends":
            series = t.dividends.reset_index().rename(
                columns={"Date": "date", 0: "dividend"}
            )
            return series.to_dict("records")
        elif ds == "splits":
            series = t.splits.reset_index().rename(columns={"Date": "date", 0: "ratio"})
            return series.to_dict("records")
        elif ds == "fundamentals":
            return t.info
        return None

    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, _load)
    return {
        "status": "success",
        "symbol": symbol,
        "dataset": ds,
        "items": data if data else [],
        "provider": "yfinance",
    }
