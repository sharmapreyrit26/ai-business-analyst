from __future__ import annotations

from typing import Any

from backend.app.services.serialization import (
    make_json_safe,
)


# ============================================================
# D2C ANALYSIS PLANS
# ============================================================


D2C_ANALYSIS_PLANS = {

    "revenue": [
        (
            "revenue_performance",
            "Establish current revenue performance and change.",
        ),
        (
            "order_performance",
            "Inspect order-volume performance as a revenue driver.",
        ),
        (
            "aov_performance",
            "Inspect average order value as a revenue driver.",
        ),
        (
            "profitability_context",
            "Check whether the revenue movement also affected profit.",
        ),
    ],

    "profitability": [
        (
            "profitability_performance",
            "Establish gross and contribution profitability.",
        ),
        (
            "revenue_context",
            "Relate profitability to current revenue performance.",
        ),
        (
            "marketing_context",
            "Inspect marketing spend, ROAS and CAC pressure.",
        ),
    ],

    "orders": [
        (
            "order_performance",
            "Establish order-volume performance.",
        ),
        (
            "revenue_context",
            "Relate order movement to revenue performance.",
        ),
        (
            "customer_context",
            "Inspect customer activity relevant to order volume.",
        ),
    ],

    "marketing": [
        (
            "marketing_performance",
            "Establish marketing spend and efficiency.",
        ),
        (
            "marketing_channels",
            "Compare acquisition-channel performance.",
        ),
        (
            "marketing_insights",
            "Review deterministic marketing insights.",
        ),
        (
            "profitability_context",
            "Relate marketing performance to contribution profit.",
        ),
    ],

    "product": [
        (
            "product_performance",
            "Establish product portfolio performance.",
        ),
        (
            "category_performance",
            "Compare category economics.",
        ),
    ],

    "customer": [
        (
            "customer_performance",
            "Establish customer health and repeat behaviour.",
        ),
        (
            "acquisition_performance",
            "Compare acquisition-channel customer quality.",
        ),
    ],

    "inventory": [
        (
            "inventory_performance",
            "Establish working-capital and stock risk.",
        ),
        (
            "inventory_sku_risk",
            "Identify SKU-level inventory risk.",
        ),
    ],

    "logistics": [
        (
            "logistics_performance",
            "Establish delivery, RTO and NDR performance.",
        ),
        (
            "courier_performance",
            "Compare courier performance.",
        ),
        (
            "payment_logistics",
            "Compare COD and prepaid logistics risk.",
        ),
        (
            "zone_performance",
            "Compare geographic logistics performance.",
        ),
    ],

    "delivery": [
        (
            "logistics_performance",
            "Establish delivery performance.",
        ),
        (
            "courier_performance",
            "Compare courier delivery performance.",
        ),
    ],

    "cancellation": [
        (
            "overview_performance",
            "Inspect available business-level cancellation context.",
        ),
    ],

    "trends": [
        (
            "overview_performance",
            "Establish current business performance.",
        ),
        (
            "revenue_context",
            "Inspect current revenue movement.",
        ),
        (
            "profitability_context",
            "Inspect current profitability movement.",
        ),
    ],

    "performance": [
        (
            "overview_performance",
            "Evaluate overall business performance.",
        ),
        (
            "revenue_context",
            "Review commercial performance.",
        ),
        (
            "profitability_context",
            "Review profitability performance.",
        ),
        (
            "logistics_performance",
            "Review operational performance.",
        ),
    ],

    "business_health": [
        (
            "overview_performance",
            "Establish overall business health.",
        ),
        (
            "profitability_context",
            "Evaluate profitability pressure.",
        ),
        (
            "marketing_performance",
            "Evaluate marketing efficiency.",
        ),
        (
            "customer_performance",
            "Evaluate customer health.",
        ),
        (
            "logistics_performance",
            "Evaluate operational risk.",
        ),
        (
            "inventory_performance",
            "Evaluate working-capital risk.",
        ),
        (
            "product_performance",
            "Evaluate portfolio performance.",
        ),
    ],

    "general_business": [
        (
            "overview_performance",
            "Establish cross-functional business context.",
        ),
        (
            "profitability_context",
            "Evaluate profitability.",
        ),
        (
            "marketing_performance",
            "Evaluate marketing.",
        ),
        (
            "customer_performance",
            "Evaluate customers.",
        ),
        (
            "logistics_performance",
            "Evaluate logistics.",
        ),
        (
            "inventory_performance",
            "Evaluate inventory.",
        ),
        (
            "product_performance",
            "Evaluate products.",
        ),
    ],

    "scenario": [
        (
            "scenario_context",
            "Identify the request as a what-if analysis.",
        ),
    ],

    "general": [
        (
            "overview_performance",
            "Establish general business context.",
        ),
    ],
}


# ============================================================
# CONTEXT ACCESS
# ============================================================


def _get_nested(
    data: dict,
    *keys: str,
) -> Any:
    """
    Safely read a nested deterministic context value.
    """

    current: Any = data

    for key in keys:

        if not isinstance(
            current,
            dict,
        ):
            return None

        current = current.get(
            key
        )

    return current


def _execute_context_analysis(
    analysis_name: str,
    context: dict,
):
    """
    Execute one D2C analysis step using only the
    deterministic context that has already been built.

    No financial calculation occurs here.
    """

    if analysis_name == "overview_performance":
        return context.get(
            "overview"
        )

    if analysis_name == "revenue_performance":
        return _get_nested(
            context,
            "overview",
            "revenue",
        )

    if analysis_name == "revenue_context":
        return _get_nested(
            context,
            "overview",
            "revenue",
        )

    if analysis_name == "order_performance":

        revenue = _get_nested(
            context,
            "overview",
            "revenue",
        )

        if not isinstance(
            revenue,
            dict,
        ):
            return None

        return {
            key: revenue.get(
                key
            )
            for key in [
                "orders",
                "order_growth_percent",
            ]
            if key in revenue
        }

    if analysis_name == "aov_performance":

        revenue = _get_nested(
            context,
            "overview",
            "revenue",
        )

        if not isinstance(
            revenue,
            dict,
        ):
            return None

        return {
            key: revenue.get(
                key
            )
            for key in [
                "aov",
                "aov_growth_percent",
            ]
            if key in revenue
        }

    if analysis_name in {
        "profitability_performance",
        "profitability_context",
    }:
        return _get_nested(
            context,
            "overview",
            "profitability",
        )

    if analysis_name == "marketing_context":
        return _get_nested(
            context,
            "overview",
            "marketing",
        )

    if analysis_name == "marketing_performance":
        return _get_nested(
            context,
            "marketing",
            "summary",
        )

    if analysis_name == "marketing_channels":
        return _get_nested(
            context,
            "marketing",
            "channels",
        )

    if analysis_name == "marketing_insights":
        return _get_nested(
            context,
            "marketing",
            "insights",
        )

    if analysis_name == "product_performance":
        return _get_nested(
            context,
            "products",
            "summary",
        )

    if analysis_name == "category_performance":
        return _get_nested(
            context,
            "products",
            "categories",
        )

    if analysis_name == "customer_performance":
        return _get_nested(
            context,
            "customers",
            "summary",
        )

    if analysis_name == "customer_context":
        return _get_nested(
            context,
            "customers",
            "summary",
        )

    if analysis_name == "acquisition_performance":
        return _get_nested(
            context,
            "customers",
            "acquisition_channels",
        )

    if analysis_name == "logistics_performance":
        return _get_nested(
            context,
            "logistics",
            "summary",
        )

    if analysis_name == "courier_performance":
        return _get_nested(
            context,
            "logistics",
            "couriers",
        )

    if analysis_name == "payment_logistics":
        return _get_nested(
            context,
            "logistics",
            "payment_logistics",
        )

    if analysis_name == "zone_performance":
        return _get_nested(
            context,
            "logistics",
            "zones",
        )

    if analysis_name == "inventory_performance":
        return _get_nested(
            context,
            "inventory",
            "summary",
        )

    if analysis_name == "inventory_sku_risk":
        return {
            "reorder_candidates":
                _get_nested(
                    context,
                    "inventory",
                    "reorder_candidates",
                ),

            "highest_trapped_inventory":
                _get_nested(
                    context,
                    "inventory",
                    "highest_trapped_inventory",
                ),
        }

    if analysis_name == "scenario_context":
        return {
            "status":
                "scenario_question",

            "message": (
                "Scenario calculations are executed "
                "by the deterministic Scenario Lab."
            ),
        }

    return None


# ============================================================
# PUBLIC EXECUTOR
# ============================================================


def execute_d2c_analysis_plan(
    question: str,
    month: str,
    question_type: str,
    business_context: dict,
):
    """
    Execute a D2C-native analytical plan against the
    deterministic business context already calculated
    for Ask ProfitLens.

    This intentionally does not call the D2C engines
    again, preventing duplicate computation.
    """

    plan_definition = (
        D2C_ANALYSIS_PLANS.get(
            question_type
        )
        or D2C_ANALYSIS_PLANS[
            "general"
        ]
    )

    results = []

    for (
        index,
        (
            analysis_name,
            reason,
        ),
    ) in enumerate(
        plan_definition,
        start=1,
    ):

        try:

            result = (
                _execute_context_analysis(
                    analysis_name=
                        analysis_name,

                    context=
                        business_context,
                )
            )

            if result is None:

                execution_status = (
                    "unavailable"
                )

                result = {
                    "status":
                        "unavailable",

                    "message": (
                        "Required deterministic "
                        "context is unavailable."
                    ),
                }

            else:

                execution_status = (
                    "complete"
                )

        except Exception as error:

            execution_status = (
                "error"
            )

            result = {
                "status":
                    "error",

                "error":
                    str(error),
            }

        results.append({
            "step":
                index,

            "analysis":
                analysis_name,

            "reason":
                reason,

            "execution_status":
                execution_status,

            "result":
                result,
        })


    successful_steps = sum(
        1
        for item in results
        if item[
            "execution_status"
        ] == "complete"
    )

    failed_steps = sum(
        1
        for item in results
        if item[
            "execution_status"
        ] == "error"
    )

    unavailable_steps = sum(
        1
        for item in results
        if item[
            "execution_status"
        ] == "unavailable"
    )


    return make_json_safe({
        "question":
            question,

        "month":
            month,

        "question_type":
            question_type,

        "total_steps":
            len(
                results
            ),

        "successful_steps":
            successful_steps,

        "failed_steps":
            failed_steps,

        "unavailable_steps":
            unavailable_steps,

        "analysis_plan": [
            {
                "step":
                    item[
                        "step"
                    ],

                "analysis":
                    item[
                        "analysis"
                    ],

                "reason":
                    item[
                        "reason"
                    ],
            }
            for item in results
        ],

        "execution_results":
            results,
    })
