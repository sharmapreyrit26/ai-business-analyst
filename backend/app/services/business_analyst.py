from backend.app.services.question_router import (
    classify_question,
)

from backend.app.services.context_builder import (
    build_context,
)

from backend.app.services.analysis_executor import (
    execute_analysis_plan,
)

from backend.app.services.insight_engine import (
    generate_business_insights,
)

from backend.app.services.scenario_executor import (
    execute_scenario_question,
)

from backend.app.services.llm_service import (
    ask_business_analyst,
)


def _find_execution_result(
    executed_analysis: dict,
    analysis_name: str,
):
    """
    Find one executed analysis result by analysis name.
    """

    for item in executed_analysis.get(
        "execution_results",
        []
    ):

        if (
            item.get("analysis")
            == analysis_name
        ):
            return item.get(
                "result"
            )

    return None


def _build_scenario_fallback(
    scenario_execution: dict
) -> dict:
    """
    Build deterministic scenario response when
    the AI service is unavailable.
    """

    if not scenario_execution:

        return {
            "answer": (
                "The requested scenario could not be "
                "executed with the available information."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    if (
        scenario_execution.get(
            "status"
        )
        != "complete"
    ):

        parser_result = scenario_execution.get(
            "parser_result",
            {}
        )

        missing = parser_result.get(
            "missing",
            []
        )

        if missing:

            answer = (
                "The scenario is missing the following "
                f"required parameter(s): "
                f"{', '.join(missing)}."
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

    result = scenario_execution[
        "scenario_result"
    ]

    scenario_type = scenario_execution[
        "scenario_type"
    ]

    evidence = []

    # --------------------------------------------------
    # ORDER RECOVERY
    # --------------------------------------------------

    if scenario_type == "order_recovery":

        difference = result[
            "difference"
        ]

        scenario_result = result[
            "scenario_result"
        ]

        recovery_percent = result[
            "assumptions"
        ]["recovery_percent"]

        answer = (
            f"Recovering {recovery_percent:.2f}% "
            f"of lost orders would add approximately "
            f"{difference['additional_orders']:.2f} orders "
            f"and increase revenue by approximately "
            f"{difference['incremental_revenue']:.2f}."
        )

        evidence = [
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
        ]

    # --------------------------------------------------
    # AOV
    # --------------------------------------------------

    elif scenario_type == "aov_change":

        difference = result[
            "difference"
        ]

        scenario_result = result[
            "scenario_result"
        ]

        change_percent = result[
            "assumptions"
        ]["aov_change_percent"]

        answer = (
            f"If AOV changes by {change_percent:.2f}%, "
            f"scenario AOV becomes "
            f"{scenario_result['aov']:.2f} and estimated "
            f"revenue becomes "
            f"{scenario_result['revenue']:.2f}. "
            f"The incremental revenue impact is "
            f"{difference['incremental_revenue']:.2f}."
        )

        evidence = [
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
            (
                f"Incremental revenue: "
                f"{difference['incremental_revenue']:.2f}."
            ),
        ]

    # --------------------------------------------------
    # COMBINED
    # --------------------------------------------------

    elif scenario_type == "combined_change":

        assumptions = result[
            "assumptions"
        ]

        scenario_result = result[
            "scenario_result"
        ]

        difference = result[
            "difference"
        ]

        answer = (
            f"If orders change by "
            f"{assumptions['order_change_percent']:.2f}% "
            f"and AOV changes by "
            f"{assumptions['aov_change_percent']:.2f}%, "
            f"estimated revenue becomes "
            f"{scenario_result['revenue']:.2f}, "
            f"an incremental change of "
            f"{difference['incremental_revenue']:.2f}."
        )

        evidence = [
            (
                f"Current orders: "
                f"{result['current']['orders']}."
            ),
            (
                f"Scenario orders: "
                f"{scenario_result['orders']:.2f}."
            ),
            (
                f"Current AOV: "
                f"{result['current']['aov']:.2f}."
            ),
            (
                f"Scenario AOV: "
                f"{scenario_result['aov']:.2f}."
            ),
        ]

    else:

        answer = (
            "The scenario was executed successfully."
        )

    return {
        "answer": answer,
        "evidence": evidence,
        "likely_driver": "Not applicable",
        "recommended_actions": [],
    }


def _build_product_fallback(
    executed_analysis: dict
) -> dict:
    """
    Build deterministic product response.
    """

    product_result = _find_execution_result(
        executed_analysis,
        "product_analysis",
    )

    if not product_result:

        return {
            "answer": (
                "Product analysis is unavailable "
                "for the selected period."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    top_products = product_result.get(
        "top_products",
        []
    )

    if not top_products:

        return {
            "answer": (
                "No product-level records were available "
                "for the selected period."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    top_product = top_products[0]

    return {
        "answer": (
            f"The highest-revenue product was "
            f"{top_product['product_id']}, generating "
            f"{top_product['revenue']:.2f} in revenue."
        ),

        "evidence": [
            (
                f"Units sold: "
                f"{top_product['units_sold']}."
            ),
            (
                f"Orders: "
                f"{top_product['orders']}."
            ),
            (
                f"Revenue share: "
                f"{top_product['revenue_share_percent']:.2f}%."
            ),
            (
                f"Freight-to-revenue ratio: "
                f"{top_product['freight_to_revenue_percent']:.2f}%."
            ),
        ],

        "likely_driver": (
            "Product revenue contribution"
        ),

        "recommended_actions": [],
    }


def _build_customer_fallback(
    executed_analysis: dict
) -> dict:
    """
    Build deterministic customer response.
    """

    customer_result = _find_execution_result(
        executed_analysis,
        "customer_analysis",
    )

    if not customer_result:

        return {
            "answer": (
                "Customer analysis is unavailable."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    unavailable = customer_result.get(
        "unavailable_analysis",
        {}
    )

    repeat_purchase = unavailable.get(
        "repeat_purchase",
        {}
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
                (
                    "The connected orders data contains "
                    "customer_id but not a persistent "
                    "customer_unique_id."
                )
            ],

            "likely_driver": (
                "Insufficient customer identity data"
            ),

            "recommended_actions": [
                (
                    "Connect persistent customer identity "
                    "data before calculating repeat purchase, "
                    "retention, cohorts or LTV."
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


def _build_logistics_fallback(
    executed_analysis: dict
) -> dict:
    """
    Build deterministic logistics response.
    """

    logistics = _find_execution_result(
        executed_analysis,
        "logistics_analysis",
    )

    if not logistics:

        return {
            "answer": (
                "Logistics analysis is unavailable."
            ),
            "evidence": [],
            "likely_driver": "Not applicable",
            "recommended_actions": [],
        }

    fulfilment = logistics.get(
        "fulfilment_tat",
        {}
    )

    purchase_to_delivery = fulfilment.get(
        "purchase_to_delivery",
        {}
    )

    delivery_promise = logistics.get(
        "delivery_promise",
        {}
    )

    average = purchase_to_delivery.get(
        "average"
    )

    p90 = purchase_to_delivery.get(
        "p90"
    )

    evidence = []

    if average is not None:

        evidence.append(
            f"Average purchase-to-delivery TAT: "
            f"{average:.2f} days."
        )

    if p90 is not None:

        evidence.append(
            f"P90 purchase-to-delivery TAT: "
            f"{p90:.2f} days."
        )

    on_time = delivery_promise.get(
        "on_time_delivery_percent"
    )

    if on_time is not None:

        evidence.append(
            f"On-time delivery rate: "
            f"{on_time:.2f}%."
        )

    late = delivery_promise.get(
        "late_delivery_percent"
    )

    if late is not None:

        evidence.append(
            f"Late delivery rate: "
            f"{late:.2f}%."
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
            "Detailed fulfilment TAT could not be "
            "calculated for the selected period."
        )

    return {
        "answer": answer,
        "evidence": evidence,
        "likely_driver": "Not applicable",
        "recommended_actions": [],
    }


def _build_analysis_fallback(
    question_type: str,
    month: str,
    executed_analysis: dict,
    insights: dict,
) -> dict:
    """
    Build deterministic fallback from the executed
    analysis plan for the standard business intents.
    """

    # --------------------------------------------------
    # REVENUE
    # --------------------------------------------------

    if question_type == "revenue":

        revenue = _find_execution_result(
            executed_analysis,
            "revenue_change",
        )

        driver = _find_execution_result(
            executed_analysis,
            "root_cause_analysis",
        )

        recommendations = _find_execution_result(
            executed_analysis,
            "recommendation_analysis",
        )

        if revenue:

            answer = (
                f"Revenue changed by "
                f"{revenue['revenue_change_percent']:.2f}% "
                f"in {month}."
            )

            evidence = [
                (
                    f"Revenue: "
                    f"{revenue['revenue']:.2f}."
                ),
                (
                    f"Previous revenue: "
                    f"{revenue['previous_revenue']:.2f}."
                ),
                (
                    f"Orders changed by "
                    f"{revenue['order_change_percent']:.2f}%."
                ),
                (
                    f"AOV changed by "
                    f"{revenue['aov_change_percent']:.2f}%."
                ),
            ]

            likely_driver = (
                driver.get(
                    "primary_explanation",
                    "Not available"
                )
                if driver
                else "Not available"
            )

            actions = []

            if recommendations:

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

                actions = [
                    recommendation[
                        "action"
                    ]
                    for recommendation
                    in revenue_group.get(
                        "recommendations",
                        []
                    )
                ]

            return {
                "answer": answer,
                "evidence": evidence,
                "likely_driver": likely_driver,
                "recommended_actions": actions,
            }

    # --------------------------------------------------
    # BUSINESS HEALTH
    # --------------------------------------------------

    if question_type in {
        "business_health",
        "general_business",
    }:

        health = _find_execution_result(
            executed_analysis,
            "business_health",
        )

        root_cause = _find_execution_result(
            executed_analysis,
            "root_cause_analysis",
        )

        evidence_sufficiency = (
            _find_execution_result(
                executed_analysis,
                "evidence_sufficiency",
            )
        )

        recommendations = (
            _find_execution_result(
                executed_analysis,
                "recommendation_analysis",
            )
        )

        evidence = []

        if health:

            kpi = health.get(
                "kpi_dashboard",
                {}
            )

            if kpi:

                evidence.extend([
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
                ])

        likely_driver = (
            root_cause.get(
                "primary_explanation",
                "Not available"
            )
            if root_cause
            else "Not available"
        )

        actions = []

        if recommendations:

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

            actions = [
                recommendation[
                    "action"
                ]
                for recommendation
                in revenue_group.get(
                    "recommendations",
                    []
                )
            ]

        if evidence_sufficiency:

            answer = evidence_sufficiency.get(
                "explanation",
                (
                    "Deterministic business analysis "
                    "has been completed."
                )
            )

        else:

            answer = (
                "Deterministic business analysis "
                "has been completed."
            )

        return {
            "answer": answer,
            "evidence": evidence,
            "likely_driver": likely_driver,
            "recommended_actions": actions,
        }

    # --------------------------------------------------
    # ORIGINAL INSIGHT FALLBACK
    # --------------------------------------------------

    selected_insight = None

    for insight in insights.get(
        "insights",
        []
    ):

        if (
            question_type == "orders"
            and insight.get("type") == "orders"
        ):
            selected_insight = insight
            break

        if (
            question_type == "delivery"
            and insight.get("type") == "delivery"
        ):
            selected_insight = insight
            break

        if (
            question_type == "cancellation"
            and insight.get("type") == "cancellation"
        ):
            selected_insight = insight
            break

    if selected_insight:

        evidence = []

        for key, value in selected_insight.items():

            if key in {
                "type",
                "period",
                "summary",
                "data_quality",
            }:
                continue

            if isinstance(
                value,
                (int, float, str)
            ):

                evidence.append(
                    f"{key.replace('_', ' ').capitalize()}: "
                    f"{value}"
                )

        return {
            "answer": selected_insight.get(
                "summary",
                (
                    "Deterministic business analysis "
                    "is available."
                )
            ),

            "evidence": evidence[:5],

            "likely_driver": (
                selected_insight.get(
                    "primary_driver",
                    "Not applicable"
                )
            ),

            "recommended_actions": [],
        }

    return {
        "answer": (
            f"Deterministic business analysis was completed "
            f"for {month}, but an AI-generated interpretation "
            f"is currently unavailable."
        ),
        "evidence": [],
        "likely_driver": "Not available",
        "recommended_actions": [],
    }


def _build_deterministic_fallback(
    question: str,
    month: str,
    question_type: str,
    executed_analysis: dict,
    insights: dict,
    scenario_execution: dict = None,
) -> dict:
    """
    Route fallback generation using executed
    deterministic analytical results.
    """

    if question_type == "scenario":

        return _build_scenario_fallback(
            scenario_execution
        )

    if question_type == "product":

        return _build_product_fallback(
            executed_analysis
        )

    if question_type == "customer":

        return _build_customer_fallback(
            executed_analysis
        )

    if question_type == "logistics":

        return _build_logistics_fallback(
            executed_analysis
        )

    return _build_analysis_fallback(
        question_type=question_type,
        month=month,
        executed_analysis=executed_analysis,
        insights=insights,
    )


def answer_business_question(
    question: str,
    month: str = "2018-06"
) -> dict:
    """
    End-to-end ProfitLens analytical pipeline.

    Flow:

    1. Classify question.
    2. Create and execute analysis plan.
    3. Build supporting deterministic context.
    4. Execute exact scenario if required.
    5. Send deterministic evidence to the AI.
    6. Fall back to deterministic answers if AI fails.
    """

    # ==================================================
    # 1. CLASSIFICATION
    # ==================================================

    question_type = classify_question(
        question
    )

    # ==================================================
    # 2. EXECUTE ANALYSIS PLAN
    # ==================================================

    executed_analysis = (
        execute_analysis_plan(
            question,
            month,
        )
    )

    # ==================================================
    # 3. BUILD SUPPORTING CONTEXT
    # ==================================================

    business_context = build_context(
        question_type,
        month,
    )

    # ==================================================
    # 4. SCENARIO EXECUTION
    # ==================================================

    scenario_execution = None

    if question_type == "scenario":

        scenario_execution = (
            execute_scenario_question(
                question,
                month,
            )
        )

        business_context[
            "executed_scenario"
        ] = scenario_execution

    # ==================================================
    # 5. DETERMINISTIC INSIGHTS
    # ==================================================

    deterministic_insights = (
        generate_business_insights(
            month
        )
    )

    # ==================================================
    # 6. EXECUTED ANALYSIS BECOMES PRIMARY EVIDENCE
    # ==================================================

    business_context[
        "executed_analysis_plan"
    ] = executed_analysis

    business_context[
        "deterministic_insights"
    ] = deterministic_insights

    business_context[
        "analysis_instruction"
    ] = (
        "The executed_analysis_plan contains the "
        "deterministically executed analyses for this "
        "specific user question. Treat those results as "
        "the primary analytical evidence. Use other context "
        "only as supporting information. Do not invent "
        "metrics or causes that are not present in the "
        "executed analysis."
    )

    if question_type == "scenario":

        business_context[
            "scenario_instruction"
        ] = (
            "Use executed_scenario as the authoritative "
            "answer to the user's what-if question. "
            "Never replace the user's exact scenario "
            "parameters with example assumptions."
        )

    # ==================================================
    # 7. AI EXPLANATION
    # ==================================================

    try:

        answer = ask_business_analyst(
            question=question,
            question_type=question_type,
            month=month,
            business_context=business_context,
        )

        ai_available = True

    except Exception:

        answer = (
            _build_deterministic_fallback(
                question=question,
                month=month,
                question_type=question_type,
                executed_analysis=executed_analysis,
                insights=deterministic_insights,
                scenario_execution=scenario_execution,
            )
        )

        ai_available = False

    # ==================================================
    # 8. FINAL RESPONSE
    # ==================================================

    return {
        "question": question,

        "month": month,

        "question_type": question_type,

        "analysis_execution": {
            "total_steps": (
                executed_analysis[
                    "total_steps"
                ]
            ),

            "successful_steps": (
                executed_analysis[
                    "successful_steps"
                ]
            ),

            "failed_steps": (
                executed_analysis[
                    "failed_steps"
                ]
            ),
        },

        "ai_available": ai_available,

        "answer": answer,
    }