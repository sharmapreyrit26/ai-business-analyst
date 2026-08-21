from functools import lru_cache

import pandas as pd

from backend.app.services.d2c_data_loader import (
    load_d2c_order_items,
    load_d2c_orders,
)


# ============================================================
# PRODUCT-LEVEL BASE DATA
# ============================================================


@lru_cache(maxsize=1)
def _get_d2c_product_base_cached():
    """
    Build the canonical order-item dataset used for
    deterministic D2C product analytics.

    Product financial metrics come from order_items.

    Order-level outcomes such as RTO and returns are
    joined from orders without allocating order-level
    logistics or payment costs to SKUs.
    """

    items = (
        load_d2c_order_items()
        .copy()
    )

    orders = (
        load_d2c_orders()
        .copy()
    )

    required_item_columns = {
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
    }

    missing_item_columns = (
        required_item_columns
        - set(items.columns)
    )

    if missing_item_columns:
        raise ValueError(
            "Missing required order-item columns: "
            + ", ".join(
                sorted(
                    missing_item_columns
                )
            )
        )

    required_order_columns = {
        "order_id",
        "order_date",
        "order_status",
        "is_cod",
        "is_rto",
        "is_returned",
    }

    missing_order_columns = (
        required_order_columns
        - set(orders.columns)
    )

    if missing_order_columns:
        raise ValueError(
            "Missing required order columns: "
            + ", ".join(
                sorted(
                    missing_order_columns
                )
            )
        )

    if not pd.api.types.is_datetime64_any_dtype(
        orders["order_date"]
    ):
        orders[
            "order_date"
        ] = pd.to_datetime(
            orders[
                "order_date"
            ],
            errors="coerce",
        )

    orders[
        "month"
    ] = (
        orders[
            "order_date"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    order_columns = (
        orders[
            [
                "order_id",
                "month",
                "order_status",
                "is_cod",
                "is_rto",
                "is_returned",
            ]
        ]
        .copy()
    )

    base = (
        items.merge(
            order_columns,
            on="order_id",
            how="left",
            validate="many_to_one",
        )
    )

    return base


def get_d2c_product_base():
    """
    Return a safe copy of the product-analysis base.
    """

    return (
        _get_d2c_product_base_cached()
        .copy()
    )


# ============================================================
# PRODUCT PERFORMANCE
# ============================================================


def get_product_performance(
    month: str,
):
    """
    Return deterministic SKU-level commercial
    performance for one reporting month.

    Contribution profit is intentionally excluded
    because shipping, RTO and payment costs currently
    exist at order level and require an allocation
    methodology before they can safely be assigned
    to individual SKUs.
    """

    df = (
        get_d2c_product_base()
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
            f"Month '{month}' not found in D2C product data."
        )

    financial = (
        month_df.groupby(
            "sku_id",
            dropna=False,
        )
        .agg(
            product_name=(
                "product_name",
                "first",
            ),
            category=(
                "category",
                "first",
            ),
            orders=(
                "order_id",
                "nunique",
            ),
            units_sold=(
                "quantity",
                "sum",
            ),
            gross_revenue=(
                "gross_revenue",
                "sum",
            ),
            discounts=(
                "discount",
                "sum",
            ),
            net_revenue=(
                "net_revenue",
                "sum",
            ),
            cogs=(
                "cogs",
                "sum",
            ),
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # UNIQUE RTO ORDERS BY SKU
    # --------------------------------------------------------

    rto_orders = (
        month_df[
            month_df[
                "is_rto"
            ]
        ]
        .groupby(
            "sku_id"
        )[
            "order_id"
        ]
        .nunique()
        .rename(
            "rto_orders"
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # UNIQUE RETURN ORDERS BY SKU
    # --------------------------------------------------------

    returned_orders = (
        month_df[
            month_df[
                "is_returned"
            ]
        ]
        .groupby(
            "sku_id"
        )[
            "order_id"
        ]
        .nunique()
        .rename(
            "returned_orders"
        )
        .reset_index()
    )

    product = (
        financial.merge(
            rto_orders,
            on="sku_id",
            how="left",
        )
        .merge(
            returned_orders,
            on="sku_id",
            how="left",
        )
    )

    product[
        [
            "rto_orders",
            "returned_orders",
        ]
    ] = (
        product[
            [
                "rto_orders",
                "returned_orders",
            ]
        ]
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # PROFITABILITY
    # --------------------------------------------------------

    product[
        "gross_profit"
    ] = (
        product[
            "net_revenue"
        ]
        - product[
            "cogs"
        ]
    )

    product[
        "gross_margin_percent"
    ] = (
        product[
            "gross_profit"
        ]
        .div(
            product[
                "net_revenue"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    total_net_revenue = float(
        product[
            "net_revenue"
        ]
        .sum()
    )

    if total_net_revenue:
        product[
            "revenue_share_percent"
        ] = (
            product[
                "net_revenue"
            ]
            / total_net_revenue
            * 100
        )
    else:
        product[
            "revenue_share_percent"
        ] = 0.0

    product[
        "average_selling_price"
    ] = (
        product[
            "net_revenue"
        ]
        .div(
            product[
                "units_sold"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    product[
        "rto_rate_percent"
    ] = (
        product[
            "rto_orders"
        ]
        .div(
            product[
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

    product[
        "return_rate_percent"
    ] = (
        product[
            "returned_orders"
        ]
        .div(
            product[
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
        "gross_revenue",
        "discounts",
        "net_revenue",
        "cogs",
        "gross_profit",
        "gross_margin_percent",
        "revenue_share_percent",
        "average_selling_price",
        "rto_rate_percent",
        "return_rate_percent",
    ]

    product[
        numeric_columns
    ] = (
        product[
            numeric_columns
        ]
        .round(2)
    )

    return (
        product.sort_values(
            [
                "net_revenue",
                "sku_id",
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
# PRODUCT SUMMARY
# ============================================================


def get_product_summary(
    month: str,
):
    """
    Return headline product analytics for one month.
    """

    product = (
        get_product_performance(
            month
        )
    )

    total_products = int(
        product[
            "sku_id"
        ]
        .nunique()
    )

    total_net_revenue = float(
        product[
            "net_revenue"
        ]
        .sum()
    )

    total_gross_profit = float(
        product[
            "gross_profit"
        ]
        .sum()
    )

    gross_margin_percent = (
        total_gross_profit
        / total_net_revenue
        * 100
        if total_net_revenue
        else 0.0
    )

    loss_making_products = int(
        (
            product[
                "gross_profit"
            ]
            < 0
        )
        .sum()
    )

    top_5_share = float(
        product.head(5)[
            "revenue_share_percent"
        ]
        .sum()
    )

    top_10_share = float(
        product.head(10)[
            "revenue_share_percent"
        ]
        .sum()
    )

    return {
        "month": month,

        "total_products": (
            total_products
        ),

        "total_net_revenue": round(
            total_net_revenue,
            2,
        ),

        "total_gross_profit": round(
            total_gross_profit,
            2,
        ),

        "gross_margin_percent": round(
            gross_margin_percent,
            2,
        ),

        "loss_making_products": (
            loss_making_products
        ),

        "top_5_revenue_share_percent": round(
            top_5_share,
            2,
        ),

        "top_10_revenue_share_percent": round(
            top_10_share,
            2,
        ),

        "top_products": (
            product.head(10)
            .to_dict(
                orient="records"
            )
        ),

        "profitability_level": (
            "gross_profit"
        ),

        "sku_contribution_profit_available": (
            False
        ),

        "sku_contribution_profit_limitation": (
            "Order-level logistics, payment and marketing "
            "costs require a defined allocation methodology "
            "before SKU contribution profit can be calculated."
        ),
    }


# ============================================================
# CATEGORY PERFORMANCE
# ============================================================


def get_category_performance(
    month: str,
):
    """
    Return category-level economics calculated
    directly from order-item data.

    Unique category orders are calculated directly
    from order IDs rather than by summing SKU-level
    order counts.
    """

    df = (
        get_d2c_product_base()
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
            f"Month '{month}' not found in D2C product data."
        )

    category = (
        month_df.groupby(
            "category",
            dropna=False,
        )
        .agg(
            products=(
                "sku_id",
                "nunique",
            ),
            orders=(
                "order_id",
                "nunique",
            ),
            units_sold=(
                "quantity",
                "sum",
            ),
            gross_revenue=(
                "gross_revenue",
                "sum",
            ),
            discounts=(
                "discount",
                "sum",
            ),
            net_revenue=(
                "net_revenue",
                "sum",
            ),
            cogs=(
                "cogs",
                "sum",
            ),
        )
        .reset_index()
    )

    category[
        "gross_profit"
    ] = (
        category[
            "net_revenue"
        ]
        - category[
            "cogs"
        ]
    )

    category[
        "gross_margin_percent"
    ] = (
        category[
            "gross_profit"
        ]
        .div(
            category[
                "net_revenue"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    total_revenue = float(
        category[
            "net_revenue"
        ]
        .sum()
    )

    if total_revenue:
        category[
            "revenue_share_percent"
        ] = (
            category[
                "net_revenue"
            ]
            / total_revenue
            * 100
        )
    else:
        category[
            "revenue_share_percent"
        ] = 0.0

    # --------------------------------------------------------
    # CATEGORY RTO ORDERS
    # --------------------------------------------------------

    category_rto = (
        month_df[
            month_df[
                "is_rto"
            ]
        ]
        .groupby(
            "category"
        )[
            "order_id"
        ]
        .nunique()
        .rename(
            "rto_orders"
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # CATEGORY RETURN ORDERS
    # --------------------------------------------------------

    category_returns = (
        month_df[
            month_df[
                "is_returned"
            ]
        ]
        .groupby(
            "category"
        )[
            "order_id"
        ]
        .nunique()
        .rename(
            "returned_orders"
        )
        .reset_index()
    )

    category = (
        category.merge(
            category_rto,
            on="category",
            how="left",
        )
        .merge(
            category_returns,
            on="category",
            how="left",
        )
    )

    category[
        [
            "rto_orders",
            "returned_orders",
        ]
    ] = (
        category[
            [
                "rto_orders",
                "returned_orders",
            ]
        ]
        .fillna(0)
        .astype(int)
    )

    category[
        "rto_rate_percent"
    ] = (
        category[
            "rto_orders"
        ]
        .div(
            category[
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

    category[
        "return_rate_percent"
    ] = (
        category[
            "returned_orders"
        ]
        .div(
            category[
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
        "gross_revenue",
        "discounts",
        "net_revenue",
        "cogs",
        "gross_profit",
        "gross_margin_percent",
        "revenue_share_percent",
        "rto_rate_percent",
        "return_rate_percent",
    ]

    category[
        numeric_columns
    ] = (
        category[
            numeric_columns
        ]
        .round(2)
    )

    return (
        category.sort_values(
            "net_revenue",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )