# backend/api/deps.py
"""
API Függőségek és Életciklus Kezelés (Redis Cache verzió)

Ez a modul felelős a FastAPI alkalmazás életciklusa során használt megosztott
erőforrások (singletonok) inicializálásáért, leállításáért és a kérések
során történő biztonságos átadásáért (Dependency Injection).

Fő komponensek:
- `lifespan_manager`: Aszinkron kontextuskezelő, amely az alkalmazás indulásakor
  létrehozza, a leállásakor pedig bezárja a globális HTTP klienst és a Redis-alapú
  CacheService példányt.
- Függőség függvények (`get_http_client`, `get_cache_service`, stb.):
  Ezeket használják az API végpontok a megosztott erőforrások példányainak
  biztonságos lekérésére egy adott kérés kontextusában.
"""

import httpx
from contextlib import asynccontextmanager
from fastapi import Request, HTTPException, FastAPI, status
import sys
import os

# --- Core Szolgáltatások Importálása ---
# A CacheService Redis-alapú implementáció
os.environ.setdefault("FINANCEHUB_CACHE_MODE", "memory")
from backend.utils.cache_service import CacheService
from backend.core.orchestrator import StockOrchestrator

# from backend.core.chat.context_manager import InMemoryHistoryManager, AbstractHistoryManager # Ha még használatban van
# from backend.core.chat.chat_service import ChatService

# --- Konfiguráció és Logger Import ---
try:
    from ..config import settings
    from ..utils.logger_config import get_logger
except ImportError as e:
    # Kritikus hiba, ha a config/logger nem érhető el
    print(
        f"FATAL ERROR [deps.py]: Could not import config/logger: {e}. Check project structure.",
        file=sys.stderr,
    )
    raise RuntimeError(
        "API Dependencies module failed to initialize due to missing config/logger."
    ) from e

logger = get_logger("aevorex_finbot_api.deps")  # Specifikus logger a modulhoz

# --- Globális Singleton Példányok (Lifespan Kezeli) ---
# Ezeket a változókat CSAK a lifespan_manager módosíthatja.
# A dependency függvények ezeket olvassák.
_http_client_instance: httpx.AsyncClient | None = None
_cache_service_instance: CacheService | None = None
_orchestrator_instance: StockOrchestrator | None = None
# _history_manager_instance: AbstractHistoryManager | None = None # Ha szükséges

# =============================================================================
# === ALKALMAZÁS ÉLETCIKLUS KEZELŐ (LIFESPAN MANAGER) ===
# =============================================================================


@asynccontextmanager
async def lifespan_manager(app: FastAPI):
    """
    Aszinkron kontextuskezelő a FastAPI alkalmazás életciklusához.

    Induláskor:
        1. Inicializálja a globális HTTP klienst.
        2. Inicializálja a Redis cache szolgáltatást és a CacheService példányt.
        3. Opcionálisan inicializál más globális erőforrásokat (pl. HistoryManager).
    Leállításkor:
        1. Lezárja a CacheService kapcsolatát.
        2. Lezárja a globális HTTP klienst.
        3. Opcionálisan lezár más globális erőforrásokat.
    """
    global _http_client_instance, _cache_service_instance, _orchestrator_instance
    logger.info(
        "[Lifespan] Startup sequence initiated: Initializing global resources..."
    )
    # Initialize app.state if it doesn't exist (though FastAPI usually does)
    if not hasattr(app, "state"):
        app.state = type(
            "AppState", (), {}
        )()  # Create a simple namespace object for app.state

    resources_initialized = {
        "http_client": False,
        "cache_service": False,
        "orchestrator": False,
        "history_manager": False,
    }
    # Initialize attributes on app.state to None or a default value
    # This ensures they exist even if initialization fails later
    app.state.http_client = None
    app.state.cache_service = None
    app.state.orchestrator = None
    app.state.history_manager = None

    try:
        # --- 1. HTTP Kliens Inicializálása ---
        logger.debug("[Lifespan] Initializing global HTTP client...")
        try:
            timeout = httpx.Timeout(
                settings.HTTP_CLIENT.REQUEST_TIMEOUT_SECONDS,
                connect=settings.HTTP_CLIENT.CONNECT_TIMEOUT_SECONDS,
                pool=settings.HTTP_CLIENT.POOL_TIMEOUT_SECONDS,
            )
            limits = httpx.Limits(
                max_connections=settings.HTTP_CLIENT.MAX_CONNECTIONS,
                max_keepalive_connections=settings.HTTP_CLIENT.MAX_KEEPALIVE_CONNECTIONS,
            )
            headers = {
                "User-Agent": settings.HTTP_CLIENT.USER_AGENT,
                "Referer": str(settings.HTTP_CLIENT.DEFAULT_REFERER),
            }
            _http_client_instance = httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                headers=headers,
                http2=True,
                follow_redirects=True,
            )
            app.state.http_client = _http_client_instance  # ASSIGN TO APP.STATE
            logger.info(
                "[Lifespan] Global httpx.AsyncClient initialized and assigned to app.state.http_client."
            )
            resources_initialized["http_client"] = True
        except Exception as e:
            logger.critical(
                f"[Lifespan] CRITICAL FAILURE: HTTP Client initialization failed: {e}",
                exc_info=True,
            )
            _http_client_instance = None  # Hiba esetén None
            app.state.http_client = None  # Ensure it's None on failure

        # --- 2. CacheService Inicializálása (Memory Cache) ---
        if resources_initialized["http_client"]:  # Csak ha az előző sikeres volt
            logger.debug("[Lifespan] Initializing global Memory-based CacheService...")
            try:
                from backend.utils.cache_service import CacheService

                # Use memory cache for development stability
                _cache_service_instance = await CacheService.create("memory")
                app.state.cache = _cache_service_instance
                app.state.cache_service = _cache_service_instance
                resources_initialized["cache_service"] = True
                logger.info("[Lifespan] Memory CacheService initialized successfully")
            except Exception as e:
                logger.error(f"[Lifespan] Failed to initialize CacheService: {e}")
                # Final fallback to None
                app.state.cache = None
                app.state.cache_service = None
                resources_initialized["cache_service"] = False

        # --- 3. Orchestrator Service Inicializálása ---
        if (
            resources_initialized["http_client"]
            and resources_initialized["cache_service"]
        ):
            logger.debug("[Lifespan] Initializing global StockOrchestrator...")
            try:
                # StockOrchestrator requires only cache, not http_client in constructor
                _orchestrator_instance = StockOrchestrator(
                    cache=_cache_service_instance
                )
                app.state.orchestrator = _orchestrator_instance
                logger.info(
                    "[Lifespan] Global StockOrchestrator initialized and assigned to app.state.orchestrator."
                )
                resources_initialized["orchestrator"] = True
            except Exception as e:
                logger.critical(
                    f"[Lifespan] CRITICAL FAILURE initializing StockOrchestrator: {e}",
                    exc_info=True,
                )
                _orchestrator_instance = None
                app.state.orchestrator = None

        # --- 4. History Manager Inicializálása (ha kell) ---
        # if resources_initialized["cache_service"]: # Csak ha az előzőek sikeresek
        #      logger.debug("[Lifespan] Initializing global HistoryManager...")
        #      try:
        #          _history_manager_instance = InMemoryHistoryManager() # Vagy más implementáció
        #          app.state.history_manager = _history_manager_instance # ASSIGN TO APP.STATE
        #          logger.info(f"[Lifespan] Global {_history_manager_instance.__class__.__name__} instance created and assigned to app.state.history_manager.")
        #          resources_initialized["history_manager"] = True
        #      except Exception as e:
        #          logger.critical(f"[Lifespan] CRITICAL FAILURE initializing History Manager: {e}", exc_info=True)
        #          _history_manager_instance = None
        #          app.state.history_manager = None # Ensure it's None on failure

        # --- Vezérlés átadása az alkalmazásnak ---
        # Csak akkor yield-elünk, ha a legfontosabbak (HTTP, Cache, Orchestrator) sikeresek
        if all(
            [
                resources_initialized["http_client"],
                resources_initialized["cache_service"],
                resources_initialized["orchestrator"],
            ]
        ):
            logger.info(
                "[Lifespan] Core resources initialized. Yielding control to application."
            )
            yield  # Alkalmazás futása
            logger.info(
                "[Lifespan] Shutdown sequence initiated: Cleaning up global resources..."
            )
        else:
            logger.critical(
                "[Lifespan] CRITICAL FAILURE during startup resource initialization. Application might not function correctly."
            )
            # Hibás indulás esetén is futtatni kell a cleanup-ot arra, ami elindult!
            yield  # Vagy dobhatnánk kivételt, de a cleanup így is lefut
            logger.warning(
                "[Lifespan] Shutdown sequence initiated after failed startup."
            )

    finally:
        # --- Leállítási Logika (Fordított Sorrendben) ---
        # Ez a blokk HIBÁS INDULÁS UTÁN IS LEFUT!

        # 4. History Manager
        # if hasattr(app.state, 'history_manager') and app.state.history_manager: # Check app.state first
        #      logger.debug("[Lifespan] Clearing app.state.history_manager reference.")
        #      app.state.history_manager = None
        # if _history_manager_instance: # Also clear the global, though app.state is primary for access
        #      _history_manager_instance = None

        # 3. Orchestrator Service
        if hasattr(app.state, "orchestrator") and app.state.orchestrator:
            logger.debug("[Lifespan] Clearing app.state.orchestrator reference.")
            app.state.orchestrator = None
        if _orchestrator_instance:
            _orchestrator_instance = None

        # 2. Cache Service Lezárása (Redis-based cache cleanup)
        if (
            hasattr(app.state, "cache_service") and app.state.cache_service
        ):  # Check app.state first
            logger.info("[Lifespan] Cleaning up CacheService (from app.state)...")
        if _cache_service_instance:  # Also clear the global
            _cache_service_instance = None

        # 1. HTTP Kliens Lezárása
        if (
            hasattr(app.state, "http_client") and app.state.http_client
        ):  # Check app.state first
            logger.info("[Lifespan] Closing HTTP Client (from app.state)...")
            try:
                await app.state.http_client.aclose()
                logger.info(
                    "[Lifespan] HTTP Client (from app.state) closed successfully."
                )
            except Exception as e:
                logger.error(
                    f"[Lifespan] Error closing HTTP Client (from app.state) during shutdown: {e}",
                    exc_info=True,
                )
            finally:
                app.state.http_client = None  # Reset app.state reference
        if _http_client_instance:  # Also clear the global
            _http_client_instance = None

        logger.info("[Lifespan] Resource cleanup finished.")


# =============================================================================
# === FÜGGŐSÉG INJEKTÁLÁSI FÜGGVÉNYEK ===
# =============================================================================


async def get_http_client(request: Request) -> httpx.AsyncClient:
    """
    FastAPI Függőség: Visszaadja a globálisan inicializált HTTP klienst.

    Raises:
        HTTPException(503): Ha a kliens nem érhető el (inicializálási hiba).
    """
    global _http_client_instance
    # Check app.state first, then fallback to global
    if (
        hasattr(request.app.state, "http_client")
        and request.app.state.http_client is not None
    ):
        return request.app.state.http_client
    elif _http_client_instance is not None:
        return _http_client_instance
    # ------------------------------------------------------------------
    # 🛟  Fallback – DEV only. In production, do NOT create on-the-fly clients.
    # ------------------------------------------------------------------
    try:
        from backend.config import settings

        if settings.ENVIRONMENT.NODE_ENV == "production":
            from backend.core.metrics import METRICS_EXPORTER

            METRICS_EXPORTER.inc_fallback("prod", "http_client")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="HTTP Client unavailable (prod, no fallback)",
            )
        timeout = httpx.Timeout(
            settings.HTTP_CLIENT.REQUEST_TIMEOUT_SECONDS,
            connect=settings.HTTP_CLIENT.CONNECT_TIMEOUT_SECONDS,
            pool=settings.HTTP_CLIENT.POOL_TIMEOUT_SECONDS,
        )
        limits = httpx.Limits(
            max_connections=settings.HTTP_CLIENT.MAX_CONNECTIONS,
            max_keepalive_connections=settings.HTTP_CLIENT.MAX_KEEPALIVE_CONNECTIONS,
        )
        headers = {
            "User-Agent": settings.HTTP_CLIENT.USER_AGENT,
            "Referer": str(settings.HTTP_CLIENT.DEFAULT_REFERER),
        }
        fallback_client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            headers=headers,
            http2=True,
            follow_redirects=True,
        )
        # Save to globals so subsequent calls reuse the same client
        _http_client_instance = fallback_client
        logger.warning(
            "[Dependency Fallback] Created on-the-fly httpx.AsyncClient fallback instance."
        )
        return fallback_client
    except Exception as e:
        logger.critical(f"[Dependency Error] Final HTTP client fallback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HTTP Client service is temporarily unavailable. Please try again later.",
        )


async def get_cache_service(request: Request) -> CacheService:
    """
    Dependency to get the initialized CacheService instance from the app state.
    Raises an HTTPException if the cache is not available.
    """
    # Prefer app.state.cache (primary) then global _cache_service_instance as fallback.
    if hasattr(request.app.state, "cache") and request.app.state.cache is not None:
        return request.app.state.cache
    global _cache_service_instance
    if _cache_service_instance is not None:
        return _cache_service_instance

    # MVP STRATEGY: On-the-fly in-memory cache fallback for single-instance deployment
    # NOTE: This is intentional for MVP - memory cache is sufficient for single-instance FinanceHub
    # Future scaling will use Supabase TTL cache instead of Redis
    try:
        from backend.config import settings

        if settings.ENVIRONMENT.NODE_ENV == "production":
            from backend.core.metrics import METRICS_EXPORTER

            METRICS_EXPORTER.inc_fallback("prod", "cache_service")
            raise HTTPException(
                status_code=503, detail="Cache service unavailable (prod, no fallback)"
            )
        from backend.utils.cache_service import CacheService as _MemCache

        mem_cache = await _MemCache.create()
        request.app.state.cache = mem_cache  # type: ignore[attr-defined]
        _cache_service_instance = mem_cache
        logger.warning(
            "[MVP Fallback] Using in-memory CacheService (Redis not configured)."
        )
        return mem_cache
    except Exception as e:
        logger.critical(f"[Dependency Error] Final cache fallback failed: {e}")
        raise HTTPException(
            status_code=503, detail="Cache service unavailable and fallback failed"
        )


async def get_orchestrator(request: Request) -> StockOrchestrator:
    """
    FastAPI Függőség: Visszaadja a globálisan inicializált StockOrchestrator példányt.
    """
    global _orchestrator_instance
    if (
        hasattr(request.app.state, "orchestrator")
        and request.app.state.orchestrator is not None
    ):
        return request.app.state.orchestrator
    elif _orchestrator_instance is not None:
        return _orchestrator_instance
    else:
        # --- Lazy fallback (DEV only) --------------------------------------
        # The orchestrator might have been garbage-collected after an automatic
        # code reload (∵ `--reload`) or during a partial startup failure. To
        # avoid surfacing a 503 to the client we instantiate a fresh instance
        # on-demand using the current cache service. This is safe because the
        # orchestrator itself is stateless apart from its cache dependency.

        try:
            from backend.config import settings

            if settings.ENVIRONMENT.NODE_ENV == "production":
                from backend.core.metrics import METRICS_EXPORTER

                METRICS_EXPORTER.inc_fallback("prod", "orchestrator")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orchestrator unavailable (prod, no lazy instantiation)",
                )
            cache_service = await get_cache_service(request)
            from backend.core.orchestrator import (
                StockOrchestrator,
            )  # local import to avoid circulars

            new_orchestrator = StockOrchestrator(cache=cache_service)

            # Persist for subsequent requests
            request.app.state.orchestrator = new_orchestrator  # type: ignore[attr-defined]
            _orchestrator_instance = new_orchestrator

            logger.warning(
                "[MVP Fallback] StockOrchestrator lazily instantiated on demand."
            )
            return new_orchestrator
        except Exception as inst_err:
            logger.critical(
                f"[Dependency Error] Failed to lazily instantiate StockOrchestrator: {inst_err}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Orchestrator service is temporarily unavailable due to internal error.",
            )


# --- History Manager Függőség (Ha Szükséges) ---
# async def get_history_manager() -> AbstractHistoryManager:
#     """
#     FastAPI Függőség: Visszaadja a globálisan inicializált History Manager példányt.
#     """
#     if _history_manager_instance is not None:
#         return _history_manager_instance
#     else:
#         logger.critical("[Dependency Error] History Manager requested but is unavailable (lifespan issue?).")
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="History Manager service is temporarily unavailable."
#         )

# async def get_chat_service(history_manager: AbstractHistoryManager = Depends(get_history_manager)) -> ChatService:
#     """
#     FastAPI Függőség: Visszaadja a ChatService példányt,
#     a szükséges függőségekkel (pl. HistoryManager) együtt.
#     """
#     try:
#         return ChatService(history_manager=history_manager)
#     except TypeError as e:
#         logger.critical(f"[Dependency Error] ChatService initialization failed: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="ChatService is temporarily unavailable due to a configuration error."
#         )


# --- Egyéb Függőségek (Példa: Szimbólum Validálás) ---
async def validate_symbol(symbol: str) -> str:
    """
    FastAPI Függőség: Validálja a részvény szimbólum formátumát.
    """
    if (
        not symbol
        or not isinstance(symbol, str)
        or not symbol.isalnum()
        or len(symbol) > 10
    ):
        logger.warning(f"[Dependency Validation] Invalid symbol received: '{symbol}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 400 helyett 422 is lehetne
            detail=f"Invalid stock symbol format provided: '{symbol}'. Expected alphanumeric, max 10 chars.",
        )
    return symbol.upper()


# =============================================================================
# Modul Betöltés Jelzése
# =============================================================================
logger.info(
    f"--- API Dependencies module ({__name__}) loaded. Lifespan and dependencies configured for Redis Cache. ---"
)
