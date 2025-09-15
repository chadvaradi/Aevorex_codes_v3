# backend/core.ppers/eodhd/news_mapper.py
# ==============================================================================
# Mappers for EODHD News data.
# ==============================================================================
import pandas as pd
from datetime import timezone
import dateutil.parser
import logging

from backend.models.stock import NewsItem
from backend.core.helpers import _clean_value, normalize_url

logger = logging.getLogger(__name__)


def map_eodhd_news_data_to_models(
    news_df: pd.DataFrame | None, request_id: str
) -> list[NewsItem] | None:
    func_name = "map_eodhd_news_data_to_models"
    log_prefix = f"[{request_id}][{func_name}]"
    logger.info(f"{log_prefix} Starting mapping..")

    if news_df is None or not isinstance(news_df, pd.DataFrame):
        logger.error(f"{log_prefix} Mapping failed: Input is None or not a DataFrame.")
        return None
    if news_df.empty:
        logger.info(f"{log_prefix} Input DataFrame is empty. Returning empty list.")
        return []

    df_copy = news_df.copy()
    required_cols = {"date", "title", "content", "link"}
    if not required_cols.issubset(df_copy.columns):
        logger.error(
            f"{log_prefix} Mapping failed: Missing required columns: {required_cols - set(df_copy.columns)}."
        )
        return None

    news_item_list: list[NewsItem] = []
    skipped_count = 0
    processed_count = 0

    for index, row in df_copy.iterrows():
        point_log_prefix = f"{log_prefix}[Row:{index}]"
        try:
            pub_at_raw = pd.to_datetime(
                row.get("date", None), utc=True, errors="coerce"
            )

            if pd.isna(pub_at_raw):
                # Fallback for non-standard date formats
                pub_at_raw_str = str(row.get("date", ""))
                published_at_dt = dateutil.parser.parse(pub_at_raw_str)
            else:
                published_at_dt = pub_at_raw

            if pd.isna(published_at_dt):
                raise ValueError("Parsed to NaT")

            if published_at_dt.tzinfo is None:
                published_at_dt = published_at_dt.replace(tzinfo=timezone.utc)

            title = _clean_value(row["title"]) if pd.notna(row["title"]) else ""
            content = (
                _clean_value(row.get("content", ""))
                if pd.notna(row.get("content", ""))
                else ""
            )
            link = (
                normalize_url(str(row["link"]).strip()) if pd.notna(row["link"]) else ""
            )
            if not title or not link:
                skipped_count += 1
                continue

            symbols_raw = row.get("symbols", [])
            symbols_list = []
            if isinstance(symbols_raw, list):
                symbols_list = sorted(
                    list(
                        {
                            str(s).strip().upper()
                            for s in symbols_raw
                            if pd.notna(s) and str(s).strip()
                        }
                    )
                )
            elif isinstance(symbols_raw, str) and symbols_raw.strip():
                symbols_list = sorted(
                    list(
                        {s.strip().upper() for s in symbols_raw.split(",") if s.strip()}
                    )
                )

            entry_data = {
                "article_date": published_at_dt.date(),
                "title": title,
                "summary": content,
                "article_url": link,
                "symbols": symbols_list,
                "data_source": "eodhd",
            }
            news_item_list.append(NewsItem(**entry_data))
            processed_count += 1
        except (ValueError, TypeError, dateutil.parser.ParserError) as e:
            logger.warning(
                f"{point_log_prefix} Skipping: Invalid 'date' ('{row['date']}'): {e}"
            )
            skipped_count += 1
            continue
        except Exception as e_point:
            logger.error(
                f"{point_log_prefix} Skipping row due to unexpected error: {e_point}.",
                exc_info=True,
            )
            skipped_count += 1

    logger.info(
        f"{log_prefix} Mapping complete. Mapped: {processed_count}, Skipped: {skipped_count}."
    )
    return news_item_list
