from backend.app.services.financial_analysis import (
    get_monthly_revenue_analysis,
)

from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
)

from backend.app.services.driver_analysis import (
    analyze_revenue_change,
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

from backend.app.services.trend_analysis import (
    detect_trends,
)

from backend.app.services.performance import (
    get_monthly_performance,
)

from backend.app.services.serialization import (
    make_json_safe,
)


def execute_fast_analysis(
    question: str,
    question_type: str,
    month: str,
):
    """
    Fast deterministic analysis used by the interactive
    ProfitLens chat endpoint.

    This intentionally avoids the full deep-analysis graph.

    The complete analysis planner/executor remains available
    separately for detailed investigations and auditability.
    """

    # =========================================================
    # REVENUE
    # =========================================================

    if question_type == "revenue":

        revenue = get_monthly_revenue_analysis(
            month
        )

        driver = analyze_revenue_change(
            month
        )

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "revenue_analysis": revenue,

            "driver_analysis": driver,

            "execution_mode": "fast",
        })

    # =========================================================
    # ORDERS
    # =========================================================

    if question_type == "orders":

        kpi = get_kpi_dashboard(
            month
        )

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "orders": kpi[
                "orders"
            ],

            "aov": kpi[
                "aov"
            ],

            "revenue": kpi[
                "revenue"
            ],

            "execution_mode": "fast",
        })

    # =========================================================
    # DELIVERY
    # =========================================================

    if question_type == "delivery":

        kpi = get_kpi_dashboard(
            month
        )

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "delivery": kpi[
                "delivery"
            ],

            "execution_mode": "fast",
        })

    # =========================================================
    # CANCELLATION
    # =========================================================

    if question_type == "cancellation":

        kpi = get_kpi_dashboard(
            month
        )

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "cancellation": kpi[
                "cancellation"
            ],

            "execution_mode": "fast",
        })

    # =========================================================
    # PRODUCT
    # =========================================================

    if question_type == "product":

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "product_analysis": (
                get_product_analytics(
                    month
                )
            ),

            "execution_mode": "fast",
        })

    # =========================================================
    # CUSTOMER
    # =========================================================

    if question_type == "customer":

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "customer_analysis": (
                get_customer_analytics()
            ),

            "execution_mode": "fast",
        })

    # =========================================================
    # LOGISTICS
    # =========================================================

    if question_type == "logistics":

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "logistics_analysis": (
                get_logistics_analytics(
                    month
                )
            ),

            "execution_mode": "fast",
        })

    # =========================================================
    # SCENARIO
    # =========================================================

    if question_type == "scenario":

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "scenario_analysis": (
                execute_scenario_question(
                    question,
                    month
                )
            ),

            "execution_mode": "fast",
        })

    # =========================================================
    # TRENDS
    # =========================================================

    if question_type in {
        "trends",
        "performance",
    }:

        return make_json_safe({
            "question_type": question_type,
            "month": month,

            "trends": (
                detect_trends()
            ),

            "monthly_performance": (
                get_monthly_performance()
                .to_dict(
                    orient="records"
                )
            ),

            "execution_mode": "fast",
        })

    # =========================================================
    # BUSINESS HEALTH / GENERAL BUSINESS
    # =========================================================

    kpi = get_kpi_dashboard(
        month
    )

    return make_json_safe({
        "question_type": question_type,
        "month": month,

        "kpi_dashboard": kpi,

        "revenue_analysis": (
            get_monthly_revenue_analysis(
                month
            )
        ),

        "driver_analysis": (
            analyze_revenue_change(
                month
            )
        ),

        "execution_mode": "fast",
    })