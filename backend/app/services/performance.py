import pandas as pd
from functools import lru_cache
from .business_data import build_business_dataset


@lru_cache(maxsize=1)
def _get_monthly_performance_cached():
    """Calculate monthly business performance for the primary reporting period."""

    df = build_business_dataset()

    # Create monthly reporting period
    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    # Retain the primary operating period
    df = df[
        (df["month"] >= "2017-01") &
        (df["month"] <= "2018-08")
    ].copy()

    monthly = (
        df.groupby("month")
        .agg(
            orders=("order_id", "nunique"),
            revenue=("revenue", "sum"),
            freight=("freight_value", "sum"),
            delivered_orders=(
                "order_status",
                lambda x: (x == "delivered").sum()
            ),
            cancelled_orders=(
                "order_status",
                lambda x: (x == "canceled").sum()
            ),
        )
        .reset_index()
    )

    # --------------------------------
    # CORE METRICS
    # --------------------------------

    monthly["aov"] = (
        monthly["revenue"] / monthly["orders"]
    )

    monthly["delivery_rate"] = (
        monthly["delivered_orders"]
        / monthly["orders"]
        * 100
    )

    monthly["cancellation_rate"] = (
        monthly["cancelled_orders"]
        / monthly["orders"]
        * 100
    )

    # --------------------------------
    # GROWTH METRICS
    # --------------------------------

    monthly["revenue_growth"] = (
        monthly["revenue"].pct_change() * 100
    )

    monthly["order_growth"] = (
        monthly["orders"].pct_change() * 100
    )

    # IMPORTANT:
    # Do NOT round here.
    #
    # Downstream analytical functions need
    # full precision to calculate driver effects.
    #
    # Rounding should happen at the final
    # presentation / serialization layer.

    return monthly

def get_monthly_performance():
    """
    Return a safe copy of cached monthly
    performance metrics.
    """

    return (
        _get_monthly_performance_cached()
        .copy()
    )