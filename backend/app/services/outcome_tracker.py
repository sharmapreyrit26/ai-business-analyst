from copy import deepcopy
from datetime import datetime

from backend.app.services.decision_memory import (
    get_decision,
)


# --------------------------------------------------
# V1 IN-MEMORY OUTCOME STORE
#
# Later this should move to PostgreSQL and link
# outcomes to persistent business decisions.
# --------------------------------------------------

_outcome_store = []


def record_outcome(
    decision_id: str,
    actual_impact: dict,
    measurement_period: str = None,
    notes: str = None,
):
    """
    Record the actual outcome of a business decision.

    Example:

    expected_impact:
        {
            "metric": "revenue",
            "estimated_value": 48662.46
        }

    actual_impact:
        {
            "metric": "revenue",
            "actual_value": 41700
        }
    """

    decision = get_decision(
        decision_id
    )

    if decision is None:
        raise ValueError(
            f"Decision not found: {decision_id}"
        )

    expected_impact = decision.get(
        "expected_impact",
        {}
    )

    expected_metric = expected_impact.get(
        "metric"
    )

    actual_metric = actual_impact.get(
        "metric"
    )

    if (
        expected_metric
        and actual_metric
        and expected_metric != actual_metric
    ):
        raise ValueError(
            "Actual impact metric does not match "
            "the expected impact metric."
        )

    expected_value = expected_impact.get(
        "estimated_value"
    )

    actual_value = actual_impact.get(
        "actual_value"
    )

    # --------------------------------------------------
    # EFFECTIVENESS
    # --------------------------------------------------

    if (
        expected_value is not None
        and actual_value is not None
        and expected_value != 0
    ):
        effectiveness_percent = (
            actual_value
            / expected_value
            * 100
        )

    else:
        effectiveness_percent = None

    # --------------------------------------------------
    # VARIANCE
    # --------------------------------------------------

    if (
        expected_value is not None
        and actual_value is not None
    ):
        variance = (
            actual_value
            - expected_value
        )

    else:
        variance = None

    outcome = {
        "decision_id": decision_id,

        "decision": decision[
            "decision"
        ],

        "related_metric": decision.get(
            "related_metric"
        ),

        "measurement_period": (
            measurement_period
        ),

        "expected_impact": (
            expected_impact
        ),

        "actual_impact": (
            actual_impact
        ),

        "variance": (
            round(
                variance,
                2
            )
            if variance is not None
            else None
        ),

        "effectiveness_percent": (
            round(
                effectiveness_percent,
                2
            )
            if effectiveness_percent is not None
            else None
        ),

        "notes": notes,

        "recorded_at": (
            datetime.utcnow()
            .isoformat()
        ),
    }

    _outcome_store.append(
        outcome
    )

    return deepcopy(
        outcome
    )


def get_outcomes():
    """
    Return all recorded outcomes.
    """

    return deepcopy(
        _outcome_store
    )


def get_outcome_for_decision(
    decision_id: str
):
    """
    Return all outcomes linked to a decision.
    """

    outcomes = [
        outcome
        for outcome in _outcome_store
        if outcome[
            "decision_id"
        ] == decision_id
    ]

    return deepcopy(
        outcomes
    )


def evaluate_decision_effectiveness(
    decision_id: str
):
    """
    Evaluate overall decision effectiveness.

    V1 assumes the latest recorded outcome is
    the most relevant measurement.
    """

    outcomes = get_outcome_for_decision(
        decision_id
    )

    if not outcomes:

        return {
            "decision_id": decision_id,
            "status": "not_measured",
            "message": (
                "No outcome has been recorded "
                "for this decision."
            )
        }

    latest_outcome = outcomes[-1]

    effectiveness = latest_outcome.get(
        "effectiveness_percent"
    )

    if effectiveness is None:

        assessment = "unavailable"

    elif effectiveness >= 100:

        assessment = "exceeded_expectation"

    elif effectiveness >= 80:

        assessment = "successful"

    elif effectiveness >= 50:

        assessment = "partially_successful"

    elif effectiveness > 0:

        assessment = "underperformed"

    else:

        assessment = "unsuccessful"

    return {
        "decision_id": decision_id,

        "status": "measured",

        "assessment": assessment,

        "effectiveness_percent": (
            effectiveness
        ),

        "expected_impact": latest_outcome[
            "expected_impact"
        ],

        "actual_impact": latest_outcome[
            "actual_impact"
        ],

        "variance": latest_outcome[
            "variance"
        ],

        "measurement_period": latest_outcome[
            "measurement_period"
        ],
    }


def build_learning_record(
    decision_id: str
):
    """
    Convert the outcome into a simple learning record.

    This becomes the foundation for the later
    decision-learning layer.
    """

    effectiveness = (
        evaluate_decision_effectiveness(
            decision_id
        )
    )

    if (
        effectiveness.get("status")
        != "measured"
    ):
        return effectiveness

    assessment = effectiveness[
        "assessment"
    ]

    if assessment == "exceeded_expectation":
        learning = (
            "The decision produced more impact "
            "than originally estimated."
        )

    elif assessment == "successful":
        learning = (
            "The decision achieved most of the "
            "expected business impact."
        )

    elif assessment == "partially_successful":
        learning = (
            "The decision produced meaningful impact "
            "but did not fully reach expectations."
        )

    elif assessment == "underperformed":
        learning = (
            "The decision produced limited impact "
            "relative to expectations."
        )

    elif assessment == "unsuccessful":
        learning = (
            "The decision did not produce the "
            "expected positive impact."
        )

    else:
        learning = (
            "Decision effectiveness cannot currently "
            "be determined."
        )

    return {
        "decision_id": decision_id,

        "assessment": assessment,

        "effectiveness_percent": (
            effectiveness[
                "effectiveness_percent"
            ]
        ),

        "learning": learning,

        "expected_impact": (
            effectiveness[
                "expected_impact"
            ]
        ),

        "actual_impact": (
            effectiveness[
                "actual_impact"
            ]
        ),

        "variance": (
            effectiveness[
                "variance"
            ]
        ),
    }


def reset_outcomes():
    """
    Clear the V1 outcome store.
    """

    _outcome_store.clear()

    return {
        "status": "reset",
        "total_outcomes": 0,
    }