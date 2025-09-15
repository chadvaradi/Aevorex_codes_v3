"""
Chart Data Validators - Handles validation and formatting of OHLCV data.
Split from chart_data_handler.py to maintain 160 LOC limit.
"""

import pandas as pd
from typing import Any
from backend.models.stock import LatestOHLCV, CompanyPriceHistoryEntry
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.ChartValidators")


class ChartDataValidator:
    """Handles validation and formatting of chart data."""

    async def validate_ohlcv_dataframe(
        self, chart_ready_list: list[dict[str, Any]], request_id: str
    ) -> pd.DataFrame | None:
        """Validate and convert chart data to DataFrame."""
        try:
            if not chart_ready_list:
                return None

            df = pd.DataFrame(chart_ready_list)

            # Ensure required columns
            required_cols = ["timestamp", "open", "high", "low", "close", "volume"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                logger.error(f"[{request_id}] Missing required columns: {missing_cols}")
                return None

            # Convert timestamp to datetime index
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)

            # Ensure numeric columns
            numeric_cols = ["open", "high", "low", "close", "volume"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Remove rows with all NaN values
            df = df.dropna(how="all")

            if df.empty:
                logger.warning(f"[{request_id}] DataFrame is empty after validation")
                return None

            return df

        except Exception as e:
            logger.error(
                f"[{request_id}] DataFrame validation failed: {e}", exc_info=True
            )
            return None

    async def prepare_ohlcv_for_response(
        self, chart_ready_ohlcv_list: list[dict[str, Any]] | None, request_id: str
    ) -> tuple:
        """Prepare OHLCV data for API response format."""
        if not chart_ready_ohlcv_list:
            return [], None, None, None

        try:
            # Convert to price history entries (FinBot expects 'date' + o/h/low/c/v)
            price_history: list[CompanyPriceHistoryEntry] = []
            for entry in chart_ready_ohlcv_list:
                ts = entry.get("timestamp")
                date_str: str | None = None
                if ts is not None:
                    try:
                        # Accept both epoch ints and ISO strings
                        if isinstance(ts, (int, float)):
                            import datetime

                            date_str = datetime.datetime.utcfromtimestamp(
                                int(ts)
                            ).strftime("%Y-%m-%d")
                        else:
                            # assume already date‐like string
                            date_str = str(ts)[:10]
                    except Exception:
                        date_str = str(ts)

                price_history.append(
                    CompanyPriceHistoryEntry(
                        date=date_str or "1970-01-01",
                        o=entry.get("open"),
                        h=entry.get("high"),
                        low=entry.get("low"),
                        c=entry.get("close"),
                        v=entry.get("volume"),
                    )
                )

            # Get latest OHLCV
            latest_entry = (
                chart_ready_ohlcv_list[-1] if chart_ready_ohlcv_list else None
            )
            latest_ohlcv = None
            latest_price_str = None
            latest_price_float = None

            if latest_entry:
                latest_ohlcv = LatestOHLCV(
                    o=latest_entry.get("open"),
                    h=latest_entry.get("high"),
                    low=latest_entry.get("low"),
                    c=latest_entry.get("close"),
                    v=latest_entry.get("volume"),
                    c_timestamp=latest_entry.get("timestamp"),
                )

                close_price = latest_entry.get("close")
                if close_price is not None:
                    latest_price_float = float(close_price)
                    latest_price_str = f"${latest_price_float:.2f}"

            return price_history, latest_ohlcv, latest_price_str, latest_price_float

        except Exception as e:
            logger.error(
                f"[{request_id}] OHLCV response preparation failed: {e}", exc_info=True
            )
            return [], None, None, None
