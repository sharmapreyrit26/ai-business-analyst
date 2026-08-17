from backend.app.services.kpi_engine import get_kpi_dashboard


def generate_revenue_insight(month: str):
    """
    Generate a deterministic revenue insight for a given month.
    """

    kpi = get_kpi_dashboard(month)

    revenue = kpi["revenue"]
    orders = kpi["orders"]
    aov = kpi["aov"]

    revenue_change = revenue["growth_percent"]
    order_change = orders["growth_percent"]
    aov_change = aov["growth_percent"]

    # ---------------------------------------------
    # REVENUE DIRECTION
    # ---------------------------------------------

    if revenue_change is None:
        direction = "Revenue performance is unavailable"

    elif revenue_change < 0:
        direction = "Revenue declined"

    elif revenue_change > 0:
        direction = "Revenue increased"

    else:
        direction = "Revenue remained stable"

    # ---------------------------------------------
    # DRIVER DETECTION
    # ---------------------------------------------

    if (
        order_change is not None
        and aov_change is not None
    ):

        order_impact = abs(order_change)
        aov_impact = abs(aov_change)

        if order_impact > aov_impact:

            primary_driver = "order_volume"

            driver_explanation = (
                f"Order volume was the stronger driver, "
                f"changing by {order_change:.2f}% compared "
                f"with an AOV change of {aov_change:.2f}%."
            )

        elif aov_impact > order_impact:

            primary_driver = "aov"

            driver_explanation = (
                f"Average order value was the stronger driver, "
                f"changing by {aov_change:.2f}% compared "
                f"with an order volume change of "
                f"{order_change:.2f}%."
            )

        else:

            primary_driver = "mixed"

            driver_explanation = (
                "Order volume and average order value "
                "changed by similar magnitudes."
            )

    else:

        primary_driver = "unknown"

        driver_explanation = (
            "There was insufficient data to identify "
            "a dominant revenue driver."
        )

    # ---------------------------------------------
    # DELIVERY CONTEXT
    # ---------------------------------------------

    delivery_rate = kpi["delivery"]["rate_percent"]

    cancellation_rate = (
        kpi["cancellation"]["rate_percent"]
    )

    if delivery_rate >= 98:

        operational_context = (
            f"Delivery performance remained strong at "
            f"{delivery_rate:.2f}%."
        )

    else:

        operational_context = (
            f"Delivery performance was "
            f"{delivery_rate:.2f}%."
        )

    # ---------------------------------------------
    # RETURN
    # ---------------------------------------------

    return {
        "period": month,

        "summary": (
            f"{direction} by "
            f"{abs(revenue_change):.2f}% "
            f"compared with the previous month."
            if revenue_change is not None
            else direction
        ),

        "revenue_change_percent": revenue_change,

        "order_change_percent": order_change,

        "aov_change_percent": aov_change,

        "primary_driver": primary_driver,

        "driver_explanation": driver_explanation,

        "delivery_rate": delivery_rate,

        "cancellation_rate": cancellation_rate,

        "operational_context": operational_context,

        "data_quality": kpi["data_quality"],
    }


def generate_order_insight(month: str):
    """
    Generate a deterministic order-volume insight.
    """

    kpi = get_kpi_dashboard(month)

    orders = kpi["orders"]

    current_orders = orders["value"]
    previous_orders = orders["previous_value"]
    order_change = orders["growth_percent"]

    if order_change is None:

        summary = (
            "Order performance is unavailable."
        )

        direction = "unavailable"

    elif order_change < 0:

        summary = (
            f"Orders declined by "
            f"{abs(order_change):.2f}% compared "
            f"with the previous month."
        )

        direction = "declined"

    elif order_change > 0:

        summary = (
            f"Orders increased by "
            f"{order_change:.2f}% compared "
            f"with the previous month."
        )

        direction = "increased"

    else:

        summary = (
            "Order volume remained stable "
            "compared with the previous month."
        )

        direction = "stable"

    return {
        "period": month,
        "summary": summary,
        "direction": direction,
        "current_orders": current_orders,
        "previous_orders": previous_orders,
        "order_change_percent": order_change,
        "data_quality": kpi["data_quality"],
    }


def generate_delivery_insight(month: str):
    """
    Generate a deterministic delivery-performance insight.
    """

    kpi = get_kpi_dashboard(month)

    delivery = kpi["delivery"]

    delivery_rate = delivery["rate_percent"]
    delivered_orders = delivery["delivered_orders"]

    if delivery_rate is None:

        performance = "unavailable"

        summary = (
            "Delivery performance is unavailable."
        )

    elif delivery_rate >= 98:

        performance = "strong"

        summary = (
            f"Delivery performance was strong at "
            f"{delivery_rate:.2f}%."
        )

    elif delivery_rate >= 95:

        performance = "acceptable"

        summary = (
            f"Delivery performance was "
            f"{delivery_rate:.2f}%."
        )

    else:

        performance = "weak"

        summary = (
            f"Delivery performance was relatively weak "
            f"at {delivery_rate:.2f}%."
        )

    return {
        "period": month,
        "summary": summary,
        "performance": performance,
        "delivery_rate_percent": delivery_rate,
        "delivered_orders": delivered_orders,
        "data_quality": kpi["data_quality"],
    }


def generate_cancellation_insight(month: str):
    """
    Generate a deterministic cancellation insight.
    """

    kpi = get_kpi_dashboard(month)

    cancellation = kpi["cancellation"]

    cancellation_rate = cancellation["rate_percent"]
    cancelled_orders = cancellation["cancelled_orders"]

    if cancellation_rate is None:

        severity = "unavailable"

        summary = (
            "Cancellation performance is unavailable."
        )

    elif cancellation_rate >= 5:

        severity = "high"

        summary = (
            f"Cancellation rate was high at "
            f"{cancellation_rate:.2f}%."
        )

    elif cancellation_rate >= 2:

        severity = "moderate"

        summary = (
            f"Cancellation rate was moderate at "
            f"{cancellation_rate:.2f}%."
        )

    else:

        severity = "low"

        summary = (
            f"Cancellation rate remained low at "
            f"{cancellation_rate:.2f}%."
        )

    return {
        "period": month,
        "summary": summary,
        "severity": severity,
        "cancellation_rate_percent": cancellation_rate,
        "cancelled_orders": cancelled_orders,
        "data_quality": kpi["data_quality"],
    }


def generate_aov_insight(month: str):
    """
    Generate a deterministic Average Order Value insight.
    """

    kpi = get_kpi_dashboard(month)

    aov = kpi["aov"]

    current_aov = aov["value"]
    previous_aov = aov["previous_value"]
    aov_change = aov["growth_percent"]

    if aov_change is None:

        direction = "unavailable"

        summary = (
            "Average order value is unavailable."
        )

    elif aov_change < 0:

        direction = "declined"

        summary = (
            f"Average order value declined by "
            f"{abs(aov_change):.2f}%."
        )

    elif aov_change > 0:

        direction = "increased"

        summary = (
            f"Average order value increased by "
            f"{aov_change:.2f}%."
        )

    else:

        direction = "stable"

        summary = (
            "Average order value remained stable."
        )

    return {
        "period": month,
        "summary": summary,
        "direction": direction,
        "current_aov": current_aov,
        "previous_aov": previous_aov,
        "aov_change_percent": aov_change,
        "data_quality": kpi["data_quality"],
    }


def generate_business_health_insight(month: str):
    """
    Generate a deterministic overall business-health assessment.
    """

    kpi = get_kpi_dashboard(month)

    revenue_change = (
        kpi["revenue"]["growth_percent"]
    )

    order_change = (
        kpi["orders"]["growth_percent"]
    )

    delivery_rate = (
        kpi["delivery"]["rate_percent"]
    )

    cancellation_rate = (
        kpi["cancellation"]["rate_percent"]
    )

    strengths = []
    risks = []

    # ---------------------------------------------
    # COMMERCIAL PERFORMANCE
    # ---------------------------------------------

    if (
        revenue_change is not None
        and revenue_change < 0
    ):
        risks.append(
            f"Revenue declined by "
            f"{abs(revenue_change):.2f}%."
        )

    elif (
        revenue_change is not None
        and revenue_change > 0
    ):
        strengths.append(
            f"Revenue increased by "
            f"{revenue_change:.2f}%."
        )

    # ---------------------------------------------
    # ORDER PERFORMANCE
    # ---------------------------------------------

    if (
        order_change is not None
        and order_change < 0
    ):
        risks.append(
            f"Order volume declined by "
            f"{abs(order_change):.2f}%."
        )

    elif (
        order_change is not None
        and order_change > 0
    ):
        strengths.append(
            f"Order volume increased by "
            f"{order_change:.2f}%."
        )

    # ---------------------------------------------
    # OPERATIONS
    # ---------------------------------------------

    if (
        delivery_rate is not None
        and delivery_rate >= 98
    ):
        strengths.append(
            f"Delivery performance remained strong "
            f"at {delivery_rate:.2f}%."
        )

    elif delivery_rate is not None:
        risks.append(
            f"Delivery performance was "
            f"{delivery_rate:.2f}%."
        )

    # ---------------------------------------------
    # CANCELLATIONS
    # ---------------------------------------------

    if (
        cancellation_rate is not None
        and cancellation_rate >= 2
    ):
        risks.append(
            f"Cancellation rate was "
            f"{cancellation_rate:.2f}%."
        )

    elif cancellation_rate is not None:
        strengths.append(
            f"Cancellation rate remained low "
            f"at {cancellation_rate:.2f}%."
        )

    # ---------------------------------------------
    # OVERALL STATUS
    # ---------------------------------------------

    if len(risks) >= 2:

        overall_status = "needs_attention"

    elif len(risks) == 1:

        overall_status = "mixed"

    else:

        overall_status = "healthy"

    return {
        "period": month,
        "overall_status": overall_status,
        "strengths": strengths,
        "risks": risks,
        "data_quality": kpi["data_quality"],
    }


def generate_business_insights(month: str):
    """
    Generate deterministic business insights across
    all major business dimensions.
    """

    revenue_insight = generate_revenue_insight(month)
    order_insight = generate_order_insight(month)
    delivery_insight = generate_delivery_insight(month)
    cancellation_insight = generate_cancellation_insight(month)
    aov_insight = generate_aov_insight(month)
    business_health = generate_business_health_insight(month)

    insights = [
        revenue_insight,
        order_insight,
        delivery_insight,
        cancellation_insight,
        aov_insight,
        business_health,
    ]

    high_priority = []

    revenue_change = (
        revenue_insight["revenue_change_percent"]
    )

    order_change = (
        order_insight["order_change_percent"]
    )

    cancellation_rate = (
        cancellation_insight[
            "cancellation_rate_percent"
        ]
    )

    # ---------------------------------------------
    # HIGH-PRIORITY CONDITIONS
    # ---------------------------------------------

    if (
        revenue_change is not None
        and revenue_change <= -10
    ):
        high_priority.append(
            revenue_insight
        )

    if (
        order_change is not None
        and order_change <= -10
    ):
        high_priority.append(
            order_insight
        )

    if (
        cancellation_rate is not None
        and cancellation_rate >= 5
    ):
        high_priority.append(
            cancellation_insight
        )

    return {
        "period": month,
        "total_insights": len(insights),
        "high_priority_insights": len(high_priority),
        "insights": insights,
        "business_health": business_health,
    }