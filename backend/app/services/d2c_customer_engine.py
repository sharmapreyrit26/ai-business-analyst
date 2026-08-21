from functools import lru_cache

import pandas as pd

from backend.app.services.d2c_data_loader import (
    load_customers,
    load_d2c_orders,
)


# ============================================================
# CUSTOMER ANALYTICS BASE
# ============================================================


@lru_cache(maxsize=1)
def _get_customer_order_base_cached():
    """
    Build the canonical customer-order dataset.

    customer_unique_id is used as the persistent customer
    identity for repeat-purchase and customer-level analysis.
    """

    customers = (
        load_customers()
        .copy()
    )

    orders = (
        load_d2c_orders()
        .copy()
    )

    required_customer_columns = {
        "customer_id",
        "customer_unique_id",
        "first_order_date",
        "city",
        "state",
        "pincode",
        "acquisition_channel",
    }

    required_order_columns = {
        "order_id",
        "customer_id",
        "order_date",
        "order_status",
        "order_value",
        "is_cod",
        "is_rto",
        "is_returned",
    }

    missing_customers = (
        required_customer_columns
        - set(customers.columns)
    )

    missing_orders = (
        required_order_columns
        - set(orders.columns)
    )

    if missing_customers:
        raise ValueError(
            "Missing required customer columns: "
            + ", ".join(
                sorted(missing_customers)
            )
        )

    if missing_orders:
        raise ValueError(
            "Missing required order columns: "
            + ", ".join(
                sorted(missing_orders)
            )
        )

    orders["order_date"] = (
        pd.to_datetime(
            orders["order_date"],
            errors="coerce",
        )
    )

    customers["first_order_date"] = (
        pd.to_datetime(
            customers["first_order_date"],
            errors="coerce",
        )
    )

    orders["month"] = (
        orders["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    customer_columns = (
        customers[
            [
                "customer_id",
                "customer_unique_id",
                "first_order_date",
                "city",
                "state",
                "pincode",
                "acquisition_channel",
            ]
        ]
        .copy()
    )

    base = (
        orders.merge(
            customer_columns,
            on="customer_id",
            how="left",
            validate="many_to_one",
        )
    )

    return base


def get_customer_order_base():
    """
    Return a safe copy of the customer-order base.
    """

    return (
        _get_customer_order_base_cached()
        .copy()
    )


# ============================================================
# CUSTOMER LIFETIME PERFORMANCE
# ============================================================


@lru_cache(maxsize=1)
def _get_customer_lifetime_performance_cached():
    """
    Calculate historical observed customer performance.

    This is historical customer value, not predictive LTV.
    """

    df = (
        _get_customer_order_base_cached()
        .copy()
    )

    customer = (
        df.groupby(
            "customer_unique_id",
            dropna=False,
        )
        .agg(
            orders=(
                "order_id",
                "nunique",
            ),
            first_order=(
                "order_date",
                "min",
            ),
            last_order=(
                "order_date",
                "max",
            ),
            total_order_value=(
                "order_value",
                "sum",
            ),
            rto_orders=(
                "is_rto",
                "sum",
            ),
            returned_orders=(
                "is_returned",
                "sum",
            ),
            cod_orders=(
                "is_cod",
                "sum",
            ),
            acquisition_channel=(
                "acquisition_channel",
                "first",
            ),
            city=(
                "city",
                "first",
            ),
            state=(
                "state",
                "first",
            ),
        )
        .reset_index()
    )

    customer[
        "average_order_value"
    ] = (
        customer[
            "total_order_value"
        ]
        .div(
            customer[
                "orders"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    customer[
        "is_repeat_customer"
    ] = (
        customer["orders"]
        > 1
    )

    customer[
        "customer_lifespan_days"
    ] = (
        customer["last_order"]
        - customer["first_order"]
    ).dt.days

    customer[
        "rto_rate_percent"
    ] = (
        customer["rto_orders"]
        .div(
            customer["orders"]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    customer[
        "return_rate_percent"
    ] = (
        customer["returned_orders"]
        .div(
            customer["orders"]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    customer[
        "cod_share_percent"
    ] = (
        customer["cod_orders"]
        .div(
            customer["orders"]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    numeric_columns = [
        "total_order_value",
        "average_order_value",
        "rto_rate_percent",
        "return_rate_percent",
        "cod_share_percent",
    ]

    customer[
        numeric_columns
    ] = (
        customer[
            numeric_columns
        ]
        .round(2)
    )

    return customer


def get_customer_lifetime_performance():
    """
    Return observed historical customer performance.
    """

    return (
        _get_customer_lifetime_performance_cached()
        .copy()
    )


# ============================================================
# CUSTOMER SUMMARY
# ============================================================


def get_customer_summary(
    month: str,
):
    """
    Return customer KPIs for one reporting month.

    New vs repeat is determined relative to the selected
    month using each customer's first observed order.
    """

    df = (
        get_customer_order_base()
    )

    month_df = (
        df[
            df["month"]
            == month
        ]
        .copy()
    )

    if month_df.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C customer data."
        )

    month_df[
        "first_order_month"
    ] = (
        month_df[
            "first_order_date"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    total_customers = int(
        month_df[
            "customer_unique_id"
        ]
        .nunique()
    )

    new_customers = int(
        month_df.loc[
            month_df[
                "first_order_month"
            ]
            == month,
            "customer_unique_id",
        ]
        .nunique()
    )

    repeat_customers = int(
        month_df.loc[
            month_df[
                "first_order_month"
            ]
            < month,
            "customer_unique_id",
        ]
        .nunique()
    )

    repeat_customer_rate = (
        repeat_customers
        / total_customers
        * 100
        if total_customers
        else 0.0
    )

    orders = int(
        month_df[
            "order_id"
        ]
        .nunique()
    )

    orders_per_customer = (
        orders
        / total_customers
        if total_customers
        else 0.0
    )

    rto_orders = int(
        month_df[
            "is_rto"
        ]
        .sum()
    )

    returned_orders = int(
        month_df[
            "is_returned"
        ]
        .sum()
    )

    cod_orders = int(
        month_df[
            "is_cod"
        ]
        .sum()
    )

    return {
        "month": month,

        "active_customers": (
            total_customers
        ),

        "new_customers": (
            new_customers
        ),

        "repeat_customers": (
            repeat_customers
        ),

        "repeat_customer_rate_percent": round(
            repeat_customer_rate,
            2,
        ),

        "orders": orders,

        "orders_per_customer": round(
            orders_per_customer,
            2,
        ),

        "rto_orders": (
            rto_orders
        ),

        "rto_rate_percent": round(
            (
                rto_orders
                / orders
                * 100
            )
            if orders
            else 0.0,
            2,
        ),

        "returned_orders": (
            returned_orders
        ),

        "return_rate_percent": round(
            (
                returned_orders
                / orders
                * 100
            )
            if orders
            else 0.0,
            2,
        ),

        "cod_orders": (
            cod_orders
        ),

        "cod_share_percent": round(
            (
                cod_orders
                / orders
                * 100
            )
            if orders
            else 0.0,
            2,
        ),
    }


# ============================================================
# ACQUISITION CHANNEL PERFORMANCE
# ============================================================


def get_acquisition_channel_performance(
    month: str,
):
    """
    Compare customer/order behaviour by acquisition channel.
    """

    df = (
        get_customer_order_base()
    )

    month_df = (
        df[
            df["month"]
            == month
        ]
        .copy()
    )

    if month_df.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C customer data."
        )

    month_df[
        "acquisition_channel"
    ] = (
        month_df[
            "acquisition_channel"
        ]
        .fillna(
            "Unknown"
        )
    )

    channel = (
        month_df.groupby(
            "acquisition_channel",
            dropna=False,
        )
        .agg(
            customers=(
                "customer_unique_id",
                "nunique",
            ),
            orders=(
                "order_id",
                "nunique",
            ),
            order_value=(
                "order_value",
                "sum",
            ),
            rto_orders=(
                "is_rto",
                "sum",
            ),
            returned_orders=(
                "is_returned",
                "sum",
            ),
        )
        .reset_index()
    )

    channel[
        "orders_per_customer"
    ] = (
        channel[
            "orders"
        ]
        .div(
            channel[
                "customers"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    channel[
        "average_order_value"
    ] = (
        channel[
            "order_value"
        ]
        .div(
            channel[
                "orders"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    channel[
        "rto_rate_percent"
    ] = (
        channel[
            "rto_orders"
        ]
        .div(
            channel[
                "orders"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    channel[
        "return_rate_percent"
    ] = (
        channel[
            "returned_orders"
        ]
        .div(
            channel[
                "orders"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    numeric_columns = [
        "order_value",
        "orders_per_customer",
        "average_order_value",
        "rto_rate_percent",
        "return_rate_percent",
    ]

    channel[
        numeric_columns
    ] = (
        channel[
            numeric_columns
        ]
        .round(2)
    )

    return (
        channel.sort_values(
            "order_value",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# CUSTOMER COHORTS
# ============================================================


def get_customer_cohorts():
    """
    Return monthly acquisition cohort behaviour.

    Retention is based on whether a customer places
    another order in later calendar months.

    This is observed historical cohort retention,
    not predictive retention.
    """

    df = (
        get_customer_order_base()
    )

    df[
        "order_month_period"
    ] = (
        df[
            "order_date"
        ]
        .dt.to_period("M")
    )

    df[
        "cohort_month_period"
    ] = (
        df[
            "first_order_date"
        ]
        .dt.to_period("M")
    )

    df = (
        df[
            df[
                "order_month_period"
            ]
            .notna()
            & df[
                "cohort_month_period"
            ]
            .notna()
        ]
        .copy()
    )

    df[
        "months_since_first_order"
    ] = (
        (
            df[
                "order_month_period"
            ]
            .dt.year
            - df[
                "cohort_month_period"
            ]
            .dt.year
        )
        * 12
        + (
            df[
                "order_month_period"
            ]
            .dt.month
            - df[
                "cohort_month_period"
            ]
            .dt.month
        )
    )

    df = (
        df[
            df[
                "months_since_first_order"
            ]
            >= 0
        ]
    )

    cohort_activity = (
        df.groupby(
            [
                "cohort_month_period",
                "months_since_first_order",
            ]
        )[
            "customer_unique_id"
        ]
        .nunique()
        .rename(
            "active_customers"
        )
        .reset_index()
    )

    cohort_sizes = (
        cohort_activity[
            cohort_activity[
                "months_since_first_order"
            ]
            == 0
        ][
            [
                "cohort_month_period",
                "active_customers",
            ]
        ]
        .rename(
            columns={
                "active_customers":
                    "cohort_size"
            }
        )
    )

    cohort_activity = (
        cohort_activity.merge(
            cohort_sizes,
            on="cohort_month_period",
            how="left",
        )
    )

    cohort_activity[
        "retention_percent"
    ] = (
        cohort_activity[
            "active_customers"
        ]
        .div(
            cohort_activity[
                "cohort_size"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
        .round(2)
    )

    cohort_activity[
        "cohort_month"
    ] = (
        cohort_activity[
            "cohort_month_period"
        ]
        .astype(str)
    )

    return (
        cohort_activity[
            [
                "cohort_month",
                "months_since_first_order",
                "cohort_size",
                "active_customers",
                "retention_percent",
            ]
        ]
        .sort_values(
            [
                "cohort_month",
                "months_since_first_order",
            ]
        )
        .reset_index(
            drop=True
        )
    )