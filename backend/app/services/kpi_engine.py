from backend.app.services.performance import get_monthly_performance
from backend.app.services.financial_analysis import (
    get_monthly_revenue_analysis,
    get_monthly_data_quality,
)
from backend.app.services.order_analysis import (
    get_order_summary,
)


def get_kpi_dashboard(month: str = "2018-06"):
    """
    Generate the central ProfitLens KPI dashboard for a month.
    """

    revenue = get_monthly_revenue_analysis(month)
    orders = get_order_summary()
    performance = get_monthly_performance()

    month_rows = performance[
        performance["month"] == month
    ]

    if month_rows.empty:
        raise ValueError(
            f"No performance data found for month: {month}"
        )

    current = month_rows.iloc[0]

    data_quality = get_monthly_data_quality()

    quality_by_month = {
        item["month"]: item
        for item in data_quality
    }

    current_quality = quality_by_month.get(
        month,
        {
            "data_quality": "unknown",
            "is_partial_month": False,
        }
    )

    return {
        "month": month,

        "data_quality": {
            "status": current_quality["data_quality"],
            "is_partial_month": current_quality[
                "is_partial_month"
            ],
        },

        "revenue": {
            "value": revenue["revenue"],
            "previous_value": revenue.get(
                "previous_revenue"
            ),
            "growth_percent": revenue.get(
                "revenue_change_percent"
            ),
        },

        "orders": {
            "value": revenue["orders"],
            "previous_value": revenue.get(
                "previous_orders"
            ),
            "growth_percent": revenue.get(
                "order_change_percent"
            ),
        },

        "aov": {
            "value": revenue["aov"],
            "previous_value": revenue.get(
                "previous_aov"
            ),
            "growth_percent": revenue.get(
                "aov_change_percent"
            ),
        },

        "delivery": {
            "rate_percent": round(
                float(current["delivery_rate"]),
                2
            ),
            "delivered_orders": int(
                current["delivered_orders"]
            ),
        },

        "cancellation": {
            "rate_percent": round(
                float(current["cancellation_rate"]),
                2
            ),
            "cancelled_orders": int(
                current["cancelled_orders"]
            ),
        },

        "freight": {
            "value": revenue["freight_value"],
        },

        "items": {
            "value": revenue["items"],
        },

        "business_totals": {
            "total_orders": orders["total_orders"],
            "delivered_orders": orders[
                "delivered_orders"
            ],
            "cancelled_orders": orders[
                "cancelled_orders"
            ],
        },
    }