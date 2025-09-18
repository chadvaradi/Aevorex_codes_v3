"""Facade service that aggregates macroeconomic data sources (ECB, BUBOR, etc)."""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Optional

from .base_service import BaseMacroService
from .fetch_mixins import ECBStandardMixin
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


def get_macro_service() -> MacroDataService:
    """Get a singleton instance of MacroDataService."""
    return MacroDataService()


class MacroDataService(ECBStandardMixin, BaseMacroService):
    """Facade service that aggregates macroeconomic data sources (ECB, BUBOR, etc).

    This service provides a clean interface to all macroeconomic data sources
    without stub implementations. All methods forward to real client implementations
    and raise RuntimeError if clients are not properly configured.
    """

    def __init__(self, cache_service=None):
        super().__init__(cache_service)
        # Expose asyncio loop for backward compatibility with legacy sync wrappers
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:  # event loop not yet set for the thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        logger.info("MacroDataService initialized with real client implementations")

    # ---- Real client forwarding methods (no stubs) --------------------
    async def get_bubor_history(self, start_date: date, end_date: date) -> dict:
        """Get BUBOR (Budapest Interbank Offered Rate) history.

        Args:
            start_date: Start date for BUBOR data
            end_date: End date for BUBOR data

        Returns:
            Dict with BUBOR rates by tenor and date

        Raises:
            RuntimeError: If BUBOR client is not configured
        """
        if not hasattr(self, "bubor_client") or self.bubor_client is None:
            raise RuntimeError("BUBOR client not configured")

        logger.info(f"Fetching BUBOR history from {start_date} to {end_date}")
        return await self.bubor_client.get_bubor_history(start_date, end_date)

    async def get_ecb_monetary_policy_info(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> dict:
        """Get ECB monetary policy information and commentary.

        Args:
            start_date: Optional start date for policy data
            end_date: Optional end date for policy data

        Returns:
            Dict with ECB monetary policy information

        Raises:
            RuntimeError: If ECB client is not configured
        """
        if not hasattr(self, "ecb_client") or self.ecb_client is None:
            raise RuntimeError("ECB client not configured")

        logger.info(
            f"Fetching ECB monetary policy info from {start_date} to {end_date}"
        )

        # Get policy rates as the core monetary policy data
        policy_rates = await self.get_ecb_policy_rates(start_date, end_date)

        # Get yield curve for additional monetary policy context
        yield_curve = await self.get_ecb_yield_curve(start_date, end_date)

        # Get ESTR rate for overnight policy rate
        estr_rate = await self.get_ecb_estr_rate(start_date, end_date)

        return {
            "current_stance": "data_driven",
            "summary": "Real ECB monetary policy data retrieved from live sources",
            "policy_rates": policy_rates,
            "yield_curve": yield_curve,
            "estr_rate": estr_rate,
            "data_source": "ECB SDMX API",
            "timestamp": asyncio.get_event_loop().time()
            if asyncio.get_event_loop().is_running()
            else None,
        }

    async def get_ecb_flow_data(
        self, flow: str, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> dict:
        """Generic method to fetch ECB dataflow data.
        
        Args:
            flow: ECB dataflow name (e.g., 'hicp', 'hur', 'bls', 'cbd')
            start_date: Optional start date for data
            end_date: Optional end date for data
            
        Returns:
            Dict with ECB dataflow data
            
        Raises:
            RuntimeError: If ECB client is not configured or flow not supported
        """
        if not hasattr(self, "ecb_client") or self.ecb_client is None:
            raise RuntimeError("ECB client not configured")

        logger.info(f"Fetching ECB {flow} dataflow from {start_date} to {end_date}")
        
        # Map flow names to service methods
        flow_method_map = {
            "hicp": self.get_ecb_hicp,
            "hur": self.get_ecb_hur,  # Unemployment rate
            "bls": self.get_ecb_bls,
            "cbd": self.get_ecb_cbd,
            "ciss": self.get_ecb_ciss,
            "rpp": self.get_ecb_rpp,
            "trd": self.get_ecb_trd,
            "irs": self.get_ecb_irs,
            "mir": self.get_ecb_mir,
            "ivf": self.get_ecb_ivf,
            "spf": self.get_ecb_spf,
            "pss": self.get_ecb_pss,
            "cpp": self.get_ecb_cpp,
        }
        
        # Get the appropriate service method
        service_method = flow_method_map.get(flow)
        if not service_method:
            raise RuntimeError(f"ECB dataflow '{flow}' not supported. Available flows: {list(flow_method_map.keys())}")
        
        # Fetch data using the appropriate method
        try:
            data = await service_method(start_date, end_date)
            return {
                "status": "success",
                "flow": flow,
                "data": data,
                "data_source": "ECB SDMX API",
                "start_date": start_date,
                "end_date": end_date
            }
        except Exception as e:
            logger.error(f"Error fetching ECB {flow} data: {e}")
            return {
                "status": "error",
                "flow": flow,
                "message": f"Failed to fetch ECB {flow} data: {str(e)}",
                "data": None
            }
