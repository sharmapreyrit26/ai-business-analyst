from functools import lru_cache

import pandas as pd

from backend.app.services.data_loader import (
    load_orders,
)

from backend.app.services.revenue import (
    load_order_items,
)


# ============================================================
# ORDER-LEVEL FINANCIAL DATA
# ============================================================


@lru_cache(maxsize=1)
def _get_order_financials_cached():
    """
    Build and cache the order-level financial dataset.

    One row represents one order.

    Revenue, freight and item count are aggregated from
    order-item level data and then joined to order metadata.
    """

    orders = load_orders()
    items = load_order_items()

    order_financials = (
        items.groupby(
            "order_id"
        )
        .agg(
            revenue=(
                "price",
                "sum",
            ),
            freight_value=(
                "freight_value",
                "sum",
            ),
            item_count=(
                "order_item_id",
                "count",
            ),
        )
        .reset_index()
    )

    order_financials = (
        order_financials.merge(
            orders[
                [
                    "order_id",
                    "customer_id",
                    "order_status",
                    "order_purchase_timestamp",
                ]
            ],
            on="order_id",
            how="left",
        )
    )

    order_financials[
        "month"
    ] = (
        order_financials[
            "order_purchase_timestamp"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    return order_financials


def get_order_financials():
    """
    Return a safe copy of cached order-level
    financial data.
    """

    return (
        _get_order_financials_cached()
        .copy()
    )


# ============================================================
# OVERALL REVENUE SUMMARY
# ============================================================


def get_revenue_summary():
    """
    Return overall revenue and order-level
    financial metrics.
    """

    df = get_order_financials()

    total_revenue = (
        df["revenue"]
        .sum()
    )

    total_orders = (
        df["order_id"]
        .nunique()
    )

    total_items = (
        df["item_count"]
        .sum()
    )

    total_freight = (
        df["freight_value"]
        .sum()
    )

    delivered_revenue = (
        df.loc[
            df["order_status"]
            == "delivered",
            "revenue",
        ]
        .sum()
    )

    cancelled_revenue = (
        df.loc[
            df["order_status"]
            == "canceled",
            "revenue",
        ]
        .sum()
    )

    aov = (
        total_revenue
        / total_orders
        if total_orders
        else 0
    )

    freight_to_revenue = (
        total_freight
        / total_revenue
        * 100
        if total_revenue
        else 0
    )

    return {
        "total_revenue": round(
            float(
                total_revenue
            ),
            2,
        ),

        "total_orders": int(
            total_orders
        ),

        "total_items": int(
            total_items
        ),

        "total_freight": round(
            float(
                total_freight
            ),
            2,
        ),

        "average_order_value": round(
            float(
                aov
            ),
            2,
        ),

        "delivered_revenue": round(
            float(
                delivered_revenue
            ),
            2,
        ),

        "cancelled_revenue": round(
            float(
                cancelled_revenue
            ),
            2,
        ),

        "freight_to_revenue_percent": round(
            float(
                freight_to_revenue
            ),
            2,
        ),
    }


# ============================================================
# MONTHLY REVENUE
# ============================================================


@lru_cache(maxsize=1)
def _get_monthly_revenue_cached():
    """
    Calculate and cache monthly financial metrics.
    """

    df = (
        _get_order_financials_cached()
    )

    monthly = (
        df.groupby(
            "month"
        )
        .agg(
            revenue=(
                "revenue",
                "sum",
            ),

            orders=(
                "order_id",
                "nunique",
            ),

            freight_value=(
                "freight_value",
                "sum",
            ),

            items=(
                "item_count",
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

    monthly[
        "aov"
    ] = (
        monthly["revenue"]
        / monthly["orders"]
    )

    monthly[
        "revenue_growth"
    ] = (
        monthly[
            "revenue"
        ]
        .pct_change()
        .mul(100)
    )

    monthly[
        "order_growth"
    ] = (
        monthly[
            "orders"
        ]
        .pct_change()
        .mul(100)
    )

    monthly[
        "aov_growth"
    ] = (
        monthly[
            "aov"
        ]
        .pct_change()
        .mul(100)
    )

    return monthly


def get_monthly_revenue():
    """
    Return a safe copy of cached monthly
    financial metrics.
    """

    return (
        _get_monthly_revenue_cached()
        .copy()
    )


# ============================================================
# MONTH-SPECIFIC REVENUE ANALYSIS
# ============================================================


def get_monthly_revenue_analysis(
    month: str,
):
    """
    Return revenue analysis for one month compared
    with the immediately previous available month.
    """

    monthly = (
        get_monthly_revenue()
        .reset_index(
            drop=True
        )
    )

    matching_rows = (
        monthly[
            monthly["month"]
            == month
        ]
    )

    if matching_rows.empty:
        raise ValueError(
            f"Month '{month}' not found in reporting period."
        )

    current_index = (
        matching_rows.index[0]
    )

    current = (
        monthly.loc[
            current_index
        ]
    )

    previous = None

    if current_index > 0:
        previous = (
            monthly.loc[
                current_index - 1
            ]
        )

    revenue = float(
        current["revenue"]
    )

    orders = int(
        current["orders"]
    )

    items = int(
        current["items"]
    )

    freight = float(
        current[
            "freight_value"
        ]
    )

    aov = float(
        current["aov"]
    )

    if previous is None:

        previous_month = None
        previous_revenue = None
        previous_orders = None
        previous_aov = None

        revenue_change = None
        order_change = None
        aov_change = None

    else:

        previous_month = str(
            previous["month"]
        )

        previous_revenue = float(
            previous["revenue"]
        )

        previous_orders = int(
            previous["orders"]
        )

        previous_aov = float(
            previous["aov"]
        )

        revenue_change = (
            (
                revenue
                - previous_revenue
            )
            / previous_revenue
            * 100
            if previous_revenue
            else None
        )

        order_change = (
            (
                orders
                - previous_orders
            )
            / previous_orders
            * 100
            if previous_orders
            else None
        )

        aov_change = (
            (
                aov
                - previous_aov
            )
            / previous_aov
            * 100
            if previous_aov
            else None
        )

    return {
        "month": month,

        "previous_month": (
            previous_month
        ),

        "revenue": round(
            revenue,
            2,
        ),

        "previous_revenue": (
            round(
                previous_revenue,
                2,
            )
            if previous_revenue
            is not None
            else None
        ),

        "revenue_change_percent": (
            round(
                revenue_change,
                2,
            )
            if revenue_change
            is not None
            else None
        ),

        "orders": orders,

        "previous_orders": (
            previous_orders
        ),

        "order_change_percent": (
            round(
                order_change,
                2,
            )
            if order_change
            is not None
            else None
        ),

        "aov": round(
            aov,
            2,
        ),

        "previous_aov": (
            round(
                previous_aov,
                2,
            )
            if previous_aov
            is not None
            else None
        ),

        "aov_change_percent": (
            round(
                aov_change,
                2,
            )
            if aov_change
            is not None
            else None
        ),

        "items": items,

        "freight_value": round(
            freight,
            2,
        ),
    }


# ============================================================
# MONTHLY DATA QUALITY
# ============================================================


@lru_cache(maxsize=1)
def _get_monthly_data_quality_cached():
    """
    Evaluate monthly reporting completeness.

    Both 'data_quality' and 'status' are returned
    for compatibility with existing ProfitLens
    services and frontend/API responses.
    """

    monthly = (
        _get_monthly_revenue_cached()
        .copy()
    )

    if monthly.empty:
        return []

    monthly = (
        monthly.sort_values(
            "month"
        )
        .reset_index(
            drop=True
        )
    )

    typical_orders = (
        monthly["orders"]
        .median()
    )

    results = []

    for _, row in monthly.iterrows():

        month = str(
            row["month"]
        )

        orders = int(
            row["orders"]
        )

        is_partial = False

        if typical_orders > 0:
            is_partial = (
                orders
                < typical_orders * 0.25
            )

        quality_status = (
            "partial"
            if is_partial
            else "complete"
        )

        results.append({
            "month": month,

            # Required by existing KPI engine.
            "data_quality": quality_status,

            # Frontend/API-friendly alias.
            "status": quality_status,

            "is_partial_month": bool(
                is_partial
            ),

            "orders": orders,
        })

    return results


def get_monthly_data_quality():
    """
    Return monthly reporting-quality information.

    Fresh dictionaries are returned so callers
    cannot mutate cached records.
    """

    return [
        dict(
            item
        )
        for item in (
            _get_monthly_data_quality_cached()
        )
    ]


# ============================================================
# PRODUCT REVENUE
# ============================================================


@lru_cache(maxsize=1)
def _get_product_revenue_cached():
    """
    Aggregate financial metrics by product.
    """

    items = load_order_items()

    product = (
        items.groupby(
            "product_id"
        )
        .agg(
            revenue=(
                "price",
                "sum",
            ),

            units_sold=(
                "order_item_id",
                "count",
            ),

            orders=(
                "order_id",
                "nunique",
            ),

            freight_value=(
                "freight_value",
                "sum",
            ),
        )
        .reset_index()
    )

    product[
        "average_selling_price"
    ] = (
        product["revenue"]
        / product["units_sold"]
    )

    total_revenue = (
        product["revenue"]
        .sum()
    )

    if total_revenue:

        product[
            "revenue_share_percent"
        ] = (
            product["revenue"]
            / total_revenue
            * 100
        )

    else:

        product[
            "revenue_share_percent"
        ] = 0.0

    product[
        "freight_to_revenue_percent"
    ] = (
        product["freight_value"]
        .div(
            product["revenue"]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0)
    )

    product = (
        product.sort_values(
            "revenue",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )

    return product


def get_product_revenue():
    """
    Return product-level financial metrics.
    """

    return (
        _get_product_revenue_cached()
        .copy()
    )


# ============================================================
# SELLER REVENUE
# ============================================================


@lru_cache(maxsize=1)
def _get_seller_revenue_cached():
    """
    Aggregate temporary Olist demonstration
    data by seller.

    Seller analytics are not part of the long-term
    single-brand ProfitLens product model.
    """

    items = load_order_items()

    if (
        "seller_id"
        not in items.columns
    ):

        return pd.DataFrame(
            columns=[
                "seller_id",
                "revenue",
                "orders",
                "units_sold",
                "freight_value",
            ]
        )

    seller = (
        items.groupby(
            "seller_id"
        )
        .agg(
            revenue=(
                "price",
                "sum",
            ),

            orders=(
                "order_id",
                "nunique",
            ),

            units_sold=(
                "order_item_id",
                "count",
            ),

            freight_value=(
                "freight_value",
                "sum",
            ),
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )

    return seller


def get_seller_revenue():
    """
    Return seller-level metrics from the temporary
    Olist demonstration dataset.
    """

    return (
        _get_seller_revenue_cached()
        .copy()
    )