from backend.app.services.question_router import (
    classify_question,
)

from backend.app.services.analysis_executor import (
    execute_analysis_plan,
)

from backend.app.services.llm_service import (
    ask_business_analyst,
)


# ============================================================
# EXECUTION HELPERS
# ============================================================


def _find_execution_result(
    executed_analysis: dict,
    analysis_name: str,
):
    """
    Return the result of one executed analysis step.
    """

    for item in executed_analysis.get(
        "execution_results",
        []
    ):
        if item.get("analysis") == analysis_name:
            return item.get("result")

    return None


def _get_recommendation_actions(
    executed_analysis: dict,
):
    """
    Extract recommendation actions from the
    recommendation engine response.
    """

    recommendations = _find_execution_result(
        executed_analysis,
        "recommendation_analysis",
    )

    if not recommendations:
        return []

    revenue_group = (
        recommendations
        .get(
            "recommendation_groups",
            {}
        )
        .get(
            "revenue",
            {}
        )
    )

    return [
        item["action"]
        for item in revenue_group.get(
            "recommendations",
            []
        )
        if item.get("action")
    ]


# ============================================================
# COMPACT LLM CONTEXT
# ============================================================


CONTEXT_ANALYSES = {
    "revenue": [
        "revenue_change",
        "order_change",
        "aov_change",
        "revenue_driver_decomposition",
        "root_cause_analysis",
        "confidence_analysis",
        "evidence_sufficiency",
        "opportunity_sizing",
        "recommendation_analysis",
    ],

    "orders": [
        "order_change",
        "historical_trends",
        "root_cause_analysis",
        "evidence_sufficiency",
    ],

    "delivery": [
        "delivery_performance",
        "historical_trends",
    ],

    "cancellation": [
        "cancellation_performance",
        "historical_trends",
    ],

    "product": [
        "product_analysis",
    ],

    "customer": [
        "customer_analysis",
    ],

    "logistics": [
        "logistics_analysis",
    ],

    "scenario": [
        "scenario_analysis",
    ],

    "trends": [
        "historical_trends",
        "revenue_change",
        "order_change",
        "delivery_performance",
        "cancellation_performance",
    ],

    "performance": [
        "historical_trends",
        "revenue_change",
        "order_change",
        "delivery_performance",
        "cancellation_performance",
    ],

    "business_health": [
        "business_health",
        "revenue_driver_decomposition",
        "root_cause_analysis",
        "confidence_analysis",
        "evidence_sufficiency",
        "opportunity_sizing",
        "recommendation_analysis",
    ],

    "general_business": [
        "business_health",
        "revenue_change",
        "order_change",
        "aov_change",
        "delivery_performance",
        "cancellation_performance",
        "root_cause_analysis",
        "confidence_analysis",
        "evidence_sufficiency",
        "opportunity_sizing",
        "recommendation_analysis",
    ],
}


def _shrink_value(
    value,
    max_list_items: int = 12,
):
    """
    Reduce large analytical structures before
    passing them to the LLM.

    The deterministic result remains untouched
    inside analysis_executor.py.

    This function only creates a smaller AI context.
    """

    if isinstance(value, list):

        return [
            _shrink_value(
                item,
                max_list_items,
            )
            for item in value[
                :max_list_items
            ]
        ]

    if isinstance(value, dict):

        return {
            key: _shrink_value(
                item,
                max_list_items,
            )
            for key, item in value.items()
        }

    return value


def _build_llm_context(
    question_type: str,
    month: str,
    executed_analysis: dict,
):
    """
    Build a compact AI context from analyses that
    have already been executed.

    No analytical engine is called from here.
    """

    allowed_analyses = CONTEXT_ANALYSES.get(
        question_type,
        []
    )

    results = {}

    for item in executed_analysis.get(
        "execution_results",
        []
    ):

        analysis_name = item.get(
            "analysis"
        )

        if (
            allowed_analyses
            and analysis_name not in allowed_analyses
        ):
            continue

        if (
            item.get("execution_status")
            != "complete"
        ):
            continue

        results[
            analysis_name
        ] = _shrink_value(
            item.get("result")
        )

    return {
        "question_type": question_type,

        "month": month,

        "analysis_execution": {
            "total_steps": (
                executed_analysis.get(
                    "total_steps",
                    0
                )
            ),

            "successful_steps": (
                executed_analysis.get(
                    "successful_steps",
                    0
                )
            ),

            "failed_steps": (
                executed_analysis.get(
                    "failed_steps",
                    0
                )
            ),
        },

        "analysis_results": results,

        "instructions": (
            "All calculations have already been performed "
            "deterministically. Use only these results. "
            "Do not invent missing metrics or causal claims."
        ),
    }


# ============================================================
# SCENARIO FALLBACK
# ============================================================


def _scenario_fallback(
    executed_analysis: dict,
):
    """
    Build deterministic scenario answer.
    """

    execution = _find_execution_result(
        executed_analysis,
        "scenario_analysis",
    )

    if not execution:

        return {
            "answer": (
                "The requested scenario could not "
                "be executed."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    if (
        execution.get("status")
        != "complete"
    ):

        parser_result = execution.get(
            "parser_result",
            {}
        )

        missing = parser_result.get(
            "missing",
            []
        )

        if missing:

            answer = (
                "The scenario is missing required "
                f"parameter(s): {', '.join(missing)}."
            )

        else:

            answer = parser_result.get(
                "message",
                (
                    "The requested scenario is not "
                    "currently supported."
                )
            )

        return {
            "answer": answer,
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    result = execution[
        "scenario_result"
    ]

    scenario_type = execution.get(
        "scenario_type"
    )

    # --------------------------------------------------
    # ORDER RECOVERY
    # --------------------------------------------------

    if scenario_type == "order_recovery":

        difference = result["difference"]

        scenario_result = result[
            "scenario_result"
        ]

        recovery = result[
            "assumptions"
        ]["recovery_percent"]

        return {
            "answer": (
                f"Recovering {recovery:.2f}% of lost "
                f"orders would add approximately "
                f"{difference['additional_orders']:.2f} "
                f"orders and increase revenue by "
                f"{difference['incremental_revenue']:.2f}."
            ),

            "evidence": [
                (
                    f"Current orders: "
                    f"{result['current']['orders']}."
                ),
                (
                    f"Scenario orders: "
                    f"{scenario_result['orders']:.2f}."
                ),
                (
                    f"Current revenue: "
                    f"{result['current']['revenue']:.2f}."
                ),
                (
                    f"Scenario revenue: "
                    f"{scenario_result['revenue']:.2f}."
                ),
            ],

            "likely_driver": "Not applicable",

            "recommended_actions": [],
        }

    # --------------------------------------------------
    # AOV CHANGE
    # --------------------------------------------------

    if scenario_type == "aov_change":

        difference = result[
            "difference"
        ]

        scenario_result = result[
            "scenario_result"
        ]

        change = result[
            "assumptions"
        ]["aov_change_percent"]

        return {
            "answer": (
                f"If AOV changes by {change:.2f}%, "
                f"scenario AOV becomes "
                f"{scenario_result['aov']:.2f} and "
                f"revenue becomes "
                f"{scenario_result['revenue']:.2f}. "
                f"The incremental revenue impact is "
                f"{difference['incremental_revenue']:.2f}."
            ),

            "evidence": [
                (
                    f"Current AOV: "
                    f"{result['current']['aov']:.2f}."
                ),
                (
                    f"Scenario AOV: "
                    f"{scenario_result['aov']:.2f}."
                ),
                (
                    f"Orders held constant at "
                    f"{result['current']['orders']}."
                ),
            ],

            "likely_driver": "Not applicable",

            "recommended_actions": [],
        }

    # --------------------------------------------------
    # COMBINED
    # --------------------------------------------------

    if scenario_type == "combined_change":

        assumptions = result[
            "assumptions"
        ]

        scenario_result = result[
            "scenario_result"
        ]

        difference = result[
            "difference"
        ]

        return {
            "answer": (
                f"If orders change by "
                f"{assumptions['order_change_percent']:.2f}% "
                f"and AOV changes by "
                f"{assumptions['aov_change_percent']:.2f}%, "
                f"estimated revenue becomes "
                f"{scenario_result['revenue']:.2f}, "
                f"an incremental change of "
                f"{difference['incremental_revenue']:.2f}."
            ),

            "evidence": [
                (
                    f"Scenario orders: "
                    f"{scenario_result['orders']:.2f}."
                ),
                (
                    f"Scenario AOV: "
                    f"{scenario_result['aov']:.2f}."
                ),
            ],

            "likely_driver": "Not applicable",

            "recommended_actions": [],
        }

    return {
        "answer": (
            "The scenario was executed successfully."
        ),
        "evidence": [],
        "likely_driver": "Not applicable",
        "recommended_actions": [],
    }


# ============================================================
# DOMAIN FALLBACK
# ============================================================


def _product_fallback(
    executed_analysis: dict,
):
    result = _find_execution_result(
        executed_analysis,
        "product_analysis",
    )

    if not result:

        return {
            "answer": (
                "Product analytics are unavailable "
                "for the selected period."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    top_products = result.get(
        "top_products",
        []
    )

    if not top_products:

        return {
            "answer": (
                "No product records were available "
                "for the selected period."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    product = top_products[0]

    return {
        "answer": (
            f"The highest-revenue product was "
            f"{product['product_id']}, generating "
            f"{product['revenue']:.2f}."
        ),

        "evidence": [
            (
                f"Units sold: "
                f"{product['units_sold']}."
            ),
            (
                f"Orders: "
                f"{product['orders']}."
            ),
            (
                f"Revenue share: "
                f"{product['revenue_share_percent']:.2f}%."
            ),
        ],

        "likely_driver": (
            "Product revenue contribution"
        ),

        "recommended_actions": [],
    }


def _customer_fallback(
    executed_analysis: dict,
):
    result = _find_execution_result(
        executed_analysis,
        "customer_analysis",
    )

    if not result:

        return {
            "answer": (
                "Customer analytics are unavailable."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    repeat_purchase = (
        result
        .get(
            "unavailable_analysis",
            {}
        )
        .get(
            "repeat_purchase",
            {}
        )
    )

    if (
        repeat_purchase.get("status")
        == "insufficient_data"
    ):

        return {
            "answer": (
                "Reliable repeat-purchase and retention "
                "metrics cannot currently be calculated "
                "because a persistent customer identifier "
                "is not available."
            ),

            "evidence": [
                repeat_purchase.get(
                    "reason",
                    (
                        "Persistent customer identity "
                        "data is unavailable."
                    )
                )
            ],

            "likely_driver": (
                "Insufficient customer identity data"
            ),

            "recommended_actions": [
                (
                    "Connect persistent customer identity "
                    "data before calculating retention, "
                    "cohorts or LTV."
                )
            ],
        }

    return {
        "answer": (
            "Customer analytics are partially available."
        ),
        "evidence": [],
        "likely_driver": "Not applicable",
        "recommended_actions": [],
    }


def _logistics_fallback(
    executed_analysis: dict,
):
    result = _find_execution_result(
        executed_analysis,
        "logistics_analysis",
    )

    if not result:

        return {
            "answer": (
                "Logistics analytics are unavailable."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    purchase_to_delivery = (
        result
        .get(
            "fulfilment_tat",
            {}
        )
        .get(
            "purchase_to_delivery",
            {}
        )
    )

    promise = result.get(
        "delivery_promise",
        {}
    )

    p90 = purchase_to_delivery.get(
        "p90"
    )

    average = purchase_to_delivery.get(
        "average"
    )

    evidence = []

    if average is not None:
        evidence.append(
            f"Average delivery TAT: "
            f"{average:.2f} days."
        )

    if p90 is not None:
        evidence.append(
            f"P90 delivery TAT: "
            f"{p90:.2f} days."
        )

    if (
        promise.get(
            "on_time_delivery_percent"
        )
        is not None
    ):
        evidence.append(
            f"On-time delivery rate: "
            f"{promise['on_time_delivery_percent']:.2f}%."
        )

    if p90 is not None:

        answer = (
            f"P90 purchase-to-delivery TAT was "
            f"{p90:.2f} days."
        )

    elif average is not None:

        answer = (
            f"Average purchase-to-delivery TAT was "
            f"{average:.2f} days."
        )

    else:

        answer = (
            "Delivery TAT could not be calculated."
        )

    return {
        "answer": answer,
        "evidence": evidence,
        "likely_driver": "Not applicable",
        "recommended_actions": [],
    }


# ============================================================
# KPI FALLBACK
# ============================================================


def _standard_fallback(
    question_type: str,
    month: str,
    executed_analysis: dict,
):
    """
    Deterministic fallback for revenue, orders,
    delivery, cancellation and broader questions.
    """

    if question_type == "revenue":

        revenue = _find_execution_result(
            executed_analysis,
            "revenue_change",
        )

        root_cause = _find_execution_result(
            executed_analysis,
            "root_cause_analysis",
        )

        if revenue:

            return {
                "answer": (
                    f"Revenue changed by "
                    f"{revenue['revenue_change_percent']:.2f}% "
                    f"in {month}, from "
                    f"{revenue['previous_revenue']:.2f} to "
                    f"{revenue['revenue']:.2f}."
                ),

                "evidence": [
                    (
                        f"Orders changed by "
                        f"{revenue['order_change_percent']:.2f}%."
                    ),
                    (
                        f"AOV changed by "
                        f"{revenue['aov_change_percent']:.2f}%."
                    ),
                ],

                "likely_driver": (
                    root_cause.get(
                        "primary_explanation",
                        "Not available"
                    )
                    if root_cause
                    else "Not available"
                ),

                "recommended_actions": (
                    _get_recommendation_actions(
                        executed_analysis
                    )
                ),
            }

    if question_type == "orders":

        result = _find_execution_result(
            executed_analysis,
            "order_change",
        )

        if result:

            orders = result.get(
                "orders",
                {}
            )

            return {
                "answer": (
                    f"Orders were "
                    f"{orders.get('value')} in {month}, "
                    f"a change of "
                    f"{orders.get('growth_percent')}% "
                    f"from the previous period."
                ),
                "evidence": [
                    (
                        f"Previous orders: "
                        f"{orders.get('previous_value')}."
                    )
                ],
                "likely_driver": "Not established",
                "recommended_actions": [],
            }

    if question_type == "delivery":

        result = _find_execution_result(
            executed_analysis,
            "delivery_performance",
        )

        if result:

            delivery = result.get(
                "delivery",
                {}
            )

            return {
                "answer": (
                    f"Delivery rate was "
                    f"{delivery.get('rate_percent')}% "
                    f"in {month}."
                ),
                "evidence": [
                    (
                        f"Delivered orders: "
                        f"{delivery.get('delivered_orders')}."
                    )
                ],
                "likely_driver": "Not applicable",
                "recommended_actions": [],
            }

    if question_type == "cancellation":

        result = _find_execution_result(
            executed_analysis,
            "cancellation_performance",
        )

        if result:

            cancellation = result.get(
                "cancellation",
                {}
            )

            return {
                "answer": (
                    f"Cancellation rate was "
                    f"{cancellation.get('rate_percent')}% "
                    f"in {month}."
                ),
                "evidence": [
                    (
                        f"Cancelled orders: "
                        f"{cancellation.get('cancelled_orders')}."
                    )
                ],
                "likely_driver": "Not established",
                "recommended_actions": [],
            }

    # Business health / general business

    health = _find_execution_result(
        executed_analysis,
        "business_health",
    )

    sufficiency = _find_execution_result(
        executed_analysis,
        "evidence_sufficiency",
    )

    root_cause = _find_execution_result(
        executed_analysis,
        "root_cause_analysis",
    )

    evidence = []

    if health:

        kpi = health.get(
            "kpi_dashboard",
            {}
        )

        if kpi:

            evidence = [
                (
                    f"Revenue growth: "
                    f"{kpi['revenue']['growth_percent']}%."
                ),
                (
                    f"Order growth: "
                    f"{kpi['orders']['growth_percent']}%."
                ),
                (
                    f"Delivery rate: "
                    f"{kpi['delivery']['rate_percent']}%."
                ),
                (
                    f"Cancellation rate: "
                    f"{kpi['cancellation']['rate_percent']}%."
                ),
            ]

    return {
        "answer": (
            sufficiency.get(
                "explanation",
                (
                    "Deterministic business analysis "
                    "was completed."
                )
            )
            if sufficiency
            else (
                "Deterministic business analysis "
                "was completed."
            )
        ),

        "evidence": evidence,

        "likely_driver": (
            root_cause.get(
                "primary_explanation",
                "Not available"
            )
            if root_cause
            else "Not available"
        ),

        "recommended_actions": (
            _get_recommendation_actions(
                executed_analysis
            )
        ),
    }


def _build_deterministic_fallback(
    question_type: str,
    month: str,
    executed_analysis: dict,
):
    """
    Route deterministic fallback by question type.
    """

    if question_type == "scenario":
        return _scenario_fallback(
            executed_analysis
        )

    if question_type == "product":
        return _product_fallback(
            executed_analysis
        )

    if question_type == "customer":
        return _customer_fallback(
            executed_analysis
        )

    if question_type == "logistics":
        return _logistics_fallback(
            executed_analysis
        )

    return _standard_fallback(
        question_type=question_type,
        month=month,
        executed_analysis=executed_analysis,
    )


# ============================================================
# PUBLIC PIPELINE
# ============================================================


def answer_business_question(
    question: str,
    month: str = "2018-06",
) -> dict:
    """
    End-to-end ProfitLens Business Analyst.

    Optimized flow:

    1. Classify question.
    2. Execute deterministic analysis exactly once.
    3. Build a compact LLM context from those results.
    4. Ask the LLM to explain.
    5. Immediately fall back to deterministic output
       if the AI service fails or times out.

    No context_builder call occurs here.
    """

    # --------------------------------------------------
    # 1. CLASSIFY
    # --------------------------------------------------

    question_type = classify_question(
        question
    )

    # --------------------------------------------------
    # 2. EXECUTE ONCE
    # --------------------------------------------------

    executed_analysis = execute_analysis_plan(
        question,
        month,
    )

    # --------------------------------------------------
    # 3. COMPACT CONTEXT
    # --------------------------------------------------

    business_context = _build_llm_context(
        question_type=question_type,
        month=month,
        executed_analysis=executed_analysis,
    )

    # --------------------------------------------------
    # 4. AI EXPLANATION
    # --------------------------------------------------

    try:

        answer = ask_business_analyst(
            question=question,
            question_type=question_type,
            month=month,
            business_context=business_context,
        )

        ai_available = True

    except Exception:

        answer = _build_deterministic_fallback(
            question_type=question_type,
            month=month,
            executed_analysis=executed_analysis,
        )

        ai_available = False

    # --------------------------------------------------
    # 5. FINAL API RESPONSE
    # --------------------------------------------------

    return {
        "question": question,

        "month": month,

        "question_type": question_type,

        "analysis_execution": {
            "total_steps": (
                executed_analysis.get(
                    "total_steps",
                    0
                )
            ),

            "successful_steps": (
                executed_analysis.get(
                    "successful_steps",
                    0
                )
            ),

            "failed_steps": (
                executed_analysis.get(
                    "failed_steps",
                    0
                )
            ),
        },

        "ai_available": ai_available,

        "answer": answer,
    }