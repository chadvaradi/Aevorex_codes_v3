"""
ECB SDMX Data Parsers
====================

Parser functions for ECB SDMX JSON responses.
"""

import logging
from typing import Any, Dict

from .exceptions import ECBDataParsingError

logger = logging.getLogger(__name__)


def parse_ecb_policy_rates_json(payload: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Parse ECB policy rates JSON response.

    Args:
        payload: ECB SDMX JSON response

    Returns:
        Dictionary with date keys and rate values

    Raises:
        ECBDataParsingError: When parsing fails
    """
    try:
        # ECB recently started returning JSON with the 'dataSets' and
        # 'structure' sections at the **top-level** instead of nesting them
        # under a `data` object.  For backward-compatibility we support both
        # structures (new TOPLEVEL style and legacy `data` style).

        # Newer ECB SDMX endpoints may put "dataSets" at the top level (breaking the old structure
        # that wrapped everything inside a "data" object).  For backward-compatibility we
        # transparently accept both formats, mirroring the logic already used in
        # parse_ecb_yield_curve_json / parse_ecb_fx_rates_json.

        data: Dict[str, Any] | None = payload.get("data")

        # Fallback 1️⃣: new SDMX responses with PascalCase `dataSets`
        if data is None and "dataSets" in payload:
            data = payload  # type: ignore[assignment]

        # Fallback 2️⃣: some edge-case endpoints returned `datasets` (all-lowercase).
        # We normalise this variant on-the-fly so downstream logic stays intact.
        if data is None and "datasets" in payload:
            normalised_payload = {
                "dataSets": payload["datasets"],
                "structure": payload.get("structure", {}),
            }
            data = normalised_payload  # type: ignore[assignment]

        if data is None:
            raise ECBDataParsingError(
                "No 'data', 'dataSets' or 'datasets' key in ECB response"
            )

        if "dataSets" not in data or not data["dataSets"]:
            raise ECBDataParsingError("No dataSets in ECB response")

        dataset = data["dataSets"][0]

        if "series" not in dataset:
            raise ECBDataParsingError("No series in ECB dataset")

        # Get dimension info
        structure = data.get("structure", {})
        dimensions = structure.get("dimensions", {}).get("series", [])

        # Parse series data
        result = {}

        for series_key, series_data in dataset["series"].items():
            if "observations" not in series_data:
                continue

            # Determine rate type from series key
            rate_type = _determine_rate_type(series_key, dimensions)

            # Parse observations
            observations = series_data["observations"]
            series_result = {}

            for obs_key, obs_data in observations.items():
                if obs_data and obs_data[0] is not None:
                    # Get date from observation key
                    date_str = _get_date_from_obs_key(obs_key, structure)
                    if date_str:
                        series_result[date_str] = float(obs_data[0])

            if series_result:
                result[rate_type] = series_result

        logger.debug(f"Parsed {len(result)} policy rate series")
        return result

    except Exception as e:
        logger.error(f"Error parsing ECB policy rates JSON: {e}")
        raise ECBDataParsingError(f"Error parsing ECB policy rates JSON: {e}") from e


def parse_ecb_yield_curve_json(payload: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Parse ECB yield curve JSON response.

    Args:
        payload: ECB SDMX JSON response

    Returns:
        Dictionary with date keys and yield values by maturity

    Raises:
        ECBDataParsingError: When parsing fails
    """
    try:
        # 1️⃣ Normalise structure -------------------------------------------------
        data: dict | None = None

        if isinstance(payload, dict):
            # Most recent ECB SDMX returns *only* "dataSets" / "structure"
            if "data" in payload:
                data = payload["data"]  # Original format
            elif "dataSets" in payload:
                # Wrap top-level keys into the old schema for backward-compat
                data = payload  # type: ignore[assignment]
            elif "datasets" in payload:  # lowercase variant observed mid-2025
                data = {
                    "dataSets": payload["datasets"],
                    "structure": payload.get("structure", {}),
                }

        if data is None:
            raise ECBDataParsingError("No 'data' or 'dataSets' key in ECB response")

        # 2️⃣ Ensure at least one dataset is present --------------------------------
        if not data.get("dataSets"):
            raise ECBDataParsingError("No dataSets in ECB response")

        dataset = data["dataSets"][0]

        # 3️⃣ Some dataflows embed a *single* unnamed series directly inside the
        #     dataset without the extra "series" nesting (regression mid-2025).
        #     Convert such structures to the expected one on-the-fly.
        if "series" not in dataset:
            if "observations" in dataset:
                dataset = {"series": {"_0": dataset}}
            else:
                raise ECBDataParsingError("No series in ECB dataset")

        # Get dimension info
        structure = data.get("structure", {})

        # Parse series data
        result = {}

        for series_key, series_data in dataset["series"].items():
            if "observations" not in series_data:
                continue

            # Determine maturity from series key
            maturity = _determine_maturity(series_key, structure)

            # Parse observations
            observations = series_data["observations"]

            for obs_key, obs_data in observations.items():
                # ECB 2024+ DSD switched to object form: {"value": 2.34, "flags": [..]}
                obs_val = None
                if isinstance(obs_data, list):
                    obs_val = obs_data[0]
                elif isinstance(obs_data, dict):
                    obs_val = obs_data.get("value") or obs_data.get("obs_value")

                if obs_val is not None:
                    date_str = _get_date_from_obs_key(obs_key, structure)
                    if date_str:
                        result.setdefault(date_str, {})[maturity] = float(obs_val)

        logger.debug(f"Parsed yield curve data for {len(result)} dates")
        return result

    except Exception as e:
        logger.error(f"Error parsing ECB yield curve JSON: {e}")
        raise ECBDataParsingError(f"Error parsing ECB yield curve JSON: {e}") from e


def parse_ecb_fx_rates_json(payload: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Parse ECB FX rates JSON response.

    Args:
        payload: ECB SDMX JSON response

    Returns:
        Dictionary with date keys and currency rate values

    Raises:
        ECBDataParsingError: When parsing fails
    """
    try:
        # ECB 'jsondata' may place 'dataSets' at the top level in newer API versions.
        # Accept both structures for backward-compatibility.
        data = payload.get("data")
        if data is None and "dataSets" in payload:
            # Wrap top-level keys into a pseudo-'data' obj so downstream logic stays intact
            data = payload
        if data is None and "datasets" in payload:
            data = {
                "dataSets": payload["datasets"],
                "structure": payload.get("structure", {}),
            }
        if data is None:
            raise ECBDataParsingError("No 'data' or 'dataSets' key in ECB response")

        if "dataSets" not in data or not data["dataSets"]:
            raise ECBDataParsingError("No dataSets in ECB response")

        dataset = data["dataSets"][0]

        if "series" not in dataset:
            raise ECBDataParsingError("No series in ECB dataset")

        # Get dimension info
        structure = data.get("structure", {})

        # Parse series data
        result = {}

        for series_key, series_data in dataset["series"].items():
            if "observations" not in series_data:
                continue

            # Determine currency from series key
            currency = _determine_currency(series_key, structure)

            # Parse observations
            observations = series_data["observations"]

            for obs_key, obs_data in observations.items():
                if obs_data and obs_data[0] is not None:
                    # Get date from observation key
                    date_str = _get_date_from_obs_key(obs_key, structure)
                    if date_str:
                        if date_str not in result:
                            result[date_str] = {}
                        result[date_str][currency] = float(obs_data[0])

        logger.debug(f"Parsed FX rates data for {len(result)} dates")
        return result

    except Exception as e:
        logger.error(f"Error parsing ECB FX rates JSON: {e}")
        raise ECBDataParsingError(f"Error parsing ECB FX rates JSON: {e}") from e


def parse_ecb_comprehensive_json(
    payload: Dict[str, Any], series_name: str
) -> Dict[str, float]:
    """
    Parse comprehensive ECB data JSON response.

    Args:
        payload: ECB SDMX JSON response
        series_name: Name of the series for logging

    Returns:
        Dictionary with date keys and values

    Raises:
        ECBDataParsingError: When parsing fails
    """
    try:
        # Newer ECB responses moved 'dataSets' to top-level. Accept both formats.
        if "data" in payload:
            data = payload["data"]
        elif "dataSets" in payload:
            # Wrap into pseudo 'data' object for backward compatibility
            data = payload  # type: ignore[assignment]
        else:
            raise ECBDataParsingError("No 'data' or 'dataSets' key in ECB response")

        if "dataSets" not in data or not data["dataSets"]:
            raise ECBDataParsingError("No dataSets in ECB response")

        dataset = data["dataSets"][0]

        if "series" not in dataset:
            # Handle edge-case where observations are placed directly under dataset
            if "observations" in dataset:
                dataset = {"series": {"_0": dataset}}
            else:
                raise ECBDataParsingError("No series in ECB dataset")

        # Get dimension info
        structure = data.get("structure", {})

        # Parse series data
        result = {}

        for series_key, series_data in dataset["series"].items():
            if "observations" not in series_data:
                continue

            # Parse observations
            observations = series_data["observations"]

            for obs_key, obs_data in observations.items():
                if obs_data and obs_data[0] is not None:
                    # Get date from observation key
                    date_str = _get_date_from_obs_key(obs_key, structure)
                    if date_str:
                        result[date_str] = float(obs_data[0])

        logger.debug(f"Parsed {series_name} data for {len(result)} dates")
        return result

    except Exception as e:
        logger.error(f"Error parsing ECB {series_name} JSON: {e}")
        raise ECBDataParsingError(f"Error parsing ECB {series_name} JSON: {e}") from e


def parse_ecb_bop_json(payload: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Parse ECB Balance-of-Payments SDMX JSON into `{date: {component: value}}`. Accepts both legacy and new top-level layouts."""
    try:
        # 1️⃣ Normalise structure -------------------------------------------------
        data: dict | None = None

        if isinstance(payload, dict):
            if "data" in payload:
                data = payload["data"]  # Original wrapper
            elif "dataSets" in payload:
                data = payload  # New structure (2025+)

        if data is None:
            raise ECBDataParsingError("No 'data' or 'dataSets' key in ECB response")

        # 2️⃣ Ensure at least one dataset is present -----------------------------
        if not data.get("dataSets"):
            raise ECBDataParsingError("No dataSets in ECB response")

        dataset = data["dataSets"][0]

        # 3️⃣ Guard against missing series --------------------------------------
        if "series" not in dataset:
            if "observations" in dataset:
                dataset = {"series": {"_0": dataset}}
            else:
                raise ECBDataParsingError("No series in ECB dataset")

        # 4️⃣ Dimension metadata --------------------------------------------------
        structure = data.get("structure", {})

        # 5️⃣ Parse series --------------------------------------------------------
        result: dict[str, dict[str, float]] = {}

        for series_key, series_data in dataset["series"].items():
            if "observations" not in series_data:
                continue

            component = _determine_bop_component(series_key, structure)
            for obs_key, obs_data in series_data["observations"].items():
                if obs_data and obs_data[0] is not None:
                    date_str = _get_date_from_obs_key(obs_key, structure)
                    if date_str:
                        result.setdefault(date_str, {})[component] = float(obs_data[0])

        logger.debug(
            "Parsed %s dates / %s components from BOP payload", len(result), component
        )
        return result

    except Exception as e:
        logger.error("Error parsing ECB BOP JSON: %s", e)
        raise ECBDataParsingError(f"Error parsing ECB BOP JSON: {e}") from e


def parse_ecb_sts_json(payload: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """Parse ECB Short-Term Statistics SDMX JSON into `{date: {indicator: value}}`. Compatible with both legacy and new layouts."""
    try:
        # 1️⃣ Normalise structure -------------------------------------------------
        data: dict | None = None

        if isinstance(payload, dict):
            if "data" in payload:
                data = payload["data"]
            elif "dataSets" in payload:
                data = payload

        if data is None:
            raise ECBDataParsingError("No 'data' or 'dataSets' key in ECB response")

        # 2️⃣ Ensure dataset present ---------------------------------------------
        if not data.get("dataSets"):
            raise ECBDataParsingError("No dataSets in ECB response")

        dataset = data["dataSets"][0]

        if "series" not in dataset:
            if "observations" in dataset:
                dataset = {"series": {"_0": dataset}}
            else:
                raise ECBDataParsingError("No series in ECB dataset")

        structure = data.get("structure", {})

        result: dict[str, dict[str, float]] = {}

        for series_key, series_data in dataset["series"].items():
            if "observations" not in series_data:
                continue

            indicator = _determine_sts_indicator(series_key, structure)
            for obs_key, obs_data in series_data["observations"].items():
                obs_val = None
                if isinstance(obs_data, list):
                    obs_val = obs_data[0]
                elif isinstance(obs_data, dict):
                    obs_val = obs_data.get("value") or obs_data.get("obs_value")

                if obs_val is not None:
                    date_str = _get_date_from_obs_key(obs_key, structure)
                    if date_str:
                        result.setdefault(date_str, {})[indicator] = float(obs_val)

        logger.debug(
            "Parsed %s dates / %s indicators from STS payload", len(result), indicator
        )
        return result

    except Exception as e:
        logger.error("Error parsing ECB STS JSON: %s", e)
        raise ECBDataParsingError(f"Error parsing ECB STS JSON: {e}") from e


# Helper functions


def _determine_rate_type(series_key: str, dimensions: list) -> str:
    """Determine rate type from series key."""
    if "MRR_FR" in series_key:
        return "main_refinancing_rate"
    elif "DFR" in series_key:
        return "deposit_facility_rate"
    elif "MLFR" in series_key:
        return "marginal_lending_facility_rate"
    else:
        return "unknown_rate"


def _determine_maturity(series_key: str, structure: dict) -> str:
    """Determine maturity from series key."""
    if "SR_1M" in series_key:
        return "1M"
    elif "SR_3M" in series_key:
        return "3M"
    elif "SR_6M" in series_key:
        return "6M"
    elif "SR_9M" in series_key:
        return "9M"
    elif "SR_1Y" in series_key:
        return "1Y"
    elif "SR_2Y" in series_key:
        return "2Y"
    elif "SR_3Y" in series_key:
        return "3Y"
    elif "SR_5Y" in series_key:
        return "5Y"
    elif "SR_10Y" in series_key:
        return "10Y"
    else:
        return "unknown_maturity"


def _determine_currency(series_key: str, structure: dict) -> str:
    """Determine currency from series key."""
    if "USD" in series_key:
        return "USD"
    elif "GBP" in series_key:
        return "GBP"
    elif "JPY" in series_key:
        return "JPY"
    elif "CHF" in series_key:
        return "CHF"
    else:
        return "unknown_currency"


def _determine_bop_component(series_key: str, structure: dict) -> str:
    """Determine BOP component from series key."""
    if "F1" in series_key:
        return "trade_balance"
    elif "F2" in series_key:
        return "services_balance"
    elif "F3" in series_key:
        return "income_balance"
    elif "F4" in series_key:
        return "capital_account"
    elif "F5" in series_key:
        return "direct_investment"
    elif "F6" in series_key:
        return "portfolio_investment"
    elif "F7" in series_key:
        return "financial_derivatives"
    elif "F.F.T" in series_key:
        return "current_account"
    else:
        return "unknown_bop_component"


def _determine_sts_indicator(series_key: str, structure: dict) -> str:
    """Determine STS indicator from series key."""
    if "PROD" in series_key:
        return "industrial_production"
    elif "RETS" in series_key:
        return "retail_sales"
    elif "CONS" in series_key:
        return "construction_output"
    elif "UNEH" in series_key:
        return "unemployment_rate"
    elif "EMPL" in series_key:
        return "employment_rate"
    elif "BSCI" in series_key:
        return "business_confidence"
    elif "CSCI" in series_key:
        return "consumer_confidence"
    elif "CAPU" in series_key:
        return "capacity_utilization"
    else:
        return "unknown_sts_indicator"


def _get_date_from_obs_key(obs_key: str, structure: dict) -> str:
    """Get date string from observation key."""
    try:
        # Get time dimension from structure
        time_dimension = structure.get("dimensions", {}).get("observation", [])
        if time_dimension:
            time_values = time_dimension[0].get("values", [])
            obs_index = int(obs_key)
            if obs_index < len(time_values):
                return time_values[obs_index]["id"]

        # Fallback: use observation key as date
        return obs_key

    except (ValueError, IndexError, KeyError):
        # Fallback: use observation key as date
        return obs_key
