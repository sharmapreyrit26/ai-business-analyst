from backend.app.services.hypothesis_engine import (
    build_hypotheses,
)


def get_investigation_priority(
    hypothesis: dict,
    primary_driver: str
) -> int:
    """
    Assign an investigation priority score.

    Higher score = investigate sooner.
    """

    score = 0

    # ---------------------------------------------
    # DRIVER RELEVANCE
    # ---------------------------------------------

    if hypothesis["related_driver"] == primary_driver:
        score += 50

    # ---------------------------------------------
    # EVIDENCE STATUS
    # ---------------------------------------------

    if hypothesis["status"] == "partially_supported":
        score += 30

    elif hypothesis["status"] == "unverified":
        score += 20

    # ---------------------------------------------
    # CONFIDENCE
    # ---------------------------------------------

    confidence_scores = {
        "high": 30,
        "medium": 20,
        "low": 10
    }

    score += confidence_scores.get(
        hypothesis["confidence"],
        0
    )

    return score


def build_investigation_plan(month: str):
    """
    Build a prioritized investigation plan.

    Flow:

    Business problem
        ↓
    Primary measurable driver
        ↓
    Hypotheses
        ↓
    Missing evidence
        ↓
    Ranked investigations
    """

    hypothesis_result = build_hypotheses(
        month
    )

    # ---------------------------------------------
    # HANDLE NON-COMPLETE STATES
    # ---------------------------------------------

    if hypothesis_result.get("status") != "complete":

        return {
            "month": month,
            "status": hypothesis_result.get(
                "status"
            ),
            "primary_driver": None,
            "total_investigations": 0,
            "investigations": [],
            "message": hypothesis_result.get(
                "message",
                "Unable to build an investigation plan."
            )
        }

    primary_driver = hypothesis_result[
        "primary_driver"
    ]

    hypotheses = hypothesis_result[
        "hypotheses"
    ]

    investigations = []

    # ---------------------------------------------
    # BUILD INVESTIGATION ITEMS
    # ---------------------------------------------

    for hypothesis in hypotheses:

        priority_score = get_investigation_priority(
            hypothesis,
            primary_driver
        )

        investigation = {
            "hypothesis_id": hypothesis[
                "hypothesis_id"
            ],

            "priority_score": priority_score,

            "hypothesis": hypothesis[
                "hypothesis"
            ],

            "related_driver": hypothesis[
                "related_driver"
            ],

            "current_status": hypothesis[
                "status"
            ],

            "confidence": hypothesis[
                "confidence"
            ],

            "current_evidence": hypothesis[
                "current_evidence"
            ],

            "data_required": hypothesis[
                "missing_evidence"
            ],

            "recommended_investigation": hypothesis[
                "recommended_investigation"
            ]
        }

        investigations.append(
            investigation
        )

    # ---------------------------------------------
    # SORT BY PRIORITY
    # ---------------------------------------------

    investigations = sorted(
        investigations,
        key=lambda x: x[
            "priority_score"
        ],
        reverse=True
    )

    # ---------------------------------------------
    # ADD PRIORITY RANK
    # ---------------------------------------------

    for index, investigation in enumerate(
        investigations,
        start=1
    ):

        investigation[
            "priority_rank"
        ] = index

    # ---------------------------------------------
    # RETURN FINAL PLAN
    # ---------------------------------------------

    return {
        "month": month,

        "status": "complete",

        "primary_driver": primary_driver,

        "total_investigations": len(
            investigations
        ),

        "investigations": investigations
    }