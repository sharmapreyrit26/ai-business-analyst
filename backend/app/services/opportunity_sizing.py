from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
)
from backend.app.services.driver_analysis import (
    analyze_revenue_change,
)


def size_revenue_recovery(
    month: str,
    recovery_percent: float = 50.0
):
    """
    Estimate the revenue opportunity if a percentage
    of the observed revenue decline is recovered.

    Example:
    recovery_percent = 50
    means recover 50% of the lost revenue.
    """

    driver_analysis = analyze_revenue_change(
        month
    )

    if driver_analysis.get("status") != "complete":

        return {
            "period": month,
            "status": "insufficient_data",
            "opportunity": None,
            "message": (
                "Revenue recovery opportunity cannot be "
                "estimated because driver analysis is incomplete."
            )
        }

    revenue_change = driver_analysis[
        "revenue_change"
    ]

    if revenue_change >= 0:

        return {
            "period": month,
            "status": "not_applicable",
            "opportunity": 0,
            "message": (
                "Revenue did not decline in the selected period, "
                "so there is no decline-recovery opportunity."
            )
        }

    lost_revenue = abs(
        revenue_change
    )

    recoverable_revenue = (
        lost_revenue
        * recovery_percent
        / 100
    )

    return {
        "period": month,
        "status": "complete",
        "recovery_percent": recovery_percent,
        "lost_revenue": round(
            lost_revenue,
            2
        ),
        "estimated_recoverable_revenue": round(
            recoverable_revenue,
            2
        ),
    }


def size_order_recovery(
    month: str,
    recovery_percent: float = 50.0
):
    """
    Estimate additional revenue if a percentage
    of lost order volume is recovered while AOV
    remains at the current-period level.
    """

    kpi = get_kpi_dashboard(
        month
    )

    orders = kpi["orders"]

    current_orders = orders["value"]
    previous_orders = orders["previous_value"]

    current_aov = kpi["aov"]["value"]

    if previous_orders is None:

        return {
            "period": month,
            "status": "insufficient_data",
            "message": (
                "Previous order volume is unavailable."
            )
        }

    lost_orders = (
        previous_orders
        - current_orders
    )

    if lost_orders <= 0:

        return {
            "period": month,
            "status": "not_applicable",
            "lost_orders": 0,
            "estimated_recoverable_orders": 0,
            "estimated_revenue_opportunity": 0,
        }

    recoverable_orders = (
        lost_orders
        * recovery_percent
        / 100
    )

    revenue_opportunity = (
        recoverable_orders
        * current_aov
    )

    return {
        "period": month,
        "status": "complete",
        "recovery_percent": recovery_percent,
        "lost_orders": int(
            lost_orders
        ),
        "estimated_recoverable_orders": round(
            recoverable_orders,
            2
        ),
        "current_aov": round(
            current_aov,
            2
        ),
        "estimated_revenue_opportunity": round(
            revenue_opportunity,
            2
        ),
    }


def size_aov_recovery(
    month: str,
    recovery_percent: float = 50.0
):
    """
    Estimate revenue opportunity from recovering
    part of the AOV decline while keeping current
    order volume constant.
    """

    kpi = get_kpi_dashboard(
        month
    )

    aov = kpi["aov"]

    current_aov = aov["value"]
    previous_aov = aov["previous_value"]

    current_orders = kpi[
        "orders"
    ]["value"]

    if previous_aov is None:

        return {
            "period": month,
            "status": "insufficient_data",
            "message": (
                "Previous AOV is unavailable."
            )
        }

    lost_aov = (
        previous_aov
        - current_aov
    )

    if lost_aov <= 0:

        return {
            "period": month,
            "status": "not_applicable",
            "lost_aov": 0,
            "estimated_recovered_aov": 0,
            "estimated_revenue_opportunity": 0,
        }

    recovered_aov = (
        lost_aov
        * recovery_percent
        / 100
    )

    revenue_opportunity = (
        recovered_aov
        * current_orders
    )

    return {
        "period": month,
        "status": "complete",
        "recovery_percent": recovery_percent,
        "lost_aov": round(
            lost_aov,
            2
        ),
        "estimated_recovered_aov": round(
            recovered_aov,
            2
        ),
        "current_orders": int(
            current_orders
        ),
        "estimated_revenue_opportunity": round(
            revenue_opportunity,
            2
        ),
    }


def build_opportunity_report(
    month: str
):
    """
    Build the complete opportunity-sizing report.

    Uses a conservative default assumption:
    recover 50% of the observed deterioration.

    These are scenario estimates, not guaranteed outcomes.
    """

    revenue_recovery = (
        size_revenue_recovery(
            month,
            recovery_percent=50
        )
    )

    order_recovery = (
        size_order_recovery(
            month,
            recovery_percent=50
        )
    )

    aov_recovery = (
        size_aov_recovery(
            month,
            recovery_percent=50
        )
    )

    opportunities = []

    if (
        order_recovery.get("status")
        == "complete"
    ):
        opportunities.append({
            "opportunity": "order_volume_recovery",
            "estimated_value": (
                order_recovery[
                    "estimated_revenue_opportunity"
                ]
            ),
            "assumption": (
                "Recover 50% of lost order volume "
                "at current AOV."
            )
        })

    if (
        aov_recovery.get("status")
        == "complete"
    ):
        opportunities.append({
            "opportunity": "aov_recovery",
            "estimated_value": (
                aov_recovery[
                    "estimated_revenue_opportunity"
                ]
            ),
            "assumption": (
                "Recover 50% of the AOV decline "
                "at current order volume."
            )
        })

    opportunities = sorted(
        opportunities,
        key=lambda x: x[
            "estimated_value"
        ],
        reverse=True
    )

    return {
        "period": month,
        "status": "complete",
        "methodology": (
            "Opportunity sizing uses scenario assumptions "
            "based on partial recovery of observed declines. "
            "Values are estimates, not forecasts."
        ),
        "revenue_recovery": revenue_recovery,
        "order_recovery": order_recovery,
        "aov_recovery": aov_recovery,
        "ranked_opportunities": opportunities,
    }