import pandas as pd

from backend.app.services.data_loader import load_orders


ORDER_ITEMS_PATH = "data/raw/olist_order_items_dataset.csv"


def load_order_items():
    """
    Load the Olist order items dataset.
    """

    df = pd.read_csv(ORDER_ITEMS_PATH)

    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce"
    )

    return df


def get_order_financials():
    """
    Create order-level financial metrics by aggregating
    all items belonging to each order.
    """

    orders = load_orders()
    items = load_order_items()

    order_financials = (
        items.groupby("order_id")
        .agg(
            revenue=("price", "sum"),
            freight_value=("freight_value", "sum"),
            item_count=("order_item_id", "count")
        )
        .reset_index()
    )

    order_financials = order_financials.merge(
        orders[
            [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp"
            ]
        ],
        on="order_id",
        how="left"
    )

    order_financials["month"] = (
        order_financials["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    return order_financials


def get_revenue_summary():
    """
    Return overall revenue and order-level financial metrics.
    """

    df = get_order_financials()

    total_revenue = df["revenue"].sum()
    total_orders = df["order_id"].nunique()

    delivered_revenue = df.loc[
        df["order_status"] == "delivered",
        "revenue"
    ].sum()

    cancelled_revenue = df.loc[
        df["order_status"] == "canceled",
        "revenue"
    ].sum()

    aov = (
        total_revenue / total_orders
        if total_orders
        else 0
    )

    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": int(total_orders),
        "average_order_value": round(float(aov), 2),
        "delivered_revenue": round(float(delivered_revenue), 2),
        "cancelled_revenue": round(float(cancelled_revenue), 2)
    }


def get_monthly_revenue():
    """
    Calculate monthly revenue, orders, AOV and freight.
    """

    df = get_order_financials()

    monthly = (
        df.groupby("month")
        .agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
            freight_value=("freight_value", "sum"),
            items=("item_count", "sum")
        )
        .reset_index()
        .sort_values("month")
    )

    monthly["aov"] = (
        monthly["revenue"] /
        monthly["orders"]
    )

    monthly["revenue_growth"] = (
        monthly["revenue"]
        .pct_change()
        .mul(100)
    )

    monthly["order_growth"] = (
        monthly["orders"]
        .pct_change()
        .mul(100)
    )

    monthly["aov_growth"] = (
        monthly["aov"]
        .pct_change()
        .mul(100)
    )

    monthly = monthly.fillna(0)

    return monthly


def get_monthly_revenue_analysis(month: str):
    """
    Return revenue metrics for a selected month
    compared with the previous month.
    """

    monthly = get_monthly_revenue()

    current_rows = monthly[
        monthly["month"] == month
    ]

    if current_rows.empty:
        raise ValueError(
            f"No revenue data found for month: {month}"
        )

    current_index = current_rows.index[0]

    current = monthly.loc[current_index]

    if current_index == monthly.index.min():
        previous = None
    else:
        previous = monthly.loc[
            monthly.index[
                monthly.index.get_loc(current_index) - 1
            ]
        ]

    result = {
        "month": month,
        "revenue": round(float(current["revenue"]), 2),
        "orders": int(current["orders"]),
        "aov": round(float(current["aov"]), 2),
        "freight_value": round(
            float(current["freight_value"]),
            2
        ),
        "items": int(current["items"])
    }

    if previous is not None:

        result.update({
            "previous_month": str(previous["month"]),

            "previous_revenue": round(
                float(previous["revenue"]),
                2
            ),

            "previous_orders": int(
                previous["orders"]
            ),

            "previous_aov": round(
                float(previous["aov"]),
                2
            ),

            "revenue_change_percent": round(
                float(current["revenue_growth"]),
                2
            ),

            "order_change_percent": round(
                float(current["order_growth"]),
                2
            ),

            "aov_change_percent": round(
                float(current["aov_growth"]),
                2
            )
        })

    return result


def get_product_revenue():
    """
    Calculate revenue by product.
    """

    items = load_order_items()

    product_revenue = (
        items.groupby("product_id")
        .agg(
            revenue=("price", "sum"),
            orders=("order_id", "nunique"),
            units=("order_item_id", "count"),
            freight_value=("freight_value", "sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    return product_revenue


def get_seller_revenue():
    """
    Calculate revenue by seller.
    """

    items = load_order_items()

    seller_revenue = (
        items.groupby("seller_id")
        .agg(
            revenue=("price", "sum"),
            orders=("order_id", "nunique"),
            units=("order_item_id", "count"),
            freight_value=("freight_value", "sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    return seller_revenue
def get_monthly_data_quality():
    """
    Identify potentially incomplete months in the dataset.

    A month is considered partial when it is the first or last
    available month in the dataset and contains significantly
    fewer orders than the surrounding months.
    """

    monthly = get_monthly_revenue()

    if monthly.empty:
        return []

    monthly = monthly.copy()

    monthly["orders"] = monthly["orders"].astype(int)

    if len(monthly) < 3:
        return monthly.to_dict(orient="records")

    median_orders = monthly["orders"].median()

    monthly["is_partial_month"] = (
        (monthly.index == monthly.index.min()) |
        (monthly.index == monthly.index.max())
    ) & (
        monthly["orders"] < median_orders * 0.5
    )

    monthly["data_quality"] = monthly[
        "is_partial_month"
    ].apply(
        lambda x: "partial" if x else "complete"
    )

    return monthly[
        [
            "month",
            "orders",
            "revenue",
            "is_partial_month",
            "data_quality"
        ]
    ].to_dict(orient="records")