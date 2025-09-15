"""
Stock Progressive Models

Temporary models for chart and progressive data endpoints.
"""

from typing import Any, Dict
from pydantic import BaseModel


class ChartDataResponse(BaseModel):
    """Response model for chart data endpoints."""

    metadata: Dict[str, Any]
    chart_data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "symbol": "AAPL",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "source": "aevorex-real-api",
                    "processing_time_ms": 150.5,
                    "data_points": 252,
                },
                "chart_data": {
                    "symbol": "AAPL",
                    "ohlcv": [],
                    "period": "1y",
                    "interval": "1d",
                    "currency": "USD",
                    "timezone": "America/New_York",
                },
            }
        }
