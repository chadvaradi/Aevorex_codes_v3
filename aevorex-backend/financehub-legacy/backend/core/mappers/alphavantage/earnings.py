from datetime import datetime
from typing import Any, cast
from datetime import date as DateObject
import time

from backend.models import EarningsData, EarningsPeriodData
from backend.core.mappers._mapper_base import logger
from backend.core.helpers import parse_optional_float
from backend.core.mappers._dynamic_validator import _dynamic_import_and_validate


def map_alpha_vantage_earnings_to_model(
    av_earnings_data: dict[str, Any] | None, request_id: str
) -> EarningsData | None:
    """
    Maps the raw dictionary response from Alpha Vantage EARNINGS API endpoint
    to the EarningsData Pydantic model using dynamic validation.
    Handles both annual and quarterly reports present in the AV response.
    """
    func_name = "map_alpha_vantage_earnings_to_model"
    log_prefix = f"[{request_id}][{func_name}]"
    logger.debug(f"{log_prefix} Starting mapping of Alpha Vantage earnings dict...")

    if not av_earnings_data or not isinstance(av_earnings_data, dict):
        logger.info(
            f"{log_prefix} Input av_earnings_data is None or not a dict. Cannot map."
        )
        return None

    map_start_time = time.monotonic()

    symbol = av_earnings_data.get("symbol")
    annual_reports_raw = av_earnings_data.get("annualEarnings")
    quarterly_reports_raw = av_earnings_data.get("quarterlyEarnings")

    if not symbol:
        logger.warning(
            f"{log_prefix} Missing 'symbol' key in Alpha Vantage response. API data might be incomplete."
        )
    if not isinstance(annual_reports_raw, list):
        logger.warning(
            f"{log_prefix} 'annualEarnings' is missing or not a list for symbol '{symbol}'. Defaulting to empty list."
        )
        annual_reports_raw = []
    if not isinstance(quarterly_reports_raw, list):
        logger.warning(
            f"{log_prefix} 'quarterlyEarnings' is missing or not a list for symbol '{symbol}'. Defaulting to empty list."
        )
        quarterly_reports_raw = []

    if not annual_reports_raw and not quarterly_reports_raw:
        logger.warning(
            f"{log_prefix} Both 'annualEarnings' and 'quarterlyEarnings' are missing or empty for symbol '{symbol}'. Cannot map any earnings data."
        )
        return None

    logger.debug(
        f"{log_prefix} Processing AV earnings for symbol '{symbol}'. Annual reports raw: {len(annual_reports_raw)}, Quarterly reports raw: {len(quarterly_reports_raw)}."
    )

    def _process_av_report_list(
        raw_list: list[dict[str, Any]], report_type: str, parent_log_prefix: str
    ) -> list[EarningsPeriodData]:
        processed_list: list[EarningsPeriodData] = []
        skipped_count = 0
        if not raw_list:
            return processed_list

        for i, report_dict in enumerate(raw_list):
            report_log_prefix = f"{parent_log_prefix}[{report_type} Raw #{i + 1}]"

            if not isinstance(report_dict, dict):
                logger.warning(
                    f"{report_log_prefix} Skipping: Item is not a dictionary (type: {type(report_dict)})."
                )
                skipped_count += 1
                continue

            try:
                fiscal_date_str = report_dict.get("fiscalDateEnding")
                reported_eps_str = report_dict.get("reportedEPS")

                fiscal_date_obj: DateObject | None = None
                if fiscal_date_str and isinstance(fiscal_date_str, str):
                    try:
                        fiscal_date_obj = datetime.strptime(
                            fiscal_date_str, "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        logger.warning(
                            f"{report_log_prefix} Could not parse 'fiscalDateEnding': '{fiscal_date_str}'. Invalid format."
                        )
                elif fiscal_date_str:
                    logger.warning(
                        f"{report_log_prefix} 'fiscalDateEnding' is not a string: '{fiscal_date_str}' (type: {type(fiscal_date_str)})."
                    )
                else:
                    logger.warning(f"{report_log_prefix} Missing 'fiscalDateEnding'.")

                reported_eps_val: float | None = parse_optional_float(
                    reported_eps_str, context=f"{report_log_prefix}:reportedEPS"
                )

                if fiscal_date_obj is None:
                    logger.warning(
                        f"{report_log_prefix} Skipping report due to missing or invalid fiscal date. Data: {report_dict}"
                    )
                    skipped_count += 1
                    continue

                period_data = {
                    "report_date": fiscal_date_obj,
                    "eps": reported_eps_val,
                    "period_type": report_type,
                }

                validated_model = _dynamic_import_and_validate(
                    model_name="EarningsPeriodData",
                    data=period_data,
                    log_prefix=report_log_prefix,
                )

                if validated_model:
                    processed_list.append(cast(EarningsPeriodData, validated_model))
                else:
                    skipped_count += 1
                    logger.warning(
                        f"{report_log_prefix} Skipping report due to validation failure. Data: {period_data}"
                    )

            except Exception as e:
                logger.error(
                    f"{report_log_prefix} Unexpected error processing report item: {e}",
                    exc_info=True,
                )
                skipped_count += 1

        if skipped_count > 0:
            logger.warning(
                f"{parent_log_prefix} Skipped {skipped_count}/{len(raw_list)} {report_type} reports due to errors."
            )

        return processed_list

    annual_reports = _process_av_report_list(annual_reports_raw, "annual", log_prefix)
    quarterly_reports = _process_av_report_list(
        quarterly_reports_raw, "quarterly", log_prefix
    )

    final_data = {
        "symbol": symbol,
        "data_source": "alphavantage",
        "annual_reports": annual_reports,
        "quarterly_reports": quarterly_reports,
    }

    validated_model = _dynamic_import_and_validate(
        model_name="EarningsData", data=final_data, log_prefix=log_prefix
    )

    map_duration = time.monotonic() - map_start_time
    if validated_model:
        logger.info(
            f"{log_prefix} Successfully mapped Alpha Vantage data to EarningsData model for symbol '{symbol}' in {map_duration:.4f} seconds."
        )
        return cast(EarningsData, validated_model)
    else:
        logger.error(
            f"{log_prefix} Final validation failed for EarningsData model for symbol '{symbol}'."
        )
        return None
