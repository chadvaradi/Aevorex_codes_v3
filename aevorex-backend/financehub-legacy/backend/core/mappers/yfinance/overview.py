from typing import Any
from pydantic import ValidationError

from backend.models import CompanyOverview
from backend.core.helpers import (
    _clean_value,
    parse_optional_float,
    parse_optional_int,
    parse_timestamp_to_iso_utc,
    normalize_url,
)
from backend.core.mappers._mapper_base import logger


def parse_ts_to_date_str(
    ts_val: Any, field_name: str, context_prefix: str
) -> str | None:
    """Parse timestamp value to date string format."""
    if ts_val is None:
        return None
    parsed_iso = parse_timestamp_to_iso_utc(
        ts_val, context=f"{context_prefix}:{field_name}"
    )
    return parsed_iso.split("T")[0] if parsed_iso else None


def map_yfinance_info_to_overview(
    info_dict: dict[str, Any] | None,
    request_id: str,
    symbol_override: str | None = None,
) -> CompanyOverview | None:
    """
    Maps the dictionary from yfinance Ticker.info to the CompanyOverview Pydantic model.
    """
    func_name = "map_yfinance_info_to_overview"
    log_prefix = f"[{request_id}][{func_name}]"

    if not info_dict:
        logger.warning(
            f"{log_prefix} Input yfinance 'info' dictionary is None or empty. Cannot map to CompanyOverview."
        )
        return None

    symbol = str(symbol_override or info_dict.get("symbol", "N/A")).upper()
    log_prefix = f"[{request_id}][{func_name}][{symbol}]"

    try:
        overview_data = {
            "symbol": symbol,
            "name": _clean_value(info_dict.get("longName")),
            "description": _clean_value(info_dict.get("longBusinessSummary")),
            "country": _clean_value(info_dict.get("country")),
            "sector": _clean_value(info_dict.get("sector")),
            "industry": _clean_value(info_dict.get("industry")),
            "address": _clean_value(info_dict.get("address1")),
            "city": _clean_value(info_dict.get("city")),
            "state": _clean_value(info_dict.get("state")),
            "zip_code": _clean_value(info_dict.get("zip")),
            "website": normalize_url(info_dict.get("website")),
            "phone": _clean_value(info_dict.get("phone")),
            "logo_url": normalize_url(info_dict.get("logo_url")),
            "full_time_employees": parse_optional_int(
                info_dict.get("fullTimeEmployees")
            ),
            "market_cap": parse_optional_int(info_dict.get("marketCap")),
            "shares_outstanding": parse_optional_int(
                info_dict.get("sharesOutstanding")
            ),
            "shares_float": parse_optional_int(info_dict.get("floatShares")),
            "pe_ratio_trailing": parse_optional_float(info_dict.get("trailingPE")),
            "pe_ratio_forward": parse_optional_float(info_dict.get("forwardPE")),
            "peg_ratio": parse_optional_float(info_dict.get("pegRatio")),
            "price_to_sales_ratio": parse_optional_float(
                info_dict.get("priceToSalesTrailing12Months")
            ),
            "price_to_book_ratio": parse_optional_float(info_dict.get("priceToBook")),
            "dividend_yield": parse_optional_float(info_dict.get("dividendYield")),
            "dividend_rate": parse_optional_float(info_dict.get("dividendRate")),
            "ex_dividend_date": parse_ts_to_date_str(
                info_dict.get("exDividendDate"), "exDividendDate", log_prefix
            ),
            "last_dividend_date": parse_ts_to_date_str(
                info_dict.get("lastDividendDate"), "lastDividendDate", log_prefix
            ),
            "beta": parse_optional_float(info_dict.get("beta")),
            "eps_trailing": parse_optional_float(info_dict.get("trailingEps")),
            "eps_forward": parse_optional_float(info_dict.get("forwardEps")),
            "fifty_two_week_high": parse_optional_float(
                info_dict.get("fiftyTwoWeekHigh")
            ),
            "fifty_two_week_low": parse_optional_float(
                info_dict.get("fiftyTwoWeekLow")
            ),
            "fifty_day_average": parse_optional_float(info_dict.get("fiftyDayAverage")),
            "two_hundred_day_average": parse_optional_float(
                info_dict.get("twoHundredDayAverage")
            ),
            "currency": _clean_value(info_dict.get("currency")),
            "exchange": _clean_value(info_dict.get("exchange")),
            "quote_type": _clean_value(info_dict.get("quoteType")),
            "data_source": "yfinance",
        }

        # Filter out None values to avoid Pydantic validation errors on optional fields
        # that are not explicitly set.
        validated_data = {k: v for k, v in overview_data.items() if v is not None}

        model = CompanyOverview(**validated_data)
        logger.info(
            f"{log_prefix} Successfully mapped yfinance 'info' to CompanyOverview model."
        )
        return model

    except ValidationError as e:
        logger.error(
            f"{log_prefix} Pydantic validation failed for CompanyOverview: {e}",
            exc_info=True,
        )
        return None
    except Exception as e:
        logger.error(f"{log_prefix} An unexpected error occurred: {e}", exc_info=True)
        return None
