"""
ECB Unified Router
=================

Configuration-driven router for all standard ECB dataflows.
Handles all ECB SDMX dataflows through a single generic endpoint.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, Path

from backend.utils.cache_service import CacheService
from backend.api.deps import get_cache_service
from backend.core.services.macro.macro_service import MacroDataService
from backend.utils.logger_config import get_logger

from backend.core.fetchers.macro.ecb_client.config import (
    get_dataflow_config,
    list_dataflows,
)

router = APIRouter(prefix="/ecb", tags=["ECB Unified"])
logger = get_logger(__name__)


def _get_macro_service(cache: CacheService | None) -> MacroDataService:
    """Get MacroDataService instance."""
    return MacroDataService(cache)


@router.get("/flows", summary="List available ECB dataflows")
async def list_ecb_flows():
    """List all available ECB dataflows."""
    flows = list_dataflows()
    return {
        "status": "success",
        "count": len(flows),
        "data": flows,
        "metadata": {
            "description": "Available ECB SDMX dataflows",
            "total_flows": len(flows),
        },
    }


@router.get("/{flow}", summary="Get ECB dataflow data")
async def get_ecb_dataflow(
    flow: str = Path(..., description="ECB dataflow name (e.g., hicp, bls, cbd)"),
    start: Optional[date] = Query(None, description="Start date YYYY-MM-DD"),
    end: Optional[date] = Query(None, description="End date YYYY-MM-DD"),
    cache: CacheService = Depends(get_cache_service),
):
    """
    Generic endpoint for all ECB dataflows.

    Uses configuration-driven approach to fetch data from ECB SDMX API.
    All standard ECB dataflows (hicp, bls, cbd, ciss, etc.) are handled here.
    """
    try:
        # Get dataflow configuration
        config = get_dataflow_config(flow)
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"ECB dataflow '{flow}' not found. Available flows: {list_dataflows()}",
            )

        # Get macro service
        service = _get_macro_service(cache)

        # Map flow name to service method
        method_map = {
            "bls": service.get_ecb_bls,
            "cbd": service.get_ecb_cbd,
            "ciss": service.get_ecb_ciss,
            "hicp": service.get_ecb_hicp,
            "rpp": service.get_ecb_rpp,
            "trd": service.get_ecb_trd,
            "irs": service.get_ecb_irs,
            "mir": service.get_ecb_mir,
            "ivf": service.get_ecb_ivf,
            "spf": service.get_ecb_spf,
            "pss": service.get_ecb_pss,
            "cpp": service.get_ecb_cpp,
        }

        # Get the appropriate service method
        service_method = method_map.get(flow)
        if not service_method:
            raise HTTPException(
                status_code=501,
                detail=f"ECB dataflow '{flow}' not implemented in MacroDataService",
            )

        # Fetch data
        logger.info(f"Fetching ECB {flow} data from {start} to {end}")
        data = await service_method(start, end)

        # Handle no data case
        if not data:
            return {
                "status": "success",
                "count": 0,
                "data": {},
                "metadata": {
                    "dataflow": flow,
                    "description": config.get("metadata", {}).get("description", ""),
                    "source": config.get("metadata", {}).get("source", "ECB SDMX"),
                    "fallback": True,
                    "message": f"No data available for {flow} in the specified date range",
                },
            }

        # Return successful response
        return {
            "status": "success",
            "count": len(data) if isinstance(data, (list, dict)) else 1,
            "data": data,
            "metadata": {
                "dataflow": flow,
                "description": config.get("metadata", {}).get("description", ""),
                "source": config.get("metadata", {}).get("source", "ECB SDMX"),
                "frequency": config.get("metadata", {}).get("frequency", "unknown"),
                "series_count": len(config.get("series", [])),
                "date_range": {
                    "start": start.isoformat() if start else None,
                    "end": end.isoformat() if end else None,
                },
            },
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except AttributeError as exc:
        logger.error(f"ECB {flow} service method missing: {exc}")
        return {
            "status": "success",
            "count": 0,
            "data": {},
            "metadata": {
                "dataflow": flow,
                "error": f"Service method not implemented: {exc}",
                "fallback": True,
            },
        }
    except Exception as exc:
        logger.error(f"Unexpected error fetching ECB {flow} data: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while fetching {flow} data: {str(exc)}",
        )


@router.get("/{flow}/config", summary="Get ECB dataflow configuration")
async def get_ecb_config(flow: str = Path(..., description="ECB dataflow name")):
    """Get configuration for a specific ECB dataflow."""
    config = get_dataflow_config(flow)
    if not config:
        raise HTTPException(status_code=404, detail=f"ECB dataflow '{flow}' not found")

    return {
        "status": "success",
        "data": config,
        "metadata": {"dataflow": flow, "description": "ECB dataflow configuration"},
    }
