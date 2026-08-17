from backend.app.services.analytics import get_order_summary
from backend.app.services.performance import get_monthly_performance
from backend.app.services.trend_analysis import detect_trends
from backend.app.services.driver_analysis import analyze_revenue_change
from backend.app.services.revenue import get_revenue_summary
from backend.app.services.financial_analysis import (
    get_monthly_revenue,
    get_monthly_revenue_analysis,
    get_monthly_data_quality,
    get_product_revenue,
    get_seller_revenue,
)
from backend.app.services.kpi_engine import get_kpi_dashboard
from backend.app.services.insight_engine import (
    generate_business_insights,
)
from backend.app.services.serialization import make_json_safe


def build_context(
    question_type: str,
    month: str
):
    """
    Build the deterministic business context that will be
    provided to the AI Business Analyst.

    All numerical facts come from Python analytics engines.
    The LLM is responsible for interpretation, not calculation.
    """

    kpi = get_kpi_dashboard(month)

    insights = generate_business_insights(month)

    # --------------------------------------------------
    # GENERAL BUSINESS
    # --------------------------------------------------

    if question_type == "general_business":

        performance = get_monthly_performance()

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "current_period": (
                get_monthly_revenue_analysis(month)
            ),

            "business_summary": (
                get_order_summary()
            ),

            "revenue_summary": (
                get_revenue_summary()
            ),

            "monthly_revenue": (
                get_monthly_revenue()
                .to_dict(
                    orient="records"
                )
            ),

            "trends": detect_trends(),

            "monthly_performance": (
                performance
                .to_dict(
                    orient="records"
                )
            ),

            "data_quality": (
                get_monthly_data_quality()
            )
        })

    # --------------------------------------------------
    # REVENUE
    # --------------------------------------------------

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

            "monthly_revenue": (
                get_monthly_revenue()
                .to_dict(
                    orient="records"
                )
            ),

            "data_quality": (
                get_monthly_data_quality()
            )
        })

    # --------------------------------------------------
    # ORDERS
    # --------------------------------------------------

    if question_type == "orders":

        performance = get_monthly_performance()

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "order_summary": (
                get_order_summary()
            ),

            "monthly_orders": (
                performance[
                    [
                        "month",
                        "orders",
                        "order_growth"
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
                        "order_growth"
                    ]
                ]
                .to_dict(
                    orient="records"
                )
            )
        })

    # --------------------------------------------------
    # DELIVERY
    # --------------------------------------------------

    if question_type == "delivery":

        performance = get_monthly_performance()

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "monthly_delivery": (
                performance[
                    [
                        "month",
                        "delivery_rate",
                        "delivered_orders"
                    ]
                ]
                .to_dict(
                    orient="records"
                )
            )
        })

    # --------------------------------------------------
    # CANCELLATION
    # --------------------------------------------------

    if question_type == "cancellation":

        performance = get_monthly_performance()

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "monthly_cancellation": (
                performance[
                    [
                        "month",
                        "cancellation_rate",
                        "cancelled_orders"
                    ]
                ]
                .to_dict(
                    orient="records"
                )
            )
        })

    # --------------------------------------------------
    # TRENDS
    # --------------------------------------------------

    if question_type == "trends":

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "trends": detect_trends(),

            "monthly_revenue": (
                get_monthly_revenue()
                .to_dict(
                    orient="records"
                )
            ),

            "data_quality": (
                get_monthly_data_quality()
            )
        })

    # --------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------

    if question_type == "performance":

        performance = get_monthly_performance()

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

            "data_quality": (
                get_monthly_data_quality()
            )
        })

    # --------------------------------------------------
    # BUSINESS HEALTH
    # --------------------------------------------------

    if question_type == "business_health":

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "kpi_dashboard": kpi,

            "business_insights": insights,

            "summary": (
                get_order_summary()
            ),

            "revenue": (
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
                )
            },

            "trends": detect_trends(),

            "monthly_performance": (
                get_monthly_performance()
                .to_dict(
                    orient="records"
                )
            )
        })

    # --------------------------------------------------
    # GENERAL
    # --------------------------------------------------

    return make_json_safe({
        "question_type": "general",
        "month": month,

        "kpi_dashboard": kpi,

        "business_insights": insights,

        "summary": (
            get_order_summary()
        ),

        "revenue": (
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
            )
        }
    })