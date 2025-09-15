"""
EODHD API Client dependency for FastAPI endpoints.
"""

import httpx
from fastapi import HTTPException, Request
from backend.config.eodhd import settings as eodhd_settings
from backend.api.deps import get_http_client


class EODHDClient:
    """EODHD API client wrapper."""
    
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
        self.base_url = eodhd_settings.BASE_URL
        self.api_key = eodhd_settings.API_KEY
        
        if not self.api_key:
            raise HTTPException(status_code=503, detail="EODHD API key not configured.")
    
    async def get(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        timeout: float = 10.0
    ) -> dict:
        """Make a GET request to the EODHD API."""
        if params is None:
            params = {}
        # Add API key and format to params
        params["api_token"] = self.api_key
        params["fmt"] = "json"

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = await self.http_client.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Truncate error message for clarity
            err_text = e.response.text
            if len(err_text) > 200:
                err_text = err_text[:200] + "..."
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"EODHD API error: {err_text}"
            )
        except Exception as e:
            msg = str(e)
            if len(msg) > 200:
                msg = msg[:200] + "..."
            raise HTTPException(
                status_code=500,
                detail=f"EODHD API request failed: {msg}"
            )


async def get_eodhd_client(request: Request) -> EODHDClient:
    """FastAPI dependency to get an EODHD client instance."""
    http_client = await get_http_client(request)
    return EODHDClient(http_client)
