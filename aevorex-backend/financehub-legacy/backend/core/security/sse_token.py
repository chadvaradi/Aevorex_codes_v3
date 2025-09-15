"""
Ephemeral SSE token utilities.

Generates and validates short‑lived HMAC tokens that can be passed via
query string for EventSource requests where browsers cannot set custom
Authorization headers. Designed for gateway/CORS scenarios.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from backend.config import settings


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def mint_sse_token(subject: str, ttl_seconds: int = 120) -> str:
    """Create a short‑lived token bound to a subject (e.g., session id).

    The payload contains `sub` and `exp` unix timestamp. The token structure is
    `<b64(payload)>.<b64(signature)>` where signature = HMAC_SHA256(secret, payload_bytes).
    """
    now = int(time.time())
    payload: dict[str, Any] = {"sub": subject, "exp": now + max(30, ttl_seconds)}
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    secret = (
        settings.GOOGLE_AUTH.SECRET_KEY.get_secret_value()
        if settings.GOOGLE_AUTH.SECRET_KEY
        else "finhub_sse"
    )
    sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    return f"{_b64url_encode(body)}.{_b64url_encode(sig)}"


def verify_sse_token(token: str) -> bool:
    """Validate token integrity and expiration."""
    try:
        body_b64, sig_b64 = token.split(".", 1)
        body = _b64url_decode(body_b64)
        secret = (
            settings.GOOGLE_AUTH.SECRET_KEY.get_secret_value()
            if settings.GOOGLE_AUTH.SECRET_KEY
            else "finhub_sse"
        )
        expected_sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_sig, _b64url_decode(sig_b64)):
            return False
        payload = json.loads(body.decode("utf-8"))
        exp = int(payload.get("exp", 0))
        if exp <= 0 or int(time.time()) > exp:
            return False
        return True
    except Exception:
        return False
