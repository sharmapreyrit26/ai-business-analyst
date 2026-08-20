from backend.app.services.confidence import (
    build_confidence_report,
)
from backend.app.services.evidence import (
    build_evidence_package,
)
from backend.app.services.root_cause_engine import (
    analyze_root_causes,
)


def evaluate_evidence_sufficiency(month: str):
    """
    Determine what ProfitLens can confidently conclude
    and where evidence is insufficient.

    The purpose is to prevent unsupported causal claims.
    """

    confidence_report = build_confidence_report(
        month
    )

    evidence_package = build_evidence_package(
        month
    )

    root_cause = analyze_root_causes(
        month
    )

    measured_driver_confidence = (
        confidence_report[
            "measured_driver_confidence"
        ]
    )

    driver_confidence_score = (
        measured_driver_confidence[
            "confidence_score"
        ]
    )

    driver_confidence_level = (
        measured_driver_confidence[
            "confidence_level"
        ]
    )

    primary_driver = (
        measured_driver_confidence[
            "primary_driver"
        ]
    )

    hypothesis_confidence = (
        confidence_report[
            "hypothesis_confidence"
        ]["hypotheses"]
    )

    # ---------------------------------------------
    # WHAT WE CAN ESTABLISH
    # ---------------------------------------------

    supported_conclusions = []

    if (
        root_cause.get("status") == "complete"
        and primary_driver
    ):
        supported_conclusions.append({
            "type": "measured_driver",
            "conclusion": (
                f"The strongest measurable revenue driver "
                f"is {primary_driver.replace('_', ' ')}."
            ),
            "confidence_score": driver_confidence_score,
            "confidence_level": driver_confidence_level,
        })

    revenue_evidence = (
        evidence_package
        .get(
            "revenue_evidence",
            {}
        )
    )

    if (
        revenue_evidence.get("status")
        == "complete"
    ):
        supported_conclusions.append({
            "type": "observed_change",
            "conclusion": (
                "The revenue change and its order/AOV "
                "decomposition are supported by "
                "deterministic evidence."
            ),
            "confidence_level": (
                driver_confidence_level
            ),
        })

    # ---------------------------------------------
    # WHAT WE CANNOT ESTABLISH
    # ---------------------------------------------

    unsupported_conclusions = []

    for hypothesis in hypothesis_confidence:

        if (
            hypothesis[
                "confidence_level"
            ]
            == "low"
        ):

            unsupported_conclusions.append({
                "hypothesis_id": hypothesis[
                    "hypothesis_id"
                ],

                "hypothesis": hypothesis[
                    "hypothesis"
                ],

                "reason": (
                    "Available evidence is insufficient "
                    "to establish this as a root cause."
                ),

                "missing_evidence": hypothesis[
                    "missing_evidence"
                ],

                "confidence_score": hypothesis[
                    "confidence_score"
                ],

                "confidence_level": hypothesis[
                    "confidence_level"
                ],
            })

    # ---------------------------------------------
    # BUILD MISSING DATA SET
    # ---------------------------------------------

    missing_data = []

    for item in unsupported_conclusions:

        for evidence in item[
            "missing_evidence"
        ]:

            if evidence not in missing_data:
                missing_data.append(
                    evidence
                )

    # ---------------------------------------------
    # SUFFICIENCY STATUS
    # ---------------------------------------------

    if (
        driver_confidence_level == "high"
        and unsupported_conclusions
    ):

        sufficiency_status = (
            "driver_known_root_cause_unknown"
        )

    elif (
        driver_confidence_level
        == "medium"
        and unsupported_conclusions
    ):

        sufficiency_status = (
            "partial_evidence"
        )

    elif (
        driver_confidence_level
        == "low"
    ):

        sufficiency_status = (
            "insufficient_evidence"
        )

    else:

        sufficiency_status = (
            "sufficient"
        )

    # ---------------------------------------------
    # USER-FACING EXPLANATION
    # ---------------------------------------------

    if (
        sufficiency_status
        == "driver_known_root_cause_unknown"
    ):

        explanation = (
            f"ProfitLens can establish that "
            f"{primary_driver.replace('_', ' ')} "
            f"is the strongest measurable driver, "
            f"but the available data is not sufficient "
            f"to determine why that driver changed."
        )

    elif (
        sufficiency_status
        == "partial_evidence"
    ):

        explanation = (
            "The available data supports part of the "
            "business explanation, but additional "
            "evidence is required before identifying "
            "the underlying root cause."
        )

    elif (
        sufficiency_status
        == "insufficient_evidence"
    ):

        explanation = (
            "There is not enough reliable evidence "
            "to determine the root cause."
        )

    else:

        explanation = (
            "Available evidence is sufficient for the "
            "current analytical conclusion."
        )

    return {
        "period": month,

        "status": sufficiency_status,

        "primary_driver": primary_driver,

        "driver_confidence": {
            "score": driver_confidence_score,
            "level": driver_confidence_level,
        },

        "supported_conclusions": (
            supported_conclusions
        ),

        "unsupported_conclusions": (
            unsupported_conclusions
        ),

        "missing_data": missing_data,

        "explanation": explanation,
    }