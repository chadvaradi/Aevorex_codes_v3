"""
Quant endpoints
===============

Phase M0–M1 minimal implementation:
- GET /api/v1/quant/factors/{ticker}
- GET /api/v1/quant/signals/{ticker}

Uses existing OHLCV fetch handler and app-level http client/cache.
Computes a small set of factors on daily closes: momentum_20d, vol_20d,
and sma_20d_deviation. Signals: a simple momentum+volatility filter.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from datetime import datetime
import math

from fastapi import APIRouter, Request, Path, HTTPException
from pydantic import BaseModel, Field

from backend.core.services.handlers.ohlcv_data_handler import (
    fetch_ohlcv_data,
)


router = APIRouter(prefix="/quant", tags=["Quant"])


class FactorResponse(BaseModel):
    ticker: str
    as_of: str = Field(description="ISO timestamp for last bar time used")
    window_days: int = Field(default=20)
    factors: Dict[str, float]


class SignalResponse(BaseModel):
    ticker: str
    as_of: str
    signal: str = Field(description="one of: long, flat, short")
    rationale: Dict[str, Any]


def _coerce_closes_and_dates(ohlcv: Any) -> Tuple[List[float], List[Any]]:
    """Return (closes, dates) from heterogeneous OHLCV payloads (DataFrame or list[dict])."""
    closes: List[float] = []
    dates: List[Any] = []
    try:
        # pandas.DataFrame path
        import pandas as pd  # type: ignore

        if hasattr(ohlcv, "__class__") and isinstance(ohlcv, pd.DataFrame):
            df = ohlcv
            # Normalize columns
            cols = {c.lower(): c for c in df.columns}
            close_col = cols.get("close") or cols.get("c")
            date_col = cols.get("date") or cols.get("datetime") or cols.get("index")
            series = df[close_col] if close_col in df.columns else None
            if series is not None:
                closes = [float(x) for x in series.tolist() if x is not None]
                if date_col and date_col in df.columns:
                    dates = df[date_col].tolist()
                else:
                    dates = getattr(df, "index", []) if df.index is not None else []
                return closes, dates
    except Exception:
        # fall through to list[dict]
        pass

    # list[dict] path
    if isinstance(ohlcv, list):
        for row in ohlcv:
            if not isinstance(row, dict):
                continue
            val = row.get("close") or row.get("Close") or row.get("c")
            dt = row.get("date") or row.get("Date") or row.get("datetime")
            try:
                if val is None:
                    continue
                closes.append(float(val))
                dates.append(dt)
            except Exception:
                continue
    return closes, dates


def _compute_factors_from_closes(
    closes: list[float], window: int = 20
) -> dict[str, float]:
    if not closes or len(closes) < window + 1:
        raise ValueError("Insufficient OHLCV length for factor computation")

    last = closes[-1]
    past = closes[-1 - window]
    momentum_20d = (last / past) - 1.0

    # Daily returns (simple) for volatility
    rets: list[float] = []
    for i in range(1, len(closes)):
        try:
            rets.append((closes[i] / closes[i - 1]) - 1.0)
        except Exception:
            rets.append(0.0)
    # Rolling std over last window
    tail = rets[-window:]
    mean = sum(tail) / len(tail)
    var = sum((r - mean) ** 2 for r in tail) / max(len(tail) - 1, 1)
    vol_20d = var**0.5

    sma = sum(closes[-window:]) / window
    sma_20d_deviation = (last / sma) - 1.0

    return {
        "momentum_20d": float(momentum_20d),
        "vol_20d": float(vol_20d),
        "sma_20d_dev": float(sma_20d_deviation),
    }


@router.get("/factors/{ticker}", response_model=FactorResponse)
async def get_factors(
    request: Request,
    ticker: str = Path(..., description="Stock ticker symbol"),
    window: int = 20,
):
    client = getattr(request.app.state, "http_client", None)
    cache = getattr(request.app.state, "cache", None)
    if client is None:
        raise HTTPException(status_code=503, detail="HTTP client unavailable")

    request_id = f"quant-{ticker}-{window}"
    # period/interval are coarse defaults for M1
    ohlcv = await fetch_ohlcv_data(
        symbol=ticker,
        period="1y",
        interval="1d",
        client=client,
        cache=cache,
        request_id=request_id,
    )
    if not ohlcv:
        raise HTTPException(status_code=502, detail="OHLCV unavailable")

    closes, _ = _coerce_closes_and_dates(ohlcv)
    factors = _compute_factors_from_closes(closes, window=window)
    as_of = datetime.utcnow().isoformat()
    return FactorResponse(
        ticker=ticker.upper(), as_of=as_of, window_days=window, factors=factors
    )


@router.get("/signals/{ticker}", response_model=SignalResponse)
async def get_signals(
    request: Request,
    ticker: str = Path(..., description="Stock ticker symbol"),
    window: int = 20,
):
    client = getattr(request.app.state, "http_client", None)
    cache = getattr(request.app.state, "cache", None)
    if client is None:
        raise HTTPException(status_code=503, detail="HTTP client unavailable")

    request_id = f"quant-signal-{ticker}-{window}"
    ohlcv = await fetch_ohlcv_data(
        symbol=ticker,
        period="1y",
        interval="1d",
        client=client,
        cache=cache,
        request_id=request_id,
    )
    if not ohlcv:
        raise HTTPException(status_code=502, detail="OHLCV unavailable")

    closes, _ = _coerce_closes_and_dates(ohlcv)
    factors = _compute_factors_from_closes(closes, window=window)

    # Simple momentum+vol filter baseline
    mom = factors.get("momentum_20d", 0.0)
    vol = factors.get("vol_20d", 0.0)
    mom_th = 0.02  # +2% over 20d
    vol_th = 0.06  # ~6% 20d std
    if mom > mom_th and vol <= vol_th:
        signal = "long"
    elif mom < -mom_th and vol <= vol_th:
        signal = "short"
    else:
        signal = "flat"

    as_of = datetime.utcnow().isoformat()
    return SignalResponse(
        ticker=ticker.upper(),
        as_of=as_of,
        signal=signal,
        rationale={
            "factors": factors,
            "thresholds": {"momentum_20d": mom_th, "vol_20d": vol_th},
        },
    )


class BacktestRequest(BaseModel):
    ticker: str
    window: int = 20
    momentum_threshold: float = 0.02  # 2% over window
    vol_cap: float = 0.06  # 6% 20d std cap
    allow_short: bool = False
    costs_bps: float = 5.0  # 5 bps per trade (position change)


class BacktestMetrics(BaseModel):
    total_return: float
    cagr: float
    vol_ann: float
    sharpe: float
    max_drawdown: float
    trades: int


class BacktestResponse(BaseModel):
    ticker: str
    as_of: str
    window_days: int
    params: Dict[str, Any]
    metrics: BacktestMetrics


def _compute_bar_by_bar_backtest(
    closes: List[float],
    window: int,
    mom_th: float,
    vol_cap: float,
    allow_short: bool,
    costs_bps: float,
) -> BacktestMetrics:
    if len(closes) < window + 2:
        raise ValueError("Insufficient OHLCV length for backtest")

    # Precompute daily returns
    rets = [(closes[i] / closes[i - 1]) - 1.0 for i in range(1, len(closes))]

    # Rolling factors each bar
    positions: List[float] = []
    last_pos = 0.0
    trades = 0

    for i in range(1, len(closes)):
        if i <= window:
            positions.append(0.0)
            continue
        # momentum and vol on [i-window, i)
        mom = (closes[i] / closes[i - window]) - 1.0
        tail = rets[i - window : i]
        mean = sum(tail) / len(tail)
        var = sum((r - mean) ** 2 for r in tail) / max(len(tail) - 1, 1)
        vol = var**0.5

        desired = 0.0
        if mom > mom_th and vol <= vol_cap:
            desired = 1.0
        elif allow_short and (mom < -mom_th and vol <= vol_cap):
            desired = -1.0

        if desired != last_pos:
            trades += 1
            last_pos = desired
        positions.append(desired)

    # Strategy returns (apply costs on position change)
    strat_rets: List[float] = []
    prev_pos = 0.0
    for i, r in enumerate(rets):
        pos = positions[i] if i < len(positions) else 0.0
        ret = pos * r
        if i < len(positions) and pos != prev_pos:
            ret -= abs(pos - prev_pos) * (costs_bps / 10000.0)
        strat_rets.append(ret)
        prev_pos = pos

    # Metrics
    total_return = math.prod(1.0 + x for x in strat_rets if not math.isnan(x)) - 1.0
    n = len(strat_rets)
    if n == 0:
        raise ValueError("No returns to evaluate")
    mean_daily = sum(strat_rets) / n
    var_daily = sum((x - mean_daily) ** 2 for x in strat_rets) / max(n - 1, 1)
    vol_ann = math.sqrt(var_daily) * math.sqrt(252.0)
    cagr = (1.0 + total_return) ** (252.0 / n) - 1.0 if n > 0 else 0.0
    sharpe = (mean_daily * 252.0) / vol_ann if vol_ann > 1e-12 else 0.0

    # Max drawdown from equity curve
    eq = []
    c = 1.0
    max_dd = 0.0
    peak = 1.0
    for r in strat_rets:
        c *= 1.0 + r
        peak = max(peak, c)
        dd = (c / peak) - 1.0
        if dd < max_dd:
            max_dd = dd

    return BacktestMetrics(
        total_return=float(total_return),
        cagr=float(cagr),
        vol_ann=float(vol_ann),
        sharpe=float(sharpe),
        max_drawdown=float(max_dd),
        trades=trades,
    )


@router.post("/backtest", response_model=BacktestResponse)
async def backtest(request: Request, payload: BacktestRequest):
    client = getattr(request.app.state, "http_client", None)
    cache = getattr(request.app.state, "cache", None)
    if client is None:
        raise HTTPException(status_code=503, detail="HTTP client unavailable")

    req_id = f"bt-{payload.ticker}-{payload.window}"
    ohlcv = await fetch_ohlcv_data(
        symbol=payload.ticker,
        period="3y",
        interval="1d",
        client=client,
        cache=cache,
        request_id=req_id,
    )
    if not ohlcv:
        raise HTTPException(status_code=502, detail="OHLCV unavailable")

    closes, _ = _coerce_closes_and_dates(ohlcv)
    metrics = _compute_bar_by_bar_backtest(
        closes=closes,
        window=payload.window,
        mom_th=payload.momentum_threshold,
        vol_cap=payload.vol_cap,
        allow_short=payload.allow_short,
        costs_bps=payload.costs_bps,
    )
    return BacktestResponse(
        ticker=payload.ticker.upper(),
        as_of=datetime.utcnow().isoformat(),
        window_days=payload.window,
        params=payload.model_dump(),
        metrics=metrics,
    )


# Expose alias for central api router include
quant_router = router
