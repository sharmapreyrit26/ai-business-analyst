from copy import deepcopy
from datetime import datetime
from uuid import uuid4


# --------------------------------------------------
# V1 IN-MEMORY DECISION STORE
#
# Later this should move to PostgreSQL and be scoped
# by business / organization / user.
# --------------------------------------------------

_decision_store = []


def _generate_decision_id() -> str:
    """
    Generate a unique decision identifier.
    """

    return str(uuid4())


def record_decision(
    decision: str,
    reason: str,
    expected_impact: dict = None,
    related_metric: str = None,
    related_period: str = None,
    source_recommendation_id: str = None,
    owner: str = None,
    status: str = "planned",
):
    """
    Record a business decision.

    Example:

    Decision:
        Investigate lost order volume.

    Reason:
        Order volume was the primary revenue driver.

    Expected impact:
        {
            "metric": "revenue",
            "estimated_value": 48662.46
        }
    """

    decision_record = {
        "decision_id": _generate_decision_id(),

        "decision": decision,

        "reason": reason,

        "related_metric": related_metric,

        "related_period": related_period,

        "source_recommendation_id": (
            source_recommendation_id
        ),

        "expected_impact": (
            expected_impact
            if expected_impact is not None
            else {}
        ),

        "owner": owner,

        "status": status,

        "created_at": (
            datetime.utcnow()
            .isoformat()
        ),

        "implemented_at": None,

        "completed_at": None,

        "notes": [],
    }

    _decision_store.append(
        decision_record
    )

    return deepcopy(
        decision_record
    )


def get_decisions():
    """
    Return all stored decisions.
    """

    return deepcopy(
        _decision_store
    )


def get_decision(
    decision_id: str
):
    """
    Return one decision by ID.
    """

    for decision in _decision_store:

        if (
            decision["decision_id"]
            == decision_id
        ):
            return deepcopy(
                decision
            )

    return None


def update_decision_status(
    decision_id: str,
    status: str
):
    """
    Update the lifecycle status of a decision.

    Supported examples:
    - planned
    - approved
    - implemented
    - completed
    - rejected
    - cancelled
    """

    allowed_statuses = {
        "planned",
        "approved",
        "implemented",
        "completed",
        "rejected",
        "cancelled",
    }

    if status not in allowed_statuses:

        raise ValueError(
            f"Unsupported decision status: {status}"
        )

    for decision in _decision_store:

        if (
            decision["decision_id"]
            == decision_id
        ):

            decision["status"] = status

            if status == "implemented":
                decision[
                    "implemented_at"
                ] = (
                    datetime.utcnow()
                    .isoformat()
                )

            if status == "completed":
                decision[
                    "completed_at"
                ] = (
                    datetime.utcnow()
                    .isoformat()
                )

            return deepcopy(
                decision
            )

    raise ValueError(
        f"Decision not found: {decision_id}"
    )


def add_decision_note(
    decision_id: str,
    note: str
):
    """
    Add a note to a decision.
    """

    for decision in _decision_store:

        if (
            decision["decision_id"]
            == decision_id
        ):

            decision["notes"].append({
                "note": note,
                "created_at": (
                    datetime.utcnow()
                    .isoformat()
                )
            })

            return deepcopy(
                decision
            )

    raise ValueError(
        f"Decision not found: {decision_id}"
    )


def get_decisions_by_status(
    status: str
):
    """
    Return decisions filtered by status.
    """

    decisions = [
        decision
        for decision in _decision_store
        if decision[
            "status"
        ] == status
    ]

    return deepcopy(
        decisions
    )


def reset_decision_memory():
    """
    Clear the V1 in-memory decision store.

    Mainly useful for tests.
    """

    _decision_store.clear()

    return {
        "status": "reset",
        "total_decisions": 0,
    }