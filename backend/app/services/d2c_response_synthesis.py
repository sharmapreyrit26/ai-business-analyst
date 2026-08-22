from __future__ import annotations

from typing import Any

from backend.app.services.serialization import (
    make_json_safe,
)


# ============================================================
# HELPERS
# ============================================================


def _claims_by_type(
    claim_analysis: dict,
    claim_type: str,
):
    return [
        claim
        for claim
        in claim_analysis.get(
            "claims",
            [],
        )
        if claim.get(
            "claim_type"
        ) == claim_type
    ]


def _unresolved_hypotheses(
    hypothesis_analysis: dict,
):
    return [
        item
        for item
        in hypothesis_analysis.get(
            "hypotheses",
            [],
        )
        if item.get(
            "status"
        )
        != "supported"
    ]


def _actions_by_readiness(
    recommendation_analysis: dict,
    readiness: str,
):
    return [
        item
        for item
        in recommendation_analysis.get(
            "recommendations",
            [],
        )
        if item.get(
            "readiness"
        ) == readiness
    ]


def _claim_projection(
    claim: dict,
):
    return {
        "claim_id":
            claim.get(
                "claim_id"
            ),

        "claim_type":
            claim.get(
                "claim_type"
            ),

        "confidence":
            claim.get(
                "confidence"
            ),

        "statement":
            claim.get(
                "statement"
            ),

        "limitation":
            claim.get(
                "limitation"
            ),
    }


def _hypothesis_projection(
    hypothesis: dict,
):
    return {
        "hypothesis_id":
            hypothesis.get(
                "hypothesis_id"
            ),

        "domain":
            hypothesis.get(
                "domain"
            ),

        "statement":
            hypothesis.get(
                "statement"
            ),

        "status":
            hypothesis.get(
                "status"
            ),

        "confidence":
            hypothesis.get(
                "confidence"
            ),

        "missing_evidence":
            hypothesis.get(
                "missing_evidence",
                [],
            ),

        "test":
            hypothesis.get(
                "test"
            ),

        "guardrail":
            hypothesis.get(
                "guardrail"
            ),
    }


def _action_projection(
    action: dict,
):
    return {
        "recommendation_id":
            action.get(
                "recommendation_id"
            ),

        "domain":
            action.get(
                "domain"
            ),

        "action":
            action.get(
                "action"
            ),

        "readiness":
            action.get(
                "readiness"
            ),

        "rationale":
            action.get(
                "rationale"
            ),

        "guardrail":
            action.get(
                "guardrail"
            ),

        "next_step":
            action.get(
                "next_step"
            ),
    }


# ============================================================
# SYNTHESIS CONTEXT
# ============================================================


def build_d2c_synthesis_context(
    *,
    question: str,
    month: str,
    question_type: str,
    claim_analysis: dict,
    hypothesis_analysis: dict,
    recommendation_analysis: dict,
):
    """
    Build the governed context used to synthesize the
    final Ask ProfitLens executive answer.

    This layer performs no new financial calculation.

    It explicitly separates:
    - verified facts
    - supported inferences
    - unresolved hypotheses
    - evidence gaps
    - approved actions
    - blocked actions

    The LLM may explain this package but must not expand
    beyond it.
    """

    facts = _claims_by_type(
        claim_analysis,
        "fact",
    )

    inferences = _claims_by_type(
        claim_analysis,
        "inference",
    )

    hypotheses = (
        _unresolved_hypotheses(
            hypothesis_analysis
        )
    )


    act_now = (
        _actions_by_readiness(
            recommendation_analysis,
            "act_now",
        )
    )

    test_first = (
        _actions_by_readiness(
            recommendation_analysis,
            "test_first",
        )
    )

    investigate_first = (
        _actions_by_readiness(
            recommendation_analysis,
            "investigate_first",
        )
    )

    do_not_act = (
        _actions_by_readiness(
            recommendation_analysis,
            "do_not_act",
        )
    )


    missing_evidence = []

    seen_evidence_ids = set()

    for hypothesis in hypotheses:

        for item in hypothesis.get(
            "missing_evidence",
            [],
        ):

            evidence_id = item.get(
                "evidence_id"
            )

            if (
                evidence_id
                and evidence_id
                not in seen_evidence_ids
            ):

                seen_evidence_ids.add(
                    evidence_id
                )

                missing_evidence.append(
                    item
                )


    strongest_inference = (
        _claim_projection(
            inferences[0]
        )
        if inferences
        else None
    )


    # Preserve the authoritative ordering produced by the
    # recommendation gate.
    #
    # Readiness is metadata about how an action should be
    # executed; it must not silently re-rank recommendations.

    ordered_recommendations = (
        recommendation_analysis.get(
            "recommendations",
            [],
        )
    )

    approved_actions = [
        item
        for item
        in ordered_recommendations
        if item.get(
            "readiness"
        )
        in {
            "act_now",
            "test_first",
            "investigate_first",
        }
    ]

    blocked_actions = [
        item
        for item
        in ordered_recommendations
        if item.get(
            "readiness"
        )
        == "do_not_act"
    ]


    return make_json_safe({
        "question":
            question,

        "month":
            month,

        "question_type":
            question_type,

        "verified_facts": [
            _claim_projection(
                claim
            )
            for claim
            in facts
        ],

        "supported_inferences": [
            _claim_projection(
                claim
            )
            for claim
            in inferences
        ],

        "strongest_supported_signal":
            strongest_inference,

        "unresolved_hypotheses": [
            _hypothesis_projection(
                item
            )
            for item
            in hypotheses
        ],

        "missing_evidence":
            missing_evidence,

        "approved_actions": [
            _action_projection(
                item
            )
            for item
            in approved_actions
        ],

        "blocked_actions": [
            _action_projection(
                item
            )
            for item
            in blocked_actions
        ],

        "action_readiness_counts":
            recommendation_analysis.get(
                "readiness_counts",
                {},
            ),

        "rules": {
            "facts_are_authoritative":
                True,

            "inferences_are_not_causal_proof":
                True,

            "unresolved_hypotheses_are_not_facts":
                True,

            "blocked_actions_must_not_be_recommended":
                True,

            "llm_may_create_new_business_facts":
                False,

            "llm_may_create_new_management_actions":
                False,
        },
    })


# ============================================================
# DETERMINISTIC RESPONSE PROJECTION
# ============================================================


def build_d2c_response_projection(
    *,
    synthesis_context: dict,
):
    """
    Build deterministic response fields that should not
    be owned by the LLM.

    The LLM may write the executive answer text, but:
    - evidence comes from governed facts
    - likely_driver comes from governed inference
    - recommended_actions come from recommendation gate
    """

    facts = synthesis_context.get(
        "verified_facts",
        [],
    )

    strongest_signal = (
        synthesis_context.get(
            "strongest_supported_signal"
        )
    )

    approved_actions = (
        synthesis_context.get(
            "approved_actions",
            [],
        )
    )


    evidence = [
        item.get(
            "statement"
        )
        for item
        in facts
        if item.get(
            "statement"
        )
    ]


    likely_driver = (
        strongest_signal.get(
            "statement"
        )
        if (
            isinstance(
                strongest_signal,
                dict,
            )
            and strongest_signal.get(
                "statement"
            )
        )
        else "Not established"
    )


    recommended_actions = [
        item.get(
            "action"
        )
        for item
        in approved_actions
        if item.get(
            "action"
        )
    ]


    return make_json_safe({
        "evidence":
            evidence,

        "likely_driver":
            likely_driver,

        "recommended_actions":
            recommended_actions,
    })


# ============================================================
# DETERMINISTIC SYNTHESIS FALLBACK
# ============================================================


def build_deterministic_synthesis_answer(
    *,
    synthesis_context: dict,
):
    """
    Produce a safe executive answer when AI synthesis is
    unavailable or fails validation.

    This intentionally prioritizes correctness over prose.
    """

    facts = synthesis_context.get(
        "verified_facts",
        [],
    )

    strongest_signal = (
        synthesis_context.get(
            "strongest_supported_signal"
        )
    )

    unresolved = (
        synthesis_context.get(
            "unresolved_hypotheses",
            [],
        )
    )

    approved_actions = (
        synthesis_context.get(
            "approved_actions",
            [],
        )
    )


    parts = []


    if facts:

        fact_statements = [
            item.get(
                "statement"
            )
            for item
            in facts[:3]
            if item.get(
                "statement"
            )
        ]

        if fact_statements:

            parts.append(
                " ".join(
                    fact_statements
                )
            )


    if (
        isinstance(
            strongest_signal,
            dict,
        )
        and strongest_signal.get(
            "statement"
        )
    ):

        parts.append(
            strongest_signal[
                "statement"
            ]
        )


    if unresolved:

        parts.append(
            (
                "The underlying cause is not fully "
                "established because material evidence "
                "is still missing."
            )
        )


    if approved_actions:

        first_action = (
            approved_actions[0]
            .get(
                "action"
            )
        )

        if first_action:

            parts.append(
                (
                    "The next evidence-supported step is: "
                    f"{first_action}"
                )
            )


    if not parts:

        return (
            "ProfitLens could not establish a sufficiently "
            "supported conclusion from the available data."
        )


    return " ".join(
        parts
    )
