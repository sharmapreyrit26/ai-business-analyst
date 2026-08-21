from functools import lru_cache

import pandas as pd

from backend.app.exceptions import (
    ResourceNotFoundError,
)

from backend.app.services.data_loader import (
    load_orders,
)

from backend.app.services.revenue import (
    load_order_items,
)


# ============================================================
# PRODUCT DATASET
# ============================================================


@lru_cache(maxsize=1)
def _get_product_dataset_cached():
    """
    Build the product-level source dataset used by
    ProfitLens product analytics.

    Order-item data is joined to order metadata so product
    metrics can be filtered by the customer's purchase month.
    """

    orders = load_orders()
    items = load_order_items()

    required_order_columns = [
        "order_id",
        "order_purchase_timestamp",
    ]

    missing_order_columns = [
        column
        for column in required_order_columns
        if column not in orders.columns
    ]

    if missing_order_columns:
        raise ValueError(
            "Orders dataset is missing required column(s): "
            + ", ".join(
                missing_order_columns
            )
        )

    required_item_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "price",
        "freight_value",
    ]

    missing_item_columns = [
        column
        for column in required_item_columns
        if column not in items.columns
    ]

    if missing_item_columns:
        raise ValueError(
            "Order-items dataset is missing required column(s): "
            + ", ".join(
                missing_item_columns
            )
        )

    product_data = (
        items.merge(
            orders[
                required_order_columns
            ],
            on="order_id",
            how="left",
        )
    )

    product_data[
        "month"
    ] = (
        product_data[
            "order_purchase_timestamp"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    return product_data


def get_product_dataset():
    """
    Return a safe copy of the cached product dataset.
    """

    return (
        _get_product_dataset_cached()
        .copy()
    )


# ============================================================
# MONTH VALIDATION
# ============================================================


def _get_month_product_data(
    month: str,
):
    """
    Return order-item records for one reporting month.

    A missing reporting month is considered a missing
    resource rather than a valid empty analytics result.
    """

    if (
        not isinstance(
            month,
            str,
        )
        or not month.strip()
    ):
        raise ValueError(
            "Month must be provided in YYYY-MM format."
        )

    month = (
        month.strip()
    )

    data = (
        _get_product_dataset_cached()
    )

    month_data = (
        data[
            data["month"]
            == month
        ]
        .copy()
    )

    if month_data.empty:
        raise ResourceNotFoundError(
            f"Product data not found for month: {month}"
        )

    return month_data


# ============================================================
# MONTHLY PRODUCT METRICS
# ============================================================


def _aggregate_products(
    month_data: pd.DataFrame,
):
    """
    Aggregate product commercial metrics for one month.
    """

    product = (
        month_data.groupby(
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
        product[
            "freight_value"
        ]
        .div(
            product[
                "revenue"
            ]
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


# ============================================================
# SERIALIZATION
# ============================================================


def _serialize_product_rows(
    product: pd.DataFrame,
    limit: int | None = None,
):
    """
    Convert product DataFrame rows into JSON-safe dictionaries.
    """

    if limit is not None:

        product = (
            product.head(
                limit
            )
        )

    records = []

    for _, row in product.iterrows():

        records.append({
            "product_id": str(
                row["product_id"]
            ),

            "revenue": round(
                float(
                    row["revenue"]
                ),
                2,
            ),

            "units_sold": int(
                row["units_sold"]
            ),

            "orders": int(
                row["orders"]
            ),

            "average_selling_price": round(
                float(
                    row[
                        "average_selling_price"
                    ]
                ),
                2,
            ),

            "freight_value": round(
                float(
                    row[
                        "freight_value"
                    ]
                ),
                2,
            ),

            "revenue_share_percent": round(
                float(
                    row[
                        "revenue_share_percent"
                    ]
                ),
                2,
            ),

            "freight_to_revenue_percent": round(
                float(
                    row[
                        "freight_to_revenue_percent"
                    ]
                ),
                2,
            ),
        })

    return records


# ============================================================
# PRODUCT CONCENTRATION
# ============================================================


def _calculate_concentration(
    product: pd.DataFrame,
    month: str,
):
    """
    Calculate product revenue concentration for one month.
    """

    total_products = int(
        len(
            product
        )
    )

    total_revenue = float(
        product[
            "revenue"
        ]
        .sum()
    )

    if total_revenue:

        top_1_share = (
            product
            .head(1)[
                "revenue"
            ]
            .sum()
            / total_revenue
            * 100
        )

        top_5_share = (
            product
            .head(5)[
                "revenue"
            ]
            .sum()
            / total_revenue
            * 100
        )

        top_10_share = (
            product
            .head(10)[
                "revenue"
            ]
            .sum()
            / total_revenue
            * 100
        )

    else:

        top_1_share = 0.0
        top_5_share = 0.0
        top_10_share = 0.0

    return {
        "month": month,

        "status": "complete",

        "total_products": (
            total_products
        ),

        "total_revenue": round(
            total_revenue,
            2,
        ),

        "top_1_revenue_share_percent": round(
            float(
                top_1_share
            ),
            2,
        ),

        "top_5_revenue_share_percent": round(
            float(
                top_5_share
            ),
            2,
        ),

        "top_10_revenue_share_percent": round(
            float(
                top_10_share
            ),
            2,
        ),
    }


# ============================================================
# PRODUCT SUMMARY
# ============================================================


def _build_product_summary(
    month: str,
    product: pd.DataFrame,
    month_data: pd.DataFrame,
):
    """
    Build the summary returned by the product analytics API.
    """

    total_products = int(
        product[
            "product_id"
        ]
        .nunique()
    )

    total_revenue = float(
        product[
            "revenue"
        ]
        .sum()
    )

    total_units = int(
        product[
            "units_sold"
        ]
        .sum()
    )

    total_orders = int(
        month_data[
            "order_id"
        ]
        .nunique()
    )

    average_revenue_per_product = (
        total_revenue
        / total_products
        if total_products
        else 0
    )

    top_products = (
        _serialize_product_rows(
            product,
            limit=10,
        )
    )

    concentration = (
        _calculate_concentration(
            product=product,
            month=month,
        )
    )

    return {
        "month": month,

        "status": "complete",

        "total_products": (
            total_products
        ),

        "total_revenue": round(
            total_revenue,
            2,
        ),

        "total_units": (
            total_units
        ),

        "total_orders": (
            total_orders
        ),

        "average_revenue_per_product": round(
            float(
                average_revenue_per_product
            ),
            2,
        ),

        "top_products": (
            top_products
        ),

        "concentration": (
            concentration
        ),

        "profitability_status": (
            "unavailable"
        ),

        "profitability_limitation": (
            "Product profitability cannot be calculated "
            "without COGS and additional variable cost data."
        ),
    }


# ============================================================
# AVAILABLE / UNAVAILABLE METRICS
# ============================================================


def _available_metrics():
    """
    Product metrics that can be measured with the
    currently connected dataset.
    """

    return [
        "product revenue",
        "units sold",
        "orders",
        "average selling price",
        "freight value",
        "revenue contribution",
        "freight-to-revenue ratio",
        "product concentration",
    ]


def _unavailable_metrics():
    """
    Product profitability metrics that must remain unavailable
    until the required cost datasets are connected.
    """

    return {
        "gross_profit": {
            "status": "insufficient_data",

            "required_data": [
                "COGS",
            ],
        },

        "contribution_margin": {
            "status": "insufficient_data",

            "required_data": [
                "COGS",
                "payment fees",
                "marketing allocation",
                "returns cost",
                "RTO cost",
            ],
        },

        "product_profitability": {
            "status": "insufficient_data",

            "required_data": [
                "COGS",
                "discounts",
                "variable costs",
            ],
        },
    }


# ============================================================
# PUBLIC PRODUCT ANALYTICS
# ============================================================


def get_product_analytics(
    month: str,
):
    """
    Return product analytics for one reporting month.

    Available analysis:
    - product revenue
    - units sold
    - unique orders
    - average selling price
    - freight value
    - freight burden
    - revenue contribution
    - product concentration

    True product profitability is deliberately unavailable
    until COGS and other variable cost data are connected.

    Raises:
        ResourceNotFoundError:
            When the requested reporting month has no
            product data.
    """

    month_data = (
        _get_month_product_data(
            month
        )
    )

    product = (
        _aggregate_products(
            month_data
        )
    )

    top_products = (
        _serialize_product_rows(
            product,
            limit=10,
        )
    )

    concentration = (
        _calculate_concentration(
            product=product,
            month=month,
        )
    )

    summary = (
        _build_product_summary(
            month=month,
            product=product,
            month_data=month_data,
        )
    )

    return {
        "month": month,

        "summary": (
            summary
        ),

        "top_products": (
            top_products
        ),

        "concentration": (
            concentration
        ),

        "available_metrics": (
            _available_metrics()
        ),

        "unavailable_metrics": (
            _unavailable_metrics()
        ),
    }