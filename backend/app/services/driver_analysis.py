from .performance import get_monthly_performance


def analyze_revenue_change(month: str):
    """
    Analyze revenue change compared with the previous month.

    All numerical calculations are performed deterministically
    using Python/Pandas. The LLM should only interpret the results.
    """

    df = get_monthly_performance()

    # --------------------------------
    # FIND CURRENT MONTH
    # --------------------------------

    current_rows = df[df["month"] == month]

    if current_rows.empty:
        raise ValueError(
            f"Month '{month}' not found in reporting period."
        )

    current_index = current_rows.index[0]

    # First month has no comparison period
    if current_index == df.index[0]:
        raise ValueError(
            f"No previous month available for {month}."
        )

    current = df.loc[current_index]
    previous = df.loc[current_index - 1]

    # --------------------------------
    # REVENUE
    # --------------------------------

    revenue_change = (
        current["revenue"] - previous["revenue"]
    )

    revenue_change_percent = (
        revenue_change / previous["revenue"] * 100
        if previous["revenue"] != 0
        else 0
    )

    # --------------------------------
    # ORDERS
    # --------------------------------

    order_change = (
        current["orders"] - previous["orders"]
    )

    order_change_percent = (
        order_change / previous["orders"] * 100
        if previous["orders"] != 0
        else 0
    )

    # --------------------------------
    # AOV
    # --------------------------------

    aov_change = (
        current["aov"] - previous["aov"]
    )

    aov_change_percent = (
        aov_change / previous["aov"] * 100
        if previous["aov"] != 0
        else 0
    )

    # --------------------------------
    # DRIVER EFFECTS
    # --------------------------------

    # Effect of order volume while keeping
    # previous AOV constant.
    order_effect = (
        order_change * previous["aov"]
    )

    # Effect of AOV while keeping
    # current order volume constant.
    aov_effect = (
        previous["orders"] * aov_change
    )

    # Interaction effect between order volume
    # and AOV.
    interaction_effect = (
        order_change * aov_change
    )

    # --------------------------------
    # PRIMARY DRIVER
    # --------------------------------

    if abs(aov_effect) > abs(order_effect):
        primary_driver = "average_order_value"
    else:
        primary_driver = "order_volume"

    # --------------------------------
    # REVENUE DIRECTION
    # --------------------------------

    if revenue_change_percent > 0:
        revenue_direction = "increase"
    elif revenue_change_percent < 0:
        revenue_direction = "decrease"
    else:
        revenue_direction = "stable"

    # --------------------------------
    # RETURN STRUCTURED ANALYSIS
    # --------------------------------

    return {
        "period": month,
        "previous_period": previous["month"],

        # Revenue
        "revenue": round(float(current["revenue"]), 2),
        "previous_revenue": round(
            float(previous["revenue"]), 2
        ),
        "revenue_change": round(
            float(revenue_change), 2
        ),
        "revenue_change_percent": round(
            float(revenue_change_percent), 2
        ),

        # Orders
        "orders": int(current["orders"]),
        "previous_orders": int(previous["orders"]),
        "order_change": int(order_change),
        "order_change_percent": round(
            float(order_change_percent), 2
        ),

        # AOV
        "aov": round(float(current["aov"]), 2),
        "previous_aov": round(
            float(previous["aov"]), 2
        ),
        "aov_change": round(
            float(aov_change), 2
        ),
        "aov_change_percent": round(
            float(aov_change_percent), 2
        ),

        # Driver effects
        "order_effect": round(
            float(order_effect), 2
        ),
        "aov_effect": round(
            float(aov_effect), 2
        ),
        "interaction_effect": round(
            float(interaction_effect), 2
        ),

        # Delivery
        "delivery_rate": round(
            float(current["delivery_rate"]), 2
        ),
        "previous_delivery_rate": round(
            float(previous["delivery_rate"]), 2
        ),
        "delivery_rate_change": round(
            float(
                current["delivery_rate"]
                - previous["delivery_rate"]
            ),
            2
        ),

        # Cancellation
        "cancellation_rate": round(
            float(current["cancellation_rate"]), 2
        ),
        "previous_cancellation_rate": round(
            float(previous["cancellation_rate"]), 2
        ),
        "cancellation_rate_change": round(
            float(
                current["cancellation_rate"]
                - previous["cancellation_rate"]
            ),
            2
        ),

        # Interpretation
        "revenue_direction": revenue_direction,
        "primary_driver": primary_driver,
    }