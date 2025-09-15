"""
ECB Service

European Central Bank dataflows and SDMX integration.
Handles ECB SDMX API calls and data processing.
"""

from typing import Dict, Any, Optional
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


import httpx
import asyncio

class ECBService:
    """Service for ECB dataflows and SDMX integration."""

    def __init__(self):
        self.provider = "ecb_sdmx"
        self.base_url = "https://sdw-wsrest.ecb.europa.eu/service"

    async def get_dataflow_list(self) -> Dict[str, Any]:
        """Get list of available ECB dataflows."""
        url = f"{self.base_url}/dataflow/ECB"
        logger.info(f"Fetching ECB dataflow list from {url}")
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(url, headers={"Accept": "application/json"})
                resp.raise_for_status()
                data = resp.json()
                logger.info("Successfully fetched ECB dataflow list")
                return data
        except Exception as e:
            logger.error(f"Error fetching ECB dataflow list: {e}")
            return {"status": "error", "message": str(e)}

    async def get_estr_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get ECB €STR time series data.
        Dataset: EST.B.EURO.RT.HSTA (Historical €STR)
        """
        # SDMX key: EST.B.EURO.RT.HSTA
        url = f"{self.base_url}/data/EST.B.EURO.RT.HSTA"
        params = {
            "startPeriod": start_date,
            "endPeriod": end_date,
        }
        logger.info(f"Fetching ECB €STR data from {url} with params {params}")
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(url, params=params, headers={"Accept": "application/json"})
                resp.raise_for_status()
                data = resp.json()
                logger.info("Successfully fetched ECB €STR data")
                return data
        except Exception as e:
            logger.error(f"Error fetching ECB €STR data: {e}")
            return {"status": "error", "message": str(e)}

    async def get_yield_curve_data(self, maturity: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get ECB yield curve data.
        Example SDMX key: YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y (1 year)
        Maturity: e.g. 'SR_1Y', 'SR_10Y', etc.
        """
        dataset_base = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM"
        sdmx_key = f"{dataset_base}.{maturity}"
        url = f"{self.base_url}/data/{sdmx_key}"
        params = {
            "startPeriod": start_date,
            "endPeriod": end_date,
        }
        logger.info(f"Fetching ECB yield curve data from {url} with params {params}")
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(url, params=params, headers={"Accept": "application/json"})
                resp.raise_for_status()
                data = resp.json()
                logger.info("Successfully fetched ECB yield curve data")
                return data
        except Exception as e:
            logger.error(f"Error fetching ECB yield curve data: {e}")
            return {"status": "error", "message": str(e)}

    async def get_policy_rates_data(self, rate_type: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get ECB policy rates data.
        Example SDMX key: FM.M.U2.EUR.4F.KR.MRR_FR.LEV (main refinancing rate)
        rate_type: e.g. 'MRR_FR' (main refinancing), 'DFR' (deposit facility), 'MRO' (marginal lending)
        """
        # Build key: FM.M.U2.EUR.4F.KR.{rate_type}.LEV
        sdmx_key = f"FM.M.U2.EUR.4F.KR.{rate_type}.LEV"
        url = f"{self.base_url}/data/{sdmx_key}"
        params = {
            "startPeriod": start_date,
            "endPeriod": end_date,
        }
        logger.info(f"Fetching ECB policy rates data from {url} with params {params}")
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(url, params=params, headers={"Accept": "application/json"})
                resp.raise_for_status()
                data = resp.json()
                logger.info("Successfully fetched ECB policy rates data")
                return data
        except Exception as e:
            logger.error(f"Error fetching ECB policy rates data: {e}")
            return {"status": "error", "message": str(e)}


__all__ = ["ECBService"]
