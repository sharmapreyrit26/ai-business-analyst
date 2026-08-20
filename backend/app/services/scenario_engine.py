from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
)


def simulate_order_recovery(
    month: str,
    recovery_percent: float
):
    """
    Simulate the effect of recovering a percentage
    of lost order volume.

    Example:
    recovery_percent = 50
    means recover 50% of lost orders.
    """

    kpi = get_kpi_dashboard(month)

    current_orders = kpi["orders"]["value"]
    previous_orders = kpi["orders"]["previous_value"]
    current_aov = kpi["aov"]["value"]
    current_revenue = kpi["revenue"]["value"]

    if previous_orders is None:
        return {
            "period": month,
            "scenario": "order_recovery",
            "status": "insufficient_data",
            "message": (
                "Previous order volume is unavailable."
            )
        }

    lost_orders = (
        previous_orders - current_orders
    )

    if lost_orders <= 0:
        return {
            "period": month,
            "scenario": "order_recovery",
            "status": "not_applicable",
            "message": (
                "Order volume did not decline in the "
                "selected period."
            )
        }

    recovered_orders = (
        lost_orders
        * recovery_percent
        / 100
    )

    scenario_orders = (
        current_orders
        + recovered_orders
    )

    incremental_revenue = (
        recovered_orders
        * current_aov
    )

    scenario_revenue = (
        current_revenue
        + incremental_revenue
    )

    return {
        "period": month,
        "scenario": "order_recovery",
        "status": "complete",

        "assumptions": {
            "recovery_percent": recovery_percent,
            "aov_held_constant": current_aov,
        },

        "current": {
            "orders": current_orders,
            "revenue": current_revenue,
        },

        "scenario_result": {
            "orders": round(
                scenario_orders,
                2
            ),
            "revenue": round(
                scenario_revenue,
                2
            ),
        },

        "difference": {
            "additional_orders": round(
                recovered_orders,
                2
            ),
            "incremental_revenue": round(
                incremental_revenue,
                2
            ),
        },

        "limitations": [
            (
                "AOV is assumed to remain constant."
            ),
            (
                "The scenario does not account for "
                "marketing, inventory, capacity, or "
                "profitability effects."
            ),
        ],
    }


def simulate_aov_change(
    month: str,
    aov_change_percent: float
):
    """
    Simulate the effect of changing AOV while
    keeping current order volume constant.
    """

    kpi = get_kpi_dashboard(month)

    current_aov = kpi["aov"]["value"]
    current_orders = kpi["orders"]["value"]
    current_revenue = kpi["revenue"]["value"]

    aov_change = (
        current_aov
        * aov_change_percent
        / 100
    )

    scenario_aov = (
        current_aov
        + aov_change
    )

    scenario_revenue = (
        scenario_aov
        * current_orders
    )

    incremental_revenue = (
        scenario_revenue
        - current_revenue
    )

    return {
        "period": month,
        "scenario": "aov_change",
        "status": "complete",

        "assumptions": {
            "aov_change_percent": (
                aov_change_percent
            ),
            "orders_held_constant": (
                current_orders
            ),
        },

        "current": {
            "aov": current_aov,
            "orders": current_orders,
            "revenue": current_revenue,
        },

        "scenario_result": {
            "aov": round(
                scenario_aov,
                2
            ),
            "revenue": round(
                scenario_revenue,
                2
            ),
        },

        "difference": {
            "aov_change": round(
                aov_change,
                2
            ),
            "incremental_revenue": round(
                incremental_revenue,
                2
            ),
        },

        "limitations": [
            (
                "Order volume is assumed to remain constant."
            ),
            (
                "The scenario does not model price "
                "elasticity or customer behaviour changes."
            ),
        ],
    }


def simulate_combined_change(
    month: str,
    order_change_percent: float = 0,
    aov_change_percent: float = 0
):
    """
    Simulate simultaneous changes in order volume
    and AOV.
    """

    kpi = get_kpi_dashboard(month)

    current_orders = kpi["orders"]["value"]
    current_aov = kpi["aov"]["value"]
    current_revenue = kpi["revenue"]["value"]

    scenario_orders = (
        current_orders
        * (
            1
            + order_change_percent / 100
        )
    )

    scenario_aov = (
        current_aov
        * (
            1
            + aov_change_percent / 100
        )
    )

    scenario_revenue = (
        scenario_orders
        * scenario_aov
    )

    incremental_revenue = (
        scenario_revenue
        - current_revenue
    )

    return {
        "period": month,
        "scenario": "combined_change",
        "status": "complete",

        "assumptions": {
            "order_change_percent": (
                order_change_percent
            ),
            "aov_change_percent": (
                aov_change_percent
            ),
        },

        "current": {
            "orders": current_orders,
            "aov": current_aov,
            "revenue": current_revenue,
        },

        "scenario_result": {
            "orders": round(
                scenario_orders,
                2
            ),
            "aov": round(
                scenario_aov,
                2
            ),
            "revenue": round(
                scenario_revenue,
                2
            ),
        },

        "difference": {
            "incremental_revenue": round(
                incremental_revenue,
                2
            ),
        },

        "limitations": [
            (
                "The scenario is mathematical and "
                "does not predict customer response."
            ),
            (
                "Costs and profit impact are not available "
                "with the current dataset."
            ),
        ],
    }


def run_scenario(
    month: str,
    scenario_type: str,
    **kwargs
):
    """
    Generic scenario dispatcher.
    """

    if scenario_type == "order_recovery":

        recovery_percent = kwargs.get(
            "recovery_percent",
            50
        )

        return simulate_order_recovery(
            month,
            recovery_percent
        )

    if scenario_type == "aov_change":

        aov_change_percent = kwargs.get(
            "aov_change_percent",
            5
        )

        return simulate_aov_change(
            month,
            aov_change_percent
        )

    if scenario_type == "combined_change":

        return simulate_combined_change(
            month,
            order_change_percent=kwargs.get(
                "order_change_percent",
                0
            ),
            aov_change_percent=kwargs.get(
                "aov_change_percent",
                0
            )
        )

    return {
        "period": month,
        "status": "unsupported_scenario",
        "scenario": scenario_type,
        "message": (
            f"Scenario type '{scenario_type}' "
            f"is not currently supported."
        ),
    }