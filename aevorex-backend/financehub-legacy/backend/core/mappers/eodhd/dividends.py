# Aevorex_codes/modules/financehub/backend/core/mappers/eodhd/dividends.py
from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING

from backend.core.mappers._mapper_base import logger
from backend.core.helpers import parse_optional_float
from backend.models.stock import DividendData

if TYPE_CHECKING:
    from ....models import DividendData


def map_eodhd_dividends_data_to_models(
    dividends_df: pd.DataFrame | None, request_id: str
) -> list["DividendData"] | None:
    from ....models import DividendData

    func_name = "map_eodhd_dividends_data_to_models"
    log_prefix = f"[{request_id}][{func_name}]"

    if not isinstance(dividends_df, pd.DataFrame) or dividends_df.empty:
        logger.info(
            f"{log_prefix} Input dividends_df is invalid or empty. Returning empty list."
        )
        return []

    dividend_models: list[DividendData] = []

    if "date" not in dividends_df.columns or "value" not in dividends_df.columns:
        logger.error(
            f"{log_prefix} Missing 'date' or 'value' column in DataFrame. Cannot process dividends."
        )
        return None

    for index, row in dividends_df.iterrows():
        try:
            dividend_date_str = row["date"]
            dividend_value_raw = row["value"]

            if not dividend_date_str or dividend_value_raw is None:
                logger.warning(
                    f"{log_prefix} Skipping dividend at index {index} due to missing data."
                )
                continue

            dividend_data = {
                "dividend_date": pd.to_datetime(dividend_date_str).date(),
                "dividend_value": parse_optional_float(dividend_value_raw),
                "data_source": "eodhd",
            }
            dividend_models.append(DividendData(**dividend_data))
        except Exception as e:
            logger.error(
                f"{log_prefix} Error processing dividend row at index {index}: {e}",
                exc_info=True,
            )

    logger.info(f"{log_prefix} Successfully mapped {len(dividend_models)} dividends.")
    return dividend_models
