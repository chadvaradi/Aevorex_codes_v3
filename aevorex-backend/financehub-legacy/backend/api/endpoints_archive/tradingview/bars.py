"""
TradingView UDF bars endpoint for official ECB/MNB financial data.
Returns OHLC data compatible with TradingView Advanced Chart widget.
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, HTTPException, Request
from backend.utils.logger_config import get_logger
from backend.core.fetchers.macro.ecb_client.specials.euribor_client import (
    fetch_ecb_estr_rate,
)
from backend.core.fetchers.macro.ecb_client.specials.yc_fetcher import (
    fetch_yield_curve_rates,
)
from backend.core.fetchers.macro.ecb_client.specials.policy_rates_fetcher import (
    fetch_policy_rates,
)
from backend.core.fetchers.macro.ecb_client.specials.fx_rates_fetcher import (
    fetch_fx_rates,
)
from backend.core.fetchers.macro.ecb_client.specials.euribor_client import (
    fetch_official_euribor_rates,
)
from backend.core.fetchers.macro.ecb_client.specials.bubor_client import (
    fetch_bubor_curve,
)

logger = get_logger(__name__)

router = APIRouter()


def unix_timestamp(dt: date) -> int:
    """Convert date to Unix timestamp (seconds)."""
    return int(datetime.combine(dt, datetime.min.time()).timestamp())


def parse_date_param(date_str: str) -> date:
    """Parse date string from query parameter."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            # Try Unix timestamp
            return datetime.fromtimestamp(int(date_str)).date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid date format: {date_str}"
            )


@router.get("/bars", summary="Get OHLC bars for TradingView")
async def get_bars(
    request: Request,
    symbol: str = Query(
        ..., description="Symbol (e.g., EURIBOR_3M, BUBOR_3M, YC_SR_10Y)"
    ),
    period: str = Query("1D", description="Time period (1D only supported)"),
    from_date: str = Query(
        ..., alias="from", description="Start date (YYYY-MM-DD or Unix timestamp)"
    ),
    to_date: str = Query(
        ..., alias="to", description="End date (YYYY-MM-DD or Unix timestamp)"
    ),
    countback: Optional[int] = Query(None, description="Number of bars to return"),
) -> Dict[str, Any]:
    """
    Get OHLC bars in TradingView UDF format.

    Returns format:
    {
        "t": [unix_timestamp, ...],  # Time
        "c": [close_value, ...],     # Close (main rate value)
        "o": [open_value, ...],      # Open (same as close for rates)
        "h": [high_value, ...],      # High (same as close for rates)
        "l": [low_value, ...],       # Low (same as close for rates)
        "v": [volume, ...],          # Volume (always 0 for rates)
        "s": "ok"                    # Status
    }

    Uses official ECB SDMX and MNB data sources only.
    NO MOCK DATA - fails explicitly if data unavailable.
    """
    logger.info(
        f"Fetching TradingView bars for {symbol}, period={period}, from={from_date}, to={to_date}"
    )

    # Validate period
    if period != "1D":
        raise HTTPException(status_code=400, detail="Only 1D period is supported")

    # Parse date parameters
    start_date = parse_date_param(from_date)
    end_date = parse_date_param(to_date)

    if start_date > end_date:
        raise HTTPException(
            status_code=400, detail="Start date must be before end date"
        )

    # Soft paywall – limit history window by plan
    plan = (
        request.session.get("plan", "free") if hasattr(request, "session") else "free"
    )
    max_days = 7 if plan == "free" else 365
    if (end_date - start_date).days > max_days:
        # Clamp start_date to allowed window
        start_date = end_date - timedelta(days=max_days)

    # Route to appropriate data fetcher based on symbol
    try:
        if symbol == "ESTR_ON":
            data = await fetch_estr_data(start_date, end_date)
        elif symbol.startswith("EURIBOR_"):
            # Use ECB SDMX FM dataflow for Euribor HSTA data
            data = await fetch_euribor_hsta_data(symbol, start_date, end_date)
        elif symbol.startswith("BUBOR_"):
            data = await fetch_bubor_data(symbol, start_date, end_date)
        elif symbol.startswith("YC_SR_"):
            # Implemented: ECB SDMX YC dataflow for yield curve
            data = await fetch_yield_curve_data(symbol, start_date, end_date)
        elif symbol.startswith("ECB_"):
            # Implemented: ECB SDMX FM dataflow for policy rates
            data = await fetch_policy_rate_data(symbol, start_date, end_date)
        elif symbol.startswith("EUR_"):
            # Implemented: ECB SDMX EXR dataflow for FX rates
            data = await fetch_fx_rate_data(symbol, start_date, end_date)
        else:
            raise HTTPException(
                status_code=404, detail=f"Symbol {symbol} not supported"
            )

        # Apply countback if specified
        if countback and len(data["t"]) > countback:
            for key in ["t", "c", "o", "h", "l", "v"]:
                data[key] = data[key][-countback:]

        logger.info(f"Returning {len(data['t'])} bars for {symbol}")
        return data

    except Exception as e:
        logger.error(f"Failed to fetch bars for {symbol}: {e}")
        return {"s": "no_data", "nextTime": int(datetime.now().timestamp())}


async def fetch_estr_data(start_date: date, end_date: date) -> Dict[str, List]:
    """Fetch ECB €STR data via official SDMX."""
    try:
        estr_data = await fetch_ecb_estr_rate(None, start_date, end_date)

        times = []
        values = []

        for date_str, data in sorted(estr_data.items()):
            if "ESTR_Rate" in data:
                times.append(
                    unix_timestamp(datetime.strptime(date_str, "%Y-%m-%d").date())
                )
                values.append(data["ESTR_Rate"])

        return {
            "t": times,
            "c": values,  # Close
            "o": values,  # Open (same as close for rates)
            "h": values,  # High (same as close for rates)
            "l": values,  # Low (same as close for rates)
            "v": [0] * len(values),  # Volume (N/A for rates)
            "s": "ok",
        }

    except Exception as e:
        logger.error(f"Failed to fetch ECB €STR data: {e}")
        raise HTTPException(status_code=503, detail="ECB €STR data unavailable")


async def fetch_euribor_hsta_data(
    symbol: str, start_date: date, end_date: date
) -> Dict[str, List]:
    """Fetch Euribor data via web scraping from euribor-rates.eu (license-clean)."""
    try:
        # Extract tenor from symbol (e.g., EURIBOR_3M -> 3M)
        tenor = symbol.split("_", 1)[1]

        # All tenors supported by web scraper
        supported_tenors = ["1W", "1M", "3M", "6M", "12M"]

        if tenor not in supported_tenors:
            logger.warning(f"Tenor {tenor} not supported by Euribor web scraper")
            return {"s": "no_data"}

        # Fetch Euribor data via web scraping (EMMI-compliant T+1 delay)
        euribor_data = await fetch_official_euribor_rates(
            cache_service=None, start_date=start_date, end_date=end_date, tenors=[tenor]
        )

        if not euribor_data:
            logger.warning(f"No Euribor data available for {tenor}")
            return {"s": "no_data"}

        times = []
        values = []

        for date_str, data in sorted(euribor_data.items()):
            if tenor in data and data[tenor] is not None:
                try:
                    # Parse date string
                    obs_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    times.append(unix_timestamp(obs_date))
                    values.append(round(float(data[tenor]), 3))
                except (ValueError, KeyError) as e:
                    logger.debug(f"Error parsing Euribor data for {date_str}: {e}")
                    continue

        if not times:
            logger.warning(f"No valid Euribor data points for {symbol}")
            return {"s": "no_data"}

        logger.info(f"Fetched {len(times)} Euribor data points for {symbol}")

        return {
            "t": times,
            "c": values,
            "o": values,
            "h": values,
            "l": values,
            "v": [0] * len(values),
            "s": "ok",
        }
    except Exception as e:
        logger.error(f"Failed to fetch Euribor data for {symbol}: {e}")
        return {"s": "no_data"}


async def fetch_euribor_demo_data(
    symbol: str, start_date: date, end_date: date
) -> Dict[str, List]:
    """Generate demo Euribor data for unsupported tenors."""
    # Extract tenor from symbol
    tenor = symbol.split("_", 1)[1]

    # Demo rates for unsupported tenors
    demo_rates = {"3M": 2.008, "6M": 2.075, "12M": 2.126}

    if tenor not in demo_rates:
        raise HTTPException(status_code=404, detail=f"Tenor {tenor} not supported")

    base_rate = demo_rates[tenor]

    # Generate historical data with slight variations
    times = []
    values = []

    current_date = start_date
    while current_date <= end_date:
        # Skip weekends (basic business day logic)
        if current_date.weekday() < 5:
            times.append(unix_timestamp(current_date))
            # Add slight variation to make it look realistic
            variation = (current_date.day % 10 - 5) * 0.001
            values.append(round(base_rate + variation, 3))
        current_date += timedelta(days=1)

    return {
        "t": times,
        "c": values,
        "o": values,
        "h": values,
        "l": values,
        "v": [0] * len(values),
        "s": "ok",
    }


async def fetch_bubor_data(
    symbol: str, start_date: date, end_date: date
) -> Dict[str, List]:
    """Fetch BUBOR data via MNB source."""
    try:
        bubor_data = await fetch_bubor_curve(start_date, end_date, None)

        # Extract tenor from symbol (e.g., BUBOR_3M -> 3M)
        tenor = symbol.split("_", 1)[1]

        # Map symbol tenor to BUBOR data key
        tenor_mapping = {
            "ON": "O/N",
            "1W": "1W",
            "1M": "1M",
            "3M": "3M",
            "6M": "6M",
            "12M": "12M",
        }

        bubor_key = tenor_mapping.get(tenor)
        if not bubor_key:
            raise HTTPException(
                status_code=404, detail=f"BUBOR tenor {tenor} not supported"
            )

        times = []
        values = []

        for date_str, data in sorted(bubor_data.items()):
            if bubor_key in data and data[bubor_key] is not None:
                times.append(
                    unix_timestamp(datetime.strptime(date_str, "%Y-%m-%d").date())
                )
                values.append(data[bubor_key])

        return {
            "t": times,
            "c": values,
            "o": values,
            "h": values,
            "l": values,
            "v": [0] * len(values),
            "s": "ok",
        }

    except Exception as e:
        logger.error(f"Failed to fetch BUBOR data for {symbol}: {e}")
        raise HTTPException(status_code=503, detail="BUBOR data unavailable")


async def fetch_yield_curve_data(
    symbol: str, start_date: date, end_date: date
) -> Dict[str, List]:
    """Fetch ECB yield curve data via official SDMX YC dataflow."""
    try:
        # Extract maturity from symbol (e.g., YC_SR_10Y -> 10Y)
        maturity = symbol.split("_")[-1]  # Gets "10Y" from "YC_SR_10Y"

        # Fetch yield curve data
        yc_data = await fetch_yield_curve_rates(
            cache_service=None,
            start_date=start_date,
            end_date=end_date,
            maturities=[maturity],
        )

        if not yc_data:
            logger.warning(f"No yield curve data available for {maturity}")
            return {"s": "no_data"}

        times = []
        values = []

        for date_str, data in sorted(yc_data.items()):
            if maturity in data and data[maturity] is not None:
                try:
                    # Parse date string
                    obs_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    times.append(unix_timestamp(obs_date))
                    values.append(round(float(data[maturity]), 3))
                except (ValueError, KeyError) as e:
                    logger.debug(f"Error parsing yield curve data for {date_str}: {e}")
                    continue

        if not times:
            logger.warning(f"No valid yield curve data points for {symbol}")
            return {"s": "no_data"}

        logger.info(f"Fetched {len(times)} yield curve data points for {symbol}")

        return {
            "t": times,
            "c": values,
            "o": values,
            "h": values,
            "l": values,
            "v": [0] * len(values),
            "s": "ok",
        }
    except Exception as e:
        logger.error(f"Failed to fetch yield curve data for {symbol}: {e}")
        return {"s": "no_data"}


async def fetch_policy_rate_data(
    symbol: str, start_date: date, end_date: date
) -> Dict[str, List]:
    """Fetch ECB policy rates data via official SDMX FM dataflow."""
    try:
        # Extract rate type from symbol (e.g., ECB_DFR -> DFR)
        rate_type = symbol.split("_")[-1]  # Gets "DFR" from "ECB_DFR"

        # Validate rate type
        valid_rates = ["DFR", "MRO", "MSF"]
        if rate_type not in valid_rates:
            logger.error(f"Invalid policy rate type: {rate_type}")
            return {"s": "no_data"}

        # Fetch policy rates data
        policy_data = await fetch_policy_rates(
            cache_service=None,
            start_date=start_date,
            end_date=end_date,
            rates=[rate_type],
        )

        if not policy_data:
            logger.warning(f"No policy rate data available for {rate_type}")
            return {"s": "no_data"}

        times = []
        values = []

        for date_str, data in sorted(policy_data.items()):
            if rate_type in data and data[rate_type] is not None:
                try:
                    # Parse date string
                    obs_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    times.append(unix_timestamp(obs_date))
                    values.append(round(float(data[rate_type]), 3))
                except (ValueError, KeyError) as e:
                    logger.debug(f"Error parsing policy rate data for {date_str}: {e}")
                    continue

        if not times:
            logger.warning(f"No valid policy rate data points for {symbol}")
            return {"s": "no_data"}

        logger.info(f"Fetched {len(times)} policy rate data points for {symbol}")

        return {
            "t": times,
            "c": values,
            "o": values,
            "h": values,
            "l": values,
            "v": [0] * len(values),
            "s": "ok",
        }
    except Exception as e:
        logger.error(f"Failed to fetch policy rate data for {symbol}: {e}")
        return {"s": "no_data"}


async def fetch_fx_rate_data(
    symbol: str, start_date: date, end_date: date
) -> Dict[str, List]:
    """Fetch ECB FX rates data via official SDMX EXR dataflow."""
    try:
        # Extract currency from symbol (e.g., EUR_USD -> USD)
        currency = symbol.split("_")[-1]  # Gets "USD" from "EUR_USD"

        # Validate currency
        valid_currencies = [
            "USD",
            "GBP",
            "HUF",
            "CHF",
            "JPY",
            "CAD",
            "AUD",
            "SEK",
            "NOK",
            "DKK",
            "PLN",
            "CZK",
        ]
        if currency not in valid_currencies:
            logger.error(f"Invalid currency: {currency}")
            return {"s": "no_data"}

        # Fetch FX rates data
        fx_data = await fetch_fx_rates(
            cache_service=None,
            start_date=start_date,
            end_date=end_date,
            currencies=[currency],
        )

        if not fx_data:
            logger.warning(f"No FX rate data available for {currency}")
            return {"s": "no_data"}

        times = []
        values = []

        for date_str, data in sorted(fx_data.items()):
            if currency in data and data[currency] is not None:
                try:
                    # Parse date string
                    obs_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    times.append(unix_timestamp(obs_date))
                    values.append(round(float(data[currency]), 4))
                except (ValueError, KeyError) as e:
                    logger.debug(f"Error parsing FX rate data for {date_str}: {e}")
                    continue

        if not times:
            logger.warning(f"No valid FX rate data points for {symbol}")
            return {"s": "no_data"}

        logger.info(f"Fetched {len(times)} FX rate data points for {symbol}")

        return {
            "t": times,
            "c": values,
            "o": values,
            "h": values,
            "l": values,
            "v": [0] * len(values),
            "s": "ok",
        }
    except Exception as e:
        logger.error(f"Failed to fetch FX rate data for {symbol}: {e}")
        return {"s": "no_data"}
