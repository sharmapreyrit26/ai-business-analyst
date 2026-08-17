import pandas as pd
from pathlib import Path


DATA_PATH = Path("data/raw/olist_order_items_dataset.csv")


def load_order_items():
    """Load the Olist order items dataset."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce"
    )

    return df


def get_revenue_summary():
    """Calculate core revenue KPIs."""

    df = load_order_items()

    total_revenue = df["price"].sum()
    total_freight = df["freight_value"].sum()

    total_order_value = total_revenue + total_freight

    unique_orders = df["order_id"].nunique()
    unique_products = df["product_id"].nunique()

    # AOV is defined consistently with performance.py:
    # revenue / orders
    average_order_value = (
        total_revenue / unique_orders
        if unique_orders > 0
        else 0
    )

    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_freight": round(float(total_freight), 2),
        "total_order_value": round(float(total_order_value), 2),
        "unique_orders": int(unique_orders),
        "unique_products": int(unique_products),
        "average_order_value": round(
            float(average_order_value), 2
        ),
    }