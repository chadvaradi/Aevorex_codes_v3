# Aevorex_codes/modules/financehub/backend/core/mappers/yfinance/earnings.py
import pandas as pd

from backend.models import EarningsPeriodData
from backend.core.mappers._mapper_base import logger, safe_get
from backend.core.helpers import parse_optional_int


def map_yfinance_financial_statement_to_earnings_periods(
    statement_df: pd.DataFrame | None,
    request_id: str,
    currency: str | None,
    report_period_type: str,
) -> list[EarningsPeriodData]:
    """
    Maps a yfinance financial statement DataFrame (quarterly or annual) to a list of
    EarningsPeriodData models.
    """
    func_name = "map_yfinance_financial_statement_to_earnings_periods"
    log_prefix = f"[{request_id}][{func_name}]"

    if not isinstance(statement_df, pd.DataFrame) or statement_df.empty:
        logger.debug(
            f"{log_prefix} Input DataFrame for '{report_period_type}' is invalid or empty. Returning empty list."
        )
        return []

    if not isinstance(statement_df.columns, pd.DatetimeIndex):
        logger.warning(
            f"{log_prefix} DataFrame for '{report_period_type}' does not have a DatetimeIndex. Columns: {statement_df.columns}. Cannot process."
        )
        return []

    earnings_periods: list[EarningsPeriodData] = []

    for period_date in statement_df.columns:
        period_log_prefix = f"{log_prefix}[{period_date.strftime('%Y-%m-%d')}]"
        try:
            revenue_raw = safe_get(statement_df, "Total Revenue", period_date)
            eps_raw = safe_get(statement_df, "Basic EPS", period_date)

            period_data = {
                "report_date": period_date.date(),
                "revenue": parse_optional_int(revenue_raw),
                "eps": parse_optional_int(
                    eps_raw
                ),  # Should be float, but let's stick to int for now as per original
                "currency_code": currency,
                "period_type": report_period_type,
            }

            earnings_periods.append(
                EarningsPeriodData(
                    **{k: v for k, v in period_data.items() if v is not None}
                )
            )
            logger.debug(
                f"{period_log_prefix} Successfully created EarningsPeriodData."
            )

        except Exception as e:
            logger.error(
                f"{period_log_prefix} Error processing period: {e}", exc_info=True
            )

    logger.info(
        f"{log_prefix} Mapped {len(earnings_periods)} '{report_period_type}' earnings periods."
    )
    return earnings_periods
