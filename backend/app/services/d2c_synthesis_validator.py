from __future__ import annotations

from typing import Any


# ============================================================
# CONSTANTS
# ============================================================


FORBIDDEN_INTERNAL_TERMS = [
    "business context",
    "python",
    "gemini",
    "llm",
    "prompt",
    "source code",
]


CAUSAL_OVERCLAIM_PHRASES = [
    "caused by",
    "was caused by",
    "because of",
    "directly caused",
    "proves that",
    "proven cause",
]


# ============================================================
# HELPERS
# ============================================================


def _ids(
    items: list[dict],
    key: str,
):
    return {
        item.get(
            key
        )
        for item
        in items
        if item.get(
            key
        )
    }


# ============================================================
# STRUCTURED SYNTHESIS VALIDATION
# ============================================================


def validate_d2c_synthesis_response(
    response: dict,
    *,
    synthesis_context: dict,
):
    """
    Validate a model-generated synthesis response.

    Expected LLM-owned output:

    {
        "answer": "...",
        "used_claim_ids": [...],
        "used_hypothesis_ids": [...],
        "used_action_ids": [...]
    }

    The IDs create an auditable connection between the
    narrative and governed analytical objects.
    """

    if not isinstance(
        response,
        dict,
    ):
        raise ValueError(
            "Synthesis response must be a dictionary."
        )


    answer = response.get(
        "answer"
    )

    if (
        not isinstance(
            answer,
            str,
        )
        or not answer.strip()
    ):
        raise ValueError(
            "Synthesis response requires a non-empty answer."
        )


    for field in [
        "used_claim_ids",
        "used_hypothesis_ids",
        "used_action_ids",
    ]:

        value = response.get(
            field,
            []
        )

        if not isinstance(
            value,
            list,
        ):
            raise ValueError(
                f"Synthesis field '{field}' must be a list."
            )

        if not all(
            isinstance(
                item,
                str,
            )
            for item
            in value
        ):
            raise ValueError(
                f"Synthesis field '{field}' must contain strings."
            )


    verified_facts = (
        synthesis_context.get(
            "verified_facts",
            [],
        )
    )

    supported_inferences = (
        synthesis_context.get(
            "supported_inferences",
            [],
        )
    )

    unresolved_hypotheses = (
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

    blocked_actions = (
        synthesis_context.get(
            "blocked_actions",
            [],
        )
    )


    allowed_claim_ids = (
        _ids(
            verified_facts,
            "claim_id",
        )
        |
        _ids(
            supported_inferences,
            "claim_id",
        )
    )

    allowed_hypothesis_ids = _ids(
        unresolved_hypotheses,
        "hypothesis_id",
    )

    allowed_action_ids = _ids(
        approved_actions,
        "recommendation_id",
    )

    blocked_action_ids = _ids(
        blocked_actions,
        "recommendation_id",
    )


    used_claim_ids = set(
        response.get(
            "used_claim_ids",
            [],
        )
    )

    used_hypothesis_ids = set(
        response.get(
            "used_hypothesis_ids",
            [],
        )
    )

    used_action_ids = set(
        response.get(
            "used_action_ids",
            [],
        )
    )


    unknown_claims = (
        used_claim_ids
        - allowed_claim_ids
    )

    if unknown_claims:
        raise ValueError(
            "Synthesis referenced unknown claims: "
            + ", ".join(
                sorted(
                    unknown_claims
                )
            )
        )


    unknown_hypotheses = (
        used_hypothesis_ids
        - allowed_hypothesis_ids
    )

    if unknown_hypotheses:
        raise ValueError(
            "Synthesis referenced unknown hypotheses: "
            + ", ".join(
                sorted(
                    unknown_hypotheses
                )
            )
        )


    unknown_actions = (
        used_action_ids
        - allowed_action_ids
    )

    if unknown_actions:
        raise ValueError(
            "Synthesis referenced unapproved actions: "
            + ", ".join(
                sorted(
                    unknown_actions
                )
            )
        )


    leaked_blocked_actions = (
        used_action_ids
        & blocked_action_ids
    )

    if leaked_blocked_actions:
        raise ValueError(
            "Synthesis attempted to recommend blocked actions: "
            + ", ".join(
                sorted(
                    leaked_blocked_actions
                )
            )
        )


    normalized_answer = (
        answer
        .lower()
    )


    for term in FORBIDDEN_INTERNAL_TERMS:

        if term in normalized_answer:

            raise ValueError(
                "Synthesis exposed internal architecture term: "
                f"{term}"
            )


    has_unresolved_hypotheses = bool(
        unresolved_hypotheses
    )

    if has_unresolved_hypotheses:

        for phrase in CAUSAL_OVERCLAIM_PHRASES:

            if phrase in normalized_answer:

                raise ValueError(
                    "Synthesis used causal language while "
                    "material hypotheses remain unresolved: "
                    f"{phrase}"
                )


    return {
        "answer":
            answer.strip(),

        "used_claim_ids":
            list(
                response.get(
                    "used_claim_ids",
                    [],
                )
            ),

        "used_hypothesis_ids":
            list(
                response.get(
                    "used_hypothesis_ids",
                    [],
                )
            ),

        "used_action_ids":
            list(
                response.get(
                    "used_action_ids",
                    [],
                )
            ),

        "validation_status":
            "verified",
    }
