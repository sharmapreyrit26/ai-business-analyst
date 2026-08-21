from functools import lru_cache

import pandas as pd

from backend.app.services.d2c_data_loader import (
    load_couriers,
    load_d2c_order_items,
    load_d2c_orders,
    load_payments,
)


# ============================================================
# ORDER-LEVEL FINANCIAL MODEL
# ============================================================


@lru_cache(maxsize=1)
def _build_order_financials_cached():
    """
    Build the canonical ProfitLens order-level
    financial model for the India D2C dataset.

    Financial treatment is status-aware:

    Delivered:
        recognized product revenue is retained.

    Returned:
        product revenue is reduced by refund amount.

    RTO:
        product revenue is not treated as realized revenue.

    Cancelled:
        product revenue is not treated as realized revenue.

    This prevents failed/RTO orders from appearing as
    successful profitable sales.
    """

    orders = load_d2c_orders()
    items = load_d2c_order_items()
    payments = load_payments()
    couriers = load_couriers()

    item_financials = (
        items.groupby(
            "order_id"
        )
        .agg(
            gross_product_revenue=(
                "gross_revenue",
                "sum",
            ),
            discount_value_items=(
                "discount",
                "sum",
            ),
            net_product_revenue=(
                "net_revenue",
                "sum",
            ),
            cogs=(
                "cogs",
                "sum",
            ),
            units=(
                "quantity",
                "sum",
            ),
            sku_count=(
                "sku_id",
                "nunique",
            ),
        )
        .reset_index()
    )

    financials = (
        orders.merge(
            item_financials,
            on="order_id",
            how="left",
        )
        .merge(
            payments[
                [
                    "order_id",
                    "payment_fee",
                    "cod_fee",
                    "refund_amount",
                ]
            ],
            on="order_id",
            how="left",
        )
        .merge(
            couriers[
                [
                    "courier_id",
                    "courier_name",
                    "base_shipping_cost",
                    "rto_fee",
                    "delivery_sla_days",
                ]
            ],
            on="courier_id",
            how="left",
        )
    )

    numeric_columns = [
        "gross_product_revenue",
        "discount_value_items",
        "net_product_revenue",
        "cogs",
        "units",
        "sku_count",
        "shipping_charge",
        "payment_fee",
        "cod_fee",
        "refund_amount",
        "base_shipping_cost",
        "rto_fee",
    ]

    for column in numeric_columns:
        financials[column] = (
            pd.to_numeric(
                financials[column],
                errors="coerce",
            )
            .fillna(0.0)
        )

    status = (
        financials[
            "order_status"
        ]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    delivered_mask = (
        status
        == "delivered"
    )

    returned_mask = (
        status
        == "returned"
    )

    rto_mask = (
        status
        == "rto"
    )

    cancelled_mask = (
        status.isin(
            [
                "cancelled",
                "canceled",
            ]
        )
    )

    # ========================================================
    # REVENUE RECOGNITION
    # ========================================================

    financials[
        "recognized_product_revenue"
    ] = 0.0

    financials.loc[
        delivered_mask,
        "recognized_product_revenue",
    ] = (
        financials.loc[
            delivered_mask,
            "net_product_revenue",
        ]
    )

    financials.loc[
        returned_mask,
        "recognized_product_revenue",
    ] = (
        financials.loc[
            returned_mask,
            "net_product_revenue",
        ]
        - financials.loc[
            returned_mask,
            "refund_amount",
        ]
    ).clip(
        lower=0.0
    )

    # RTO and cancelled orders remain zero recognized revenue.

    financials[
        "recognized_shipping_revenue"
    ] = 0.0

    financials.loc[
        delivered_mask,
        "recognized_shipping_revenue",
    ] = (
        financials.loc[
            delivered_mask,
            "shipping_charge",
        ]
    )

    financials.loc[
        returned_mask,
        "recognized_shipping_revenue",
    ] = (
        financials.loc[
            returned_mask,
            "shipping_charge",
        ]
    )

    financials[
        "realized_revenue"
    ] = (
        financials[
            "recognized_product_revenue"
        ]
        + financials[
            "recognized_shipping_revenue"
        ]
    )

    # ========================================================
    # COST RECOGNITION
    # ========================================================

    # COGS is recognized for delivered and returned orders.
    # RTO/cancelled merchandise is not treated as consumed COGS
    # in this demo model.
    financials[
        "recognized_cogs"
    ] = 0.0

    financials.loc[
        delivered_mask | returned_mask,
        "recognized_cogs",
    ] = (
        financials.loc[
            delivered_mask | returned_mask,
            "cogs",
        ]
    )

    # Forward shipping applies once a courier shipment exists.
    financials[
        "forward_shipping_cost"
    ] = 0.0

    shipped_mask = (
        delivered_mask
        | returned_mask
        | rto_mask
    )

    financials.loc[
        shipped_mask,
        "forward_shipping_cost",
    ] = (
        financials.loc[
            shipped_mask,
            "base_shipping_cost",
        ]
    )

    financials[
        "rto_cost"
    ] = 0.0

    financials.loc[
        rto_mask,
        "rto_cost",
    ] = (
        financials.loc[
            rto_mask,
            "rto_fee",
        ]
    )

    # COD fee applies only to orders marked COD.
    financials[
        "recognized_cod_fee"
    ] = (
        financials[
            "cod_fee"
        ]
        * financials[
            "is_cod"
        ]
        .astype(int)
    )

    # Payment fee stays as provided by payments.csv.
    financials[
        "recognized_payment_fee"
    ] = (
        financials[
            "payment_fee"
        ]
    )

    # ========================================================
    # PROFITABILITY
    # ========================================================

    financials[
        "gross_profit"
    ] = (
        financials[
            "recognized_product_revenue"
        ]
        - financials[
            "recognized_cogs"
        ]
    )

    financials[
        "contribution_profit_before_marketing"
    ] = (
        financials[
            "realized_revenue"
        ]
        - financials[
            "recognized_cogs"
        ]
        - financials[
            "forward_shipping_cost"
        ]
        - financials[
            "recognized_cod_fee"
        ]
        - financials[
            "recognized_payment_fee"
        ]
        - financials[
            "rto_cost"
        ]
    )

    financials[
        "gross_margin_percent"
    ] = (
        financials[
            "gross_profit"
        ]
        .div(
            financials[
                "recognized_product_revenue"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    financials[
        "contribution_margin_percent"
    ] = (
        financials[
            "contribution_profit_before_marketing"
        ]
        .div(
            financials[
                "realized_revenue"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    return financials


def get_d2c_order_financials():
    """
    Return a safe copy of canonical order-level
    D2C financials.
    """

    return (
        _build_order_financials_cached()
        .copy()
    )


# ============================================================
# MONTHLY FINANCIALS
# ============================================================


@lru_cache(maxsize=1)
def _get_monthly_d2c_financials_cached():
    """
    Aggregate canonical D2C financial metrics by month.
    """

    df = (
        _build_order_financials_cached()
    )

    monthly = (
        df.groupby(
            "month"
        )
        .agg(
            orders=(
                "order_id",
                "nunique",
            ),
            gross_product_revenue=(
                "gross_product_revenue",
                "sum",
            ),
            discounts=(
                "discount_value_items",
                "sum",
            ),
            net_product_revenue=(
                "net_product_revenue",
                "sum",
            ),
            realized_revenue=(
                "realized_revenue",
                "sum",
            ),
            recognized_cogs=(
                "recognized_cogs",
                "sum",
            ),
            gross_profit=(
                "gross_profit",
                "sum",
            ),
            forward_shipping_cost=(
                "forward_shipping_cost",
                "sum",
            ),
            cod_fees=(
                "recognized_cod_fee",
                "sum",
            ),
            payment_fees=(
                "recognized_payment_fee",
                "sum",
            ),
            rto_cost=(
                "rto_cost",
                "sum",
            ),
            refunds=(
                "refund_amount",
                "sum",
            ),
            contribution_profit_before_marketing=(
                "contribution_profit_before_marketing",
                "sum",
            ),
            units=(
                "units",
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
        monthly[
            "realized_revenue"
        ]
        / monthly[
            "orders"
        ]
    )

    monthly[
        "gross_margin_percent"
    ] = (
        monthly[
            "gross_profit"
        ]
        .div(
            monthly[
                "realized_revenue"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    monthly[
        "contribution_margin_percent"
    ] = (
        monthly[
            "contribution_profit_before_marketing"
        ]
        .div(
            monthly[
                "realized_revenue"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    monthly[
        "revenue_growth_percent"
    ] = (
        monthly[
            "realized_revenue"
        ]
        .pct_change()
        .mul(100)
        .fillna(0.0)
    )

    monthly[
        "order_growth_percent"
    ] = (
        monthly[
            "orders"
        ]
        .pct_change()
        .mul(100)
        .fillna(0.0)
    )

    monthly[
        "contribution_growth_percent"
    ] = (
        monthly[
            "contribution_profit_before_marketing"
        ]
        .pct_change()
        .mul(100)
        .fillna(0.0)
    )

    return monthly


def get_monthly_d2c_financials():
    return (
        _get_monthly_d2c_financials_cached()
        .copy()
    )


# ============================================================
# MONTH-SPECIFIC FINANCIAL SUMMARY
# ============================================================


def get_d2c_financial_summary(
    month: str,
):
    """
    Return one month's financial summary with
    previous-month comparison.
    """

    monthly = (
        get_monthly_d2c_financials()
        .reset_index(
            drop=True
        )
    )

    matches = (
        monthly[
            monthly[
                "month"
            ]
            == month
        ]
    )

    if matches.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C reporting period."
        )

    index = (
        matches.index[0]
    )

    current = (
        monthly.loc[
            index
        ]
    )

    previous = (
        monthly.loc[
            index - 1
        ]
        if index > 0
        else None
    )

    def rounded(
        value,
        digits=2,
    ):
        return round(
            float(value),
            digits,
        )

    result = {
        "month": month,

        "orders": int(
            current[
                "orders"
            ]
        ),

        "gross_product_revenue": rounded(
            current[
                "gross_product_revenue"
            ]
        ),

        "discounts": rounded(
            current[
                "discounts"
            ]
        ),

        "net_product_revenue": rounded(
            current[
                "net_product_revenue"
            ]
        ),

        "realized_revenue": rounded(
            current[
                "realized_revenue"
            ]
        ),

        "aov": rounded(
            current[
                "aov"
            ]
        ),

        "cogs": rounded(
            current[
                "recognized_cogs"
            ]
        ),

        "gross_profit": rounded(
            current[
                "gross_profit"
            ]
        ),

        "gross_margin_percent": rounded(
            current[
                "gross_margin_percent"
            ]
        ),

        "forward_shipping_cost": rounded(
            current[
                "forward_shipping_cost"
            ]
        ),

        "cod_fees": rounded(
            current[
                "cod_fees"
            ]
        ),

        "payment_fees": rounded(
            current[
                "payment_fees"
            ]
        ),

        "rto_cost": rounded(
            current[
                "rto_cost"
            ]
        ),

        "refunds": rounded(
            current[
                "refunds"
            ]
        ),

        "contribution_profit_before_marketing": rounded(
            current[
                "contribution_profit_before_marketing"
            ]
        ),

        "contribution_margin_percent": rounded(
            current[
                "contribution_margin_percent"
            ]
        ),

        "revenue_growth_percent": rounded(
            current[
                "revenue_growth_percent"
            ]
        ),

        "order_growth_percent": rounded(
            current[
                "order_growth_percent"
            ]
        ),

        "contribution_growth_percent": rounded(
            current[
                "contribution_growth_percent"
            ]
        ),

        "previous_month": (
            str(
                previous[
                    "month"
                ]
            )
            if previous is not None
            else None
        ),
    }

    if previous is not None:

        result[
            "previous_realized_revenue"
        ] = rounded(
            previous[
                "realized_revenue"
            ]
        )

        result[
            "previous_orders"
        ] = int(
            previous[
                "orders"
            ]
        )

        result[
            "previous_contribution_profit"
        ] = rounded(
            previous[
                "contribution_profit_before_marketing"
            ]
        )

    else:

        result[
            "previous_realized_revenue"
        ] = None

        result[
            "previous_orders"
        ] = None

        result[
            "previous_contribution_profit"
        ] = None

    return result