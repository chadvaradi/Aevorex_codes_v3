# Aevorex_codes/modules/financehub/backend/core/mappers/fmp/ratings.py
import time
from typing import Any

from backend.models import RatingPoint
from backend.core.mappers._mapper_base import logger


def map_fmp_raw_ratings_to_rating_points(
    ratings_list: list[dict[str, Any]] | None, request_id: str
) -> list[RatingPoint] | None:
    """
    Maps a list of historical rating dictionaries from the FMP API
    to a list of RatingPoint Pydantic model instances.
    """
    func_name = "map_fmp_raw_ratings_to_rating_points"
    log_prefix = f"[{request_id}][{func_name}]"

    if not ratings_list:
        logger.info(
            f"{log_prefix} Input ratings_list is None or empty. No ratings to map, returning None."
        )
        return None
    if not isinstance(ratings_list, list):
        logger.warning(
            f"{log_prefix} Input ratings_list is not a list (type: {type(ratings_list)}). Cannot map, returning None."
        )
        return None

    map_start_time = time.monotonic()
    processed_rating_points: list[RatingPoint] = []
    skipped_item_count = 0

    for i, raw_rating_item in enumerate(ratings_list):
        item_log_prefix = f"{log_prefix}[RatingItem #{i + 1}/{len(ratings_list)}]"
        if not isinstance(raw_rating_item, dict):
            logger.warning(
                f"{item_log_prefix} Skipping: Item is not a dictionary (type: {type(raw_rating_item)})."
            )
            skipped_item_count += 1
            continue

        try:
            validated_point = RatingPoint.model_validate(raw_rating_item)
            processed_rating_points.append(validated_point)
        except Exception as e:
            logger.warning(
                f"{item_log_prefix} Skipping rating due to validation error: {e}. Raw data: {raw_rating_item}"
            )
            skipped_item_count += 1

    map_duration = time.monotonic() - map_start_time
    logger.info(
        f"{log_prefix} Mapped {len(processed_rating_points)} FMP rating items in {map_duration:.4f}s. Skipped {skipped_item_count} items."
    )

    return processed_rating_points if processed_rating_points else None
