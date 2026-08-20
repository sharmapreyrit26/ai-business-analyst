from backend.app.services.analysis_planner import (
    build_analysis_plan,
)

from backend.app.services.financial_analysis import (
    get_monthly_revenue_analysis,
)

from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
)

from backend.app.services.performance import (
    get_monthly_performance,
)

from backend.app.services.trend_analysis import (
    detect_trends,
)

from backend.app.services.driver_analysis import (
    analyze_revenue_change,
)

from backend.app.services.root_cause_engine import (
    analyze_root_causes,
)

from backend.app.services.hypothesis_engine import (
    build_hypotheses,
)

from backend.app.services.evidence import (
    build_evidence_package,
)

from backend.app.services.confidence import (
    build_confidence_report,
)

from backend.app.services.insufficient_evidence import (
    evaluate_evidence_sufficiency,
)

from backend.app.services.insight_engine import (
    generate_business_insights,
)

from backend.app.services.product_analysis import (
    get_product_analytics,
)

from backend.app.services.customer import (
    get_customer_analytics,
)

from backend.app.services.logistics_analysis import (
    get_logistics_analytics,
)

from backend.app.services.scenario_executor import (
    execute_scenario_question,
)

from backend.app.services.opportunity_sizing import (
    build_opportunity_report,
)

from backend.app.services.recommendation_engine import (
    build_recommendation_report,
)

from backend.app.services.cross_functional_investigation import (
    build_cross_functional_investigation,
)

from backend.app.services.serialization import (
    make_json_safe,
)


def _execute_analysis(
    analysis_name: str,
    question: str,
    month: str,
):
    """
    Execute one analysis-plan step.

    Every supported analysis is mapped to a
    deterministic Python analytics engine.
    """

    # --------------------------------------------------
    # REVENUE
    # --------------------------------------------------

    if analysis_name == "revenue_change":

        return get_monthly_revenue_analysis(
            month
        )

    # --------------------------------------------------
    # ORDERS
    # --------------------------------------------------

    if analysis_name == "order_change":

        kpi = get_kpi_dashboard(
            month
        )

        return {
            "month": month,
            "orders": kpi["orders"],
        }

    # --------------------------------------------------
    # AOV
    # --------------------------------------------------

    if analysis_name == "aov_change":

        kpi = get_kpi_dashboard(
            month
        )

        return {
            "month": month,
            "aov": kpi["aov"],
        }

    # --------------------------------------------------
    # REVENUE DRIVER DECOMPOSITION
    # --------------------------------------------------

    if (
        analysis_name
        == "revenue_driver_decomposition"
    ):

        return analyze_revenue_change(
            month
        )

    # --------------------------------------------------
    # DELIVERY
    # --------------------------------------------------

    if (
        analysis_name
        == "delivery_performance"
    ):

        kpi = get_kpi_dashboard(
            month
        )

        return {
            "month": month,
            "delivery": kpi[
                "delivery"
            ],
        }

    # --------------------------------------------------
    # CANCELLATION
    # --------------------------------------------------

    if (
        analysis_name
        == "cancellation_performance"
    ):

        kpi = get_kpi_dashboard(
            month
        )

        return {
            "month": month,
            "cancellation": kpi[
                "cancellation"
            ],
        }

    # --------------------------------------------------
    # HISTORICAL TRENDS
    # --------------------------------------------------

    if analysis_name == "historical_trends":

        return {
            "trends": (
                detect_trends()
            ),

            "monthly_performance": (
                get_monthly_performance()
                .to_dict(
                    orient="records"
                )
            ),
        }

    # --------------------------------------------------
    # ROOT CAUSE
    # --------------------------------------------------

    if (
        analysis_name
        == "root_cause_analysis"
    ):

        return analyze_root_causes(
            month
        )

    # --------------------------------------------------
    # HYPOTHESES
    # --------------------------------------------------

    if (
        analysis_name
        == "hypothesis_analysis"
    ):

        return build_hypotheses(
            month
        )

    # --------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------

    if (
        analysis_name
        == "evidence_analysis"
    ):

        return build_evidence_package(
            month
        )

    # --------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------

    if (
        analysis_name
        == "confidence_analysis"
    ):

        return build_confidence_report(
            month
        )

    # --------------------------------------------------
    # BUSINESS HEALTH
    # --------------------------------------------------

    if analysis_name == "business_health":

        return {
            "kpi_dashboard": (
                get_kpi_dashboard(
                    month
                )
            ),

            "business_insights": (
                generate_business_insights(
                    month
                )
            ),

            "cross_functional_investigation": (
                build_cross_functional_investigation(
                    month
                )
            ),
        }

    # --------------------------------------------------
    # PRODUCT
    # --------------------------------------------------

    if analysis_name == "product_analysis":

        return get_product_analytics(
            month
        )

    # --------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------

    if analysis_name == "customer_analysis":

        return get_customer_analytics()

    # --------------------------------------------------
    # LOGISTICS
    # --------------------------------------------------

    if analysis_name == "logistics_analysis":

        return get_logistics_analytics(
            month
        )

    # --------------------------------------------------
    # SCENARIO
    # --------------------------------------------------

    if analysis_name == "scenario_analysis":

        return execute_scenario_question(
            question,
            month
        )

    # --------------------------------------------------
    # OPPORTUNITY
    # --------------------------------------------------

    if analysis_name == "opportunity_sizing":

        return build_opportunity_report(
            month
        )

    # --------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------

    if analysis_name == "recommendation_analysis":

        return build_recommendation_report(
            month
        )

    # --------------------------------------------------
    # INSUFFICIENT EVIDENCE
    # --------------------------------------------------

    if (
        analysis_name
        == "evidence_sufficiency"
    ):

        return evaluate_evidence_sufficiency(
            month
        )

    # --------------------------------------------------
    # UNSUPPORTED
    # --------------------------------------------------

    return {
        "status": "unsupported_analysis",
        "analysis": analysis_name,
    }


def execute_analysis_plan(
    question: str,
    month: str = "2018-06"
):
    """
    Build and execute the complete deterministic
    analysis plan for a business question.

    Flow:

    Question
        ↓
    Analysis planner
        ↓
    Step-by-step deterministic execution
        ↓
    Structured analytical result
    """

    plan = build_analysis_plan(
        question,
        month
    )

    results = []

    # --------------------------------------------------
    # EXECUTE PLANNED STEPS
    # --------------------------------------------------

    for step in plan[
        "analysis_plan"
    ]:

        analysis_name = step[
            "analysis"
        ]

        try:

            result = _execute_analysis(
                analysis_name=analysis_name,
                question=question,
                month=month,
            )

            execution_status = (
                "complete"
            )

        except Exception as error:

            result = {
                "status": "error",
                "error": str(error),
            }

            execution_status = (
                "error"
            )

        results.append({
            "step": step[
                "step"
            ],

            "analysis": (
                analysis_name
            ),

            "reason": step[
                "reason"
            ],

            "execution_status": (
                execution_status
            ),

            "result": result,
        })

    # --------------------------------------------------
    # EXECUTION SUMMARY
    # --------------------------------------------------

    successful_steps = sum(
        1
        for result in results
        if result[
            "execution_status"
        ] == "complete"
    )

    failed_steps = (
        len(results)
        - successful_steps
    )

    return make_json_safe({
        "question": question,

        "month": month,

        "question_type": plan[
            "question_type"
        ],

        "total_steps": plan[
            "total_steps"
        ],

        "successful_steps": (
            successful_steps
        ),

        "failed_steps": (
            failed_steps
        ),

        "analysis_plan": plan[
            "analysis_plan"
        ],

        "execution_results": results,
    })