from functools import lru_cache

import pandas as pd

from backend.app.services.d2c_data_loader import (
    load_marketing,
)


# ============================================================
# MARKETING BASE
# ============================================================


@lru_cache(maxsize=1)
def _get_marketing_base_cached():
    """
    Return normalized campaign/day marketing data.

    This dataset is aggregate marketing attribution data.
    It is not directly joinable to individual orders.
    """

    marketing = (
        load_marketing()
        .copy()
    )

    required_columns = {
        "date",
        "channel",
        "campaign",
        "spend",
        "clicks",
        "sessions",
        "orders",
        "new_customers",
        "attributed_revenue",
        "month",
    }

    missing = (
        required_columns
        - set(marketing.columns)
    )

    if missing:
        raise ValueError(
            "Missing required marketing columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    marketing[
        "channel"
    ] = (
        marketing[
            "channel"
        ]
        .fillna(
            "Unknown"
        )
    )

    marketing[
        "campaign"
    ] = (
        marketing[
            "campaign"
        ]
        .fillna(
            "Unknown"
        )
    )

    return marketing


def get_marketing_base():
    return (
        _get_marketing_base_cached()
        .copy()
    )


# ============================================================
# DERIVED METRICS
# ============================================================


def _add_efficiency_metrics(
    dataframe: pd.DataFrame,
):
    """
    Add deterministic marketing efficiency metrics.
    """

    df = dataframe.copy()

    df[
        "roas"
    ] = (
        df[
            "attributed_revenue"
        ]
        .div(
            df[
                "spend"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    df[
        "cac"
    ] = (
        df[
            "spend"
        ]
        .div(
            df[
                "new_customers"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    df[
        "cost_per_order"
    ] = (
        df[
            "spend"
        ]
        .div(
            df[
                "orders"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    df[
        "session_conversion_percent"
    ] = (
        df[
            "orders"
        ]
        .div(
            df[
                "sessions"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    df[
        "click_through_percent"
    ] = (
        df[
            "clicks"
        ]
        .div(
            df[
                "sessions"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    df[
        "revenue_per_order"
    ] = (
        df[
            "attributed_revenue"
        ]
        .div(
            df[
                "orders"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    df[
        "revenue_per_new_customer"
    ] = (
        df[
            "attributed_revenue"
        ]
        .div(
            df[
                "new_customers"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    numeric_columns = [
        "spend",
        "attributed_revenue",
        "roas",
        "cac",
        "cost_per_order",
        "session_conversion_percent",
        "click_through_percent",
        "revenue_per_order",
        "revenue_per_new_customer",
    ]

    df[
        numeric_columns
    ] = (
        df[
            numeric_columns
        ]
        .round(2)
    )

    return df


# ============================================================
# MONTHLY MARKETING SUMMARY
# ============================================================


def get_marketing_summary(
    month: str,
):
    """
    Return headline marketing metrics for one month.
    """

    df = (
        get_marketing_base()
    )

    month_df = (
        df[
            df[
                "month"
            ]
            == month
        ]
        .copy()
    )

    if month_df.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C marketing data."
        )

    total_spend = float(
        month_df[
            "spend"
        ]
        .sum()
    )

    attributed_revenue = float(
        month_df[
            "attributed_revenue"
        ]
        .sum()
    )

    orders = int(
        month_df[
            "orders"
        ]
        .sum()
    )

    new_customers = int(
        month_df[
            "new_customers"
        ]
        .sum()
    )

    sessions = int(
        month_df[
            "sessions"
        ]
        .sum()
    )

    clicks = int(
        month_df[
            "clicks"
        ]
        .sum()
    )

    paid_mask = (
        month_df[
            "spend"
        ]
        > 0
    )

    paid_spend = float(
        month_df.loc[
            paid_mask,
            "spend",
        ]
        .sum()
    )

    paid_revenue = float(
        month_df.loc[
            paid_mask,
            "attributed_revenue",
        ]
        .sum()
    )

    return {
        "month": month,

        "marketing_spend": round(
            total_spend,
            2,
        ),

        "attributed_revenue": round(
            attributed_revenue,
            2,
        ),

        "blended_roas": round(
            (
                attributed_revenue
                / total_spend
            )
            if total_spend
            else 0.0,
            2,
        ),

        "paid_roas": round(
            (
                paid_revenue
                / paid_spend
            )
            if paid_spend
            else 0.0,
            2,
        ),

        "attributed_orders": orders,

        "new_customers": (
            new_customers
        ),

        "cac": round(
            (
                total_spend
                / new_customers
            )
            if new_customers
            else 0.0,
            2,
        ),

        "cost_per_order": round(
            (
                total_spend
                / orders
            )
            if orders
            else 0.0,
            2,
        ),

        "sessions": sessions,

        "clicks": clicks,

        "session_conversion_percent": round(
            (
                orders
                / sessions
                * 100
            )
            if sessions
            else 0.0,
            2,
        ),

        "click_through_percent": round(
            (
                clicks
                / sessions
                * 100
            )
            if sessions
            else 0.0,
            2,
        ),

        "attribution_level": (
            "aggregate_campaign_daily"
        ),

        "order_level_attribution_available": (
            False
        ),
    }


# ============================================================
# CHANNEL PERFORMANCE
# ============================================================


def get_channel_performance(
    month: str,
):
    """
    Return marketing performance by acquisition channel.
    """

    df = (
        get_marketing_base()
    )

    month_df = (
        df[
            df[
                "month"
            ]
            == month
        ]
        .copy()
    )

    if month_df.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C marketing data."
        )

    channel = (
        month_df.groupby(
            "channel",
            dropna=False,
        )
        .agg(
            spend=(
                "spend",
                "sum",
            ),
            attributed_revenue=(
                "attributed_revenue",
                "sum",
            ),
            orders=(
                "orders",
                "sum",
            ),
            new_customers=(
                "new_customers",
                "sum",
            ),
            clicks=(
                "clicks",
                "sum",
            ),
            sessions=(
                "sessions",
                "sum",
            ),
        )
        .reset_index()
    )

    channel = (
        _add_efficiency_metrics(
            channel
        )
    )

    return (
        channel.sort_values(
            [
                "attributed_revenue",
                "channel",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# CAMPAIGN PERFORMANCE
# ============================================================


def get_campaign_performance(
    month: str,
):
    """
    Return campaign-level marketing performance.
    """

    df = (
        get_marketing_base()
    )

    month_df = (
        df[
            df[
                "month"
            ]
            == month
        ]
        .copy()
    )

    if month_df.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C marketing data."
        )

    campaign = (
        month_df.groupby(
            [
                "channel",
                "campaign",
            ],
            dropna=False,
        )
        .agg(
            spend=(
                "spend",
                "sum",
            ),
            attributed_revenue=(
                "attributed_revenue",
                "sum",
            ),
            orders=(
                "orders",
                "sum",
            ),
            new_customers=(
                "new_customers",
                "sum",
            ),
            clicks=(
                "clicks",
                "sum",
            ),
            sessions=(
                "sessions",
                "sum",
            ),
        )
        .reset_index()
    )

    campaign = (
        _add_efficiency_metrics(
            campaign
        )
    )

    return (
        campaign.sort_values(
            [
                "attributed_revenue",
                "campaign",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# MONTHLY TREND
# ============================================================


@lru_cache(maxsize=1)
def _get_monthly_marketing_trend_cached():
    """
    Return monthly marketing performance and
    month-over-month changes.
    """

    df = (
        _get_marketing_base_cached()
        .copy()
    )

    monthly = (
        df.groupby(
            "month"
        )
        .agg(
            spend=(
                "spend",
                "sum",
            ),
            attributed_revenue=(
                "attributed_revenue",
                "sum",
            ),
            orders=(
                "orders",
                "sum",
            ),
            new_customers=(
                "new_customers",
                "sum",
            ),
            clicks=(
                "clicks",
                "sum",
            ),
            sessions=(
                "sessions",
                "sum",
            ),
        )
        .reset_index()
        .sort_values(
            "month"
        )
        .reset_index(
            drop=True
        )
    )

    monthly = (
        _add_efficiency_metrics(
            monthly
        )
    )

    monthly[
        "spend_growth_percent"
    ] = (
        monthly[
            "spend"
        ]
        .pct_change()
        .mul(100)
        .fillna(0.0)
        .round(2)
    )

    monthly[
        "revenue_growth_percent"
    ] = (
        monthly[
            "attributed_revenue"
        ]
        .pct_change()
        .mul(100)
        .fillna(0.0)
        .round(2)
    )

    monthly[
        "roas_change_percent"
    ] = (
        monthly[
            "roas"
        ]
        .pct_change()
        .mul(100)
        .fillna(0.0)
        .round(2)
    )

    monthly[
        "cac_change_percent"
    ] = (
        monthly[
            "cac"
        ]
        .pct_change()
        .mul(100)
        .fillna(0.0)
        .round(2)
    )

    return monthly


def get_monthly_marketing_trend():
    return (
        _get_monthly_marketing_trend_cached()
        .copy()
    )


# ============================================================
# MARKETING INSIGHTS
# ============================================================


def get_marketing_insights(
    month: str,
):
    """
    Return deterministic best/worst channel signals.

    These are rule-based analytical facts, not LLM output.
    """

    channel = (
        get_channel_performance(
            month
        )
    )

    paid = (
        channel[
            channel[
                "spend"
            ]
            > 0
        ]
        .copy()
    )

    if paid.empty:
        return {
            "month": month,
            "best_roas_channel": None,
            "lowest_cac_channel": None,
            "highest_revenue_channel": None,
        }

    best_roas = (
        paid.sort_values(
            "roas",
            ascending=False,
        )
        .iloc[0]
    )

    lowest_cac = (
        paid[
            paid[
                "new_customers"
            ]
            > 0
        ]
        .sort_values(
            "cac",
            ascending=True,
        )
    )

    highest_revenue = (
        channel.sort_values(
            "attributed_revenue",
            ascending=False,
        )
        .iloc[0]
    )

    return {
        "month": month,

        "best_roas_channel": {
            "channel": (
                best_roas[
                    "channel"
                ]
            ),
            "roas": float(
                best_roas[
                    "roas"
                ]
            ),
        },

        "lowest_cac_channel": (
            {
                "channel": (
                    lowest_cac.iloc[0][
                        "channel"
                    ]
                ),
                "cac": float(
                    lowest_cac.iloc[0][
                        "cac"
                    ]
                ),
            }
            if not lowest_cac.empty
            else None
        ),

        "highest_revenue_channel": {
            "channel": (
                highest_revenue[
                    "channel"
                ]
            ),
            "attributed_revenue": float(
                highest_revenue[
                    "attributed_revenue"
                ]
            ),
        },
    }