from backend.app.services.financial_analysis import (
    get_monthly_revenue_analysis,
)


def analyze_revenue_change(month: str):
    """
    Decompose revenue change into:

    1. Order volume effect
    2. Average order value effect
    3. Interaction effect

    Revenue = Orders × AOV
    """

    current = get_monthly_revenue_analysis(month)

    current_revenue = current["revenue"]
    current_orders = current["orders"]
    current_aov = current["aov"]

    previous_revenue = current["previous_revenue"]
    previous_orders = current["previous_orders"]
    previous_aov = current["previous_aov"]

    if (
        previous_revenue is None
        or previous_orders is None
        or previous_aov is None
    ):
        return {
            "month": month,
            "status": "insufficient_data",
            "message": (
                "Previous period data is unavailable, "
                "so revenue driver analysis cannot be performed."
            )
        }

    # ---------------------------------------------
    # TOTAL REVENUE CHANGE
    # ---------------------------------------------

    revenue_change = (
        current_revenue - previous_revenue
    )

    # ---------------------------------------------
    # DRIVER DECOMPOSITION
    #
    # Revenue = Orders × AOV
    #
    # Order effect:
    # (Current Orders - Previous Orders) × Previous AOV
    #
    # AOV effect:
    # (Current AOV - Previous AOV) × Previous Orders
    #
    # Interaction effect:
    # (Change in Orders) × (Change in AOV)
    # ---------------------------------------------

    order_effect = (
        (current_orders - previous_orders)
        * previous_aov
    )

    aov_effect = (
        (current_aov - previous_aov)
        * previous_orders
    )

    interaction_effect = (
        (current_orders - previous_orders)
        * (current_aov - previous_aov)
    )

    # ---------------------------------------------
    # RECONCILIATION CHECK
    # ---------------------------------------------

    reconstructed_change = (
        order_effect
        + aov_effect
        + interaction_effect
    )

    reconciliation_difference = (
        revenue_change
        - reconstructed_change
    )

    # ---------------------------------------------
    # DETERMINE DOMINANT DRIVER
    # ---------------------------------------------

    effects = {
        "order_volume": order_effect,
        "aov": aov_effect,
        "interaction": interaction_effect,
    }

    primary_driver = max(
        effects,
        key=lambda key: abs(effects[key])
    )

    # ---------------------------------------------
    # DRIVER CONTRIBUTION
    # ---------------------------------------------

    if revenue_change != 0:

        order_contribution_percent = (
            order_effect
            / revenue_change
            * 100
        )

        aov_contribution_percent = (
            aov_effect
            / revenue_change
            * 100
        )

        interaction_contribution_percent = (
            interaction_effect
            / revenue_change
            * 100
        )

    else:

        order_contribution_percent = 0
        aov_contribution_percent = 0
        interaction_contribution_percent = 0

    return {
        "month": month,

        "status": "complete",

        "current_period": {
            "revenue": round(
                current_revenue,
                2
            ),
            "orders": int(
                current_orders
            ),
            "aov": round(
                current_aov,
                2
            ),
        },

        "previous_period": {
            "month": current[
                "previous_month"
            ],
            "revenue": round(
                previous_revenue,
                2
            ),
            "orders": int(
                previous_orders
            ),
            "aov": round(
                previous_aov,
                2
            ),
        },

        "revenue_change": round(
            revenue_change,
            2
        ),

        "drivers": {
            "order_volume": {
                "effect": round(
                    order_effect,
                    2
                ),
                "contribution_percent": round(
                    order_contribution_percent,
                    2
                ),
            },

            "aov": {
                "effect": round(
                    aov_effect,
                    2
                ),
                "contribution_percent": round(
                    aov_contribution_percent,
                    2
                ),
            },

            "interaction": {
                "effect": round(
                    interaction_effect,
                    2
                ),
                "contribution_percent": round(
                    interaction_contribution_percent,
                    2
                ),
            },
        },

        "primary_driver": primary_driver,

        "reconciliation": {
            "reconstructed_change": round(
                reconstructed_change,
                2
            ),

            "actual_change": round(
                revenue_change,
                2
            ),

            "difference": round(
                reconciliation_difference,
                6
            ),
        },
    }