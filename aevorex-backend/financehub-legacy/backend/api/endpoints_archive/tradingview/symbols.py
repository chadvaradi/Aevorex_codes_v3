"""
TradingView UDF symbols endpoint for official ECB/MNB financial data.
Provides symbol configuration for: €STR, Euribor HSTA, BUBOR, Yield Curve, Policy Rates, FX.
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Official ECB/MNB symbol definitions for TradingView
OFFICIAL_SYMBOLS = {
    # =========== FIXING RATES ===========
    # ECB €STR (Overnight)
    "ESTR_ON": {
        "symbol": "ESTR_ON",
        "full_name": "ECB Euro Short-Term Rate (Overnight)",
        "description": "Official ECB €STR - Euro area risk-free overnight rate",
        "type": "interest_rate",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,  # 3 decimal places
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX EST/B.EU000A2X2A25.WT",
        "license": "CC BY 4.0",
    },
    # Euribor HSTA (Historical Statistical Average) - License-clean
    "EURIBOR_1W": {
        "symbol": "EURIBOR_1W",
        "full_name": "Euribor 1 Week HSTA",
        "description": "Euribor 1W Historical Statistical Average (ECB FM dataflow)",
        "type": "interest_rate",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX FM.M.U2.EUR.RT.MM.EURIBOR1WD_.HSTA",
        "license": "CC BY 4.0",
    },
    "EURIBOR_1M": {
        "symbol": "EURIBOR_1M",
        "full_name": "Euribor 1 Month HSTA",
        "description": "Euribor 1M Historical Statistical Average (ECB FM dataflow)",
        "type": "interest_rate",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX FM.M.U2.EUR.RT.MM.EURIBOR1MD_.HSTA",
        "license": "CC BY 4.0",
    },
    "EURIBOR_3M": {
        "symbol": "EURIBOR_3M",
        "full_name": "Euribor 3 Month HSTA",
        "description": "Euribor 3M Historical Statistical Average (ECB FM dataflow)",
        "type": "interest_rate",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA",
        "license": "CC BY 4.0",
    },
    "EURIBOR_6M": {
        "symbol": "EURIBOR_6M",
        "full_name": "Euribor 6 Month HSTA",
        "description": "Euribor 6M Historical Statistical Average (ECB FM dataflow)",
        "type": "interest_rate",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX FM.M.U2.EUR.RT.MM.EURIBOR6MD_.HSTA",
        "license": "CC BY 4.0",
    },
    "EURIBOR_12M": {
        "symbol": "EURIBOR_12M",
        "full_name": "Euribor 12 Month HSTA",
        "description": "Euribor 12M Historical Statistical Average (ECB FM dataflow)",
        "type": "interest_rate",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX FM.M.U2.EUR.RT.MM.EURIBOR12MD_.HSTA",
        "license": "CC BY 4.0",
    },
    # =========== BUBOR (MNB) ===========
    "BUBOR_ON": {
        "symbol": "BUBOR_ON",
        "full_name": "BUBOR Overnight",
        "description": "Hungarian Interbank Offered Rate O/N (MNB official)",
        "type": "interest_rate",
        "session": "0900-1700",
        "timezone": "Europe/Budapest",
        "minmov": 1,
        "pricescale": 100,  # 2 decimal places
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "MNB XLS https://www.mnb.hu/arfolyamok/bubor",
        "license": "CC BY 4.0",
    },
    "BUBOR_1W": {
        "symbol": "BUBOR_1W",
        "full_name": "BUBOR 1 Week",
        "description": "Hungarian Interbank Offered Rate 1W (MNB official)",
        "type": "interest_rate",
        "session": "0900-1700",
        "timezone": "Europe/Budapest",
        "minmov": 1,
        "pricescale": 100,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "MNB XLS https://www.mnb.hu/arfolyamok/bubor",
        "license": "CC BY 4.0",
    },
    "BUBOR_1M": {
        "symbol": "BUBOR_1M",
        "full_name": "BUBOR 1 Month",
        "description": "Hungarian Interbank Offered Rate 1M (MNB official)",
        "type": "interest_rate",
        "session": "0900-1700",
        "timezone": "Europe/Budapest",
        "minmov": 1,
        "pricescale": 100,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "MNB XLS https://www.mnb.hu/arfolyamok/bubor",
        "license": "CC BY 4.0",
    },
    "BUBOR_3M": {
        "symbol": "BUBOR_3M",
        "full_name": "BUBOR 3 Month",
        "description": "Hungarian Interbank Offered Rate 3M (MNB official)",
        "type": "interest_rate",
        "session": "0900-1700",
        "timezone": "Europe/Budapest",
        "minmov": 1,
        "pricescale": 100,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "MNB XLS https://www.mnb.hu/arfolyamok/bubor",
        "license": "CC BY 4.0",
    },
    "BUBOR_6M": {
        "symbol": "BUBOR_6M",
        "full_name": "BUBOR 6 Month",
        "description": "Hungarian Interbank Offered Rate 6M (MNB official)",
        "type": "interest_rate",
        "session": "0900-1700",
        "timezone": "Europe/Budapest",
        "minmov": 1,
        "pricescale": 100,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "MNB XLS https://www.mnb.hu/arfolyamok/bubor",
        "license": "CC BY 4.0",
    },
    "BUBOR_12M": {
        "symbol": "BUBOR_12M",
        "full_name": "BUBOR 12 Month",
        "description": "Hungarian Interbank Offered Rate 12M (MNB official)",
        "type": "interest_rate",
        "session": "0900-1700",
        "timezone": "Europe/Budapest",
        "minmov": 1,
        "pricescale": 100,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "MNB XLS https://www.mnb.hu/arfolyamok/bubor",
        "license": "CC BY 4.0",
    },
    # =========== YIELD CURVE ===========
    "YC_SR_1Y": {
        "symbol": "YC_SR_1Y",
        "full_name": "ECB Euro Area Yield Curve 1 Year",
        "description": "Risk-free Euro area yield curve spot rate 1Y (ECB official)",
        "type": "yield_curve",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y",
        "license": "CC BY 4.0",
    },
    "YC_SR_2Y": {
        "symbol": "YC_SR_2Y",
        "full_name": "ECB Euro Area Yield Curve 2 Year",
        "description": "Risk-free Euro area yield curve spot rate 2Y (ECB official)",
        "type": "yield_curve",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y",
        "license": "CC BY 4.0",
    },
    "YC_SR_5Y": {
        "symbol": "YC_SR_5Y",
        "full_name": "ECB Euro Area Yield Curve 5 Year",
        "description": "Risk-free Euro area yield curve spot rate 5Y (ECB official)",
        "type": "yield_curve",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_5Y",
        "license": "CC BY 4.0",
    },
    "YC_SR_10Y": {
        "symbol": "YC_SR_10Y",
        "full_name": "ECB Euro Area Yield Curve 10 Year",
        "description": "Risk-free Euro area yield curve spot rate 10Y (ECB official)",
        "type": "yield_curve",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y",
        "license": "CC BY 4.0",
    },
    "YC_SR_30Y": {
        "symbol": "YC_SR_30Y",
        "full_name": "ECB Euro Area Yield Curve 30 Year",
        "description": "Risk-free Euro area yield curve spot rate 30Y (ECB official)",
        "type": "yield_curve",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_30Y",
        "license": "CC BY 4.0",
    },
    # =========== POLICY RATES ===========
    "ECB_DFR": {
        "symbol": "ECB_DFR",
        "full_name": "ECB Deposit Facility Rate",
        "description": "European Central Bank Deposit Facility Rate (official)",
        "type": "policy_rate",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX FM.D.EZB.DFR.LEV",
        "license": "CC BY 4.0",
    },
    "ECB_MRO": {
        "symbol": "ECB_MRO",
        "full_name": "ECB Main Refinancing Operations Rate",
        "description": "European Central Bank Main Refinancing Operations Rate (official)",
        "type": "policy_rate",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX FM.D.EZB.MRO.LEV",
        "license": "CC BY 4.0",
    },
    "ECB_MSF": {
        "symbol": "ECB_MSF",
        "full_name": "ECB Marginal Lending Facility Rate",
        "description": "European Central Bank Marginal Lending Facility Rate (official)",
        "type": "policy_rate",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX FM.D.EZB.MSF.LEV",
        "license": "CC BY 4.0",
    },
    # =========== FX RATES (EUR-based) ===========
    "EUR_USD": {
        "symbol": "EUR_USD",
        "full_name": "EUR/USD Exchange Rate",
        "description": "Euro to US Dollar reference exchange rate (ECB official)",
        "type": "forex",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 10000,  # 4 decimal places
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX EXR.D.USD.EUR.SP00.A",
        "license": "CC BY 4.0",
    },
    "EUR_HUF": {
        "symbol": "EUR_HUF",
        "full_name": "EUR/HUF Exchange Rate",
        "description": "Euro to Hungarian Forint reference exchange rate (ECB official)",
        "type": "forex",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 1000,  # 3 decimal places
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX EXR.D.HUF.EUR.SP00.A",
        "license": "CC BY 4.0",
    },
    "EUR_GBP": {
        "symbol": "EUR_GBP",
        "full_name": "EUR/GBP Exchange Rate",
        "description": "Euro to British Pound reference exchange rate (ECB official)",
        "type": "forex",
        "session": "0900-1800",
        "timezone": "Europe/Frankfurt",
        "minmov": 1,
        "pricescale": 10000,  # 4 decimal places
        "has_intraday": False,
        "supported_resolutions": ["1D"],
        "data_source": "ECB SDMX EXR.D.GBP.EUR.SP00.A",
        "license": "CC BY 4.0",
    },
}


@router.get("/symbols", summary="Get available symbols for TradingView")
async def get_symbols() -> List[Dict[str, Any]]:
    """
    Get all available financial symbols for TradingView Advanced Chart.
    Returns symbol configuration for official ECB/MNB data sources only.
    NO MOCK DATA - only license-clean official sources (CC BY 4.0).
    """
    logger.info("Fetching available TradingView symbols from official ECB/MNB sources")

    symbols_list = []

    for symbol_id, config in OFFICIAL_SYMBOLS.items():
        symbols_list.append(
            {
                "symbol": config["symbol"],
                "full_name": config["full_name"],
                "description": config["description"],
                "type": config["type"],
                "session": config["session"],
                "timezone": config["timezone"],
                "minmov": config["minmov"],
                "pricescale": config["pricescale"],
                "has_intraday": config["has_intraday"],
                "supported_resolutions": config["supported_resolutions"],
                "data_source": config["data_source"],
                "license": config["license"],
            }
        )

    logger.info(f"Returning {len(symbols_list)} official symbols")
    return symbols_list


@router.get("/symbols/{symbol}", summary="Get specific symbol configuration")
async def get_symbol_config(symbol: str) -> Dict[str, Any]:
    """Get configuration for a specific symbol."""

    if symbol not in OFFICIAL_SYMBOLS:
        return {
            "error": f"Symbol {symbol} not found",
            "available_symbols": list(OFFICIAL_SYMBOLS.keys()),
        }

    config = OFFICIAL_SYMBOLS[symbol]
    logger.info(f"Returning config for symbol: {symbol}")

    return {
        "symbol": config["symbol"],
        "full_name": config["full_name"],
        "description": config["description"],
        "type": config["type"],
        "session": config["session"],
        "timezone": config["timezone"],
        "minmov": config["minmov"],
        "pricescale": config["pricescale"],
        "has_intraday": config["has_intraday"],
        "supported_resolutions": config["supported_resolutions"],
        "data_source": config["data_source"],
        "license": config["license"],
    }
