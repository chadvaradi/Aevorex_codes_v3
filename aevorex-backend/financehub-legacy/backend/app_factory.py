"""
Application Factory
===================

This module contains the `create_app` factory function, which is responsible
for instantiating and configuring the FastAPI application, including its
middleware, routers, and exception handlers.
"""

# --- EARLY ENV LOADING ------------------------------------------------------
# Ensure every Uvicorn reload child sees the same env vars (e.g. API keys)
# Centralized env loader
from backend.config.env_loader import load_environment_once

load_environment_once()
from contextlib import asynccontextmanager
import logging
import httpx
import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from backend.middleware.deprecated_monitor import DeprecatedRouteMonitorMiddleware
from backend.api import api_router
from backend.config import settings
from backend.core.metrics import METRICS_EXPORTER, get_metrics_router
from backend.core.openapi import custom_openapi
from backend.utils.cache_service import CacheService
from backend.utils.logger_config import get_logger

# Module logger
logger = get_logger(__name__)


# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    lifespan_logger = logging.getLogger("aevorex_finbot_api.lifespan")
    lifespan_logger.info("Application startup sequence initiated...")

    # Initialize Database Pool
    lifespan_logger.info("Initializing database connection pool...")
    try:
        from backend.core.performance.database_pool import main_db_pool

        await main_db_pool.initialize()
        lifespan_logger.info("✅ Database pool initialized successfully.")
    except Exception as e:
        lifespan_logger.critical(
            f"FATAL: Database pool initialization failed: {e}", exc_info=True
        )
        # Continue without database for now

    # Initialize HTTP Client
    lifespan_logger.info("Initializing global HTTP client...")
    try:
        app.state.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            follow_redirects=True,
        )
        lifespan_logger.info("✅ HTTP Client initialized and attached to app state.")
    except Exception as e:
        lifespan_logger.critical(
            f"FATAL: HTTP Client initialization failed: {e}", exc_info=True
        )
        app.state.http_client = None

    # Initialize Cache Service
    if settings.CACHE.ENABLED:
        lifespan_logger.info("Cache is enabled, initializing CacheService...")
        try:
            cache_service = await CacheService.create(
                redis_host=settings.REDIS.HOST,
                redis_port=settings.REDIS.PORT,
                redis_db=settings.REDIS.DB_CACHE,
                connect_timeout=settings.REDIS.CONNECT_TIMEOUT_SECONDS,
                socket_op_timeout=settings.REDIS.SOCKET_TIMEOUT_SECONDS,
                default_ttl=settings.CACHE.DEFAULT_TTL_SECONDS,
                lock_ttl=settings.CACHE.LOCK_TTL_SECONDS,
                lock_retry_delay=settings.CACHE.LOCK_RETRY_DELAY_SECONDS,
            )
            app.state.cache = cache_service
            lifespan_logger.info(
                "✅ CacheService initialized and attached to app state."
            )
        except Exception as e:
            lifespan_logger.critical(
                f"FATAL: CacheService initialization failed: {e}", exc_info=True
            )
            # ⚠️ MVP STRATEGY: Fallback to in-memory cache for single-instance deployment
            # NOTE: This is intentional for MVP - no Redis required, memory cache is sufficient
            # for single-instance FinanceHub. Future scaling will use Supabase TTL cache.
            try:
                from backend.utils.cache_service import CacheService as _CS

                cache_service = await _CS.create("memory")
                app.state.cache = cache_service
                lifespan_logger.warning(
                    "⚠️ MVP Mode: Using in-memory CacheService (Redis not configured)."
                )
            except Exception as mem_err:
                lifespan_logger.critical(
                    f"Failed to initialise in-memory cache: {mem_err}"
                )
                app.state.cache = None
    else:
        lifespan_logger.warning(
            "Cache is disabled in settings. Skipping initialization."
        )
        app.state.cache = None

    # ------------------------------------------------------------------
    # Initialise StockOrchestrator so chat / premium endpoints get a live instance
    # ------------------------------------------------------------------
    if getattr(app.state, "cache", None):
        try:
            from backend.core.orchestrator import StockOrchestrator

            app.state.orchestrator = StockOrchestrator(cache=app.state.cache)
            lifespan_logger.info(
                "✅ StockOrchestrator initialised and attached to app state."
            )
        except Exception as orch_err:
            lifespan_logger.error(f"Could not initialise StockOrchestrator: {orch_err}")
            app.state.orchestrator = None
    else:
        lifespan_logger.warning(
            "StockOrchestrator not initialised because cache is unavailable."
        )

    # --- Diagnostics: EODHD key presence (masked) & route dump (subset) ---
    try:
        eodhd_key_present = bool(
            os.getenv("FINBOT_API_KEYS__EODHD") or os.getenv("EODHD_API_KEY")
        )
        lifespan_logger.info(
            "EODHD key present: %s", "yes" if eodhd_key_present else "no"
        )
    except Exception:
        lifespan_logger.info("EODHD key present: unknown")

    try:
        api_prefix = settings.API_PREFIX.rstrip("/")
        sample_routes = []
        for r in getattr(app, "routes", []):
            path = getattr(r, "path", "")
            methods = sorted(getattr(r, "methods", []) or [])
            if path.startswith(api_prefix):
                sample_routes.append((path, ",".join(methods)))
        # log only a limited subset to avoid noisy output
        sample_routes = sorted(sample_routes)[:25]
        for p, m in sample_routes:
            lifespan_logger.info("Route registered: %s [%s]", p, m)
    except Exception as _route_err:
        lifespan_logger.warning("Route dump failed: %s", _route_err)

    yield

    # Shutdown sequence
    lifespan_logger.info("Application shutdown sequence initiated...")

    # Close Database Pool
    try:
        from backend.core.performance.database_pool import main_db_pool

        await main_db_pool.close()
        lifespan_logger.info("✅ Database pool closed.")
    except Exception as e:
        lifespan_logger.error(f"Error closing database pool: {e}")

    # Close HTTP Client
    if hasattr(app.state, "http_client") and app.state.http_client:
        await app.state.http_client.aclose()
        lifespan_logger.info("✅ HTTP Client connection closed.")

    # Close Cache Service
    if hasattr(app.state, "cache") and app.state.cache:
        await app.state.cache.close()
        lifespan_logger.info("✅ CacheService connection closed.")

    lifespan_logger.info("Shutdown complete.")


def create_app(lite: bool = False) -> FastAPI:
    """
    Creates and configures a FastAPI application instance.
    """
    app = FastAPI(
        title=settings.APP_META.TITLE,
        description=settings.APP_META.DESCRIPTION,
        version=settings.APP_META.VERSION,
        lifespan=lifespan,
        # Use built-in Swagger UI instead of CDN to avoid CSP issues
        swagger_ui_parameters={"syntaxHighlight": True},
        swagger_ui_init_oauth={},
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    

    # --- Metrics Endpoint ---
    # Expose Prometheus metrics at /metrics
    # Mount Prometheus metrics exactly at /metrics (no double prefix)
    metrics_router = get_metrics_router(METRICS_EXPORTER)
    app.include_router(metrics_router, tags=["Metrics"])

    # Root and Health Check are always available
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")

    @app.get(f"{settings.API_PREFIX}/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "timestamp": "now"}

    @app.get("/health", include_in_schema=False)
    async def health_check_legacy():
        """Lightweight health endpoint without API prefix for browser preflight checks."""
        return {"status": "ok"}

    if lite:
        return app

    # --- Full Application Setup ---
    # --- Middleware Setup ---
    # Session Middleware for Google OAuth
    if settings.GOOGLE_AUTH.ENABLED:
        # Decide cookie flags based on redirect URI host/scheme to guarantee
        # correct behavior in local HTTP dev (no Secure, SameSite=Lax) while
        # keeping production HTTPS with SameSite=None; Secure.
        try:
            from urllib.parse import urlparse

            ru = urlparse(str(settings.GOOGLE_AUTH.REDIRECT_URI))
            is_local_http = (ru.scheme == "http") and (
                ru.hostname in {"localhost", "127.0.0.1"}
            )
            cookie_domain = None if is_local_http else (ru.hostname or None)
        except Exception:
            is_local_http = False
            cookie_domain = None

        if is_local_http:
            session_same_site = "lax"  # send on same-site navigations
            session_https_only = False  # allow over HTTP in dev
        else:
            session_same_site = (
                "none"  # allow cross-site in production (gateway → backend)
            )
            session_https_only = True  # require HTTPS in production

        app.add_middleware(
            SessionMiddleware,
            secret_key=settings.GOOGLE_AUTH.SECRET_KEY.get_secret_value(),
            same_site=session_same_site,
            https_only=session_https_only,
            domain=cookie_domain,
        )

    # ------------------------------------------------------------------
    # CORS Middleware – Demo-friendly configuration
    # ------------------------------------------------------------------
    # Build allowed origins from settings.CORS, fallback to dev friendly defaults
    allowed_origins = [
        "http://localhost:8083",
        "http://127.0.0.1:8083",
    ]
    # Include common local network pattern if Vite exposes a Network URL
    if "http://0.0.0.0:8083" not in allowed_origins:
        allowed_origins.append("http://0.0.0.0:8083")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["content-type"],
        max_age=3600,
    )

    # Deprecated route monitor – counts alias usage
    async def _get_cache(request: Request):  # noqa: D401
        return getattr(request.app.state, "cache", None)

    app.add_middleware(
        DeprecatedRouteMonitorMiddleware, cache_service_factory=_get_cache
    )

    # --- JWT Authentication Middleware ---
    from backend.middleware.jwt_auth.factory import create_jwt_middleware
    
    # Get JWT secret key from environment
    jwt_secret_key = os.getenv("GOOGLE_AUTH_SECRET_KEY", "default-secret-key-change-in-production")
    
    # Add JWT middleware
    app.add_middleware(
        create_jwt_middleware,
        secret_key=jwt_secret_key,
        algorithm="HS256",
        token_expiration=900,  # 15 minutes
        enable_redis=True
    )

    # --- API Router Registration ---
    # The routers are imported here, inside the factory, to prevent
    # circular dependencies when other modules import `main.app`.
    # from backend.api.routers import api_router

    # Correctly include the single, aggregated API router
    app.include_router(api_router, prefix=f"{settings.API_PREFIX}")

    # AI router is included via api_router. Duplicate inclusion removed to avoid operationId clashes.

    # --- SPA & Static File Handling ---
    # Middleware to serve the Single Page Application
    # Temporarily disabled to debug API endpoints
    # @app.middleware("http")
    # async def spa_fallback(request: Request, call_next):
    #     # Skip SPA fallback for API, docs, openapi.json, and metrics endpoints
    #     path = request.url.path
    #     if (path.startswith(settings.API_PREFIX) or
    #         path.startswith("/docs") or
    #         path == "/openapi.json" or
    #         path.startswith("/metrics")):
    #         return await call_next(request)
    #
    #     # Serve SPA for all other paths
    #     static_dir = settings.PATHS.STATIC_DIR
    #     index_path = os.path.join(static_dir, 'index.html')
    #     if os.path.exists(index_path):
    #         return FileResponse(index_path)
    #     return await call_next(request)

    # Add custom exception handlers
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return {"error": "An error occurred. Please try again later."}

    # Set custom OpenAPI schema
    app.openapi = lambda: custom_openapi(app)

    return app
