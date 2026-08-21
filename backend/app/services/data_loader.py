from functools import lru_cache
from pathlib import Path

import pandas as pd


DATA_PATH = Path(
    "data/raw/olist_orders_dataset.csv"
)


@lru_cache(maxsize=1)
def _load_orders_cached():
    """
    Load and cache the raw orders dataset.

    The CSV does not change during a running
    ProfitLens process, so parsing it repeatedly
    is unnecessary.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )

    df = pd.read_csv(
        DATA_PATH
    )

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in date_columns:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )

    return df


def load_orders():
    """
    Return a copy of the cached orders dataset.

    Returning a copy prevents downstream analytics
    from accidentally modifying the cached source.
    """

    return (
        _load_orders_cached()
        .copy()
    )