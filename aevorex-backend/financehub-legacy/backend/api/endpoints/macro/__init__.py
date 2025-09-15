"""
Macro API endpoints module.

Provides comprehensive macroeconomic data endpoints including:
- ECB dataflows and SDMX integration
- BUBOR (Hungarian interbank rates)
- Yield curves (ECB, US Treasury)
- Fixing rates (€STR, Euribor, BUBOR)
- Federal Reserve policy rates and FRED data
- Economic indicators and time series
"""
"""
Macro API endpoints package.

Provides structured access to macroeconomic data:
- ECB (unified SDMX flows + special endpoints)
- BUBOR (Hungarian interbank rates)
- Yield curves (ECB + US Treasury via FRED)
- Fixing rates (€STR, Euribor, BUBOR)
- Federal Reserve / FRED (policy rates, series, search)
"""

from .macro_router import router as macro_router

__all__ = ["macro_router"]
