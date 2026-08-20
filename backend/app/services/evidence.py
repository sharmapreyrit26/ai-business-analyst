from backend.app.services.kpi_engine import get_kpi_dashboard
from backend.app.services.driver_analysis import analyze_revenue_change
from backend.app.services.root_cause_engine import analyze_root_causes
from backend.app.services.hypothesis_engine import build_hypotheses
from backend.app.services.investigation_engine import (
    build_investigation_plan,
)


def build_revenue_evidence(month: str):
    """
    Build structured evidence for revenue analysis.

    Evidence should describe:
    - what changed
    - compared with what
    - which driver contributed
    - how much the driver contributed
    - data quality
    """

    kpi = get_kpi_dashboard(month)

    driver_analysis = analyze_revenue_change(month)

    if driver_analysis.get("status") != "complete":
        return {
            "metric": "revenue",
            "period": month,
            "status": "insufficient_data",
            "evidence": [],
            "message": driver_analysis.get(
                "message",
                "Revenue evidence could not be calculated."
            ),
        }

    revenue = kpi["revenue"]
    orders = kpi["orders"]
    aov = kpi["aov"]

    drivers = driver_analysis["drivers"]

    evidence = [
        {
            "evidence_id": "E1",
            "metric": "revenue",
            "current_value": revenue["value"],
            "previous_value": revenue["previous_value"],
            "change_percent": revenue["growth_percent"],
            "period": month,
            "source": "kpi_engine",
            "statement": (
                f"Revenue changed from "
                f"{revenue['previous_value']:.2f} to "
                f"{revenue['value']:.2f}, a change of "
                f"{revenue['growth_percent']:.2f}%."
            ),
        },

        {
            "evidence_id": "E2",
            "metric": "orders",
            "current_value": orders["value"],
            "previous_value": orders["previous_value"],
            "change_percent": orders["growth_percent"],
            "period": month,
            "source": "kpi_engine",
            "statement": (
                f"Orders changed from "
                f"{orders['previous_value']:,} to "
                f"{orders['value']:,}, a change of "
                f"{orders['growth_percent']:.2f}%."
            ),
        },

        {
            "evidence_id": "E3",
            "metric": "aov",
            "current_value": aov["value"],
            "previous_value": aov["previous_value"],
            "change_percent": aov["growth_percent"],
            "period": month,
            "source": "kpi_engine",
            "statement": (
                f"AOV changed from "
                f"{aov['previous_value']:.2f} to "
                f"{aov['value']:.2f}, a change of "
                f"{aov['growth_percent']:.2f}%."
            ),
        },

        {
            "evidence_id": "E4",
            "metric": "order_volume_effect",
            "value": drivers["order_volume"]["effect"],
            "contribution_percent": drivers[
                "order_volume"
            ]["contribution_percent"],
            "period": month,
            "source": "driver_analysis",
            "statement": (
                f"Order-volume effect on revenue was "
                f"{drivers['order_volume']['effect']:.2f}."
            ),
        },

        {
            "evidence_id": "E5",
            "metric": "aov_effect",
            "value": drivers["aov"]["effect"],
            "contribution_percent": drivers[
                "aov"
            ]["contribution_percent"],
            "period": month,
            "source": "driver_analysis",
            "statement": (
                f"AOV effect on revenue was "
                f"{drivers['aov']['effect']:.2f}."
            ),
        },

        {
            "evidence_id": "E6",
            "metric": "interaction_effect",
            "value": drivers["interaction"]["effect"],
            "contribution_percent": drivers[
                "interaction"
            ]["contribution_percent"],
            "period": month,
            "source": "driver_analysis",
            "statement": (
                f"Order/AOV interaction effect was "
                f"{drivers['interaction']['effect']:.2f}."
            ),
        },
    ]

    return {
        "metric": "revenue",
        "period": month,
        "status": "complete",
        "primary_driver": driver_analysis["primary_driver"],
        "evidence_count": len(evidence),
        "evidence": evidence,
        "data_quality": kpi["data_quality"],
        "reconciliation": driver_analysis["reconciliation"],
    }


def build_operational_evidence(month: str):
    """
    Build evidence for delivery and cancellation performance.
    """

    kpi = get_kpi_dashboard(month)

    delivery = kpi["delivery"]
    cancellation = kpi["cancellation"]

    evidence = [
        {
            "evidence_id": "E7",
            "metric": "delivery_rate",
            "value": delivery["rate_percent"],
            "delivered_orders": delivery["delivered_orders"],
            "period": month,
            "source": "kpi_engine",
            "statement": (
                f"Delivery rate was "
                f"{delivery['rate_percent']:.2f}% with "
                f"{delivery['delivered_orders']:,} "
                f"delivered orders."
            ),
        },

        {
            "evidence_id": "E8",
            "metric": "cancellation_rate",
            "value": cancellation["rate_percent"],
            "cancelled_orders": cancellation[
                "cancelled_orders"
            ],
            "period": month,
            "source": "kpi_engine",
            "statement": (
                f"Cancellation rate was "
                f"{cancellation['rate_percent']:.2f}% with "
                f"{cancellation['cancelled_orders']:,} "
                f"cancelled orders."
            ),
        },
    ]

    return {
        "period": month,
        "status": "complete",
        "evidence_count": len(evidence),
        "evidence": evidence,
        "data_quality": kpi["data_quality"],
    }


def build_hypothesis_evidence(month: str):
    """
    Attach evidence availability to each hypothesis.

    Important:
    hypotheses without supporting data remain unverified.
    """

    hypotheses_result = build_hypotheses(month)

    if hypotheses_result.get("status") != "complete":
        return {
            "period": month,
            "status": hypotheses_result.get(
                "status",
                "insufficient_data"
            ),
            "hypotheses": [],
        }

    result = []

    for hypothesis in hypotheses_result["hypotheses"]:

        missing = hypothesis.get(
            "missing_evidence",
            []
        )

        current = hypothesis.get(
            "current_evidence",
            []
        )

        if current and not missing:
            evidence_status = "supported"

        elif current and missing:
            evidence_status = "partial"

        else:
            evidence_status = "insufficient"

        result.append({
            "hypothesis_id": hypothesis["hypothesis_id"],
            "hypothesis": hypothesis["hypothesis"],
            "related_driver": hypothesis["related_driver"],
            "evidence_status": evidence_status,
            "current_evidence": current,
            "missing_evidence": missing,
        })

    return {
        "period": month,
        "status": "complete",
        "hypotheses": result,
    }


def build_evidence_package(month: str):
    """
    Build the complete evidence package used by
    root-cause, confidence and recommendation layers.
    """

    revenue = build_revenue_evidence(month)

    operations = build_operational_evidence(month)

    hypothesis_evidence = build_hypothesis_evidence(month)

    root_cause = analyze_root_causes(month)

    investigation = build_investigation_plan(month)

    return {
        "period": month,
        "status": "complete",
        "revenue_evidence": revenue,
        "operational_evidence": operations,
        "hypothesis_evidence": hypothesis_evidence,
        "root_cause": root_cause,
        "investigation_plan": investigation,
    }