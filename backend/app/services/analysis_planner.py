from backend.app.services.question_router import (
    classify_question,
)


SUPPORTED_ANALYSES = {
    "revenue_change": {
        "description": (
            "Compare current and previous revenue performance."
        ),
        "dependencies": [
            "revenue"
        ],
    },

    "order_change": {
        "description": (
            "Compare current and previous order volume."
        ),
        "dependencies": [
            "orders"
        ],
    },

    "aov_change": {
        "description": (
            "Compare current and previous average order value."
        ),
        "dependencies": [
            "revenue",
            "orders",
        ],
    },

    "revenue_driver_decomposition": {
        "description": (
            "Decompose revenue movement into order-volume, "
            "AOV and interaction effects."
        ),
        "dependencies": [
            "revenue",
            "orders",
            "aov",
        ],
    },

    "delivery_performance": {
        "description": (
            "Evaluate delivery success and delivered orders."
        ),
        "dependencies": [
            "delivery_rate"
        ],
    },

    "cancellation_performance": {
        "description": (
            "Evaluate cancellation rate and cancelled orders."
        ),
        "dependencies": [
            "cancellation_rate"
        ],
    },

    "historical_trends": {
        "description": (
            "Analyse historical business-performance patterns."
        ),
        "dependencies": [
            "monthly_performance"
        ],
    },

    "root_cause_analysis": {
        "description": (
            "Identify the strongest measurable business driver "
            "and distinguish measured facts from hypotheses."
        ),
        "dependencies": [
            "revenue_driver_decomposition"
        ],
    },

    "hypothesis_analysis": {
        "description": (
            "Generate possible underlying explanations for "
            "the measurable business driver."
        ),
        "dependencies": [
            "root_cause_analysis"
        ],
    },

    "evidence_analysis": {
        "description": (
            "Evaluate available evidence and missing evidence."
        ),
        "dependencies": [
            "root_cause_analysis",
            "hypothesis_analysis",
        ],
    },

    "confidence_analysis": {
        "description": (
            "Calculate confidence in the measurable conclusion."
        ),
        "dependencies": [
            "evidence_analysis"
        ],
    },

    "evidence_sufficiency": {
        "description": (
            "Determine whether available evidence is sufficient "
            "to support a causal conclusion."
        ),
        "dependencies": [
            "confidence_analysis"
        ],
    },

    "opportunity_sizing": {
        "description": (
            "Estimate the potential business value of recovering "
            "part of the identified performance deterioration."
        ),
        "dependencies": [
            "root_cause_analysis"
        ],
    },

    "recommendation_analysis": {
        "description": (
            "Generate evidence-aware business recommendations."
        ),
        "dependencies": [
            "evidence_analysis",
            "confidence_analysis",
            "opportunity_sizing",
        ],
    },

    "business_health": {
        "description": (
            "Evaluate overall commercial and operational "
            "business health."
        ),
        "dependencies": [
            "revenue",
            "orders",
            "delivery_rate",
            "cancellation_rate",
        ],
    },

    "product_analysis": {
        "description": (
            "Analyse product-level revenue, units, orders, "
            "freight burden and revenue concentration."
        ),
        "dependencies": [
            "product_id",
            "price",
            "freight_value",
        ],
    },

    "customer_analysis": {
        "description": (
            "Evaluate available customer analytics and identify "
            "which customer metrics cannot be calculated reliably."
        ),
        "dependencies": [
            "customer_id"
        ],
    },

    "logistics_analysis": {
        "description": (
            "Analyse fulfilment TAT, P90 TAT, promised delivery "
            "performance and logistics data quality."
        ),
        "dependencies": [
            "order_purchase_timestamp",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    },

    "scenario_analysis": {
        "description": (
            "Parse and execute the user's requested business "
            "what-if scenario deterministically."
        ),
        "dependencies": [
            "scenario_parameters"
        ],
    },
}


def _create_step(
    step_number: int,
    analysis: str,
    reason: str,
):
    """
    Create one structured analysis-plan step.
    """

    definition = SUPPORTED_ANALYSES[
        analysis
    ]

    return {
        "step": step_number,
        "analysis": analysis,
        "description": definition[
            "description"
        ],
        "reason": reason,
        "dependencies": definition[
            "dependencies"
        ],
    }


def _build_steps(
    definitions
):
    """
    Convert a sequence of:
        (analysis_name, reason)

    into numbered plan steps.
    """

    return [
        _create_step(
            index,
            analysis,
            reason,
        )
        for index, (
            analysis,
            reason,
        )
        in enumerate(
            definitions,
            start=1,
        )
    ]


def build_analysis_plan(
    question: str,
    month: str = "2018-06",
):
    """
    Build the deterministic analysis plan required
    to answer a ProfitLens business question.

    This function plans the analyses.

    analysis_executor.py is responsible for
    executing these steps.
    """

    question_type = classify_question(
        question
    )

    # ==================================================
    # REVENUE
    # ==================================================

    if question_type == "revenue":

        steps = _build_steps([
            (
                "revenue_change",
                (
                    "Establish whether revenue changed "
                    "and by how much."
                ),
            ),
            (
                "order_change",
                (
                    "Determine whether order volume "
                    "contributed to the revenue movement."
                ),
            ),
            (
                "aov_change",
                (
                    "Determine whether AOV contributed "
                    "to the revenue movement."
                ),
            ),
            (
                "revenue_driver_decomposition",
                (
                    "Measure the financial contribution "
                    "of orders, AOV and interaction."
                ),
            ),
            (
                "root_cause_analysis",
                (
                    "Identify the strongest measurable "
                    "revenue driver."
                ),
            ),
            (
                "hypothesis_analysis",
                (
                    "Generate possible explanations for "
                    "why the measured driver changed."
                ),
            ),
            (
                "evidence_analysis",
                (
                    "Determine which explanations are "
                    "supported by available evidence."
                ),
            ),
            (
                "confidence_analysis",
                (
                    "Calculate confidence in the measurable "
                    "analytical conclusion."
                ),
            ),
            (
                "evidence_sufficiency",
                (
                    "Determine whether the underlying root "
                    "cause can actually be established."
                ),
            ),
            (
                "opportunity_sizing",
                (
                    "Estimate the value of recovering part "
                    "of the deterioration."
                ),
            ),
            (
                "recommendation_analysis",
                (
                    "Generate evidence-aware next actions."
                ),
            ),
        ])

    # ==================================================
    # ORDERS
    # ==================================================

    elif question_type == "orders":

        steps = _build_steps([
            (
                "order_change",
                "Establish how order volume changed.",
            ),
            (
                "historical_trends",
                (
                    "Determine whether the order movement "
                    "is unusual or recurring."
                ),
            ),
            (
                "root_cause_analysis",
                (
                    "Identify measurable business drivers "
                    "related to order performance."
                ),
            ),
            (
                "hypothesis_analysis",
                (
                    "Generate possible underlying causes "
                    "without treating them as facts."
                ),
            ),
            (
                "evidence_analysis",
                (
                    "Determine what evidence exists and "
                    "what data is missing."
                ),
            ),
            (
                "confidence_analysis",
                (
                    "Calculate confidence in the available "
                    "business explanation."
                ),
            ),
            (
                "evidence_sufficiency",
                (
                    "Determine whether the underlying "
                    "cause can be established."
                ),
            ),
        ])

    # ==================================================
    # DELIVERY
    # ==================================================

    elif question_type == "delivery":

        steps = _build_steps([
            (
                "delivery_performance",
                (
                    "Measure delivery performance for "
                    "the requested period."
                ),
            ),
            (
                "historical_trends",
                (
                    "Compare delivery performance with "
                    "historical periods."
                ),
            ),
        ])

    # ==================================================
    # CANCELLATION
    # ==================================================

    elif question_type == "cancellation":

        steps = _build_steps([
            (
                "cancellation_performance",
                (
                    "Measure cancellation performance "
                    "for the requested period."
                ),
            ),
            (
                "historical_trends",
                (
                    "Determine whether cancellation "
                    "performance is unusual."
                ),
            ),
            (
                "evidence_analysis",
                (
                    "Determine whether available evidence "
                    "supports a causal explanation."
                ),
            ),
        ])

    # ==================================================
    # PRODUCT
    # ==================================================

    elif question_type == "product":

        steps = _build_steps([
            (
                "product_analysis",
                (
                    "Analyse product-level commercial "
                    "performance."
                ),
            ),
        ])

    # ==================================================
    # CUSTOMER
    # ==================================================

    elif question_type == "customer":

        steps = _build_steps([
            (
                "customer_analysis",
                (
                    "Evaluate available customer data and "
                    "determine which customer metrics can "
                    "be calculated reliably."
                ),
            ),
        ])

    # ==================================================
    # LOGISTICS
    # ==================================================

    elif question_type == "logistics":

        steps = _build_steps([
            (
                "logistics_analysis",
                (
                    "Analyse fulfilment TAT, P90 TAT, "
                    "late delivery and promised-delivery "
                    "performance."
                ),
            ),
        ])

    # ==================================================
    # SCENARIO
    # ==================================================

    elif question_type == "scenario":

        steps = _build_steps([
            (
                "scenario_analysis",
                (
                    "Parse the user's requested scenario "
                    "and execute the exact deterministic "
                    "what-if calculation."
                ),
            ),
        ])

    # ==================================================
    # TRENDS
    # ==================================================

    elif question_type == "trends":

        steps = _build_steps([
            (
                "historical_trends",
                (
                    "Identify meaningful historical "
                    "business patterns."
                ),
            ),
            (
                "revenue_change",
                "Review significant revenue movements.",
            ),
            (
                "order_change",
                "Review significant order movements.",
            ),
            (
                "delivery_performance",
                "Review delivery-performance trends.",
            ),
            (
                "cancellation_performance",
                "Review cancellation patterns.",
            ),
        ])

    # ==================================================
    # PERFORMANCE
    # ==================================================

    elif question_type == "performance":

        steps = _build_steps([
            (
                "historical_trends",
                "Compare performance across periods.",
            ),
            (
                "revenue_change",
                "Evaluate commercial performance.",
            ),
            (
                "order_change",
                "Evaluate demand performance.",
            ),
            (
                "delivery_performance",
                "Evaluate delivery performance.",
            ),
            (
                "cancellation_performance",
                "Evaluate cancellation performance.",
            ),
        ])

    # ==================================================
    # BUSINESS HEALTH
    # ==================================================

    elif question_type == "business_health":

        steps = _build_steps([
            (
                "business_health",
                (
                    "Evaluate overall commercial and "
                    "operational health."
                ),
            ),
            (
                "revenue_driver_decomposition",
                (
                    "Identify the largest measurable "
                    "commercial drivers."
                ),
            ),
            (
                "root_cause_analysis",
                (
                    "Investigate the most important "
                    "measurable business problem."
                ),
            ),
            (
                "hypothesis_analysis",
                (
                    "Generate possible underlying causes."
                ),
            ),
            (
                "evidence_analysis",
                (
                    "Determine which conclusions are "
                    "supported by evidence."
                ),
            ),
            (
                "confidence_analysis",
                (
                    "Calculate confidence in the "
                    "management conclusions."
                ),
            ),
            (
                "evidence_sufficiency",
                (
                    "Identify where the system must say "
                    "insufficient evidence."
                ),
            ),
            (
                "opportunity_sizing",
                (
                    "Estimate the potential value of "
                    "addressing major issues."
                ),
            ),
            (
                "recommendation_analysis",
                (
                    "Generate prioritized evidence-aware "
                    "actions."
                ),
            ),
        ])

    # ==================================================
    # GENERAL BUSINESS
    # ==================================================

    elif question_type == "general_business":

        steps = _build_steps([
            (
                "business_health",
                (
                    "Establish the relevant overall "
                    "business context."
                ),
            ),
            (
                "revenue_change",
                "Evaluate revenue performance.",
            ),
            (
                "order_change",
                "Evaluate order performance.",
            ),
            (
                "aov_change",
                "Evaluate average order value.",
            ),
            (
                "delivery_performance",
                "Evaluate delivery performance.",
            ),
            (
                "cancellation_performance",
                "Evaluate cancellation performance.",
            ),
            (
                "revenue_driver_decomposition",
                (
                    "Measure the commercial contribution "
                    "of orders and AOV."
                ),
            ),
            (
                "root_cause_analysis",
                (
                    "Identify the strongest measurable "
                    "business driver."
                ),
            ),
            (
                "hypothesis_analysis",
                (
                    "Generate possible underlying "
                    "business explanations."
                ),
            ),
            (
                "evidence_analysis",
                (
                    "Separate measured evidence from "
                    "unsupported hypotheses."
                ),
            ),
            (
                "confidence_analysis",
                (
                    "Calculate confidence in the "
                    "business conclusion."
                ),
            ),
            (
                "evidence_sufficiency",
                (
                    "Determine what the system can and "
                    "cannot establish."
                ),
            ),
            (
                "opportunity_sizing",
                (
                    "Estimate the value of addressing "
                    "the measurable issue."
                ),
            ),
            (
                "recommendation_analysis",
                (
                    "Generate evidence-aware actions."
                ),
            ),
        ])

    # ==================================================
    # GENERAL FALLBACK
    # ==================================================

    else:

        steps = _build_steps([
            (
                "business_health",
                (
                    "Establish general business context "
                    "relevant to the question."
                ),
            ),
        ])

    return {
        "question": question,
        "month": month,
        "question_type": question_type,
        "total_steps": len(
            steps
        ),
        "analysis_plan": steps,
    }