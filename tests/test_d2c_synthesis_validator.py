from backend.app.services.d2c_synthesis_validator import (
    validate_d2c_synthesis_response,
)


def _context():
    return {
        "verified_facts": [
            {
                "claim_id": "revenue_change",
                "claim_type": "fact",
                "confidence": "high",
                "statement": "Revenue declined.",
                "limitation": None,
            }
        ],

        "supported_inferences": [
            {
                "claim_id": "order_volume_signal",
                "claim_type": "inference",
                "confidence": "high",
                "statement": (
                    "Lower order volume is the strongest "
                    "observed commercial signal."
                ),
                "limitation": (
                    "This is association, not causal proof."
                ),
            }
        ],

        "unresolved_hypotheses": [
            {
                "hypothesis_id": "traffic_decline",
                "statement": (
                    "Traffic deterioration may have "
                    "contributed."
                ),
                "status": "insufficient_evidence",
            }
        ],

        "approved_actions": [
            {
                "recommendation_id": "investigate_orders",
                "action": (
                    "Investigate the order-volume decline."
                ),
                "readiness": "act_now",
            }
        ],

        "blocked_actions": [
            {
                "recommendation_id": "block_cod",
                "action": "Disable COD.",
                "readiness": "do_not_act",
            }
        ],
    }


def test_valid_governed_synthesis_passes():

    response = {
        "answer": (
            "Revenue declined. Lower order volume is the "
            "strongest observed signal, while the underlying "
            "cause remains unresolved."
        ),
        "used_claim_ids": [
            "revenue_change",
            "order_volume_signal",
        ],
        "used_hypothesis_ids": [
            "traffic_decline",
        ],
        "used_action_ids": [
            "investigate_orders",
        ],
    }

    result = validate_d2c_synthesis_response(
        response,
        synthesis_context=_context(),
    )

    assert result["validation_status"] == "verified"


def test_unknown_claim_is_rejected():

    response = {
        "answer": "Revenue declined.",
        "used_claim_ids": [
            "invented_claim",
        ],
        "used_hypothesis_ids": [],
        "used_action_ids": [],
    }

    try:

        validate_d2c_synthesis_response(
            response,
            synthesis_context=_context(),
        )

    except ValueError as error:

        assert "unknown claims" in str(error).lower()

    else:

        raise AssertionError(
            "Unknown claim should have been rejected."
        )


def test_unknown_hypothesis_is_rejected():

    response = {
        "answer": (
            "The underlying cause remains unresolved."
        ),
        "used_claim_ids": [],
        "used_hypothesis_ids": [
            "invented_hypothesis",
        ],
        "used_action_ids": [],
    }

    try:

        validate_d2c_synthesis_response(
            response,
            synthesis_context=_context(),
        )

    except ValueError as error:

        assert "unknown hypotheses" in str(error).lower()

    else:

        raise AssertionError(
            "Unknown hypothesis should have been rejected."
        )


def test_blocked_action_is_rejected():

    response = {
        "answer": "Disable COD.",
        "used_claim_ids": [],
        "used_hypothesis_ids": [],
        "used_action_ids": [
            "block_cod",
        ],
    }

    try:

        validate_d2c_synthesis_response(
            response,
            synthesis_context=_context(),
        )

    except ValueError as error:

        message = str(error).lower()

        assert (
            "unapproved actions" in message
            or "blocked actions" in message
        )

    else:

        raise AssertionError(
            "Blocked action should have been rejected."
        )


def test_causal_overclaim_is_rejected():

    response = {
        "answer": (
            "Revenue declined because of lower traffic."
        ),
        "used_claim_ids": [
            "revenue_change",
        ],
        "used_hypothesis_ids": [
            "traffic_decline",
        ],
        "used_action_ids": [],
    }

    try:

        validate_d2c_synthesis_response(
            response,
            synthesis_context=_context(),
        )

    except ValueError as error:

        assert "causal language" in str(error).lower()

    else:

        raise AssertionError(
            "Causal overclaim should have been rejected."
        )


def test_internal_architecture_leak_is_rejected():

    response = {
        "answer": (
            "The LLM reviewed the business context "
            "and found that revenue declined."
        ),
        "used_claim_ids": [
            "revenue_change",
        ],
        "used_hypothesis_ids": [],
        "used_action_ids": [],
    }

    try:

        validate_d2c_synthesis_response(
            response,
            synthesis_context=_context(),
        )

    except ValueError as error:

        assert (
            "internal architecture" in str(error).lower()
        )

    else:

        raise AssertionError(
            "Internal architecture leakage "
            "should have been rejected."
        )
