import pandas as pd

from backend.app.services.data_loader import (
    load_orders,
)


ITEMS_PATH = (
    "data/raw/olist_order_items_dataset.csv"
)


def _load_product_dataset():
    """
    Build the item-level product dataset by combining
    order items with order-level information.
    """

    items = pd.read_csv(
        ITEMS_PATH
    )

    orders = load_orders()

    required_columns = [
        "order_id",
        "product_id",
        "seller_id",
        "price",
        "freight_value",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in items.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required item columns: "
            f"{missing_columns}"
        )

    merged = items.merge(
        orders[
            [
                "order_id",
                "order_status",
                "order_purchase_timestamp",
            ]
        ],
        on="order_id",
        how="left",
    )

    merged["month"] = (
        merged[
            "order_purchase_timestamp"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    return merged


def get_product_performance(
    month: str = None,
    delivered_only: bool = False,
):
    """
    Calculate product-level commercial performance.

    This is revenue analysis, NOT profitability.
    """

    df = _load_product_dataset()

    if month is not None:
        df = df[
            df["month"] == month
        ].copy()

    if delivered_only:
        df = df[
            df["order_status"]
            == "delivered"
        ].copy()

    if df.empty:
        return []

    product = (
        df.groupby(
            "product_id"
        )
        .agg(
            revenue=(
                "price",
                "sum",
            ),
            units_sold=(
                "order_id",
                "size",
            ),
            orders=(
                "order_id",
                "nunique",
            ),
            average_selling_price=(
                "price",
                "mean",
            ),
            freight_value=(
                "freight_value",
                "sum",
            ),
        )
        .reset_index()
    )

    total_revenue = (
        product["revenue"].sum()
    )

    product[
        "revenue_share_percent"
    ] = (
        product["revenue"]
        / total_revenue
        * 100
        if total_revenue
        else 0
    )

    product[
        "freight_to_revenue_percent"
    ] = product.apply(
        lambda row: (
            row["freight_value"]
            / row["revenue"]
            * 100
        )
        if row["revenue"]
        else 0,
        axis=1,
    )

    product = product.sort_values(
        "revenue",
        ascending=False,
    )

    numeric_columns = [
        "revenue",
        "average_selling_price",
        "freight_value",
        "revenue_share_percent",
        "freight_to_revenue_percent",
    ]

    product[numeric_columns] = (
        product[numeric_columns]
        .round(2)
    )

    return product.to_dict(
        orient="records"
    )


def get_top_products(
    month: str = None,
    limit: int = 10,
):
    """
    Return the highest-revenue products.
    """

    products = (
        get_product_performance(
            month=month
        )
    )

    return products[:limit]


def get_product_concentration(
    month: str = None,
):
    """
    Measure how concentrated revenue is among
    the highest-revenue products.
    """

    products = (
        get_product_performance(
            month=month
        )
    )

    if not products:
        return {
            "month": month,
            "status": "no_data",
        }

    total_revenue = sum(
        product["revenue"]
        for product in products
    )

    top_1_revenue = sum(
        product["revenue"]
        for product in products[:1]
    )

    top_5_revenue = sum(
        product["revenue"]
        for product in products[:5]
    )

    top_10_revenue = sum(
        product["revenue"]
        for product in products[:10]
    )

    def share(value):
        return round(
            value
            / total_revenue
            * 100,
            2,
        ) if total_revenue else 0

    return {
        "month": month,
        "status": "complete",

        "total_products": len(
            products
        ),

        "total_revenue": round(
            total_revenue,
            2,
        ),

        "top_1_revenue_share_percent": (
            share(top_1_revenue)
        ),

        "top_5_revenue_share_percent": (
            share(top_5_revenue)
        ),

        "top_10_revenue_share_percent": (
            share(top_10_revenue)
        ),
    }


def get_product_summary(
    month: str = None,
):
    """
    Build a management-level product summary.
    """

    products = (
        get_product_performance(
            month=month
        )
    )

    if not products:
        return {
            "month": month,
            "status": "no_data",
        }

    total_revenue = sum(
        product["revenue"]
        for product in products
    )

    total_units = sum(
        product["units_sold"]
        for product in products
    )

    total_orders = len(
        {
            row["order_id"]
            for _, row
            in _load_product_dataset().iterrows()
            if (
                month is None
                or row["month"] == month
            )
        }
    )

    return {
        "month": month,

        "status": "complete",

        "total_products": len(
            products
        ),

        "total_revenue": round(
            total_revenue,
            2
        ),

        "total_units": int(
            total_units
        ),

        "total_orders": int(
            total_orders
        ),

        "average_revenue_per_product": round(
            total_revenue
            / len(products),
            2,
        ),

        "top_products": (
            products[:10]
        ),

        "concentration": (
            get_product_concentration(
                month
            )
        ),

        "profitability_status": (
            "unavailable"
        ),

        "profitability_limitation": (
            "Product profitability cannot be calculated "
            "without COGS and additional variable cost data."
        ),
    }


def get_product_analytics(
    month: str = None,
):
    """
    Complete V1 product analytics response.
    """

    return {
        "month": month,

        "summary": (
            get_product_summary(
                month
            )
        ),

        "top_products": (
            get_top_products(
                month=month,
                limit=10,
            )
        ),

        "concentration": (
            get_product_concentration(
                month
            )
        ),

        "available_metrics": [
            "product revenue",
            "units sold",
            "orders",
            "average selling price",
            "freight value",
            "revenue contribution",
            "freight-to-revenue ratio",
            "product concentration",
        ],

        "unavailable_metrics": {
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
        },
    }