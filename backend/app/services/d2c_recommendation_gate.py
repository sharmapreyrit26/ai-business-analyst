from __future__ import annotations

from typing import Any

from backend.app.services.serialization import (
    make_json_safe,
)


# ============================================================
# HELPERS
# ============================================================


def _find_claim(
    claim_analysis: dict,
    claim_id: str,
) -> dict | None:

    for claim in claim_analysis.get(
        "claims",
        [],
    ):

        if claim.get(
            "claim_id"
        ) == claim_id:
            return claim

    return None


def _find_hypothesis(
    hypothesis_analysis: dict,
    hypothesis_id: str,
) -> dict | None:

    for item in hypothesis_analysis.get(
        "hypotheses",
        [],
    ):

        if item.get(
            "hypothesis_id"
        ) == hypothesis_id:
            return item

    return None


def _recommendation(
    *,
    recommendation_id: str,
    domain: str,
    action: str,
    readiness: str,
    rationale: str,
    evidence_claim_ids: list[str],
    related_hypothesis_ids: list[str] | None = None,
    guardrail: str | None = None,
    next_step: str | None = None,
):
    """
    Recommendation readiness:

    act_now
        Strong deterministic facts support an operational
        action that does not require causal proof.

    test_first
        Strong signal exists, but causal evidence is not
        sufficient for a broad rollout.

    investigate_first
        A plausible hypothesis exists, but material
        evidence is missing.

    do_not_act
        The proposed action would overreach the available
        evidence or violate a known analytical limitation.
    """

    return {
        "recommendation_id":
            recommendation_id,

        "domain":
            domain,

        "action":
            action,

        "readiness":
            readiness,

        "rationale":
            rationale,

        "evidence_claim_ids":
            evidence_claim_ids,

        "related_hypothesis_ids":
            related_hypothesis_ids
            or [],

        "guardrail":
            guardrail,

        "next_step":
            next_step,
    }


# ============================================================
# REVENUE
# ============================================================


def _build_revenue_recommendations(
    claim_analysis: dict,
    hypothesis_analysis: dict,
):
    recommendations = []

    order_signal = _find_claim(
        claim_analysis,
        "order_volume_signal",
    )

    demand_hypothesis = _find_hypothesis(
        hypothesis_analysis,
        "revenue_demand_weakness",
    )

    acquisition_hypothesis = _find_hypothesis(
        hypothesis_analysis,
        "revenue_acquisition_weakness",
    )

    inventory_hypothesis = _find_hypothesis(
        hypothesis_analysis,
        "revenue_inventory_constraint",
    )


    if order_signal:

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "revenue_investigate_order_decline",

                domain=
                    "revenue",

                action=(
                    "Investigate the order-volume decline "
                    "before changing pricing, acquisition "
                    "or product strategy."
                ),

                readiness=
                    "act_now",

                rationale=(
                    "Order volume is the strongest observed "
                    "commercial signal associated with the "
                    "revenue decline, while the underlying "
                    "cause remains unresolved."
                ),

                evidence_claim_ids=[
                    "revenue_change",
                    "order_change",
                    "order_volume_signal",
                ],

                related_hypothesis_ids=[
                    "revenue_demand_weakness",
                    "revenue_acquisition_weakness",
                    "revenue_inventory_constraint",
                ],

                guardrail=(
                    "Do not present lower demand, weaker "
                    "acquisition or inventory constraints "
                    "as established causes yet."
                ),

                next_step=(
                    "Compare historical traffic, conversion, "
                    "new-customer acquisition and SKU "
                    "availability with the prior period."
                ),
            )
        )


    if (
        demand_hypothesis
        and demand_hypothesis.get(
            "status"
        )
        == "insufficient_evidence"
    ):

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "revenue_test_demand",

                domain=
                    "revenue",

                action=(
                    "Test whether traffic or conversion "
                    "deterioration explains the order decline."
                ),

                readiness=
                    "investigate_first",

                rationale=(
                    "Revenue and orders declined materially, "
                    "but historical traffic and conversion "
                    "trends are missing."
                ),

                evidence_claim_ids=[
                    "revenue_change",
                    "order_change",
                ],

                related_hypothesis_ids=[
                    "revenue_demand_weakness",
                ],

                next_step=
                    demand_hypothesis.get(
                        "test"
                    ),
            )
        )


    if (
        acquisition_hypothesis
        and acquisition_hypothesis.get(
            "status"
        )
        == "insufficient_evidence"
    ):

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "revenue_test_acquisition",

                domain=
                    "customer",

                action=(
                    "Compare new-customer acquisition "
                    "and CAC by channel before changing "
                    "acquisition spend."
                ),

                readiness=
                    "investigate_first",

                rationale=(
                    "Current customer counts are available, "
                    "but historical acquisition trends are "
                    "not sufficient to establish weakening "
                    "acquisition as the cause."
                ),

                evidence_claim_ids=[],

                related_hypothesis_ids=[
                    "revenue_acquisition_weakness",
                ],

                guardrail=(
                    "Do not cut or increase acquisition "
                    "spend solely from the current-period "
                    "customer count."
                ),

                next_step=
                    acquisition_hypothesis.get(
                        "test"
                    ),
            )
        )


    if (
        inventory_hypothesis
        and inventory_hypothesis.get(
            "status"
        )
        == "insufficient_evidence"
    ):

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "revenue_test_inventory_constraint",

                domain=
                    "inventory",

                action=(
                    "Test whether SKU availability "
                    "constrained order capture."
                ),

                readiness=
                    "investigate_first",

                rationale=(
                    "Current reorder risk exists, but "
                    "inventory is a snapshot and does not "
                    "prove that availability constrained "
                    "historical demand."
                ),

                evidence_claim_ids=[
                    "replenishment_risk",
                ],

                related_hypothesis_ids=[
                    "revenue_inventory_constraint",
                ],

                next_step=
                    inventory_hypothesis.get(
                        "test"
                    ),
            )
        )


    return recommendations


# ============================================================
# LOGISTICS
# ============================================================


def _build_logistics_recommendations(
    claim_analysis: dict,
    hypothesis_analysis: dict,
):
    recommendations = []

    cod_signal = _find_claim(
        claim_analysis,
        "cod_rto_signal",
    )

    cod_hypothesis = _find_hypothesis(
        hypothesis_analysis,
        "rto_cod_customer_intent",
    )

    ndr_hypothesis = _find_hypothesis(
        hypothesis_analysis,
        "rto_ndr_execution",
    )

    mix_hypothesis = _find_hypothesis(
        hypothesis_analysis,
        "rto_mix_effect",
    )


    if cod_signal:

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "logistics_test_cod_controls",

                domain=
                    "logistics",

                action=(
                    "Pilot stronger COD confirmation "
                    "controls on a limited high-risk cohort."
                ),

                readiness=
                    "test_first",

                rationale=(
                    "COD shows materially higher RTO than "
                    "prepaid, but the available evidence "
                    "does not prove that payment mode itself "
                    "causes RTO."
                ),

                evidence_claim_ids=[
                    "overall_rto",
                    "cod_rto_signal",
                ],

                related_hypothesis_ids=[
                    "rto_cod_customer_intent",
                ],

                guardrail=(
                    "Use a measured pilot rather than a "
                    "blanket COD restriction."
                ),

                next_step=(
                    "Measure RTO, conversion and cancellation "
                    "impact for verified vs unverified COD."
                ),
            )
        )


    if (
        ndr_hypothesis
        and ndr_hypothesis.get(
            "status"
        )
        == "insufficient_evidence"
    ):

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "logistics_investigate_ndr",

                domain=
                    "logistics",

                action=(
                    "Investigate NDR reason codes and "
                    "delivery-attempt sequences."
                ),

                readiness=
                    "investigate_first",

                rationale=(
                    "NDR is elevated, but aggregate NDR "
                    "does not identify which operational "
                    "failure modes become RTO."
                ),

                evidence_claim_ids=[
                    "delivery_health",
                    "overall_rto",
                ],

                related_hypothesis_ids=[
                    "rto_ndr_execution",
                ],

                next_step=
                    ndr_hypothesis.get(
                        "test"
                    ),
            )
        )


    if (
        mix_hypothesis
        and mix_hypothesis.get(
            "status"
        )
        == "insufficient_evidence"
    ):

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "logistics_investigate_mix",

                domain=
                    "logistics",

                action=(
                    "Decompose RTO by courier and zone "
                    "before reallocating shipping volume."
                ),

                readiness=
                    "investigate_first",

                rationale=(
                    "Current courier and zone performance "
                    "is available, but historical mix shifts "
                    "are not yet measured."
                ),

                evidence_claim_ids=[
                    "overall_rto",
                ],

                related_hypothesis_ids=[
                    "rto_mix_effect",
                ],

                guardrail=(
                    "Do not reallocate courier volume based "
                    "only on current aggregate RTO."
                ),

                next_step=
                    mix_hypothesis.get(
                        "test"
                    ),
            )
        )


    if (
        cod_hypothesis
        and cod_hypothesis.get(
            "status"
        )
        == "insufficient_evidence"
    ):

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "logistics_do_not_block_cod",

                domain=
                    "logistics",

                action=(
                    "Do not broadly disable COD based only "
                    "on the observed RTO gap."
                ),

                readiness=
                    "do_not_act",

                rationale=(
                    "COD is associated with higher RTO, "
                    "but customer-intent and confirmation "
                    "evidence is still missing."
                ),

                evidence_claim_ids=[
                    "cod_rto_signal",
                ],

                related_hypothesis_ids=[
                    "rto_cod_customer_intent",
                ],

                guardrail=(
                    "A blanket COD restriction could reduce "
                    "conversion without proving the underlying "
                    "RTO mechanism."
                ),
            )
        )


    return recommendations


# ============================================================
# INVENTORY
# ============================================================


def _build_inventory_recommendations(
    claim_analysis: dict,
):
    recommendations = []

    trapped = _find_claim(
        claim_analysis,
        "trapped_inventory",
    )

    reorder = _find_claim(
        claim_analysis,
        "replenishment_risk",
    )


    if trapped:

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "inventory_review_overstock",

                domain=
                    "inventory",

                action=(
                    "Prioritize review of the highest "
                    "trapped-inventory positions."
                ),

                readiness=
                    "act_now",

                rationale=(
                    "Excess inventory exposure is directly "
                    "measured by the deterministic inventory "
                    "engine."
                ),

                evidence_claim_ids=[
                    "trapped_inventory",
                ],

                guardrail=(
                    "The trapped-inventory value is a "
                    "heuristic exposure estimate, not "
                    "guaranteed recoverable cash."
                ),

                next_step=(
                    "Rank overstocked SKU-warehouse positions "
                    "by trapped inventory cost and sales velocity."
                ),
            )
        )


    if reorder:

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "inventory_review_replenishment",

                domain=
                    "inventory",

                action=(
                    "Review below-reorder SKU-warehouse "
                    "positions for replenishment."
                ),

                readiness=
                    "act_now",

                rationale=(
                    "Below-reorder positions are directly "
                    "observed in the current inventory snapshot."
                ),

                evidence_claim_ids=[
                    "replenishment_risk",
                ],

                guardrail=(
                    "Potential revenue at risk is an estimate, "
                    "so replenishment quantities should still "
                    "consider demand velocity."
                ),
            )
        )


    return recommendations


# ============================================================
# MARKETING
# ============================================================


def _build_marketing_recommendations(
    claim_analysis: dict,
):
    recommendations = []

    blended_roas = _find_claim(
        claim_analysis,
        "blended_roas",
    )

    if blended_roas:

        recommendations.append(
            _recommendation(
                recommendation_id=
                    "marketing_do_not_scale_from_roas_only",

                domain=
                    "marketing",

                action=(
                    "Do not scale or cut marketing solely "
                    "from aggregate ROAS."
                ),

                readiness=
                    "do_not_act",

                rationale=(
                    "ROAS is an attributed metric and the "
                    "current dataset does not measure "
                    "incrementality."
                ),

                evidence_claim_ids=[
                    "blended_roas",
                    "paid_roas",
                    "customer_acquisition",
                ],

                guardrail=(
                    "Channel investment decisions should "
                    "consider scale, CAC, customer quality, "
                    "conversion and incremental lift."
                ),

                next_step=(
                    "Compare channel-level efficiency, scale "
                    "and customer acquisition before changing "
                    "budget allocation."
                ),
            )
        )


    return recommendations


# ============================================================
# BUSINESS HEALTH
# ============================================================


def _build_business_health_recommendations(
    claim_analysis: dict,
    hypothesis_analysis: dict,
):
    """
    Compose material cross-functional management actions.
    """

    combined = (
        _build_revenue_recommendations(
            claim_analysis,
            hypothesis_analysis,
        )
        + _build_logistics_recommendations(
            claim_analysis,
            hypothesis_analysis,
        )
        + _build_inventory_recommendations(
            claim_analysis,
        )
        + _build_marketing_recommendations(
            claim_analysis,
        )
    )


    preferred_ids = {
        "revenue_investigate_order_decline",
        "logistics_test_cod_controls",
        "logistics_investigate_ndr",
        "inventory_review_overstock",
        "inventory_review_replenishment",
        "marketing_do_not_scale_from_roas_only",
    }


    return [
        item
        for item in combined
        if item.get(
            "recommendation_id"
        )
        in preferred_ids
    ]


# ============================================================
# PUBLIC GATE
# ============================================================


def build_d2c_recommendation_gate(
    *,
    question_type: str,
    claim_analysis: dict,
    hypothesis_analysis: dict,
):
    """
    Convert evidence strength into action readiness.

    This layer does not perform new financial or operational
    calculations. It gates actions using deterministic claims,
    hypothesis status and known analytical limitations.
    """

    if question_type == "revenue":

        recommendations = (
            _build_revenue_recommendations(
                claim_analysis,
                hypothesis_analysis,
            )
        )

    elif question_type in {
        "logistics",
        "delivery",
    }:

        recommendations = (
            _build_logistics_recommendations(
                claim_analysis,
                hypothesis_analysis,
            )
        )

    elif question_type == "inventory":

        recommendations = (
            _build_inventory_recommendations(
                claim_analysis,
            )
        )

    elif question_type == "marketing":

        recommendations = (
            _build_marketing_recommendations(
                claim_analysis,
            )
        )

    elif question_type in {
        "business_health",
        "performance",
        "general_business",
        "general",
    }:

        recommendations = (
            _build_business_health_recommendations(
                claim_analysis,
                hypothesis_analysis,
            )
        )

    else:

        recommendations = []


    readiness_counts = {
        "act_now": 0,
        "test_first": 0,
        "investigate_first": 0,
        "do_not_act": 0,
    }


    for item in recommendations:

        readiness = item.get(
            "readiness"
        )

        if readiness in readiness_counts:

            readiness_counts[
                readiness
            ] += 1


    return make_json_safe({
        "status":
            "complete",

        "question_type":
            question_type,

        "recommendations":
            recommendations,

        "recommendation_count":
            len(
                recommendations
            ),

        "readiness_counts":
            readiness_counts,

        "readiness_definition": {
            "act_now": (
                "Deterministic evidence is sufficient "
                "for an operational action that does not "
                "require causal proof."
            ),

            "test_first": (
                "A strong signal exists, but a measured "
                "pilot should precede broad rollout."
            ),

            "investigate_first": (
                "A plausible explanation exists but "
                "required evidence is still missing."
            ),

            "do_not_act": (
                "The proposed action would overreach "
                "the available evidence or a known "
                "analytical limitation."
            ),
        },

        "guardrail": (
            "Recommendation readiness reflects evidence "
            "strength and analytical limitations. It is "
            "not AI confidence."
        ),
    })
