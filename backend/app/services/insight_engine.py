from backend.app.services.kpi_engine import get_kpi_dashboard
from backend.app.services.performance import get_monthly_performance
from backend.app.services.financial_analysis import get_monthly_revenue


def generate_revenue_insight(month: str):
    kpi = get_kpi_dashboard(month)

    revenue = kpi["revenue"]
    orders = kpi["orders"]
    aov = kpi["aov"]

    revenue_change = revenue["growth_percent"]
    order_change = orders["growth_percent"]
    aov_change = aov["growth_percent"]

    if revenue_change is None:
        summary = "Revenue performance is unavailable."
        primary_driver = "unknown"
        driver_explanation = (
            "There is insufficient data to identify the revenue driver."
        )

    elif revenue_change < 0:
        summary = (
            f"Revenue declined by {abs(revenue_change):.2f}% "
            f"compared with the previous month."
        )

        if (
            order_change is not None
            and aov_change is not None
        ):
            if abs(order_change) > abs(aov_change):
                primary_driver = "order_volume"
                driver_explanation = (
                    f"Order volume was the stronger driver, "
                    f"changing by {order_change:.2f}% compared "
                    f"with an AOV change of {aov_change:.2f}%."
                )
            elif abs(aov_change) > abs(order_change):
                primary_driver = "aov"
                driver_explanation = (
                    f"AOV was the stronger driver, changing by "
                    f"{aov_change:.2f}% compared with an order "
                    f"volume change of {order_change:.2f}%."
                )
            else:
                primary_driver = "mixed"
                driver_explanation = (
                    "Order volume and AOV changed by similar magnitudes."
                )
        else:
            primary_driver = "unknown"
            driver_explanation = (
                "There is insufficient data to identify a dominant driver."
            )

    elif revenue_change > 0:
        summary = (
            f"Revenue increased by {revenue_change:.2f}% "
            f"compared with the previous month."
        )

        if (
            order_change is not None
            and aov_change is not None
        ):
            if abs(order_change) > abs(aov_change):
                primary_driver = "order_volume"
                driver_explanation = (
                    f"Order volume was the stronger contributor, "
                    f"changing by {order_change:.2f}%."
                )
            elif abs(aov_change) > abs(order_change):
                primary_driver = "aov"
                driver_explanation = (
                    f"AOV was the stronger contributor, "
                    f"changing by {aov_change:.2f}%."
                )
            else:
                primary_driver = "mixed"
                driver_explanation = (
                    "Order volume and AOV contributed similarly."
                )
        else:
            primary_driver = "unknown"
            driver_explanation = (
                "There is insufficient data to identify a dominant driver."
            )

    else:
        summary = "Revenue remained stable compared with the previous month."
        primary_driver = "none"
        driver_explanation = "There was no meaningful revenue change."

    return {
        "type": "revenue",
        "period": month,
        "summary": summary,
        "revenue_change_percent": revenue_change,
        "order_change_percent": order_change,
        "aov_change_percent": aov_change,
        "primary_driver": primary_driver,
        "driver_explanation": driver_explanation,
        "data_quality": kpi["data_quality"],
    }


def generate_orders_insight(month: str):
    kpi = get_kpi_dashboard(month)

    orders = kpi["orders"]

    current_orders = orders["value"]
    previous_orders = orders["previous_value"]
    order_change = orders["growth_percent"]

    if order_change is None:
        summary = (
            f"{current_orders:,} orders were recorded in {month}."
        )
        direction = "unavailable"
    elif order_change < 0:
        summary = (
            f"Orders declined by {abs(order_change):.2f}% "
            f"from {previous_orders:,} to {current_orders:,}."
        )
        direction = "declined"
    elif order_change > 0:
        summary = (
            f"Orders increased by {order_change:.2f}% "
            f"from {previous_orders:,} to {current_orders:,}."
        )
        direction = "increased"
    else:
        summary = (
            f"Orders remained stable at {current_orders:,}."
        )
        direction = "stable"

    return {
        "type": "orders",
        "period": month,
        "summary": summary,
        "orders": current_orders,
        "previous_orders": previous_orders,
        "order_change_percent": order_change,
        "direction": direction,
        "data_quality": kpi["data_quality"],
    }


def generate_delivery_insight(month: str):
    kpi = get_kpi_dashboard(month)

    delivery = kpi["delivery"]

    delivery_rate = delivery["rate_percent"]
    delivered_orders = delivery["delivered_orders"]
    total_orders = kpi["orders"]["value"]

    if delivery_rate >= 98:
        assessment = "strong"
    elif delivery_rate >= 95:
        assessment = "healthy"
    elif delivery_rate >= 90:
        assessment = "needs_attention"
    else:
        assessment = "weak"

    return {
        "type": "delivery",
        "period": month,
        "summary": (
            f"Delivery rate was {delivery_rate:.2f}%, "
            f"with {delivered_orders:,} delivered orders "
            f"out of {total_orders:,}."
        ),
        "delivery_rate_percent": delivery_rate,
        "delivered_orders": delivered_orders,
        "total_orders": total_orders,
        "assessment": assessment,
        "data_quality": kpi["data_quality"],
    }


def generate_cancellation_insight(month: str):
    kpi = get_kpi_dashboard(month)

    cancellation = kpi["cancellation"]

    cancellation_rate = cancellation["rate_percent"]
    cancelled_orders = cancellation["cancelled_orders"]
    total_orders = kpi["orders"]["value"]

    if cancellation_rate <= 1:
        assessment = "low"
    elif cancellation_rate <= 3:
        assessment = "moderate"
    elif cancellation_rate <= 5:
        assessment = "high"
    else:
        assessment = "critical"

    return {
        "type": "cancellation",
        "period": month,
        "summary": (
            f"Cancellation rate was {cancellation_rate:.2f}%, "
            f"with {cancelled_orders:,} cancelled orders "
            f"out of {total_orders:,}."
        ),
        "cancellation_rate_percent": cancellation_rate,
        "cancelled_orders": cancelled_orders,
        "total_orders": total_orders,
        "assessment": assessment,
        "data_quality": kpi["data_quality"],
    }


def generate_trend_insight(month: str):
    revenue_df = get_monthly_revenue()

    valid_data = revenue_df[
        revenue_df["month"] != "2018-09"
    ].copy()

    if valid_data.empty:
        return {
            "type": "trends",
            "period": month,
            "summary": "Insufficient historical data to identify trends.",
            "trends": [],
        }

    highest_revenue = valid_data.loc[
        valid_data["revenue"].idxmax()
    ]

    lowest_revenue = valid_data.loc[
        valid_data["revenue"].idxmin()
    ]

    highest_orders = valid_data.loc[
        valid_data["orders"].idxmax()
    ]

    trends = [
        {
            "metric": "revenue",
            "pattern": (
                f"Highest revenue was recorded in "
                f"{highest_revenue['month']}."
            ),
            "value": float(highest_revenue["revenue"]),
        },
        {
            "metric": "revenue",
            "pattern": (
                f"Lowest complete-month revenue was recorded in "
                f"{lowest_revenue['month']}."
            ),
            "value": float(lowest_revenue["revenue"]),
        },
        {
            "metric": "orders",
            "pattern": (
                f"Highest order volume was recorded in "
                f"{highest_orders['month']}."
            ),
            "value": int(highest_orders["orders"]),
        },
    ]

    return {
        "type": "trends",
        "period": month,
        "summary": (
            f"Historical data shows meaningful variation in revenue "
            f"and order volume across months."
        ),
        "trends": trends,
    }


def generate_performance_insight(month: str):
    performance = get_monthly_performance()

    valid_data = performance[
        performance["month"] != "2018-09"
    ].copy()

    if valid_data.empty:
        return {
            "type": "performance",
            "period": month,
            "summary": "Performance data is unavailable.",
        }

    best_revenue = valid_data.loc[
        valid_data["revenue"].idxmax()
    ]

    best_orders = valid_data.loc[
        valid_data["orders"].idxmax()
    ]

    best_delivery = valid_data.loc[
        valid_data["delivery_rate"].idxmax()
    ]

    return {
        "type": "performance",
        "period": month,
        "summary": (
            f"Best revenue performance occurred in "
            f"{best_revenue['month']}, while the highest order "
            f"volume occurred in {best_orders['month']}."
        ),
        "best_revenue_month": best_revenue["month"],
        "best_revenue": float(best_revenue["revenue"]),
        "best_orders_month": best_orders["month"],
        "best_orders": int(best_orders["orders"]),
        "best_delivery_month": best_delivery["month"],
        "best_delivery_rate": float(best_delivery["delivery_rate"]),
    }


def generate_business_health_insight(month: str):
    kpi = get_kpi_dashboard(month)

    revenue_change = kpi["revenue"]["growth_percent"]
    order_change = kpi["orders"]["growth_percent"]
    delivery_rate = kpi["delivery"]["rate_percent"]
    cancellation_rate = kpi["cancellation"]["rate_percent"]

    priorities = []

    if revenue_change is not None and revenue_change <= -10:
        priorities.append(
            "Investigate the significant decline in revenue."
        )

    if order_change is not None and order_change <= -10:
        priorities.append(
            "Investigate the decline in order volume."
        )

    if delivery_rate < 95:
        priorities.append(
            "Improve delivery performance."
        )

    if cancellation_rate > 3:
        priorities.append(
            "Investigate elevated cancellation levels."
        )

    if not priorities:
        priorities.append(
            "Maintain current performance while monitoring "
            "revenue, orders and operational KPIs."
        )

    return {
        "type": "business_health",
        "period": month,
        "summary": "Business health assessment based on current KPIs.",
        "priorities": priorities,
        "revenue_change_percent": revenue_change,
        "order_change_percent": order_change,
        "delivery_rate_percent": delivery_rate,
        "cancellation_rate_percent": cancellation_rate,
        "data_quality": kpi["data_quality"],
    }


def generate_business_insights(month: str):
    """
    Generate deterministic insights across all supported
    business dimensions.
    """

    insights = [
        generate_revenue_insight(month),
        generate_orders_insight(month),
        generate_delivery_insight(month),
        generate_cancellation_insight(month),
        generate_trend_insight(month),
        generate_performance_insight(month),
        generate_business_health_insight(month),
    ]

    high_priority = []

    for insight in insights:

        if insight["type"] == "revenue":
            change = insight["revenue_change_percent"]

            if change is not None and change <= -10:
                high_priority.append(insight)

        elif insight["type"] == "orders":
            change = insight["order_change_percent"]

            if change is not None and change <= -10:
                high_priority.append(insight)

        elif insight["type"] == "delivery":
            if insight["delivery_rate_percent"] < 95:
                high_priority.append(insight)

        elif insight["type"] == "cancellation":
            if insight["cancellation_rate_percent"] > 3:
                high_priority.append(insight)

    return {
        "period": month,
        "total_insights": len(insights),
        "high_priority_insights": len(high_priority),
        "insights": insights,
    }