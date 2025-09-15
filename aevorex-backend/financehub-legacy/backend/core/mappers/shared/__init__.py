"""Public API for the Shared Mapper logic."""

from .shared_mappers import (
    map_raw_news_to_standard_dicts,
    map_standard_dicts_to_newsitems,
)

__all__ = [
    "map_raw_news_to_standard_dicts",
    "map_standard_dicts_to_newsitems",
]
