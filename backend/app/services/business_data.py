import pandas as pd

from .data_loader import load_orders
from .revenue import load_order_items


def build_business_dataset():
    """Combine orders and order items into an analytical dataset."""

    orders = load_orders()
    items = load_order_items()

    item_summary = (
        items
        .groupby("order_id")
        .agg(
            revenue=("price", "sum"),
            freight_value=("freight_value", "sum"),
            item_count=("order_item_id", "count"),
            product_count=("product_id", "nunique"),
        )
        .reset_index()
    )

    business_df = orders.merge(
        item_summary,
        on="order_id",
        how="left"
    )

    business_df["revenue"] = business_df["revenue"].fillna(0)
    business_df["freight_value"] = business_df["freight_value"].fillna(0)
    business_df["item_count"] = business_df["item_count"].fillna(0)
    business_df["product_count"] = business_df["product_count"].fillna(0)

    return business_df