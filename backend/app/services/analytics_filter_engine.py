from __future__ import annotations

from typing import Iterable

import pandas as pd

from backend.app.analytics_context import (
    AnalyticsFilters,
)


# ============================================================
# FILTER FIELD MAP
# ============================================================


FILTER_FIELD_CANDIDATES = {
    "channels": [
        "channel",
        "marketing_channel",
        "acquisition_channel",
    ],

    "categories": [
        "category",
        "product_category",
    ],

    "skus": [
        "sku",
        "sku_id",
        "product_sku",
    ],

    "couriers": [
        "courier",
        "courier_name",
        "courier_id",
    ],

    "warehouses": [
        "warehouse",
        "warehouse_name",
        "warehouse_id",
    ],

    "payment_methods": [
        "payment_method",
        "payment_type",
    ],

    "states": [
        "state",
        "customer_state",
        "shipping_state",
    ],

    "zones": [
        "zone",
        "shipping_zone",
        "customer_zone",
    ],
}


# ============================================================
# HELPERS
# ============================================================


def _normalize_values(
    values: Iterable,
) -> set[str]:
    """
    Normalize filter values so matching is:
    - case insensitive
    - whitespace tolerant
    - safe for numeric/string values
    """

    result = set()

    for value in values:

        if value is None:
            continue

        normalized = (
            str(value)
            .strip()
            .lower()
        )

        if normalized:
            result.add(
                normalized
            )

    return result


def _find_column(
    dataframe: pd.DataFrame,
    candidates: list[str],
) -> str | None:
    """
    Find the first matching dataframe column from
    a list of semantic aliases.
    """

    normalized_columns = {
        str(column).strip().lower():
            column
        for column in dataframe.columns
    }

    for candidate in candidates:

        match = (
            normalized_columns.get(
                candidate.lower()
            )
        )

        if match is not None:
            return match

    return None


def _apply_single_filter(
    dataframe: pd.DataFrame,
    column: str,
    values: list[str],
) -> pd.DataFrame:
    """
    Apply one inclusive filter.

    Example:
        channels = ["Meta", "Google"]

    means:
        Meta OR Google
    """

    normalized_filter_values = (
        _normalize_values(
            values
        )
    )

    if not normalized_filter_values:
        return dataframe

    normalized_series = (
        dataframe[column]
        .astype("string")
        .fillna("")
        .str.strip()
        .str.lower()
    )

    mask = normalized_series.isin(
        normalized_filter_values
    )

    return dataframe.loc[
        mask
    ]


# ============================================================
# MAIN FILTER ENGINE
# ============================================================


def apply_analytics_filters(
    dataframe: pd.DataFrame,
    filters: AnalyticsFilters,
    *,
    strict: bool = False,
) -> pd.DataFrame:
    """
    Apply ProfitLens global analytics filters.

    Rules:
    - Empty filter lists do nothing.
    - Multiple values within one filter are OR conditions.
    - Different filter dimensions are AND conditions.
    - Column aliases are resolved automatically.
    - Original dataframe is never mutated.

    strict=False:
        Ignore a requested filter when the dataframe
        does not contain a compatible column.

    strict=True:
        Raise ValueError when an active requested filter
        cannot be applied.
    """

    if not isinstance(
        dataframe,
        pd.DataFrame,
    ):
        raise TypeError(
            "dataframe must be a pandas DataFrame."
        )

    result = dataframe.copy()

    filter_values = (
        filters.model_dump()
    )

    for (
        filter_name,
        selected_values,
    ) in filter_values.items():

        if not selected_values:
            continue

        candidates = (
            FILTER_FIELD_CANDIDATES.get(
                filter_name
            )
        )

        if not candidates:
            if strict:
                raise ValueError(
                    f"Unsupported filter: {filter_name}"
                )

            continue

        column = _find_column(
            result,
            candidates,
        )

        if column is None:

            if strict:
                raise ValueError(
                    "Cannot apply filter "
                    f"'{filter_name}'. "
                    "No compatible dataframe column "
                    "was found."
                )

            continue

        result = _apply_single_filter(
            result,
            column,
            selected_values,
        )

    return (
        result
        .copy()
        .reset_index(
            drop=True
        )
    )


# ============================================================
# FILTER OPTIONS
# ============================================================


def get_available_filter_options(
    dataframe: pd.DataFrame,
) -> dict[str, list[str]]:
    """
    Inspect a dataframe and return filter values
    that can be exposed to the frontend.

    Example:
    {
        "channels": ["Google", "Meta"],
        "zones": ["North", "South"]
    }
    """

    if not isinstance(
        dataframe,
        pd.DataFrame,
    ):
        raise TypeError(
            "dataframe must be a pandas DataFrame."
        )

    result: dict[
        str,
        list[str],
    ] = {}

    for (
        filter_name,
        candidates,
    ) in FILTER_FIELD_CANDIDATES.items():

        column = _find_column(
            dataframe,
            candidates,
        )

        if column is None:
            result[
                filter_name
            ] = []

            continue

        values = (
            dataframe[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        values = values[
            values != ""
        ]

        unique_values = sorted(
            values.unique().tolist()
        )

        result[
            filter_name
        ] = unique_values

    return result


# ============================================================
# FILTER SUMMARY
# ============================================================


def summarize_active_filters(
    filters: AnalyticsFilters,
) -> dict:
    """
    Return a frontend-friendly summary of active filters.
    """

    dumped = (
        filters.model_dump()
    )

    active = {
        key: value
        for key, value
        in dumped.items()
        if value
    }

    active_count = sum(
        len(values)
        for values in active.values()
    )

    return {
        "active_filter_groups":
            len(active),

        "active_filter_values":
            active_count,

        "filters":
            active,
    }
