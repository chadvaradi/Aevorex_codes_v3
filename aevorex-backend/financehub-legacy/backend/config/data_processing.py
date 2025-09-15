"""
Data processing settings.
"""

import json
from typing import Any
from pydantic import field_validator, BaseModel, Field, model_validator
from pydantic.types import PositiveInt, PositiveFloat


class DataProcessingSettings(BaseModel):
    """Adatfeldolgozási beállítások."""

    OHLCV_YEARS_TO_FETCH: PositiveInt = Field(default=2)
    OHLCV_YEARS_TO_PROCESS_INDICATORS: PositiveInt = Field(default=1)
    CHART_HISTORY_YEARS: PositiveFloat = Field(default=2.0)

    INDICATOR_PARAMS: dict[str, PositiveInt | PositiveFloat | bool] = Field(
        default_factory=lambda: {
            "sma_short": 20,
            "sma_long": 50,
            "ema_short": 12,
            "ema_long": 26,
            "rsi_period": 14,
            "bbands_period": 20,
            "bbands_std_dev": 2,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "stoch_k": 14,
            "stoch_d": 3,
            "stoch_smooth_k": 3,
        }
    )

    @field_validator("INDICATOR_PARAMS", mode="before")
    @classmethod
    def _parse_indicator_params_json(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError(
                    "INDICATOR_PARAMS must be a valid JSON string if provided as a string."
                )
        return v

    @model_validator(mode="after")
    def _check_year_limits_consistency(self) -> "DataProcessingSettings":
        if self.OHLCV_YEARS_TO_PROCESS_INDICATORS > self.OHLCV_YEARS_TO_FETCH:
            raise ValueError(
                "OHLCV_YEARS_TO_PROCESS_INDICATORS cannot be greater than OHLCV_YEARS_TO_FETCH."
            )
        return self
