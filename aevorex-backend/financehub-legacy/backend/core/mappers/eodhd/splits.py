# Aevorex_codes/modules/financehub/backend/core/mappers/eodhd/splits.py
from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING

from backend.core.mappers._mapper_base import logger
from backend.core.helpers import _clean_value
from backend.models.stock import StockSplitData

if TYPE_CHECKING:
    from ....models import StockSplitData


def map_eodhd_splits_data_to_models(
    splits_df: pd.DataFrame | None, request_id: str
) -> list["StockSplitData"] | None:
    from ....models import StockSplitData

    func_name = "map_eodhd_splits_data_to_models"
    log_prefix = f"[{request_id}][{func_name}]"

    if not isinstance(splits_df, pd.DataFrame) or splits_df.empty:
        logger.info(
            f"{log_prefix} Input splits_df is invalid or empty. Returning empty list."
        )
        return []

    split_models: list[StockSplitData] = []

    # Ensure the columns are as expected from the fetcher
    if "Date" not in splits_df.columns or "Stock_Split" not in splits_df.columns:
        logger.error(
            f"{log_prefix} Missing 'Date' or 'Stock_Split' column in DataFrame. Cannot process splits."
        )
        return None

    for index, row in splits_df.iterrows():
        try:
            split_date_str = row["Date"]
            split_ratio_str = _clean_value(row["Stock_Split"])

            if not split_date_str or not split_ratio_str:
                logger.warning(
                    f"{log_prefix} Skipping split at index {index} due to missing data."
                )
                continue

            # Further processing can be added here, e.g., parsing the ratio string
            split_data = {
                "split_date": pd.to_datetime(split_date_str).date(),
                "split_ratio": split_ratio_str,
                "data_source": "eodhd",
            }
            split_models.append(StockSplitData(**split_data))
        except Exception as e:
            logger.error(
                f"{log_prefix} Error processing split row at index {index}: {e}",
                exc_info=True,
            )

    logger.info(f"{log_prefix} Successfully mapped {len(split_models)} stock splits.")
    return split_models
