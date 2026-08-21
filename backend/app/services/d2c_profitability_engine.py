from functools import lru_cache

import pandas as pd

from backend.app.services.d2c_data_loader import (
    load_marketing,
)

from backend.app.services.d2c_financial_engine import (
    get_monthly_d2c_financials,
)


# ============================================================
# MONTHLY MARKETING PERFORMANCE
# ============================================================


@lru_cache(maxsize=1)
def _get_monthly_marketing_cached():
    """
    Aggregate campaign/day marketing data into
    monthly ProfitLens marketing performance.

    Marketing remains aggregate because the current
    dataset does not provide order-level campaign
    attribution.
    """

    marketing = load_marketing()

    monthly = (
        marketing.groupby(
            "month"
        )
        .agg(
            marketing_spend=(
                "spend",
                "sum",
            ),

            attributed_revenue=(
                "attributed_revenue",
                "sum",
            ),

            attributed_orders=(
                "orders",
                "sum",
            ),

            new_customers=(
                "new_customers",
                "sum",
            ),

            clicks=(
                "clicks",
                "sum",
            ),

            sessions=(
                "sessions",
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
        "roas"
    ] = (
        monthly[
            "attributed_revenue"
        ]
        .div(
            monthly[
                "marketing_spend"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    monthly[
        "cac"
    ] = (
        monthly[
            "marketing_spend"
        ]
        .div(
            monthly[
                "new_customers"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    monthly[
        "cost_per_attributed_order"
    ] = (
        monthly[
            "marketing_spend"
        ]
        .div(
            monthly[
                "attributed_orders"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    monthly[
        "session_conversion_percent"
    ] = (
        monthly[
            "attributed_orders"
        ]
        .div(
            monthly[
                "sessions"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .mul(100)
        .fillna(0.0)
    )

    return monthly


def get_monthly_marketing():
    return (
        _get_monthly_marketing_cached()
        .copy()
    )


# ============================================================
# FINAL MONTHLY PROFITABILITY
# ============================================================


@lru_cache(maxsize=1)
def _get_monthly_profitability_cached():
    """
    Combine deterministic financial performance
    with aggregate monthly marketing economics.

    This produces ProfitLens contribution profit
    after marketing without inventing order-level
    marketing attribution.
    """

    financial = (
        get_monthly_d2c_financials()
    )

    marketing = (
        _get_monthly_marketing_cached()
    )

    result = (
        financial.merge(
            marketing,
            on="month",
            how="left",
        )
    )

    marketing_columns = [
        "marketing_spend",
        "attributed_revenue",
        "attributed_orders",
        "new_customers",
        "clicks",
        "sessions",
        "roas",
        "cac",
        "cost_per_attributed_order",
        "session_conversion_percent",
    ]

    for column in marketing_columns:
        result[
            column
        ] = (
            pd.to_numeric(
                result[
                    column
                ],
                errors="coerce",
            )
            .fillna(0.0)
        )

    result[
        "contribution_profit_after_marketing"
    ] = (
        result[
            "contribution_profit_before_marketing"
        ]
        - result[
            "marketing_spend"
        ]
    )

    result[
        "contribution_margin_after_marketing_percent"
    ] = (
        result[
            "contribution_profit_after_marketing"
        ]
        .div(
            result[
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

    result[
        "marketing_spend_percent_of_revenue"
    ] = (
        result[
            "marketing_spend"
        ]
        .div(
            result[
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

    result[
        "profit_after_marketing_growth_percent"
    ] = (
        result[
            "contribution_profit_after_marketing"
        ]
        .pct_change()
        .mul(100)
        .fillna(0.0)
    )

    return result


def get_monthly_profitability():
    """
    Return a safe copy of monthly final
    ProfitLens profitability metrics.
    """

    return (
        _get_monthly_profitability_cached()
        .copy()
    )


# ============================================================
# MONTH-SPECIFIC PROFITABILITY
# ============================================================


def get_profitability_summary(
    month: str,
):
    """
    Return final profitability and marketing
    performance for one reporting month.
    """

    monthly = (
        get_monthly_profitability()
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
            f"Month '{month}' not found in D2C profitability data."
        )

    row = (
        matches.iloc[0]
    )

    def rounded(
        value,
        digits=2,
    ):
        return round(
            float(value),
            digits,
        )

    return {
        "month": month,

        "orders": int(
            row[
                "orders"
            ]
        ),

        "realized_revenue": rounded(
            row[
                "realized_revenue"
            ]
        ),

        "gross_profit": rounded(
            row[
                "gross_profit"
            ]
        ),

        "gross_margin_percent": rounded(
            row[
                "gross_margin_percent"
            ]
        ),

        "contribution_profit_before_marketing": rounded(
            row[
                "contribution_profit_before_marketing"
            ]
        ),

        "contribution_margin_before_marketing_percent": rounded(
            row[
                "contribution_margin_percent"
            ]
        ),

        "marketing_spend": rounded(
            row[
                "marketing_spend"
            ]
        ),

        "attributed_revenue": rounded(
            row[
                "attributed_revenue"
            ]
        ),

        "roas": rounded(
            row[
                "roas"
            ]
        ),

        "cac": rounded(
            row[
                "cac"
            ]
        ),

        "attributed_orders": int(
            row[
                "attributed_orders"
            ]
        ),

        "new_customers": int(
            row[
                "new_customers"
            ]
        ),

        "cost_per_attributed_order": rounded(
            row[
                "cost_per_attributed_order"
            ]
        ),

        "session_conversion_percent": rounded(
            row[
                "session_conversion_percent"
            ]
        ),

        "marketing_spend_percent_of_revenue": rounded(
            row[
                "marketing_spend_percent_of_revenue"
            ]
        ),

        "contribution_profit_after_marketing": rounded(
            row[
                "contribution_profit_after_marketing"
            ]
        ),

        "contribution_margin_after_marketing_percent": rounded(
            row[
                "contribution_margin_after_marketing_percent"
            ]
        ),

        "profit_after_marketing_growth_percent": rounded(
            row[
                "profit_after_marketing_growth_percent"
            ]
        ),

        "marketing_attribution_level": (
            "aggregate_monthly"
        ),

        "order_level_marketing_allocation_available": False,
    }