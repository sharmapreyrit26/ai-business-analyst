from backend.app.services.root_cause_engine import (
    analyze_root_causes,
)


def build_hypotheses(month: str):
    """
    Build and structure business hypotheses.

    A hypothesis is NOT treated as a fact.

    Each hypothesis contains:
    - possible explanation
    - measurable driver
    - current evidence status
    - missing evidence
    - confidence
    - recommended investigation
    """

    root_cause = analyze_root_causes(
        month
    )

    # ---------------------------------------------
    # HANDLE INSUFFICIENT DATA
    # ---------------------------------------------

    if root_cause.get("status") != "complete":

        return {
            "month": month,
            "status": "insufficient_data",
            "hypotheses": [],
            "message": (
                "Insufficient data is available "
                "to generate structured hypotheses."
            )
        }

    hypotheses = []

    measured_drivers = root_cause[
        "measured_drivers"
    ]

    # ---------------------------------------------
    # BUILD HYPOTHESES BASED ON
    # THE PRIMARY MEASURABLE DRIVER
    # ---------------------------------------------

    if not measured_drivers:

        return {
            "month": month,
            "status": "no_driver_identified",
            "hypotheses": [],
            "message": (
                "No measurable business driver was "
                "identified."
            )
        }

    primary_driver = measured_drivers[0][
        "driver"
    ]

    # ---------------------------------------------
    # ORDER VOLUME HYPOTHESES
    # ---------------------------------------------

    if primary_driver == "order_volume":

        hypotheses.extend([

            {
                "hypothesis_id": "H1",

                "hypothesis": (
                    "Customer demand may have weakened."
                ),

                "related_driver": (
                    "order_volume"
                ),

                "status": "unverified",

                "current_evidence": [
                    "Order volume changed significantly."
                ],

                "missing_evidence": [
                    "customer demand metrics",
                    "repeat purchase behaviour",
                    "customer activity data"
                ],

                "confidence": "low",

                "recommended_investigation": (
                    "Analyse customer activity, repeat "
                    "purchase behaviour and demand trends."
                )
            },

            {
                "hypothesis_id": "H2",

                "hypothesis": (
                    "Website or marketplace traffic may "
                    "have declined."
                ),

                "related_driver": (
                    "order_volume"
                ),

                "status": "unverified",

                "current_evidence": [
                    "Order volume changed significantly."
                ],

                "missing_evidence": [
                    "website traffic",
                    "channel traffic",
                    "marketing acquisition data"
                ],

                "confidence": "low",

                "recommended_investigation": (
                    "Compare traffic and customer "
                    "acquisition by channel."
                )
            },

            {
                "hypothesis_id": "H3",

                "hypothesis": (
                    "Customer conversion may have declined."
                ),

                "related_driver": (
                    "order_volume"
                ),

                "status": "unverified",

                "current_evidence": [
                    "Order volume changed significantly."
                ],

                "missing_evidence": [
                    "conversion rate",
                    "checkout funnel data",
                    "session data"
                ],

                "confidence": "low",

                "recommended_investigation": (
                    "Analyse the customer funnel and "
                    "conversion rate by channel."
                )
            }
        ])

    # ---------------------------------------------
    # AOV HYPOTHESES
    # ---------------------------------------------

    elif primary_driver == "aov":

        hypotheses.extend([

            {
                "hypothesis_id": "H1",

                "hypothesis": (
                    "Customers may be purchasing lower "
                    "value products."
                ),

                "related_driver": "aov",

                "status": "unverified",

                "current_evidence": [
                    "Average order value changed "
                    "significantly."
                ],

                "missing_evidence": [
                    "product-level revenue",
                    "product mix",
                    "category performance"
                ],

                "confidence": "low",

                "recommended_investigation": (
                    "Analyse changes in product mix and "
                    "category contribution."
                )
            },

            {
                "hypothesis_id": "H2",

                "hypothesis": (
                    "Pricing or discounting may have "
                    "reduced average order value."
                ),

                "related_driver": "aov",

                "status": "unverified",

                "current_evidence": [
                    "Average order value changed "
                    "significantly."
                ],

                "missing_evidence": [
                    "pricing history",
                    "discount data",
                    "promotion data"
                ],

                "confidence": "low",

                "recommended_investigation": (
                    "Review pricing, discounting and "
                    "promotion changes."
                )
            },

            {
                "hypothesis_id": "H3",

                "hypothesis": (
                    "Customers may be buying fewer items "
                    "per order."
                ),

                "related_driver": "aov",

                "status": "unverified",

                "current_evidence": [
                    "Average order value changed "
                    "significantly."
                ],

                "missing_evidence": [
                    "items per order",
                    "basket composition",
                    "product quantity trends"
                ],

                "confidence": "low",

                "recommended_investigation": (
                    "Analyse basket size and items per "
                    "order."
                )
            }
        ])

    # ---------------------------------------------
    # INTERACTION HYPOTHESES
    # ---------------------------------------------

    else:

        hypotheses.extend([

            {
                "hypothesis_id": "H1",

                "hypothesis": (
                    "Changes in both order volume and "
                    "average order value may be affecting "
                    "business performance simultaneously."
                ),

                "related_driver": "interaction",

                "status": "partially_supported",

                "current_evidence": [
                    "Both order volume and AOV changed."
                ],

                "missing_evidence": [
                    "customer behaviour data",
                    "product mix data",
                    "marketing data"
                ],

                "confidence": "medium",

                "recommended_investigation": (
                    "Analyse order volume and basket "
                    "behaviour together."
                )
            }
        ])

    # ---------------------------------------------
    # RETURN RESULT
    # ---------------------------------------------

    return {
        "month": month,

        "status": "complete",

        "primary_driver": primary_driver,

        "total_hypotheses": len(
            hypotheses
        ),

        "hypotheses": hypotheses,

        "investigation_priority": [
            hypothesis["hypothesis_id"]
            for hypothesis in hypotheses
        ]
    }