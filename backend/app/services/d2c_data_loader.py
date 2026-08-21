from functools import lru_cache
from pathlib import Path

import pandas as pd


# ============================================================
# DATASET LOCATION
# ============================================================


DATA_DIR = Path(
    "data/demo_india_d2c/"
    "indian_d2c_synthetic_dataset"
)


# ============================================================
# EXPECTED SCHEMAS
# ============================================================


EXPECTED_COLUMNS = {
    "products": {
        "sku_id",
        "product_name",
        "category",
        "list_price",
        "cogs_per_unit",
    },

    "customers": {
        "customer_id",
        "customer_unique_id",
        "first_order_date",
        "city",
        "state",
        "pincode",
        "acquisition_channel",
    },

    "couriers": {
        "courier_id",
        "courier_name",
        "zone",
        "base_shipping_cost",
        "cod_fee",
        "rto_fee",
        "delivery_sla_days",
    },

    "orders": {
        "order_id",
        "customer_id",
        "order_date",
        "order_status",
        "payment_method",
        "order_value",
        "discount_value",
        "shipping_charge",
        "courier_id",
        "pincode",
        "city",
        "state",
        "zone",
        "is_cod",
        "is_rto",
        "is_returned",
        "ndr_flag",
        "first_attempt_delivery",
        "order_delivered_date",
        "promised_delivery_date",
    },

    "order_items": {
        "order_id",
        "sku_id",
        "product_name",
        "category",
        "quantity",
        "selling_price",
        "discount",
        "cogs",
        "gross_revenue",
        "net_revenue",
    },

    "payments": {
        "order_id",
        "payment_method",
        "payment_gateway",
        "payment_fee",
        "cod_fee",
        "refund_amount",
    },

    "marketing": {
        "date",
        "channel",
        "campaign",
        "spend",
        "clicks",
        "sessions",
        "orders",
        "new_customers",
        "attributed_revenue",
    },

    "inventory": {
        "sku_id",
        "warehouse",
        "opening_stock",
        "closing_stock",
        "units_sold",
        "units_received",
        "reorder_point",
    },
}


# ============================================================
# GENERIC HELPERS
# ============================================================


def _validate_columns(
    dataframe: pd.DataFrame,
    table_name: str,
):
    """
    Validate that the loaded table contains
    the expected ProfitLens D2C columns.
    """

    required = (
        EXPECTED_COLUMNS[
            table_name
        ]
    )

    missing = (
        required
        - set(
            dataframe.columns
        )
    )

    if missing:
        raise ValueError(
            f"{table_name} is missing required columns: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )


def _normalize_boolean(
    series: pd.Series,
):
    """
    Convert common boolean representations
    into native Python/Pandas booleans.
    """

    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(
            [
                "1",
                "true",
                "yes",
                "y",
            ]
        )
    )


def _load_csv(
    filename: str,
    table_name: str,
    date_columns: list[str] | None = None,
):
    """
    Load and validate a ProfitLens dataset.
    """

    path = (
        DATA_DIR
        / filename
    )

    if not path.exists():
        raise FileNotFoundError(
            f"ProfitLens dataset not found: {path}"
        )

    dataframe = pd.read_csv(
        path,
        low_memory=False,
    )

    _validate_columns(
        dataframe,
        table_name,
    )

    for column in (
        date_columns
        or []
    ):

        dataframe[
            column
        ] = pd.to_datetime(
            dataframe[
                column
            ],
            errors="coerce",
        )

    return dataframe


# ============================================================
# PRODUCTS
# ============================================================


@lru_cache(maxsize=1)
def _load_products_cached():
    return _load_csv(
        filename="products.csv",
        table_name="products",
    )


def load_products():
    return (
        _load_products_cached()
        .copy()
    )


# ============================================================
# CUSTOMERS
# ============================================================


@lru_cache(maxsize=1)
def _load_customers_cached():
    return _load_csv(
        filename="customers.csv",
        table_name="customers",
        date_columns=[
            "first_order_date",
        ],
    )


def load_customers():
    return (
        _load_customers_cached()
        .copy()
    )


# ============================================================
# COURIERS
# ============================================================


@lru_cache(maxsize=1)
def _load_couriers_cached():
    return _load_csv(
        filename="couriers.csv",
        table_name="couriers",
    )


def load_couriers():
    return (
        _load_couriers_cached()
        .copy()
    )


# ============================================================
# ORDERS
# ============================================================


@lru_cache(maxsize=1)
def _load_orders_cached():

    dataframe = _load_csv(
        filename="orders.csv",
        table_name="orders",
        date_columns=[
            "order_date",
            "first_attempt_delivery",
            "order_delivered_date",
            "promised_delivery_date",
        ],
    )

    for column in [
        "is_cod",
        "is_rto",
        "is_returned",
        "ndr_flag",
    ]:

        dataframe[
            column
        ] = _normalize_boolean(
            dataframe[
                column
            ]
        )

    dataframe[
        "month"
    ] = (
        dataframe[
            "order_date"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    return dataframe


def load_d2c_orders():
    return (
        _load_orders_cached()
        .copy()
    )


# ============================================================
# ORDER ITEMS
# ============================================================


@lru_cache(maxsize=1)
def _load_order_items_cached():

    dataframe = _load_csv(
        filename="order_items.csv",
        table_name="order_items",
    )

    return dataframe


def load_d2c_order_items():
    return (
        _load_order_items_cached()
        .copy()
    )


# ============================================================
# PAYMENTS
# ============================================================


@lru_cache(maxsize=1)
def _load_payments_cached():

    dataframe = _load_csv(
        filename="payments.csv",
        table_name="payments",
    )

    return dataframe


def load_payments():
    return (
        _load_payments_cached()
        .copy()
    )


# ============================================================
# MARKETING
# ============================================================


@lru_cache(maxsize=1)
def _load_marketing_cached():

    dataframe = _load_csv(
        filename="marketing.csv",
        table_name="marketing",
        date_columns=[
            "date",
        ],
    )

    dataframe[
        "month"
    ] = (
        dataframe[
            "date"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    return dataframe


def load_marketing():
    return (
        _load_marketing_cached()
        .copy()
    )


# ============================================================
# INVENTORY
# ============================================================


@lru_cache(maxsize=1)
def _load_inventory_cached():

    dataframe = _load_csv(
        filename="inventory.csv",
        table_name="inventory",
    )

    return dataframe


def load_inventory():
    return (
        _load_inventory_cached()
        .copy()
    )


# ============================================================
# DATASET SUMMARY
# ============================================================


def get_d2c_dataset_summary():
    """
    Return lightweight metadata about the
    currently connected ProfitLens demo dataset.
    """

    orders = (
        _load_orders_cached()
    )

    customers = (
        _load_customers_cached()
    )

    products = (
        _load_products_cached()
    )

    items = (
        _load_order_items_cached()
    )

    payments = (
        _load_payments_cached()
    )

    marketing = (
        _load_marketing_cached()
    )

    couriers = (
        _load_couriers_cached()
    )

    inventory = (
        _load_inventory_cached()
    )

    return {
        "dataset": (
            "ProfitLens India D2C Demo Dataset v1.1"
        ),

        "orders": int(
            len(
                orders
            )
        ),

        "order_items": int(
            len(
                items
            )
        ),

        "customers": int(
            len(
                customers
            )
        ),

        "products": int(
            len(
                products
            )
        ),

        "payments": int(
            len(
                payments
            )
        ),

        "marketing_rows": int(
            len(
                marketing
            )
        ),

        "couriers": int(
            len(
                couriers
            )
        ),

        "inventory_rows": int(
            len(
                inventory
            )
        ),

        "start_date": (
            orders[
                "order_date"
            ]
            .min()
            .date()
            .isoformat()
        ),

        "end_date": (
            orders[
                "order_date"
            ]
            .max()
            .date()
            .isoformat()
        ),

        "months": sorted(
            orders[
                "month"
            ]
            .dropna()
            .unique()
            .tolist()
        ),
    }