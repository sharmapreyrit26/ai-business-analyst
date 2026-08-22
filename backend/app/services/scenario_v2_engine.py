from __future__ import annotations

from backend.app.scenario_v2_contracts import (
    ScenarioChanges,
    ScenarioControlCapability,
    ScenarioExplanation,
    ScenarioV2Request,
    ScenarioV2Response,
    ScenarioWaterfallItem,
)

from backend.app.services.scenario_engine import (
    run_scenario,
)


# ============================================================
# CAPABILITY REGISTRY
# ============================================================


SCENARIO_CONTROLS = [
    ScenarioControlCapability(
        control_id="orders_change_percent",
        label="Orders",
        unit="percent",
        enabled=True,
        combined_supported=True,
        minimum=-90,
        maximum=200,
        step=1,
        description=(
            "Change total order volume while "
            "holding other assumptions constant."
        ),
    ),

    ScenarioControlCapability(
        control_id="aov_change_percent",
        label="Average Order Value",
        unit="percent",
        enabled=True,
        combined_supported=True,
        minimum=-90,
        maximum=200,
        step=1,
        description=(
            "Change average order value."
        ),
    ),

    ScenarioControlCapability(
        control_id="rto_reduction_percent",
        label="RTO Reduction",
        unit="percent",
        enabled=True,
        combined_supported=True,
        minimum=0,
        maximum=100,
        step=1,
        description=(
            "Model the financial impact of "
            "reducing return-to-origin exposure."
        ),
    ),

    ScenarioControlCapability(
        control_id="marketing_spend_change_percent",
        label="Marketing Spend",
        unit="percent",
        enabled=True,
        combined_supported=True,
        minimum=-100,
        maximum=300,
        step=1,
        description=(
            "Change aggregate marketing spend."
        ),
    ),

    ScenarioControlCapability(
        control_id="cac_change_percent",
        label="CAC",
        unit="percent",
        enabled=True,
        combined_supported=False,
        minimum=-90,
        maximum=300,
        step=1,
        description=(
            "Model customer acquisition cost changes."
        ),
        limitation=(
            "CAC currently runs as a standalone "
            "scenario and is not combined with the "
            "main operating scenario."
        ),
    ),

    ScenarioControlCapability(
        control_id="discount_rate_change_percent",
        label="Discount Rate",
        unit="percent",
        enabled=False,
        combined_supported=False,
        minimum=-100,
        maximum=100,
        step=1,
        description=(
            "Future deterministic discount-rate scenario."
        ),
        limitation=(
            "Disabled until ProfitLens has a "
            "deterministic discount elasticity and "
            "margin-impact model."
        ),
    ),
]


# ============================================================
# HELPERS
# ============================================================


def get_scenario_v2_capabilities():
    """
    Return controls that the future Scenario Lab
    should render.

    Disabled controls remain visible to the frontend so
    the UI can explain upcoming/unsupported assumptions
    rather than silently pretending they are calculated.
    """

    return [
        item.model_dump()
        for item in SCENARIO_CONTROLS
    ]


def _validate_changes(
    changes: ScenarioChanges,
):
    if (
        changes.rto_reduction_percent
        < 0
        or changes.rto_reduction_percent
        > 100
    ):
        raise ValueError(
            "rto_reduction_percent must be "
            "between 0 and 100."
        )

    if (
        changes.orders_change_percent
        <= -100
    ):
        raise ValueError(
            "orders_change_percent cannot "
            "reduce orders by 100% or more."
        )

    if (
        changes.aov_change_percent
        <= -100
    ):
        raise ValueError(
            "aov_change_percent cannot "
            "reduce AOV by 100% or more."
        )

    if (
        changes.marketing_spend_change_percent
        < -100
    ):
        raise ValueError(
            "marketing_spend_change_percent "
            "cannot be below -100%."
        )

    if (
        changes.discount_rate_change_percent
        != 0
    ):
        raise ValueError(
            "Discount-rate scenarios are not yet "
            "supported by the deterministic engine."
        )


def _has_main_combined_changes(
    changes: ScenarioChanges,
) -> bool:
    return any(
        [
            changes.orders_change_percent != 0,
            changes.aov_change_percent != 0,
            changes.rto_reduction_percent != 0,
            changes.marketing_spend_change_percent != 0,
        ]
    )


def _format_currency(
    value,
):
    if value is None:
        return None

    numeric = float(
        value
    )

    sign = (
        "+"
        if numeric > 0
        else ""
    )

    return (
        f"{sign}₹{numeric:,.2f}"
    )


# ============================================================
# WATERFALL
# ============================================================


def _build_waterfall(
    difference: dict,
) -> list[
    ScenarioWaterfallItem
]:
    mappings = [
        (
            "incremental_revenue",
            "Revenue Impact",
        ),
        (
            "incremental_contribution_profit_after_marketing",
            "Contribution Profit Impact",
        ),
        (
            "marketing_spend_change",
            "Marketing Spend Change",
        ),
        (
            "recovered_rto_orders",
            "Recovered RTO Orders",
        ),
    ]

    result = []

    for (
        driver_id,
        label,
    ) in mappings:

        if (
            driver_id
            not in difference
        ):
            continue

        value = (
            difference.get(
                driver_id
            )
        )

        if value is None:
            continue

        numeric = float(
            value
        )

        direction = "neutral"

        if numeric > 0:
            direction = "positive"

        elif numeric < 0:
            direction = "negative"

        if (
            driver_id
            == "recovered_rto_orders"
        ):
            formatted = (
                f"{numeric:,.1f}"
            )

        else:
            formatted = (
                _format_currency(
                    numeric
                )
            )

        result.append(
            ScenarioWaterfallItem(
                driver_id=driver_id,
                label=label,
                impact=numeric,
                formatted_impact=(
                    formatted
                ),
                direction=direction,
            )
        )

    return result


# ============================================================
# EXPLANATIONS
# ============================================================


def _build_explanations(
    changes: ScenarioChanges,
    difference: dict,
) -> list[
    ScenarioExplanation
]:
    result = []

    incremental_revenue = (
        difference.get(
            "incremental_revenue"
        )
    )

    incremental_profit = (
        difference.get(
            "incremental_contribution_profit_after_marketing"
        )
    )

    if (
        incremental_revenue
        is not None
    ):
        result.append(
            ScenarioExplanation(
                headline=(
                    "Revenue impact"
                ),
                explanation=(
                    "Projected revenue changes because "
                    "the scenario modifies order volume, "
                    "AOV and/or recovered RTO exposure."
                ),
                evidence=[
                    (
                        "Incremental revenue: "
                        f"{_format_currency(incremental_revenue)}"
                    ),
                    (
                        "Orders change: "
                        f"{changes.orders_change_percent:.2f}%"
                    ),
                    (
                        "AOV change: "
                        f"{changes.aov_change_percent:.2f}%"
                    ),
                ],
            )
        )

    if (
        incremental_profit
        is not None
    ):
        result.append(
            ScenarioExplanation(
                headline=(
                    "Contribution profit impact"
                ),
                explanation=(
                    "Contribution profit reflects the "
                    "deterministic operating and marketing "
                    "effects produced by the underlying "
                    "ProfitLens scenario engine."
                ),
                evidence=[
                    (
                        "Incremental contribution profit: "
                        f"{_format_currency(incremental_profit)}"
                    ),
                    (
                        "Marketing spend change: "
                        f"{changes.marketing_spend_change_percent:.2f}%"
                    ),
                    (
                        "RTO reduction: "
                        f"{changes.rto_reduction_percent:.2f}%"
                    ),
                ],
            )
        )

    return result


# ============================================================
# ASSUMPTIONS
# ============================================================


def _build_assumptions(
    changes: ScenarioChanges,
) -> list[str]:
    assumptions = [
        (
            "Scenario calculations are deterministic "
            "what-if estimates, not forecasts."
        ),
        (
            "Only explicitly changed variables are "
            "modified unless the underlying scenario "
            "engine requires a linked calculation."
        ),
        (
            "Historical unit economics from the selected "
            "period are used as the scenario baseline."
        ),
    ]

    if (
        changes.marketing_spend_change_percent
        != 0
    ):
        assumptions.append(
            (
                "Marketing-spend changes do not assume "
                "a new attribution or media-response curve "
                "unless explicitly modeled by the engine."
            )
        )

    if (
        changes.rto_reduction_percent
        != 0
    ):
        assumptions.append(
            (
                "Recovered RTO economics use observed "
                "period-level order economics."
            )
        )

    return assumptions


# ============================================================
# MAIN ENGINE
# ============================================================


def run_scenario_v2(
    request: ScenarioV2Request,
) -> ScenarioV2Response:
    """
    Execute the structured Scenario Lab contract.

    This layer never invents financial calculations.

    It delegates numerical truth to the existing
    deterministic scenario_engine and converts the
    result into a stable frontend-oriented contract.
    """

    changes = (
        request.changes
    )

    _validate_changes(
        changes
    )

    main_changes = (
        _has_main_combined_changes(
            changes
        )
    )

    cac_changed = (
        changes.cac_change_percent
        != 0
    )

    if (
        main_changes
        and cac_changed
    ):
        raise ValueError(
            "CAC cannot currently be combined with "
            "orders, AOV, RTO or marketing-spend "
            "changes in one deterministic scenario."
        )

    if cac_changed:

        raw = run_scenario(
            request.month,
            "cac_change",
            cac_change_percent=(
                changes.cac_change_percent
            ),
        )

        scenario_type = (
            "cac_change"
        )

    else:

        raw = run_scenario(
            request.month,
            "d2c_combined_change",
            order_change_percent=(
                changes.orders_change_percent
            ),
            aov_change_percent=(
                changes.aov_change_percent
            ),
            rto_reduction_percent=(
                changes.rto_reduction_percent
            ),
            marketing_spend_change_percent=(
                changes.marketing_spend_change_percent
            ),
        )

        scenario_type = (
            "d2c_combined_change"
        )

    current = (
        raw.get(
            "current",
            {},
        )
    )

    projected = (
        raw.get(
            "scenario_result",
            {},
        )
    )

    difference = (
        raw.get(
            "difference",
            {},
        )
    )

    limitations = list(
        raw.get(
            "limitations",
            [],
        )
        or []
    )

    if (
        changes.cac_change_percent
        != 0
    ):
        limitations.append(
            (
                "CAC scenario currently executes "
                "independently from the combined "
                "operating scenario."
            )
        )

    return ScenarioV2Response(
        status=raw.get(
            "status",
            "complete",
        ),

        month=request.month,

        name=request.name,

        scenario_type=(
            scenario_type
        ),

        changes=changes,

        current=current,

        projected=projected,

        difference=difference,

        waterfall=(
            _build_waterfall(
                difference
            )
        ),

        explanations=(
            _build_explanations(
                changes,
                difference,
            )
        ),

        assumptions=(
            _build_assumptions(
                changes
            )
        ),

        limitations=limitations,
    )
