"""Simple header-rewriting proxy for ECB Data Portal (#008 compliant, <60 LOC)."""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Request, Response

router = APIRouter(prefix="/proxy/ecb", tags=["ECB Proxy"])

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36",
    "Referer": "https://sdw.ecb.europa.eu/",
    "Cookie": "__Secure_SDWTS=1",
}


@router.get("/{full_path:path}")  # noqa: D401 – simple passthrough
async def proxy_ecb(full_path: str, request: Request):
    """Forward request to ECB API with anti-bot headers."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream = f"https://data-api.ecb.europa.eu/{full_path}"
        r = await client.get(upstream, params=request.query_params, headers=_HEADERS)
    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=r.headers.get("content-type", "application/json"),
    )
