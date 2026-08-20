from backend.app.services.root_cause_engine import (
    analyze_root_causes,
)
from backend.app.services.confidence import (
    build_confidence_report,
)
from backend.app.services.insufficient_evidence import (
    evaluate_evidence_sufficiency,
)
from backend.app.services.opportunity_sizing import (
    build_opportunity_report,
)


def _priority_from_value(
    estimated_value: float
) -> str:
    """
    Convert estimated opportunity value into
    a simple recommendation priority.

    These thresholds are temporary V1 rules and can
    later be made configurable by business size.
    """

    if estimated_value >= 100000:
        return "high"

    if estimated_value >= 25000:
        return "medium"

    return "low"


def _get_opportunity(
    opportunity_report: dict,
    opportunity_type: str
):
    """
    Find a ranked opportunity by type.
    """

    for opportunity in opportunity_report.get(
        "ranked_opportunities",
        []
    ):

        if (
            opportunity.get("opportunity")
            == opportunity_type
        ):
            return opportunity

    return None


def build_revenue_recommendations(
    month: str
):
    """
    Build evidence-aware recommendations for
    revenue performance.

    Important:
    Recommendations should not claim that an
    unverified hypothesis is a confirmed root cause.
    """

    root_cause = analyze_root_causes(
        month
    )

    confidence = build_confidence_report(
        month
    )

    sufficiency = evaluate_evidence_sufficiency(
        month
    )

    opportunity_report = (
        build_opportunity_report(
            month
        )
    )

    # ---------------------------------------------
    # HANDLE INSUFFICIENT ANALYSIS
    # ---------------------------------------------

    if root_cause.get("status") != "complete":

        return {
            "period": month,
            "status": "insufficient_data",
            "recommendations": [],
            "message": (
                "Recommendations cannot be generated "
                "because the analytical foundation "
                "is incomplete."
            )
        }

    primary_driver = root_cause[
        "measured_drivers"
    ][0]["driver"]

    measured_confidence = confidence[
        "measured_driver_confidence"
    ]

    confidence_score = measured_confidence[
        "confidence_score"
    ]

    confidence_level = measured_confidence[
        "confidence_level"
    ]

    recommendations = []

    # ---------------------------------------------
    # ORDER VOLUME DRIVER
    # ---------------------------------------------

    if primary_driver == "order_volume":

        opportunity = _get_opportunity(
            opportunity_report,
            "order_volume_recovery"
        )

        estimated_value = (
            opportunity["estimated_value"]
            if opportunity
            else 0
        )

        recommendations.append({
            "recommendation_id": "R1",

            "action": (
                "Investigate the decline in order volume "
                "before increasing acquisition spend."
            ),

            "reason": (
                "Order volume is the largest measurable "
                "driver of the revenue movement."
            ),

            "evidence": [
                root_cause[
                    "primary_explanation"
                ]
            ],

            "expected_impact": {
                "metric": "revenue",
                "estimated_value": round(
                    estimated_value,
                    2
                ),
                "basis": (
                    "Estimated revenue opportunity from "
                    "recovering 50% of lost order volume "
                    "at the current AOV."
                )
            },

            "priority": _priority_from_value(
                estimated_value
            ),

            "confidence": {
                "score": confidence_score,
                "level": confidence_level
            },

            "risk": (
                "The system knows that orders declined, "
                "but current data cannot yet prove whether "
                "traffic, conversion, retention, or another "
                "factor caused the decline."
            ),

            "next_investigation": [
                "traffic",
                "conversion rate",
                "customer activity",
                "repeat purchase behaviour",
                "marketing acquisition"
            ]
        })

    # ---------------------------------------------
    # AOV DRIVER
    # ---------------------------------------------

    elif primary_driver == "aov":

        opportunity = _get_opportunity(
            opportunity_report,
            "aov_recovery"
        )

        estimated_value = (
            opportunity["estimated_value"]
            if opportunity
            else 0
        )

        recommendations.append({
            "recommendation_id": "R1",

            "action": (
                "Investigate product mix, basket size, "
                "pricing and discounting before making "
                "pricing changes."
            ),

            "reason": (
                "Average order value is the largest "
                "measurable driver of the revenue movement."
            ),

            "evidence": [
                root_cause[
                    "primary_explanation"
                ]
            ],

            "expected_impact": {
                "metric": "revenue",
                "estimated_value": round(
                    estimated_value,
                    2
                ),
                "basis": (
                    "Estimated revenue opportunity from "
                    "recovering 50% of the AOV decline "
                    "at current order volume."
                )
            },

            "priority": _priority_from_value(
                estimated_value
            ),

            "confidence": {
                "score": confidence_score,
                "level": confidence_level
            },

            "risk": (
                "The system can measure the AOV decline "
                "but cannot yet establish whether product "
                "mix, pricing, discounting or basket size "
                "caused it."
            ),

            "next_investigation": [
                "product mix",
                "items per order",
                "pricing",
                "discounts",
                "category contribution"
            ]
        })

    # ---------------------------------------------
    # INTERACTION / MIXED DRIVER
    # ---------------------------------------------

    else:

        recommendations.append({
            "recommendation_id": "R1",

            "action": (
                "Investigate order volume and AOV together "
                "before selecting a commercial intervention."
            ),

            "reason": (
                "No single commercial driver clearly "
                "dominates the measured revenue movement."
            ),

            "evidence": [
                root_cause[
                    "primary_explanation"
                ]
            ],

            "expected_impact": {
                "metric": "revenue",
                "estimated_value": None,
                "basis": (
                    "A reliable opportunity estimate requires "
                    "a clearer dominant driver."
                )
            },

            "priority": "medium",

            "confidence": {
                "score": confidence_score,
                "level": confidence_level
            },

            "risk": (
                "Acting on only one metric may miss the "
                "combined commercial effect."
            ),

            "next_investigation": [
                "order volume",
                "AOV",
                "customer mix",
                "product mix"
            ]
        })

    # ---------------------------------------------
    # EVIDENCE-GAP RECOMMENDATION
    # ---------------------------------------------

    if sufficiency[
        "status"
    ] in {
        "driver_known_root_cause_unknown",
        "partial_evidence",
        "insufficient_evidence"
    }:

        missing_data = sufficiency.get(
            "missing_data",
            []
        )

        recommendations.append({
            "recommendation_id": (
                f"R{len(recommendations) + 1}"
            ),

            "action": (
                "Connect the missing evidence required "
                "to validate the underlying root cause."
            ),

            "reason": (
                "The current analytical evidence identifies "
                "the measurable driver but does not fully "
                "establish the causal business reason."
            ),

            "evidence": (
                sufficiency[
                    "supported_conclusions"
                ]
            ),

            "expected_impact": {
                "metric": "decision_quality",
                "estimated_value": None,
                "basis": (
                    "Additional evidence reduces the risk "
                    "of acting on an unsupported hypothesis."
                )
            },

            "priority": "high",

            "confidence": {
                "score": confidence_score,
                "level": confidence_level
            },

            "risk": (
                "Without additional evidence, management "
                "could act on the wrong underlying cause."
            ),

            "next_investigation": missing_data
        })

    return {
        "period": month,
        "status": "complete",
        "primary_driver": primary_driver,
        "evidence_sufficiency": sufficiency[
            "status"
        ],
        "total_recommendations": len(
            recommendations
        ),
        "recommendations": recommendations,
    }


def build_recommendation_report(
    month: str
):
    """
    Build the complete recommendation report.
    """

    revenue_recommendations = (
        build_revenue_recommendations(
            month
        )
    )

    return {
        "period": month,
        "status": (
            revenue_recommendations[
                "status"
            ]
        ),
        "recommendation_groups": {
            "revenue": (
                revenue_recommendations
            )
        },
    }