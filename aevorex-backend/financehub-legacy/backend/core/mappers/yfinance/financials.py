# Aevorex_codes/modules/financehub/backend/core/mappers/yfinance/financials.py
import pandas as pd
from typing import Any

from backend.models import FinancialsData
from backend.core.mappers._mapper_base import logger, safe_get
from backend.core.helpers import parse_optional_int

_YFINANCE_REVENUE_KEYS: list[str] = [
    "Total Revenue",
    "Revenues",
    "Revenue",
    "Net Revenue",
]
_YFINANCE_NET_INCOME_KEYS: list[str] = [
    "Net Income",
    "Net Income Common Stockholders",
    "Net Income From Continuing Operations",
    "Net Income Applicable To Common Shares",
    "Net Income Available to Common Stockholders",
]
_YFINANCE_ASSETS_KEYS: list[str] = ["Total Assets"]
_YFINANCE_LIABILITIES_KEYS: list[str] = [
    "Total Liabilities Net Minority",
    "Total Liabilities",
    "Total Liabilities Net Minority",
]


def get_latest_financial_values(
    df: pd.DataFrame | None,
    df_name: str,
    df_type_log: str,
    request_id: str,
    symbol: str = "N/A_SYMBOL",
) -> dict[str, Any]:
    """
    Helper to extract the latest values for key metrics from a single DataFrame.
    Handles both annual and quarterly data by using the most recent column.
    """
    log_prefix = f"[{request_id}][get_latest_financial_values][{symbol}]"
    inner_log_prefix = f"{log_prefix}[{df_name}]"
    results: dict[str, Any] = {
        "latest_revenue": None,
        "latest_net_income": None,
        "latest_total_assets": None,
        "latest_total_liabilities": None,
        "latest_report_date": None,
        "latest_report_type": df_type_log,
    }

    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.debug(f"{inner_log_prefix} DataFrame is missing or empty. Skipping.")
        return results

    if not isinstance(df.columns, pd.DatetimeIndex):
        logger.warning(
            f"{inner_log_prefix} DataFrame columns are not a DatetimeIndex. Cannot reliably determine the latest period. Columns: {df.columns}"
        )
        return results

    latest_column = df.columns.max()
    results["latest_report_date"] = latest_column.strftime("%Y-%m-%d")
    logger.debug(
        f"{inner_log_prefix} Identified latest report date: {results['latest_report_date']}"
    )

    key_mapping = [
        ("latest_revenue", _YFINANCE_REVENUE_KEYS),
        ("latest_net_income", _YFINANCE_NET_INCOME_KEYS),
        ("latest_total_assets", _YFINANCE_ASSETS_KEYS),
        ("latest_total_liabilities", _YFINANCE_LIABILITIES_KEYS),
    ]

    for result_key, item_keys in key_mapping:
        for item_key in item_keys:
            value = safe_get(df, item_key, latest_column)
            if value is not None:
                parsed_value = parse_optional_int(value)
                if parsed_value is not None:
                    results[result_key] = parsed_value
                    logger.debug(
                        f"{inner_log_prefix} Found and parsed '{item_key}' as {result_key}: {parsed_value}"
                    )
                    break
        if results[result_key] is None:
            logger.debug(
                f"{inner_log_prefix} Could not find a valid value for {result_key} using keys: {item_keys}"
            )

    return results


def map_financial_dataframes_to_financials_model(
    financial_dfs: dict[str, pd.DataFrame | None],
    request_id: str,
    currency: str | None,
    symbol: str | None = "N/A_SYMBOL",
) -> FinancialsData | None:
    """
    Maps a dictionary of pandas DataFrames (from yfinance financials, balance_sheet)
    to the FinancialsData Pydantic model. It robustly extracts the latest
    available data for key financial metrics.
    """
    func_name = "map_financial_dataframes_to_financials_model"
    log_prefix = f"[{request_id}][{func_name}][{symbol}]"

    if not financial_dfs or not any(
        isinstance(df, pd.DataFrame) and not df.empty for df in financial_dfs.values()
    ):
        logger.warning(
            f"{log_prefix} Input financial_dfs is None, empty, or contains no valid DataFrames. Cannot map to FinancialsData."
        )
        return None

    annual_financials = get_latest_financial_values(
        financial_dfs.get("financials_annual"),
        "financials_annual",
        "annual",
        request_id,
        symbol,
    )
    quarterly_financials = get_latest_financial_values(
        financial_dfs.get("financials_quarterly"),
        "financials_quarterly",
        "quarterly",
        request_id,
        symbol,
    )
    annual_balance = get_latest_financial_values(
        financial_dfs.get("balance_sheet_annual"),
        "balance_sheet_annual",
        "annual",
        request_id,
        symbol,
    )
    quarterly_balance = get_latest_financial_values(
        financial_dfs.get("balance_sheet_quarterly"),
        "balance_sheet_quarterly",
        "quarterly",
        request_id,
        symbol,
    )

    final_data = {
        "symbol": symbol,
        "data_source": "yfinance",
        "currency_code": currency,
        "annual_revenue": annual_financials["latest_revenue"],
        "quarterly_revenue": quarterly_financials["latest_revenue"],
        "annual_net_income": annual_financials["latest_net_income"],
        "quarterly_net_income": quarterly_financials["latest_net_income"],
        "total_assets": annual_balance["latest_total_assets"]
        or quarterly_balance["latest_total_assets"],
        "total_liabilities": annual_balance["latest_total_liabilities"]
        or quarterly_balance["latest_total_liabilities"],
        "last_annual_report_date": annual_financials["latest_report_date"],
        "last_quarterly_report_date": quarterly_financials["latest_report_date"],
    }

    try:
        model = FinancialsData(**{k: v for k, v in final_data.items() if v is not None})
        logger.info(
            f"{log_prefix} Successfully mapped financial DataFrames to FinancialsData model."
        )
        return model
    except Exception as e:
        logger.error(
            f"{log_prefix} Pydantic validation failed for FinancialsData: {e}",
            exc_info=True,
        )
        return None
