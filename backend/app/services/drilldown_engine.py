from __future__ import annotations

from backend.app.drilldown_contracts import (
    DrilldownComponent,
    DrilldownSource,
    MetricDrilldown,
)

from backend.app.metric_contracts import (
    MetricQuality,
)

from backend.app.services.metric_dictionary_service import (
    build_registered_metric,
    get_metric_definition,
)


# ============================================================
# REGISTERED CALCULATION COMPONENTS
# ============================================================


CALCULATION_COMPONENTS = {
    "contribution_profit_after_marketing": [
        {
            "component_id":
                "realized_revenue",
            "label":
                "Realized Revenue",
            "operator":
                "+",
        },
        {
            "component_id":
                "recognized_cogs",
            "label":
                "Recognized COGS",
            "operator":
                "-",
        },
        {
            "component_id":
                "forward_shipping",
            "label":
                "Forward Shipping",
            "operator":
                "-",
        },
        {
            "component_id":
                "cod_fees",
            "label":
                "COD Fees",
            "operator":
                "-",
        },
        {
            "component_id":
                "payment_fees",
            "label":
                "Payment Fees",
            "operator":
                "-",
        },
        {
            "component_id":
                "rto_costs",
            "label":
                "RTO Costs",
            "operator":
                "-",
        },
        {
            "component_id":
                "marketing_spend",
            "label":
                "Marketing Spend",
            "operator":
                "-",
        },
    ],

    "blended_roas": [
        {
            "component_id":
                "attributed_revenue",
            "label":
                "Attributed Revenue",
            "operator":
                "/",
        },
        {
            "component_id":
                "marketing_spend",
            "label":
                "Marketing Spend",
            "operator":
                None,
        },
    ],

    "cac": [
        {
            "component_id":
                "marketing_spend",
            "label":
                "Marketing Spend",
            "operator":
                "/",
        },
        {
            "component_id":
                "new_customers",
            "label":
                "New Customers",
            "operator":
                None,
        },
    ],

    "rto_rate_percent": [
        {
            "component_id":
                "rto_orders",
            "label":
                "RTO Orders",
            "operator":
                "/",
        },
        {
            "component_id":
                "orders",
            "label":
                "Total Orders",
            "operator":
                "* 100",
        },
    ],

    "repeat_customer_rate_percent": [
        {
            "component_id":
                "repeat_customers",
            "label":
                "Repeat Customers",
            "operator":
                "/",
        },
        {
            "component_id":
                "active_customers",
            "label":
                "Active Customers",
            "operator":
                "* 100",
        },
    ],
}


# ============================================================
# RELATED METRICS
# ============================================================


RELATED_METRICS = {
    "realized_revenue": [
        "orders",
        "aov",
        "contribution_profit_after_marketing",
    ],

    "contribution_profit_after_marketing": [
        "realized_revenue",
        "marketing_spend",
        "rto_rate_percent",
        "contribution_margin_after_marketing_percent",
    ],

    "blended_roas": [
        "marketing_spend",
        "cac",
        "realized_revenue",
    ],

    "cac": [
        "blended_roas",
        "marketing_spend",
        "repeat_customer_rate_percent",
    ],

    "rto_rate_percent": [
        "ndr_rate_percent",
        "average_delivery_tat_days",
        "contribution_profit_after_marketing",
    ],

    "estimated_trapped_inventory_cost": [
        "inventory_cost_value",
        "realized_revenue",
    ],
}


# ============================================================
# SUGGESTED QUESTIONS
# ============================================================


SUGGESTED_QUESTIONS = {
    "realized_revenue": [
        "Why did revenue change?",
        "Which products drove the change?",
        "Was the change caused by orders or AOV?",
    ],

    "contribution_profit_after_marketing": [
        "Why did contribution profit change?",
        "Which cost line had the largest impact?",
        "What scenario improves contribution margin most?",
    ],

    "blended_roas": [
        "Which channel has the best ROAS?",
        "Which channel should receive more budget?",
        "Is CAC worsening?",
    ],

    "rto_rate_percent": [
        "Why is RTO high?",
        "Which courier has the highest RTO?",
        "How much profit could be recovered if RTO improves?",
    ],

    "estimated_trapped_inventory_cost": [
        "Which SKUs have the most trapped capital?",
        "Which inventory should be redistributed?",
        "Which products need markdown action?",
    ],
}


# ============================================================
# HELPERS
# ============================================================


def _build_sources(
    definition: dict,
) -> list[
    DrilldownSource
]:
    sources = []

    engine = definition.get(
        "source_engine"
    )

    if engine:
        sources.append(
            DrilldownSource(
                source_type="engine",
                source_name=engine,
                description=(
                    "Deterministic ProfitLens "
                    "calculation engine."
                ),
            )
        )

    for table in definition.get(
        "source_tables",
        [],
    ):
        sources.append(
            DrilldownSource(
                source_type="table",
                source_name=table,
                fields=(
                    definition.get(
                        "source_fields",
                        [],
                    )
                ),
            )
        )

    return sources


def _build_components(
    metric_id: str,
    component_values: dict | None,
) -> list[
    DrilldownComponent
]:
    registered = (
        CALCULATION_COMPONENTS.get(
            metric_id,
            [],
        )
    )

    values = (
        component_values
        or {}
    )

    result = []

    for component in registered:

        component_id = (
            component[
                "component_id"
            ]
        )

        value = values.get(
            component_id
        )

        result.append(
            DrilldownComponent(
                component_id=(
                    component_id
                ),
                label=(
                    component[
                        "label"
                    ]
                ),
                operator=(
                    component.get(
                        "operator"
                    )
                ),
                value=value,
                formatted_value=(
                    str(value)
                    if value is not None
                    else None
                ),
            )
        )

    return result


# ============================================================
# MAIN DRILLDOWN BUILDER
# ============================================================


def build_metric_drilldown(
    *,
    metric_id: str,
    value,
    previous_value=None,
    component_values: dict | None = None,
    metadata: dict | None = None,
) -> MetricDrilldown:
    """
    Build a trusted metric drilldown.

    The drilldown itself performs no new financial truth
    calculations. It assembles metric metadata, lineage,
    components and related investigation paths.
    """

    definition = (
        get_metric_definition(
            metric_id
        )
    )

    metric = (
        build_registered_metric(
            metric_id,
            value=value,
            previous_value=(
                previous_value
            ),
            metadata=(
                metadata
                or {}
            ),
        )
    )

    return MetricDrilldown(
        metric=metric,

        calculation_components=(
            _build_components(
                metric_id,
                component_values,
            )
        ),

        sources=(
            _build_sources(
                definition
            )
        ),

        limitations=(
            definition.get(
                "limitations",
                [],
            )
        ),

        data_quality=(
            definition.get(
                "data_quality",
                MetricQuality.verified,
            )
        ),

        related_metrics=(
            RELATED_METRICS.get(
                metric_id,
                [],
            )
        ),

        suggested_questions=(
            SUGGESTED_QUESTIONS.get(
                metric_id,
                [],
            )
        ),

        metadata={
            "grain":
                definition.get(
                    "grain"
                ),

            **(
                metadata
                or {}
            ),
        },
    )
