"""Main router for all Macroeconomic endpoints."""

from fastapi import APIRouter

from .ecb import router as ecb_router
from .rates import router as rates_router
from .bubor import router as bubor_router
from .forex import router as forex_router
from .curve import curve_router
from .fixing_rates import router as fixing_rates_router
from .fed_policy import router as fed_policy_router
from .fed_series import router as fed_series_router
from .fed_search import router as fed_search_router

macro_router = APIRouter(tags=["Macro"])

macro_router.include_router(ecb_router)
macro_router.include_router(rates_router)
macro_router.include_router(bubor_router, prefix="/bubor")
macro_router.include_router(forex_router)
macro_router.include_router(curve_router)
macro_router.include_router(fixing_rates_router, prefix="/fixing-rates")
macro_router.include_router(fed_policy_router)
macro_router.include_router(fed_series_router)
macro_router.include_router(fed_search_router)

__all__ = ["macro_router"]
