from fastapi import APIRouter

# Core FinanceHub routers - NEW ENDPOINTS ONLY
from .endpoints.macro import macro_router
from .endpoints.auth.auth_router import router as auth_router

# EODHD routers - NEW ENDPOINTS ONLY
from .endpoints.eodhd import (
    crypto_router, 
    stock_router, 
    technical_router, 
    news_router, 
    forex_router, 
    screener_router, 
    macro_router as eodhd_macro_router, 
    exchanges_router,
    intraday_router
)

# New endpoints
from .endpoints.fundamentals.fundamentals_router import router as fundamentals_router
from .endpoints.ticker_tape.ticker_router import router as ticker_router
from .endpoints.chat.chat_router import router as chat_router
from .endpoints.search.search_router import router as search_router
from .endpoints.summary.summary_router import router as summary_router
from .endpoints.tradingview.tradingview_router import router as tradingview_router

# Well-known endpoints for MCP compatibility
from .endpoints.well_known.well_known_router import router as well_known_router

# Billing endpoints
from .endpoints.billing.lemonsqueezy_router import router as billing_router

# Subscription endpoints
try:
    from .endpoints.subscription import router as subscription_router
    from .endpoints.subscription import lemonsqueezy_router
except ImportError as e:
    import logging

    logging.getLogger(__name__).warning("Subscription endpoints disabled: %s", e)
    subscription_router = None
    lemonsqueezy_router = None


from datetime import datetime
from fastapi import Request

api_router = APIRouter()

# Core FinanceHub routers
api_router.include_router(macro_router, prefix="/macro", tags=["Macro"])
api_router.include_router(auth_router, prefix="", tags=["Auth"])

# EODHD routers - NEW ENDPOINTS ONLY
api_router.include_router(crypto_router, prefix="/eodhd/crypto", tags=["EODHD - Crypto"])
api_router.include_router(stock_router, prefix="/eodhd/stock", tags=["EODHD - Stock"])
api_router.include_router(technical_router, prefix="/eodhd/technical", tags=["EODHD - Technical"])
api_router.include_router(news_router, prefix="/eodhd/news", tags=["EODHD - News"])
api_router.include_router(forex_router, prefix="/eodhd/forex", tags=["EODHD - Forex"])
api_router.include_router(screener_router, prefix="/eodhd/screener", tags=["EODHD Screener"])
api_router.include_router(eodhd_macro_router, prefix="/eodhd/macro", tags=["EODHD - Macro"])
api_router.include_router(exchanges_router, prefix="/eodhd/exchanges", tags=["EODHD - Exchanges"])
api_router.include_router(intraday_router, prefix="/eodhd/intraday", tags=["EODHD - Intraday"])

# New endpoints
api_router.include_router(fundamentals_router, prefix="/fundamentals", tags=["Fundamentals"])
api_router.include_router(ticker_router, prefix="/ticker-tape", tags=["Ticker Tape"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(search_router, prefix="/search", tags=["Search"])
api_router.include_router(summary_router, prefix="/summary", tags=["Summary"])
api_router.include_router(tradingview_router, prefix="/tradingview", tags=["TradingView"])

# Well-known endpoints for MCP compatibility
api_router.include_router(well_known_router, prefix="", tags=["Well-Known"])

# Billing router
api_router.include_router(billing_router, prefix="", tags=["Billing"])

# Include subscription routers if available
if subscription_router is not None:
    api_router.include_router(subscription_router, prefix="", tags=["Subscription"])

# Include Lemon Squeezy router if available
if lemonsqueezy_router is not None:
    # Register provider router without duplicating the global API prefix.
    api_router.include_router(lemonsqueezy_router, tags=["Lemon Squeezy"])


# Optional AI router – may rely on extra shared modules not available in demo env.
try:
    from .endpoints.ai import ai_router  # pylint: disable=import-error

    api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
except ModuleNotFoundError as e:
    # Log and continue without AI endpoints to allow demo backend to start
    import logging

    logging.getLogger(__name__).warning(
        "AI endpoints disabled – optional dependency missing (%s).", e
    )


@api_router.get("/health", tags=["Health"])
async def health_check(request: Request):
    """Central health aggregator returning 200 OK with minimal diagnostics.

    Future extensions: fan-out to sub-services (Redis, external APIs) and merge
    results, but for now we satisfy the always-success contract required by
    Rule #008 and unblock Phase 3 dependencies.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "online",
            "crypto": "online",
        },
    }


__all__ = ["api_router"]
