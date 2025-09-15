"""
Inflation (HICP) Handler

Provides Euro Area Inflation (HICP) data endpoints.
Handles HICP data via ECB unified dataflows.
"""

from fastapi import APIRouter, Depends, Query
from datetime import date
from typing import Optional, Dict, Any

from backend.core.services.macro.macro_service import MacroDataService, get_macro_service

router = APIRouter(
    tags=["Macro"]
)


@router.get("/", summary="Eurozone Inflation Time Series (HICP)")
async def get_inflation_data(
    start_date: Optional[date] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[date] = Query(None, description="End date (ISO format)"),
    macro_service: MacroDataService = Depends(get_macro_service)
) -> Dict[str, Any]:
    """
    Get Eurozone inflation time series data (HICP).
    Returns Euro Area Inflation (HICP) data via ECB unified dataflows.
    
    This endpoint wraps the ECB unified dataflows for HICP (Harmonised Index of Consumer Prices).
    Returns inflation data for the Euro Area with optional date range filtering.
    
    Args:
        start_date: Optional start date for the data range
        end_date: Optional end date for the data range
        macro_service: Injected macro data service
        
    Returns:
        Dict containing inflation data with status, metadata, and data fields
    """
    return await macro_service.get_ecb_flow_data(
        flow="hicp",
        start_date=start_date,
        end_date=end_date
    )


__all__ = ["router"]
