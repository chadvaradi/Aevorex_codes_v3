"""
API endpoints for user authentication (Google OAuth).
This file is migrated from the old monolithic auth.py.
"""

import logging
from fastapi import APIRouter, Request, Response, Depends
import time
import hmac
import hashlib
import base64
import json
import secrets
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.responses import HTMLResponse
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import (
    InvalidClientError,
    InvalidGrantError,
    OAuth2Error,
)
from backend.middleware.jwt_auth.deps import get_current_user
from starlette.exceptions import HTTPException
from starlette import status
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth")


# --- Google OAuth2 Settings ---
# Note: These should be populated via environment variables
CLIENT_ID = settings.GOOGLE_AUTH.CLIENT_ID
CLIENT_SECRET = (
    settings.GOOGLE_AUTH.CLIENT_SECRET.get_secret_value()
    if settings.GOOGLE_AUTH.CLIENT_SECRET
    else None
)
REDIRECT_URI = (
    str(settings.GOOGLE_AUTH.REDIRECT_URI)
    if settings.GOOGLE_AUTH.REDIRECT_URI
    else None
)
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

# Initialize Google OAuth client
google_client_id = settings.GOOGLE_AUTH.CLIENT_ID



# --- Internal Helpers ---

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign_state(payload: dict, secret: str) -> str:
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    return f"{_b64url_encode(body)}.{_b64url_encode(sig)}"


def _verify_state(state: str, secret: str, max_age_seconds: int = 600) -> dict | None:
    try:
        body_b64, sig_b64 = state.split(".", 1)
        body = _b64url_decode(body_b64)
        expected_sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_sig, _b64url_decode(sig_b64)):
            return None
        payload = json.loads(body.decode("utf-8"))
        ts = int(payload.get("ts", 0))
        if ts <= 0 or (int(time.time()) - ts) > max_age_seconds:
            return None
        return payload
    except Exception:
        return None

# --- OAuth2 Flow Endpoints ---



@router.get("/login")
async def login(request: Request, next: str = "/", redirect: bool = False):
    """
    Returns a JSON payload containing the Google OAuth authorization URL rather than
    issuing an immediate 307 redirect. This avoids automated scanners flagging the
    endpoint as a non-200 response while still allowing the frontend to perform
    the redirect client-side.
    """
    if not settings.GOOGLE_AUTH.ENABLED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Google Auth is not enabled."
        )

    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
        logger.error("Google Auth credentials are not configured in settings.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is not configured.",
        )

    google = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    # Generate stateless, HMAC-signed state so callback nem függ a session cookie jelenlététől
    state_payload = {
        "nonce": secrets.token_urlsafe(16),
        "ts": int(time.time()),
        "next": next,
    }
    signed_state = _sign_state(
        state_payload, settings.GOOGLE_AUTH.SECRET_KEY.get_secret_value()
    )
    authorization_url, _ = google.authorization_url(
        AUTHORIZATION_BASE_URL,
        access_type="offline",
        prompt="select_account",
        state=signed_state,
    )

    # Store the redirect path in the session
    request.session["next_url"] = next

    # If explicit redirect is requested, issue a server-side redirect to Google
    if redirect:
        return RedirectResponse(
            url=authorization_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    # Default: return the URL in JSON so the frontend can handle navigation
    return JSONResponse(
        status_code=200, content={"auth_url": authorization_url, "status": "ok"}
    )


@router.get("/start")
async def start(request: Request, next: str = "/"):
    """
    Cookie-seed + redirect starter for strict browsers.
    1) Creates OAuth state in the server-side session (sets cookie on this HTML response)
    2) Immediately navigates the browser to Google's authorization URL from same-site HTML
    """
    if not settings.GOOGLE_AUTH.ENABLED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Google Auth is not enabled."
        )

    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
        logger.error("Google Auth credentials are not configured in settings.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is not configured.",
        )

    google = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    # Generate stateless, HMAC-signed state and redirect immediately
    state_payload = {
        "nonce": secrets.token_urlsafe(16),
        "ts": int(time.time()),
        "next": next,
    }
    signed_state = _sign_state(
        state_payload, settings.GOOGLE_AUTH.SECRET_KEY.get_secret_value()
    )
    authorization_url, _ = google.authorization_url(
        AUTHORIZATION_BASE_URL,
        access_type="offline",
        prompt="select_account",
        state=signed_state,
    )
    # Persist next hop for post-login redirect
    request.session["next_url"] = next

    html = f"""
    <!doctype html>
    <html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'/>
    <title>Signing in…</title></head>
    <body style='font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif'>
      <noscript>Redirecting to Google… <a href='{authorization_url}'>Continue</a></noscript>
      <script>location.replace({authorization_url!r});</script>
    </body></html>
    """
    return HTMLResponse(content=html, status_code=200)


@router.get("/callback")
async def callback(request: Request, response: Response):
    """
    Handles the callback from Google after user authentication.
    """
    if not settings.GOOGLE_AUTH.ENABLED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Google Auth is not enabled."
        )

    # Stateless state validation (HMAC) – no dependency on prior session cookie
    incoming_state = request.query_params.get("state")
    if not incoming_state:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing state parameter."
        )
    verified = _verify_state(
        incoming_state, settings.GOOGLE_AUTH.SECRET_KEY.get_secret_value()
    )
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid state parameter. CSRF attack detected.",
        )

    # IMPORTANT: Bind redirect_uri on the OAuth2Session and DO NOT pass it again to fetch_token,
    # because requests-oauthlib forwards `redirect_uri=self.redirect_uri` explicitly and
    # passing it again via kwargs would cause "multiple values for keyword argument 'redirect_uri'".
    google = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    try:
        # Use explicit code + redirect_uri to avoid host mismatch when the
        # callback is proxied through API Gateway (the backend sees its own
        # run.app host, while Google redirected to the gateway host).
        auth_code = request.query_params.get("code")
        if not auth_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing authorization code.",
            )
        token = google.fetch_token(
            TOKEN_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            code=auth_code,
            include_client_id=True,
        )
        request.session["oauth_token"] = token
        # Pop state only after a successful token exchange
        request.session.pop("oauth_state", None)
    except InvalidClientError as e:
        logger.error(
            "Google token exchange failed: invalid_client: %s",
            getattr(e, "description", str(e)),
        )
        if request.query_params.get("debug") == "1":
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_client",
                    "detail": getattr(e, "description", str(e)),
                },
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch token.",
        )
    except InvalidGrantError as e:
        logger.error(
            "Google token exchange failed: invalid_grant: %s",
            getattr(e, "description", str(e)),
        )
        if request.query_params.get("debug") == "1":
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_grant",
                    "detail": getattr(e, "description", str(e)),
                },
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch token.",
        )
    except OAuth2Error as e:
        logger.error(
            "Google token exchange failed (oauth2): %s",
            getattr(e, "description", str(e)),
        )
        if request.query_params.get("debug") == "1":
            return JSONResponse(
                status_code=400,
                content={
                    "error": "oauth2_error",
                    "detail": getattr(e, "description", str(e)),
                },
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch token.",
        )
    except Exception as e:
        # Try to surface Google's error_description without leaking secrets
        err_detail = None
        try:
            resp = getattr(e, "response", None)
            if resp is not None:
                data = resp.json() if hasattr(resp, "json") else None
                if isinstance(data, dict):
                    err_detail = data.get("error_description") or data.get("error")
        except Exception:
            pass
        if err_detail:
            logger.error(f"Failed to fetch token from Google: {err_detail}")
        else:
            logger.error(f"Failed to fetch token from Google: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch token.",
        )

    user_info = google.get("https://www.googleapis.com/oauth2/v3/userinfo").json()

    # Store user info in session
    request.session["user"] = {
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
    }

    # Initialize a default plan if not set (soft paywall baseline)
    # Plans: free | pro | team | enterprise
    if "plan" not in request.session:
        request.session["plan"] = "free"

    # Generate JWT token for API access
    from backend.middleware.jwt_auth.config import JWT_SECRET_KEY, JWT_ALGORITHM
    import jwt

    jwt_payload = {
        "user_id": user_info.get("sub"),  # Google user ID
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "exp": datetime.utcnow() + timedelta(hours=24),  # 24 hour expiry
        "iat": datetime.utcnow(),
    }
    jwt_token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Store JWT token in session for frontend access
    request.session["jwt_token"] = jwt_token

    # Redirect to the path stored in the session, or to the root
    next_url = request.session.pop("next_url", "/")
    return RedirectResponse(url=next_url)



# --- Session Management Endpoints ---

@router.get("/status")
async def auth_status(request: Request):
    """
    Returns the current user's authentication status.
    """
    if "user" in request.session:
        return JSONResponse(
            content={
                "status": "authenticated",
                "user": request.session["user"],
                "plan": request.session.get("plan", "free"),
            }
        )
    return JSONResponse(content={"status": "unauthenticated", "user": None})


# Note: /auth/start implemented above; no alias to avoid duplicate route


# Alias expected by frontend: /api/v1/auth/me → same payload shape
@router.get("/me")
async def auth_me(request: Request):
    if "user" in request.session:
        return JSONResponse(
            content={
                "status": "authenticated",
                "authenticated": True,
                "user": request.session["user"],
                "plan": request.session.get("plan", "free"),
                "jwt_token": request.session.get(
                    "jwt_token"
                ),  # Include JWT token for frontend
            }
        )
    return JSONResponse(
        content={"status": "unauthenticated", "authenticated": False, "user": None}
    )


# JWT-based /auth/me endpoint for API access
@router.get("/me/jwt")
async def auth_me_jwt(current_user: dict = Depends(get_current_user)):
    """
    JWT-based authentication endpoint for API access.
    Returns user information from JWT token.
    """
    return JSONResponse(
        content={
            "status": "authenticated",
            "authenticated": True,
            "user": current_user,
            "plan": current_user.get("plan", "free"),
        }
    )


# Unified /logout endpoint – supports both GET and POST to guarantee a 200
# response without relying on method-specific calls.  This eliminates the prior
# 405 status when the client attempted a GET request.


@router.api_route("/logout", methods=["GET", "POST"])
async def logout(request: Request):
    """
    Clears the user's session, effectively logging them out.
    """
    request.session.pop("user", None)
    request.session.pop("oauth_state", None)
    request.session.pop("oauth_token", None)
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "User logged out successfully.",
        },
    )


@router.post("/refresh-token")
async def refresh_token(request: Request):
    """
    Refreshes the OAuth2 token if it has expired.
    """
    if "oauth_token" not in request.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No token in session."
        )

    token = request.session["oauth_token"]

    google = OAuth2Session(CLIENT_ID, token=token)

    if google.authorized:
        # Token is still valid
        return JSONResponse(content={"status": "token_valid"})

    try:
        new_token = google.refresh_token(
            TOKEN_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
        )
        request.session["oauth_token"] = new_token
        logger.info("Successfully refreshed OAuth token.")
        return JSONResponse(content={"status": "token_refreshed", "token": new_token})
    except Exception as e:
        logger.error(f"Failed to refresh token: {e}")
        # If refresh fails, the user needs to log in again
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token. Please log in again.",
        )
