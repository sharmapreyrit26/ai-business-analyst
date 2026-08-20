from backend.app.services.order_analysis import (
    get_order_summary,
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

from backend.app.services.revenue import (
    get_revenue_summary,
)

from backend.app.services.financial_analysis import (
    get_monthly_revenue,
    get_monthly_revenue_analysis,
    get_monthly_data_quality,
)

from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
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

from backend.app.services.scenario_engine import (
    simulate_order_recovery,
    simulate_aov_change,
    simulate_combined_change,
)

from backend.app.services.root_cause_engine import (
    analyze_root_causes,
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

from backend.app.services.recommendation_engine import (
    build_recommendation_report,
)

from backend.app.services.opportunity_sizing import (
    build_opportunity_report,
)

from backend.app.services.anomaly_detection import (
    build_anomaly_report,
)

from backend.app.services.cross_functional_investigation import (
    build_cross_functional_investigation,
)

from backend.app.services.serialization import (
    make_json_safe,
)


def build_context(
    question_type: str,
    month: str
):
    """
    Build deterministic business context for the
    ProfitLens AI Business Analyst.

    Important architectural rule:

    Python analytics calculate business facts.
    The LLM interprets those facts.

    The LLM must not become the source of truth
    for numerical business calculations.
    """

    # --------------------------------------------------
    # COMMON FOUNDATION
    # --------------------------------------------------

    kpi = get_kpi_dashboard(
        month
    )

    insights = generate_business_insights(
        month
    )

    # ==================================================
    # REVENUE
    # ==================================================

    if question_type == "revenue":

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "revenue_analysis": (
                get_monthly_revenue_analysis(
                    month
                )
            ),

            "revenue_summary": (
                get_revenue_summary()
            ),

            "revenue_driver_analysis": (
                analyze_revenue_change(
                    month
                )
            ),

            "root_cause_analysis": (
                analyze_root_causes(
                    month
                )
            ),

            "evidence": (
                build_evidence_package(
                    month
                )
            ),

            "confidence": (
                build_confidence_report(
                    month
                )
            ),

            "evidence_sufficiency": (
                evaluate_evidence_sufficiency(
                    month
                )
            ),

            "opportunity_sizing": (
                build_opportunity_report(
                    month
                )
            ),

            "recommendations": (
                build_recommendation_report(
                    month
                )
            ),

            "monthly_revenue": (
                get_monthly_revenue()
                .to_dict(
                    orient="records"
                )
            ),

            "data_quality": (
                get_monthly_data_quality()
            ),
        })

    # ==================================================
    # ORDERS
    # ==================================================

    if question_type == "orders":

        performance = (
            get_monthly_performance()
        )

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "order_summary": (
                get_order_summary()
            ),

            "current_order_metrics": (
                kpi["orders"]
            ),

            "monthly_orders": (
                performance[
                    [
                        "month",
                        "orders",
                        "order_growth",
                    ]
                ]
                .to_dict(
                    orient="records"
                )
            ),

            "financial_order_metrics": (
                get_monthly_revenue()[
                    [
                        "month",
                        "orders",
                        "items",
                        "aov",
                        "order_growth",
                    ]
                ]
                .to_dict(
                    orient="records"
                )
            ),

            "root_cause_context": (
                analyze_root_causes(
                    month
                )
            ),

            "evidence_sufficiency": (
                evaluate_evidence_sufficiency(
                    month
                )
            ),

            "opportunity_sizing": (
                build_opportunity_report(
                    month
                )
            ),
        })

    # ==================================================
    # DELIVERY
    # ==================================================

    if question_type == "delivery":

        performance = (
            get_monthly_performance()
        )

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "current_delivery": (
                kpi["delivery"]
            ),

            "monthly_delivery": (
                performance[
                    [
                        "month",
                        "delivery_rate",
                        "delivered_orders",
                    ]
                ]
                .to_dict(
                    orient="records"
                )
            ),

            "logistics_context": (
                get_logistics_analytics(
                    month
                )
            ),
        })

    # ==================================================
    # CANCELLATION
    # ==================================================

    if question_type == "cancellation":

        performance = (
            get_monthly_performance()
        )

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "current_cancellation": (
                kpi["cancellation"]
            ),

            "monthly_cancellation": (
                performance[
                    [
                        "month",
                        "cancellation_rate",
                        "cancelled_orders",
                    ]
                ]
                .to_dict(
                    orient="records"
                )
            ),

            "logistics_context": (
                get_logistics_analytics(
                    month
                )
            ),
        })

    # ==================================================
    # PRODUCT
    # ==================================================

    if question_type == "product":

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "product_analytics": (
                get_product_analytics(
                    month
                )
            ),

            "data_limitations": {
                "profitability_available": False,

                "reason": (
                    "Product revenue and freight can be "
                    "analysed, but true profitability "
                    "requires COGS and additional variable "
                    "cost data."
                ),
            },
        })

    # ==================================================
    # CUSTOMER
    # ==================================================

    if question_type == "customer":

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "customer_analytics": (
                get_customer_analytics()
            ),

            "important_guardrail": (
                "Do not infer repeat purchase, retention, "
                "LTV or CAC when the required customer "
                "identity or marketing data is unavailable."
            ),
        })

    # ==================================================
    # LOGISTICS
    # ==================================================

    if question_type == "logistics":

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "logistics_analytics": (
                get_logistics_analytics(
                    month
                )
            ),

            "current_delivery": (
                kpi["delivery"]
            ),

            "current_cancellation": (
                kpi["cancellation"]
            ),

            "limitations": {
                "rto": (
                    "RTO analysis requires explicit "
                    "RTO status data."
                ),

                "courier_performance": (
                    "Courier analysis requires courier "
                    "identifier data."
                ),

                "cod_vs_prepaid": (
                    "COD versus prepaid analysis requires "
                    "payment-method data."
                ),
            },
        })

    # ==================================================
    # SCENARIO
    # ==================================================

    if question_type == "scenario":

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "scenario_engine": {
                "supported_scenarios": [
                    "order_recovery",
                    "aov_change",
                    "combined_change",
                ],

                "example_order_recovery": (
                    simulate_order_recovery(
                        month,
                        50
                    )
                ),

                "example_aov_change": (
                    simulate_aov_change(
                        month,
                        5
                    )
                ),

                "example_combined_change": (
                    simulate_combined_change(
                        month,
                        order_change_percent=5,
                        aov_change_percent=5,
                    )
                ),
            },

            "scenario_guardrail": (
                "Scenario outputs are mathematical "
                "estimates based on explicit assumptions. "
                "They are not forecasts or guaranteed "
                "business outcomes."
            ),
        })

    # ==================================================
    # TRENDS
    # ==================================================

    if question_type == "trends":

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "trends": (
                detect_trends()
            ),

            "monthly_revenue": (
                get_monthly_revenue()
                .to_dict(
                    orient="records"
                )
            ),

            "monthly_performance": (
                get_monthly_performance()
                .to_dict(
                    orient="records"
                )
            ),

            "anomalies": (
                build_anomaly_report()
            ),

            "data_quality": (
                get_monthly_data_quality()
            ),
        })

    # ==================================================
    # PERFORMANCE
    # ==================================================

    if question_type == "performance":

        performance = (
            get_monthly_performance()
        )

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "monthly_performance": (
                performance
                .to_dict(
                    orient="records"
                )
            ),

            "monthly_revenue": (
                get_monthly_revenue()
                .to_dict(
                    orient="records"
                )
            ),

            "trends": (
                detect_trends()
            ),

            "anomalies": (
                build_anomaly_report()
            ),

            "data_quality": (
                get_monthly_data_quality()
            ),
        })

    # ==================================================
    # BUSINESS HEALTH
    # ==================================================

    if question_type == "business_health":

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "business_summary": (
                get_order_summary()
            ),

            "revenue_summary": (
                get_revenue_summary()
            ),

            "current_period": (
                get_monthly_revenue_analysis(
                    month
                )
            ),

            "root_cause_analysis": (
                analyze_root_causes(
                    month
                )
            ),

            "cross_functional_investigation": (
                build_cross_functional_investigation(
                    month
                )
            ),

            "evidence": (
                build_evidence_package(
                    month
                )
            ),

            "confidence": (
                build_confidence_report(
                    month
                )
            ),

            "evidence_sufficiency": (
                evaluate_evidence_sufficiency(
                    month
                )
            ),

            "opportunity_sizing": (
                build_opportunity_report(
                    month
                )
            ),

            "recommendations": (
                build_recommendation_report(
                    month
                )
            ),

            "anomalies": (
                build_anomaly_report()
            ),

            "product_context": (
                get_product_analytics(
                    month
                )
            ),

            "customer_context": (
                get_customer_analytics()
            ),

            "logistics_context": (
                get_logistics_analytics(
                    month
                )
            ),

            "data_quality": (
                get_monthly_data_quality()
            ),
        })

    # ==================================================
    # GENERAL BUSINESS
    # ==================================================

    if question_type == "general_business":

        performance = (
            get_monthly_performance()
        )

        return make_json_safe({
            "question_type": question_type,

            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "current_period": (
                get_monthly_revenue_analysis(
                    month
                )
            ),

            "business_summary": (
                get_order_summary()
            ),

            "revenue_summary": (
                get_revenue_summary()
            ),

            "revenue_driver_analysis": (
                analyze_revenue_change(
                    month
                )
            ),

            "root_cause_analysis": (
                analyze_root_causes(
                    month
                )
            ),

            "cross_functional_investigation": (
                build_cross_functional_investigation(
                    month
                )
            ),

            "evidence": (
                build_evidence_package(
                    month
                )
            ),

            "confidence": (
                build_confidence_report(
                    month
                )
            ),

            "evidence_sufficiency": (
                evaluate_evidence_sufficiency(
                    month
                )
            ),

            "opportunity_sizing": (
                build_opportunity_report(
                    month
                )
            ),

            "recommendations": (
                build_recommendation_report(
                    month
                )
            ),

            "product_context": (
                get_product_analytics(
                    month
                )
            ),

            "customer_context": (
                get_customer_analytics()
            ),

            "logistics_context": (
                get_logistics_analytics(
                    month
                )
            ),

            "trends": (
                detect_trends()
            ),

            "monthly_performance": (
                performance
                .to_dict(
                    orient="records"
                )
            ),

            "data_quality": (
                get_monthly_data_quality()
            ),
        })

    # ==================================================
    # GENERAL FALLBACK
    # ==================================================

    return make_json_safe({
        "question_type": "general",

        "month": month,

        "kpi_dashboard": kpi,

        "business_insights": insights,

        "business_summary": (
            get_order_summary()
        ),

        "revenue_summary": (
            get_revenue_summary()
        ),

        "financial_analysis": {
            "monthly_revenue": (
                get_monthly_revenue()
                .to_dict(
                    orient="records"
                )
            ),

            "data_quality": (
                get_monthly_data_quality()
            ),
        },

        "available_analysis_domains": [
            "revenue",
            "orders",
            "delivery",
            "cancellation",
            "product",
            "customer",
            "logistics",
            "trends",
            "performance",
            "business health",
            "scenario analysis",
        ],
    })