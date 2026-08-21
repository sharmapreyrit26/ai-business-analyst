def _get_legacy_kpi_dashboard(
    month: str,
):
    """
    Lazy-load the legacy Olist KPI engine only
    when a legacy reporting period is requested.
    """

    from backend.app.services.kpi_engine import (
        get_kpi_dashboard,
    )

    return get_kpi_dashboard(
        month
    )

from backend.app.services.d2c_financial_engine import (
    get_d2c_financial_summary,
    get_d2c_order_financials,
)

from backend.app.services.d2c_profitability_engine import (
    get_profitability_summary,
)

from backend.app.services.d2c_overview_engine import (
    get_d2c_overview,
)


# ============================================================
# COMMON HELPERS
# ============================================================


def _is_d2c_month(
    month: str,
) -> bool:
    """
    Route 2025 reporting periods to the
    India D2C scenario engine.
    """

    return (
        isinstance(
            month,
            str,
        )
        and month.startswith(
            "2025-"
        )
    )


def _native_float(
    value,
):
    """
    Convert numpy / pandas numeric scalars
    into standard Python floats.

    This keeps API responses JSON-safe and avoids
    values such as np.float64(...) leaking into
    scenario results.
    """

    if value is None:
        return None

    return float(
        value
    )


def _safe_margin(
    profit: float,
    revenue: float,
):
    """
    Calculate contribution margin safely.
    """

    profit = _native_float(
        profit
    )

    revenue = _native_float(
        revenue
    )

    if not revenue:
        return None

    return round(
        (
            profit
            / revenue
        )
        * 100,
        2,
    )


def _get_d2c_base(
    month: str,
):
    """
    Load deterministic D2C financial truth required
    by the scenario engine.
    """

    financial = (
        get_d2c_financial_summary(
            month
        )
    )

    profitability = (
        get_profitability_summary(
            month
        )
    )

    overview = (
        get_d2c_overview(
            month
        )
    )

    return {
        "financial": financial,
        "profitability": profitability,
        "overview": overview,
    }


# ============================================================
# D2C COMMERCIAL SCENARIO
# ============================================================


def simulate_d2c_commercial_change(
    month: str,
    order_change_percent: float = 0,
    aov_change_percent: float = 0,
    marketing_spend_change_percent: float = 0,
):
    """
    Deterministic commercial sensitivity model.

    Supports:
    - order-volume changes
    - AOV changes
    - marketing-spend changes
    - combinations of the above

    Assumptions:

    1. Contribution profit before marketing scales
       proportionally with realized revenue.

    2. Marketing spend changes only when explicitly
       requested.

    3. Marketing spend changes do not independently
       create revenue.

    4. This is a sensitivity calculation, not a forecast.
    """

    base = _get_d2c_base(
        month
    )

    financial = base[
        "financial"
    ]

    profitability = base[
        "profitability"
    ]

    current_orders = _native_float(
        financial[
            "orders"
        ]
    )

    current_aov = _native_float(
        financial[
            "aov"
        ]
    )

    current_revenue = _native_float(
        financial[
            "realized_revenue"
        ]
    )

    current_cp_before = _native_float(
        financial[
            "contribution_profit_before_marketing"
        ]
    )

    current_marketing_spend = _native_float(
        profitability[
            "marketing_spend"
        ]
    )

    current_cp_after = _native_float(
        profitability[
            "contribution_profit_after_marketing"
        ]
    )

    order_change_percent = _native_float(
        order_change_percent
    )

    aov_change_percent = _native_float(
        aov_change_percent
    )

    marketing_spend_change_percent = (
        _native_float(
            marketing_spend_change_percent
        )
    )

    order_factor = (
        1
        + order_change_percent
        / 100
    )

    aov_factor = (
        1
        + aov_change_percent
        / 100
    )

    marketing_factor = (
        1
        + marketing_spend_change_percent
        / 100
    )

    if order_factor < 0:
        raise ValueError(
            "Order scenario cannot produce "
            "negative order volume."
        )

    if aov_factor < 0:
        raise ValueError(
            "AOV scenario cannot produce "
            "negative AOV."
        )

    if marketing_factor < 0:
        raise ValueError(
            "Marketing spend scenario cannot "
            "produce negative marketing spend."
        )

    scenario_orders = _native_float(
        current_orders
        * order_factor
    )

    scenario_aov = _native_float(
        current_aov
        * aov_factor
    )

    commercial_scale = _native_float(
        order_factor
        * aov_factor
    )

    scenario_revenue = _native_float(
        current_revenue
        * commercial_scale
    )

    scenario_cp_before = _native_float(
        current_cp_before
        * commercial_scale
    )

    scenario_marketing_spend = _native_float(
        current_marketing_spend
        * marketing_factor
    )

    scenario_cp_after = _native_float(
        scenario_cp_before
        - scenario_marketing_spend
    )

    return {
        "period": month,

        "scenario": (
            "d2c_commercial_change"
        ),

        "status": "complete",

        "assumptions": {
            "order_change_percent": (
                order_change_percent
            ),

            "aov_change_percent": (
                aov_change_percent
            ),

            "marketing_spend_change_percent": (
                marketing_spend_change_percent
            ),

            "contribution_economics": (
                "Contribution profit before marketing "
                "scales proportionally with realized revenue."
            ),

            "marketing_revenue_response": (
                "No incremental revenue response is "
                "assumed from marketing spend changes."
            ),
        },

        "current": {
            "orders": round(
                current_orders,
                2,
            ),

            "aov": round(
                current_aov,
                2,
            ),

            "revenue": round(
                current_revenue,
                2,
            ),

            "contribution_profit_before_marketing": round(
                current_cp_before,
                2,
            ),

            "marketing_spend": round(
                current_marketing_spend,
                2,
            ),

            "contribution_profit_after_marketing": round(
                current_cp_after,
                2,
            ),

            "contribution_margin_after_marketing_percent": (
                profitability[
                    "contribution_margin_after_marketing_percent"
                ]
            ),
        },

        "scenario_result": {
            "orders": round(
                scenario_orders,
                2,
            ),

            "aov": round(
                scenario_aov,
                2,
            ),

            "revenue": round(
                scenario_revenue,
                2,
            ),

            "contribution_profit_before_marketing": round(
                scenario_cp_before,
                2,
            ),

            "marketing_spend": round(
                scenario_marketing_spend,
                2,
            ),

            "contribution_profit_after_marketing": round(
                scenario_cp_after,
                2,
            ),

            "contribution_margin_after_marketing_percent": (
                _safe_margin(
                    scenario_cp_after,
                    scenario_revenue,
                )
            ),
        },

        "difference": {
            "additional_orders": round(
                scenario_orders
                - current_orders,
                2,
            ),

            "aov_change": round(
                scenario_aov
                - current_aov,
                2,
            ),

            "incremental_revenue": round(
                scenario_revenue
                - current_revenue,
                2,
            ),

            "marketing_spend_change": round(
                scenario_marketing_spend
                - current_marketing_spend,
                2,
            ),

            "incremental_contribution_profit_after_marketing": round(
                scenario_cp_after
                - current_cp_after,
                2,
            ),
        },

        "limitations": [
            (
                "This is a deterministic sensitivity "
                "calculation, not a forecast."
            ),
            (
                "Contribution economics are assumed to "
                "remain proportional to realized revenue."
            ),
            (
                "The model does not estimate price elasticity "
                "or customer demand response."
            ),
            (
                "Marketing-spend changes do not automatically "
                "create additional revenue in this model."
            ),
        ],
    }


# ============================================================
# D2C ORDER RECOVERY
# ============================================================


def simulate_d2c_order_recovery(
    month: str,
    recovery_percent: float,
):
    """
    Recover a percentage of the observed order-volume
    gap versus the previous reporting month.
    """

    financial = (
        get_d2c_financial_summary(
            month
        )
    )

    current_orders = _native_float(
        financial[
            "orders"
        ]
    )

    previous_orders = (
        financial.get(
            "previous_orders"
        )
    )

    if previous_orders is None:
        return {
            "period": month,
            "scenario": (
                "order_recovery"
            ),
            "status": (
                "insufficient_data"
            ),
            "message": (
                "Previous order volume is unavailable."
            ),
        }

    previous_orders = _native_float(
        previous_orders
    )

    recovery_percent = _native_float(
        recovery_percent
    )

    if (
        recovery_percent < 0
        or recovery_percent > 100
    ):
        raise ValueError(
            "Recovery percent must be between "
            "0 and 100."
        )

    lost_orders = _native_float(
        previous_orders
        - current_orders
    )

    if lost_orders <= 0:
        return {
            "period": month,
            "scenario": (
                "order_recovery"
            ),
            "status": (
                "not_applicable"
            ),
            "message": (
                "Order volume did not decline in "
                "the selected period."
            ),
        }

    recovered_orders = _native_float(
        lost_orders
        * recovery_percent
        / 100
    )

    order_change_percent = _native_float(
        recovered_orders
        / current_orders
        * 100
    )

    result = (
        simulate_d2c_commercial_change(
            month=month,
            order_change_percent=(
                order_change_percent
            ),
        )
    )

    result[
        "scenario"
    ] = (
        "order_recovery"
    )

    result[
        "assumptions"
    ][
        "recovery_percent"
    ] = recovery_percent

    result[
        "assumptions"
    ][
        "lost_orders_vs_previous_month"
    ] = round(
        lost_orders,
        2,
    )

    result[
        "difference"
    ][
        "recovered_orders"
    ] = round(
        recovered_orders,
        2,
    )

    return result


# ============================================================
# D2C RTO REDUCTION
# ============================================================


def simulate_d2c_rto_reduction(
    month: str,
    rto_reduction_percent: float,
):
    """
    Deterministic sensitivity model for reducing RTO.

    Assumption:

    Reduced RTO orders convert into delivered orders
    using current average delivered-order economics.

    Marketing spend remains unchanged.
    """

    rto_reduction_percent = (
        _native_float(
            rto_reduction_percent
        )
    )

    if (
        rto_reduction_percent < 0
        or rto_reduction_percent > 100
    ):
        raise ValueError(
            "RTO reduction percent must be "
            "between 0 and 100."
        )

    base = _get_d2c_base(
        month
    )

    financial = base[
        "financial"
    ]

    profitability = base[
        "profitability"
    ]

    overview = base[
        "overview"
    ]

    order_financials = (
        get_d2c_order_financials()
    )

    month_rows = (
        order_financials[
            order_financials[
                "month"
            ]
            == month
        ]
        .copy()
    )

    if month_rows.empty:
        raise ValueError(
            f"Month '{month}' not found in "
            "D2C order financials."
        )

    delivered_rows = (
        month_rows[
            month_rows[
                "order_status"
            ]
            == "Delivered"
        ]
    )

    rto_rows = (
        month_rows[
            month_rows[
                "order_status"
            ]
            == "RTO"
        ]
    )

    if (
        delivered_rows.empty
        or rto_rows.empty
    ):
        return {
            "period": month,
            "scenario": (
                "rto_reduction"
            ),
            "status": (
                "insufficient_data"
            ),
            "message": (
                "Delivered or RTO order economics "
                "are unavailable."
            ),
        }

    current_rto_orders = _native_float(
        len(
            rto_rows
        )
    )

    recovered_rto_orders = _native_float(
        current_rto_orders
        * rto_reduction_percent
        / 100
    )

    average_delivered_revenue = (
        _native_float(
            delivered_rows[
                "realized_revenue"
            ]
            .mean()
        )
    )

    average_delivered_cp = (
        _native_float(
            delivered_rows[
                "contribution_profit_before_marketing"
            ]
            .mean()
        )
    )

    average_rto_cp = (
        _native_float(
            rto_rows[
                "contribution_profit_before_marketing"
            ]
            .mean()
        )
    )

    incremental_revenue = _native_float(
        recovered_rto_orders
        * average_delivered_revenue
    )

    incremental_cp_before = _native_float(
        recovered_rto_orders
        * (
            average_delivered_cp
            - average_rto_cp
        )
    )

    current_revenue = _native_float(
        financial[
            "realized_revenue"
        ]
    )

    current_cp_before = _native_float(
        financial[
            "contribution_profit_before_marketing"
        ]
    )

    current_cp_after = _native_float(
        profitability[
            "contribution_profit_after_marketing"
        ]
    )

    marketing_spend = _native_float(
        profitability[
            "marketing_spend"
        ]
    )

    current_orders = _native_float(
        financial[
            "orders"
        ]
    )

    current_aov = _native_float(
        financial[
            "aov"
        ]
    )

    scenario_revenue = _native_float(
        current_revenue
        + incremental_revenue
    )

    scenario_cp_before = _native_float(
        current_cp_before
        + incremental_cp_before
    )

    scenario_cp_after = _native_float(
        scenario_cp_before
        - marketing_spend
    )

    current_rto_rate = _native_float(
        overview[
            "logistics"
        ][
            "rto_rate_percent"
        ]
    )

    scenario_rto_rate = _native_float(
        current_rto_rate
        * (
            1
            - rto_reduction_percent
            / 100
        )
    )

    scenario_aov = _native_float(
        (
            scenario_revenue
            / current_orders
        )
        if current_orders
        else 0
    )

    return {
        "period": month,

        "scenario": (
            "rto_reduction"
        ),

        "status": "complete",

        "assumptions": {
            "rto_reduction_percent": (
                rto_reduction_percent
            ),

            "recovered_rto_orders_are_delivered": (
                True
            ),

            "delivered_order_economics": (
                "Recovered RTO orders use current "
                "average delivered-order economics."
            ),

            "marketing_spend_held_constant": (
                marketing_spend
            ),
        },

        "current": {
            "orders": round(
                current_orders,
                2,
            ),

            "aov": round(
                current_aov,
                2,
            ),

            "revenue": round(
                current_revenue,
                2,
            ),

            "rto_orders": round(
                current_rto_orders,
                2,
            ),

            "rto_rate_percent": round(
                current_rto_rate,
                2,
            ),

            "contribution_profit_after_marketing": round(
                current_cp_after,
                2,
            ),
        },

        "scenario_result": {
            "orders": round(
                current_orders,
                2,
            ),

            "aov": round(
                scenario_aov,
                2,
            ),

            "revenue": round(
                scenario_revenue,
                2,
            ),

            "rto_orders": round(
                current_rto_orders
                - recovered_rto_orders,
                2,
            ),

            "rto_rate_percent": round(
                scenario_rto_rate,
                2,
            ),

            "contribution_profit_before_marketing": round(
                scenario_cp_before,
                2,
            ),

            "contribution_profit_after_marketing": round(
                scenario_cp_after,
                2,
            ),

            "contribution_margin_after_marketing_percent": (
                _safe_margin(
                    scenario_cp_after,
                    scenario_revenue,
                )
            ),
        },

        "difference": {
            "recovered_rto_orders": round(
                recovered_rto_orders,
                2,
            ),

            "incremental_revenue": round(
                incremental_revenue,
                2,
            ),

            "incremental_contribution_profit_after_marketing": round(
                scenario_cp_after
                - current_cp_after,
                2,
            ),

            "rto_rate_change_percentage_points": round(
                scenario_rto_rate
                - current_rto_rate,
                2,
            ),
        },

        "limitations": [
            (
                "This is a deterministic sensitivity "
                "calculation, not an RTO forecast."
            ),
            (
                "Reduced RTO orders are assumed to "
                "convert into delivered orders."
            ),
            (
                "Recovered orders use current average "
                "delivered-order economics."
            ),
            (
                "The model does not estimate behavioural "
                "changes caused by COD verification, "
                "courier changes or customer interventions."
            ),
        ],
    }


# ============================================================
# D2C MARKETING SPEND
# ============================================================


def simulate_d2c_marketing_spend_change(
    month: str,
    marketing_spend_change_percent: float,
):
    """
    Change marketing spend while keeping revenue constant.

    Profit changes only because marketing spend changes.

    This deliberately avoids inventing an unsupported
    revenue response to incremental marketing spend.
    """

    result = (
        simulate_d2c_commercial_change(
            month=month,
            marketing_spend_change_percent=(
                marketing_spend_change_percent
            ),
        )
    )

    result[
        "scenario"
    ] = (
        "marketing_spend_change"
    )

    return result


# ============================================================
# D2C CAC
# ============================================================


def simulate_d2c_cac_change(
    month: str,
    cac_change_percent: float,
):
    """
    Change CAC while marketing spend remains constant.

    This estimates acquisition volume only.

    Additional customers are NOT translated into revenue,
    orders, LTV or contribution profit because that causal
    relationship has not been deterministically defined.
    """

    profitability = (
        get_profitability_summary(
            month
        )
    )

    current_cac = _native_float(
        profitability[
            "cac"
        ]
    )

    current_spend = _native_float(
        profitability[
            "marketing_spend"
        ]
    )

    current_new_customers = _native_float(
        profitability[
            "new_customers"
        ]
    )

    cac_change_percent = (
        _native_float(
            cac_change_percent
        )
    )

    factor = (
        1
        + cac_change_percent
        / 100
    )

    if factor <= 0:
        raise ValueError(
            "CAC scenario must produce "
            "a positive CAC."
        )

    scenario_cac = _native_float(
        current_cac
        * factor
    )

    scenario_new_customers = (
        _native_float(
            current_spend
            / scenario_cac
        )
    )

    return {
        "period": month,

        "scenario": (
            "cac_change"
        ),

        "status": "complete",

        "assumptions": {
            "cac_change_percent": (
                cac_change_percent
            ),

            "marketing_spend_held_constant": (
                current_spend
            ),

            "customer_revenue_response_modeled": (
                False
            ),
        },

        "current": {
            "cac": round(
                current_cac,
                2,
            ),

            "marketing_spend": round(
                current_spend,
                2,
            ),

            "new_customers": round(
                current_new_customers,
                2,
            ),
        },

        "scenario_result": {
            "cac": round(
                scenario_cac,
                2,
            ),

            "marketing_spend": round(
                current_spend,
                2,
            ),

            "new_customers": round(
                scenario_new_customers,
                2,
            ),
        },

        "difference": {
            "cac_change": round(
                scenario_cac
                - current_cac,
                2,
            ),

            "additional_new_customers": round(
                scenario_new_customers
                - current_new_customers,
                2,
            ),
        },

        "limitations": [
            (
                "Marketing spend is held constant."
            ),
            (
                "The model estimates acquisition "
                "volume from CAC only."
            ),
            (
                "Additional customers are not translated "
                "into revenue, LTV or profit because that "
                "relationship has not been deterministically "
                "defined."
            ),
        ],
    }


# ============================================================
# D2C COMBINED SCENARIO
# ============================================================


def simulate_d2c_combined_change(
    month: str,
    order_change_percent: float = 0,
    aov_change_percent: float = 0,
    rto_reduction_percent: float = 0,
    marketing_spend_change_percent: float = 0,
):
    """
    Combined D2C commercial sensitivity model.

    Execution order:

    1. Orders / AOV / marketing-spend sensitivity.
    2. RTO recovery impact layered on top when requested.

    This remains deterministic and is not a behavioural
    forecast.
    """

    commercial = (
        simulate_d2c_commercial_change(
            month=month,

            order_change_percent=(
                order_change_percent
            ),

            aov_change_percent=(
                aov_change_percent
            ),

            marketing_spend_change_percent=(
                marketing_spend_change_percent
            ),
        )
    )

    commercial[
        "scenario"
    ] = (
        "d2c_combined_change"
    )

    rto_reduction_percent = (
        _native_float(
            rto_reduction_percent
        )
    )

    if not rto_reduction_percent:
        return commercial

    rto = (
        simulate_d2c_rto_reduction(
            month=month,

            rto_reduction_percent=(
                rto_reduction_percent
            ),
        )
    )

    if (
        rto.get(
            "status"
        )
        != "complete"
    ):
        return rto

    rto_incremental_revenue = (
        _native_float(
            rto[
                "difference"
            ][
                "incremental_revenue"
            ]
        )
    )

    rto_incremental_profit = (
        _native_float(
            rto[
                "difference"
            ][
                "incremental_contribution_profit_after_marketing"
            ]
        )
    )

    scenario = commercial[
        "scenario_result"
    ]

    scenario_revenue = _native_float(
        scenario[
            "revenue"
        ]
        + rto_incremental_revenue
    )

    scenario_profit = _native_float(
        scenario[
            "contribution_profit_after_marketing"
        ]
        + rto_incremental_profit
    )

    scenario[
        "revenue"
    ] = round(
        scenario_revenue,
        2,
    )

    scenario[
        "contribution_profit_after_marketing"
    ] = round(
        scenario_profit,
        2,
    )

    scenario[
        "rto_rate_percent"
    ] = _native_float(
        rto[
            "scenario_result"
        ][
            "rto_rate_percent"
        ]
    )

    scenario[
        "rto_orders"
    ] = _native_float(
        rto[
            "scenario_result"
        ][
            "rto_orders"
        ]
    )

    scenario[
        "contribution_margin_after_marketing_percent"
    ] = (
        _safe_margin(
            scenario_profit,
            scenario_revenue,
        )
    )

    commercial_incremental_revenue = (
        _native_float(
            commercial[
                "difference"
            ][
                "incremental_revenue"
            ]
        )
    )

    commercial_incremental_profit = (
        _native_float(
            commercial[
                "difference"
            ][
                "incremental_contribution_profit_after_marketing"
            ]
        )
    )

    commercial[
        "difference"
    ][
        "incremental_revenue"
    ] = round(
        commercial_incremental_revenue
        + rto_incremental_revenue,
        2,
    )

    commercial[
        "difference"
    ][
        "incremental_contribution_profit_after_marketing"
    ] = round(
        commercial_incremental_profit
        + rto_incremental_profit,
        2,
    )

    commercial[
        "difference"
    ][
        "recovered_rto_orders"
    ] = _native_float(
        rto[
            "difference"
        ][
            "recovered_rto_orders"
        ]
    )

    commercial[
        "assumptions"
    ][
        "rto_reduction_percent"
    ] = (
        rto_reduction_percent
    )

    commercial[
        "limitations"
    ].extend(
        [
            (
                "The RTO component assumes reduced "
                "RTO orders convert into delivered orders."
            ),
            (
                "Combined effects are deterministic "
                "sensitivity effects, not behavioural forecasts."
            ),
        ]
    )

    return commercial


# ============================================================
# LEGACY ORDER RECOVERY
# ============================================================


def simulate_order_recovery(
    month: str,
    recovery_percent: float,
):
    """
    Legacy-compatible order-recovery scenario.

    D2C months are automatically routed into the
    D2C scenario engine.
    """

    if _is_d2c_month(
        month
    ):
        return (
            simulate_d2c_order_recovery(
                month,
                recovery_percent,
            )
        )

    kpi = (
        _get_legacy_kpi_dashboard(
            month
        )
    )

    current_orders = (
        kpi[
            "orders"
        ][
            "value"
        ]
    )

    previous_orders = (
        kpi[
            "orders"
        ][
            "previous_value"
        ]
    )

    current_aov = (
        kpi[
            "aov"
        ][
            "value"
        ]
    )

    current_revenue = (
        kpi[
            "revenue"
        ][
            "value"
        ]
    )

    if previous_orders is None:
        return {
            "period": month,
            "scenario": (
                "order_recovery"
            ),
            "status": (
                "insufficient_data"
            ),
            "message": (
                "Previous order volume is unavailable."
            ),
        }

    lost_orders = (
        previous_orders
        - current_orders
    )

    if lost_orders <= 0:
        return {
            "period": month,
            "scenario": (
                "order_recovery"
            ),
            "status": (
                "not_applicable"
            ),
            "message": (
                "Order volume did not decline in "
                "the selected period."
            ),
        }

    recovered_orders = (
        lost_orders
        * recovery_percent
        / 100
    )

    scenario_orders = (
        current_orders
        + recovered_orders
    )

    incremental_revenue = (
        recovered_orders
        * current_aov
    )

    scenario_revenue = (
        current_revenue
        + incremental_revenue
    )

    return {
        "period": month,

        "scenario": (
            "order_recovery"
        ),

        "status": "complete",

        "assumptions": {
            "recovery_percent": (
                recovery_percent
            ),

            "aov_held_constant": (
                current_aov
            ),
        },

        "current": {
            "orders": (
                current_orders
            ),

            "revenue": (
                current_revenue
            ),
        },

        "scenario_result": {
            "orders": round(
                scenario_orders,
                2,
            ),

            "revenue": round(
                scenario_revenue,
                2,
            ),
        },

        "difference": {
            "additional_orders": round(
                recovered_orders,
                2,
            ),

            "incremental_revenue": round(
                incremental_revenue,
                2,
            ),
        },

        "limitations": [
            (
                "AOV is assumed to remain constant."
            ),
            (
                "The scenario does not account for "
                "marketing, inventory, capacity or "
                "profitability effects."
            ),
        ],
    }


# ============================================================
# LEGACY / D2C AOV
# ============================================================


def simulate_aov_change(
    month: str,
    aov_change_percent: float,
):
    """
    AOV scenario compatible with both legacy and D2C data.
    """

    if _is_d2c_month(
        month
    ):

        result = (
            simulate_d2c_commercial_change(
                month=month,

                aov_change_percent=(
                    aov_change_percent
                ),
            )
        )

        result[
            "scenario"
        ] = (
            "aov_change"
        )

        return result

    kpi = (
        _get_legacy_kpi_dashboard(
            month
        )
    )

    current_aov = (
        kpi[
            "aov"
        ][
            "value"
        ]
    )

    current_orders = (
        kpi[
            "orders"
        ][
            "value"
        ]
    )

    current_revenue = (
        kpi[
            "revenue"
        ][
            "value"
        ]
    )

    aov_change = (
        current_aov
        * aov_change_percent
        / 100
    )

    scenario_aov = (
        current_aov
        + aov_change
    )

    scenario_revenue = (
        scenario_aov
        * current_orders
    )

    incremental_revenue = (
        scenario_revenue
        - current_revenue
    )

    return {
        "period": month,

        "scenario": (
            "aov_change"
        ),

        "status": "complete",

        "assumptions": {
            "aov_change_percent": (
                aov_change_percent
            ),

            "orders_held_constant": (
                current_orders
            ),
        },

        "current": {
            "aov": (
                current_aov
            ),

            "orders": (
                current_orders
            ),

            "revenue": (
                current_revenue
            ),
        },

        "scenario_result": {
            "aov": round(
                scenario_aov,
                2,
            ),

            "revenue": round(
                scenario_revenue,
                2,
            ),
        },

        "difference": {
            "aov_change": round(
                aov_change,
                2,
            ),

            "incremental_revenue": round(
                incremental_revenue,
                2,
            ),
        },

        "limitations": [
            (
                "Order volume is assumed "
                "to remain constant."
            ),
            (
                "The scenario does not model "
                "price elasticity or customer "
                "behaviour changes."
            ),
        ],
    }


# ============================================================
# LEGACY / D2C COMBINED ORDER + AOV
# ============================================================


def simulate_combined_change(
    month: str,
    order_change_percent: float = 0,
    aov_change_percent: float = 0,
):
    """
    Combined order/AOV scenario compatible
    with legacy and D2C data.
    """

    if _is_d2c_month(
        month
    ):

        result = (
            simulate_d2c_commercial_change(
                month=month,

                order_change_percent=(
                    order_change_percent
                ),

                aov_change_percent=(
                    aov_change_percent
                ),
            )
        )

        result[
            "scenario"
        ] = (
            "combined_change"
        )

        return result

    kpi = (
        _get_legacy_kpi_dashboard(
            month
        )
    )

    current_orders = (
        kpi[
            "orders"
        ][
            "value"
        ]
    )

    current_aov = (
        kpi[
            "aov"
        ][
            "value"
        ]
    )

    current_revenue = (
        kpi[
            "revenue"
        ][
            "value"
        ]
    )

    scenario_orders = (
        current_orders
        * (
            1
            + order_change_percent
            / 100
        )
    )

    scenario_aov = (
        current_aov
        * (
            1
            + aov_change_percent
            / 100
        )
    )

    scenario_revenue = (
        scenario_orders
        * scenario_aov
    )

    incremental_revenue = (
        scenario_revenue
        - current_revenue
    )

    return {
        "period": month,

        "scenario": (
            "combined_change"
        ),

        "status": "complete",

        "assumptions": {
            "order_change_percent": (
                order_change_percent
            ),

            "aov_change_percent": (
                aov_change_percent
            ),
        },

        "current": {
            "orders": (
                current_orders
            ),

            "aov": (
                current_aov
            ),

            "revenue": (
                current_revenue
            ),
        },

        "scenario_result": {
            "orders": round(
                scenario_orders,
                2,
            ),

            "aov": round(
                scenario_aov,
                2,
            ),

            "revenue": round(
                scenario_revenue,
                2,
            ),
        },

        "difference": {
            "incremental_revenue": round(
                incremental_revenue,
                2,
            ),
        },

        "limitations": [
            (
                "The scenario is mathematical "
                "and does not predict customer response."
            ),
            (
                "Costs and profit impact are not "
                "available with the legacy dataset."
            ),
        ],
    }


# ============================================================
# PUBLIC DISPATCHER
# ============================================================


def run_scenario(
    month: str,
    scenario_type: str,
    **kwargs,
):
    """
    Generic deterministic scenario dispatcher.

    2025 periods:
        India D2C scenario engine

    Other periods:
        temporary legacy scenario engine
    """

    # --------------------------------------------------------
    # ORDER RECOVERY
    # --------------------------------------------------------

    if (
        scenario_type
        == "order_recovery"
    ):

        return (
            simulate_order_recovery(
                month,

                kwargs.get(
                    "recovery_percent",
                    50,
                ),
            )
        )

    # --------------------------------------------------------
    # AOV
    # --------------------------------------------------------

    if (
        scenario_type
        == "aov_change"
    ):

        return (
            simulate_aov_change(
                month,

                kwargs.get(
                    "aov_change_percent",
                    5,
                ),
            )
        )

    # --------------------------------------------------------
    # ORDER / AOV
    # --------------------------------------------------------

    if (
        scenario_type
        == "combined_change"
    ):

        return (
            simulate_combined_change(
                month,

                order_change_percent=(
                    kwargs.get(
                        "order_change_percent",
                        0,
                    )
                ),

                aov_change_percent=(
                    kwargs.get(
                        "aov_change_percent",
                        0,
                    )
                ),
            )
        )

    # --------------------------------------------------------
    # RTO
    # --------------------------------------------------------

    if (
        scenario_type
        == "rto_reduction"
    ):

        if not _is_d2c_month(
            month
        ):
            return {
                "period": month,

                "scenario": (
                    scenario_type
                ),

                "status": (
                    "unsupported_scenario"
                ),

                "message": (
                    "RTO scenarios are supported "
                    "only for the D2C dataset."
                ),
            }

        return (
            simulate_d2c_rto_reduction(
                month,

                kwargs.get(
                    "rto_reduction_percent",
                    10,
                ),
            )
        )

    # --------------------------------------------------------
    # MARKETING SPEND
    # --------------------------------------------------------

    if (
        scenario_type
        == "marketing_spend_change"
    ):

        if not _is_d2c_month(
            month
        ):
            return {
                "period": month,

                "scenario": (
                    scenario_type
                ),

                "status": (
                    "unsupported_scenario"
                ),

                "message": (
                    "Marketing scenarios are supported "
                    "only for the D2C dataset."
                ),
            }

        return (
            simulate_d2c_marketing_spend_change(
                month,

                kwargs.get(
                    "marketing_spend_change_percent",
                    0,
                ),
            )
        )

    # --------------------------------------------------------
    # CAC
    # --------------------------------------------------------

    if (
        scenario_type
        == "cac_change"
    ):

        if not _is_d2c_month(
            month
        ):
            return {
                "period": month,

                "scenario": (
                    scenario_type
                ),

                "status": (
                    "unsupported_scenario"
                ),

                "message": (
                    "CAC scenarios are supported only "
                    "for the D2C dataset."
                ),
            }

        return (
            simulate_d2c_cac_change(
                month,

                kwargs.get(
                    "cac_change_percent",
                    0,
                ),
            )
        )

    # --------------------------------------------------------
    # D2C COMBINED
    # --------------------------------------------------------

    if (
        scenario_type
        == "d2c_combined_change"
    ):

        if not _is_d2c_month(
            month
        ):
            return {
                "period": month,

                "scenario": (
                    scenario_type
                ),

                "status": (
                    "unsupported_scenario"
                ),

                "message": (
                    "D2C combined scenarios are supported "
                    "only for the D2C dataset."
                ),
            }

        return (
            simulate_d2c_combined_change(
                month=month,

                order_change_percent=(
                    kwargs.get(
                        "order_change_percent",
                        0,
                    )
                ),

                aov_change_percent=(
                    kwargs.get(
                        "aov_change_percent",
                        0,
                    )
                ),

                rto_reduction_percent=(
                    kwargs.get(
                        "rto_reduction_percent",
                        0,
                    )
                ),

                marketing_spend_change_percent=(
                    kwargs.get(
                        "marketing_spend_change_percent",
                        0,
                    )
                ),
            )
        )

    # --------------------------------------------------------
    # UNSUPPORTED
    # --------------------------------------------------------

    return {
        "period": month,

        "status": (
            "unsupported_scenario"
        ),

        "scenario": (
            scenario_type
        ),

        "message": (
            f"Scenario type '{scenario_type}' "
            f"is not currently supported."
        ),
    }