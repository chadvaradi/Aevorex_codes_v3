"""
Model Builders for Stock Data
"""

import logging
from datetime import datetime
import pandas as pd

from fastapi.responses import JSONResponse
from fastapi import status

logger = logging.getLogger(__name__)


def build_technical_analysis_response(
    symbol: str,
    technical_indicators: dict,
    ohlcv_df: "pd.DataFrame",
    request_id: str,
    processing_time: float,
    cache_hit: bool,
):
    """
    Builds the JSONResponse for the technical analysis endpoint.
    """
    latest_ohlcv = None
    change_percent_day = None
    if ohlcv_df is not None and not ohlcv_df.empty:
        try:
            last_row = ohlcv_df.iloc[-1]
            latest_ohlcv = {
                "timestamp": int(last_row.name.timestamp() * 1000)
                if hasattr(last_row.name, "timestamp")
                else None,
                "open": float(last_row.get("open", 0)),
                "high": float(last_row.get("high", 0)),
                "low": float(last_row.get("low", 0)),
                "close": float(last_row.get("close", 0)),
                "volume": int(last_row.get("volume", 0)),
            }

            if len(ohlcv_df) >= 2:
                prev_close = float(ohlcv_df.iloc[-2].get("close", 0))
                curr_close = float(last_row.get("close", 0))
                if prev_close:
                    change_percent_day = round(
                        ((curr_close - prev_close) / prev_close) * 100, 4
                    )
        except Exception as e:
            logger.warning(f"[{request_id}] ⚠️ Error extracting latest OHLCV: {e}")

    analytics_data = {
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "latest_ohlcv": latest_ohlcv,
        "change_percent_day": change_percent_day,
        "latest_indicators": technical_indicators,
        "indicator_count": len(technical_indicators),
        "data_quality": "high" if len(technical_indicators) > 5 else "medium",
        "optimization_metrics": {
            "parallel_fetch_used": True,
            "cache_enabled": True,
            "fallback_used": False,
        },
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "metadata": {
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "aevorex-optimized-api",
                "cache_hit": cache_hit,
                "processing_time_ms": processing_time,
                "data_type": "technical_analysis_optimized",
                "provider": "parallel_fetcher_v2",
                "version": "3.2.0-optimized",
            },
            "technical_analysis": analytics_data,
        },
    )
