from __future__ import annotations

from hashlib import sha1

from backend.app.investigation_contracts import (
    Investigation,
    InvestigationAction,
    InvestigationConfidence,
    InvestigationDriver,
    InvestigationEvidence,
    InvestigationSeverity,
)

from backend.app.services.d2c_customer_engine import (
    get_customer_summary,
)

from backend.app.services.d2c_inventory_engine import (
    get_inventory_summary,
)

from backend.app.services.d2c_logistics_engine import (
    get_logistics_summary,
)

from backend.app.services.d2c_marketing_engine import (
    get_marketing_summary,
)

from backend.app.services.d2c_overview_engine import (
    get_d2c_overview,
)


# ============================================================
# HELPERS
# ============================================================


def _format_currency(
    value: float | int | None,
) -> str | None:
    if value is None:
        return None

    numeric = float(
        value
    )

    absolute = abs(
        numeric
    )

    sign = (
        "-"
        if numeric < 0
        else ""
    )

    if absolute >= 10_000_000:
        return (
            f"{sign}₹"
            f"{absolute / 10_000_000:.2f} Cr"
        )

    if absolute >= 100_000:
        return (
            f"{sign}₹"
            f"{absolute / 100_000:.2f} L"
        )

    return (
        f"{sign}₹"
        f"{absolute:,.0f}"
    )


def _investigation_id(
    month: str,
    category: str,
    title: str,
) -> str:
    raw = (
        f"{month}|{category}|{title}"
    )

    digest = (
        sha1(
            raw.encode(
                "utf-8"
            )
        )
        .hexdigest()[:10]
        .upper()
    )

    return (
        f"INV_{digest}"
    )


# ============================================================
# REVENUE / PROFITABILITY
# ============================================================


def _build_revenue_investigation(
    month: str,
    overview: dict,
) -> Investigation | None:
    revenue = overview.get(
        "revenue",
        {},
    )

    profitability = overview.get(
        "profitability",
        {},
    )

    revenue_growth = (
        revenue.get(
            "revenue_growth_percent"
        )
    )

    order_growth = (
        revenue.get(
            "order_growth_percent"
        )
    )

    contribution_growth = (
        profitability.get(
            "profit_after_marketing_growth_percent"
        )
    )

    current_revenue = (
        revenue.get(
            "realized_revenue"
        )
    )

    if (
        revenue_growth is None
        or revenue_growth > -10
    ):
        return None

    severity = (
        InvestigationSeverity.critical
        if revenue_growth <= -25
        else InvestigationSeverity.warning
    )

    estimated_impact = None

    if (
        current_revenue is not None
        and revenue_growth != -100
    ):
        previous_revenue = (
            float(current_revenue)
            / (
                1
                + (
                    float(revenue_growth)
                    / 100
                )
            )
        )

        estimated_impact = (
            float(current_revenue)
            - previous_revenue
        )

    drivers = []

    if order_growth is not None:
        drivers.append(
            InvestigationDriver(
                driver_id="order_volume",
                label="Order Volume",
                metric_id="orders",
                evidence=[
                    (
                        "Order growth: "
                        f"{order_growth:.2f}%"
                    )
                ],
            )
        )

    if (
        contribution_growth
        is not None
    ):
        drivers.append(
            InvestigationDriver(
                driver_id=(
                    "contribution_profit"
                ),
                label=(
                    "Contribution Profit"
                ),
                metric_id=(
                    "contribution_profit_after_marketing"
                ),
                evidence=[
                    (
                        "Contribution profit growth: "
                        f"{contribution_growth:.2f}%"
                    )
                ],
            )
        )

    title = (
        "Revenue Has Declined Materially"
    )

    return Investigation(
        investigation_id=(
            _investigation_id(
                month,
                "revenue",
                title,
            )
        ),
        title=title,
        category="revenue",
        severity=severity,
        confidence=(
            InvestigationConfidence.high
        ),
        month=month,
        summary=(
            "Realized revenue declined materially "
            "versus the comparison period."
        ),
        estimated_impact=(
            estimated_impact
        ),
        formatted_impact=(
            _format_currency(
                estimated_impact
            )
        ),
        primary_metric_id=(
            "realized_revenue"
        ),
        drivers=drivers,
        evidence=[
            InvestigationEvidence(
                evidence_id=(
                    "revenue_growth"
                ),
                label=(
                    "Revenue Growth"
                ),
                value=revenue_growth,
                formatted_value=(
                    f"{revenue_growth:.2f}%"
                ),
                metric_id=(
                    "realized_revenue"
                ),
                source_engine=(
                    "d2c_overview_engine"
                ),
            ),
            InvestigationEvidence(
                evidence_id=(
                    "realized_revenue"
                ),
                label=(
                    "Realized Revenue"
                ),
                value=(
                    current_revenue
                ),
                formatted_value=(
                    _format_currency(
                        current_revenue
                    )
                ),
                metric_id=(
                    "realized_revenue"
                ),
                source_engine=(
                    "d2c_overview_engine"
                ),
            ),
        ],
        recommended_actions=[
            InvestigationAction(
                action_id=(
                    "review_order_decline"
                ),
                label=(
                    "Review order-volume decline "
                    "across acquisition, product "
                    "and customer segments."
                ),
                priority=1,
                related_page=(
                    "/products"
                ),
            ),
            InvestigationAction(
                action_id=(
                    "investigate_profit"
                ),
                label=(
                    "Review contribution-profit "
                    "drivers before changing "
                    "growth strategy."
                ),
                priority=2,
                related_page=(
                    "/revenue-profit"
                ),
            ),
        ],
        related_metrics=[
            "orders",
            "aov",
            "contribution_profit_after_marketing",
        ],
        related_pages=[
            "/",
            "/products",
            "/marketing",
        ],
        scenario_suggestions=[
            (
                "What happens if orders "
                "recover by 10%?"
            ),
            (
                "What if orders increase "
                "by 10% and AOV by 5%?"
            ),
        ],
    )


# ============================================================
# LOGISTICS
# ============================================================


def _build_logistics_investigation(
    month: str,
    logistics: dict,
) -> Investigation | None:
    rto = logistics.get(
        "rto_rate_percent"
    )

    ndr = logistics.get(
        "ndr_rate_percent"
    )

    cod_rto = logistics.get(
        "cod_rto_rate_percent"
    )

    on_time = logistics.get(
        "on_time_delivery_percent"
    )

    if (
        rto is None
        or rto < 10
    ):
        return None

    severity = (
        InvestigationSeverity.critical
        if rto >= 15
        else InvestigationSeverity.warning
    )

    title = (
        "RTO Exposure Requires Attention"
    )

    drivers = []

    if cod_rto is not None:
        drivers.append(
            InvestigationDriver(
                driver_id="cod_rto",
                label="COD RTO",
                metric_id=(
                    "rto_rate_percent"
                ),
                evidence=[
                    (
                        "COD RTO rate: "
                        f"{cod_rto:.2f}%"
                    )
                ],
            )
        )

    if ndr is not None:
        drivers.append(
            InvestigationDriver(
                driver_id="ndr",
                label="NDR",
                metric_id=(
                    "ndr_rate_percent"
                ),
                evidence=[
                    (
                        "NDR rate: "
                        f"{ndr:.2f}%"
                    )
                ],
            )
        )

    return Investigation(
        investigation_id=(
            _investigation_id(
                month,
                "logistics",
                title,
            )
        ),
        title=title,
        category="logistics",
        severity=severity,
        confidence=(
            InvestigationConfidence.high
        ),
        month=month,
        summary=(
            "RTO levels are high enough to "
            "create meaningful operational and "
            "profitability risk."
        ),
        primary_metric_id=(
            "rto_rate_percent"
        ),
        drivers=drivers,
        evidence=[
            InvestigationEvidence(
                evidence_id="rto_rate",
                label="RTO Rate",
                value=rto,
                formatted_value=(
                    f"{rto:.2f}%"
                ),
                metric_id=(
                    "rto_rate_percent"
                ),
                source_engine=(
                    "d2c_logistics_engine"
                ),
            ),
            InvestigationEvidence(
                evidence_id=(
                    "on_time_delivery"
                ),
                label=(
                    "On-Time Delivery"
                ),
                value=on_time,
                formatted_value=(
                    (
                        f"{on_time:.2f}%"
                    )
                    if on_time is not None
                    else None
                ),
                source_engine=(
                    "d2c_logistics_engine"
                ),
            ),
        ],
        recommended_actions=[
            InvestigationAction(
                action_id=(
                    "review_cod_risk"
                ),
                label=(
                    "Review COD-heavy segments "
                    "with elevated RTO."
                ),
                priority=1,
                related_page=(
                    "/logistics"
                ),
            ),
            InvestigationAction(
                action_id=(
                    "review_ndr"
                ),
                label=(
                    "Audit NDR handling and "
                    "first-attempt failures."
                ),
                priority=2,
                related_page=(
                    "/logistics"
                ),
            ),
        ],
        related_metrics=[
            "ndr_rate_percent",
            "average_delivery_tat_days",
            "contribution_profit_after_marketing",
        ],
        related_pages=[
            "/logistics",
            "/scenario",
        ],
        scenario_suggestions=[
            (
                "What if RTO reduces by 10%?"
            ),
            (
                "What if RTO reduces by 20%?"
            ),
        ],
    )


# ============================================================
# MARKETING
# ============================================================


def _build_marketing_investigation(
    month: str,
    marketing: dict,
) -> Investigation | None:
    roas = marketing.get(
        "blended_roas"
    )

    cac = marketing.get(
        "cac"
    )

    spend = marketing.get(
        "marketing_spend"
    )

    if roas is None:
        return None

    if roas >= 3:
        return None

    title = (
        "Marketing Efficiency Is Weak"
    )

    return Investigation(
        investigation_id=(
            _investigation_id(
                month,
                "marketing",
                title,
            )
        ),
        title=title,
        category="marketing",
        severity=(
            InvestigationSeverity.warning
        ),
        confidence=(
            InvestigationConfidence.high
        ),
        month=month,
        summary=(
            "Blended ROAS is below the "
            "configured operating threshold."
        ),
        primary_metric_id=(
            "blended_roas"
        ),
        drivers=[
            InvestigationDriver(
                driver_id="roas",
                label="ROAS",
                metric_id=(
                    "blended_roas"
                ),
                evidence=[
                    (
                        "Blended ROAS: "
                        f"{roas:.2f}x"
                    )
                ],
            )
        ],
        evidence=[
            InvestigationEvidence(
                evidence_id="roas",
                label="Blended ROAS",
                value=roas,
                formatted_value=(
                    f"{roas:.2f}x"
                ),
                metric_id=(
                    "blended_roas"
                ),
                source_engine=(
                    "d2c_marketing_engine"
                ),
            ),
            InvestigationEvidence(
                evidence_id="cac",
                label="CAC",
                value=cac,
                formatted_value=(
                    _format_currency(
                        cac
                    )
                ),
                metric_id="cac",
                source_engine=(
                    "d2c_marketing_engine"
                ),
            ),
            InvestigationEvidence(
                evidence_id=(
                    "marketing_spend"
                ),
                label=(
                    "Marketing Spend"
                ),
                value=spend,
                formatted_value=(
                    _format_currency(
                        spend
                    )
                ),
                metric_id=(
                    "marketing_spend"
                ),
                source_engine=(
                    "d2c_marketing_engine"
                ),
            ),
        ],
        recommended_actions=[
            InvestigationAction(
                action_id=(
                    "review_channel_efficiency"
                ),
                label=(
                    "Review channel-level ROAS "
                    "and CAC before reallocating spend."
                ),
                priority=1,
                related_page=(
                    "/marketing"
                ),
            ),
        ],
        related_metrics=[
            "cac",
            "marketing_spend",
            "realized_revenue",
        ],
        related_pages=[
            "/marketing",
            "/scenario",
        ],
        scenario_suggestions=[
            (
                "What if marketing spend "
                "decreases by 10%?"
            ),
        ],
    )


# ============================================================
# INVENTORY
# ============================================================


def _build_inventory_investigation(
    month: str,
    inventory: dict,
) -> Investigation | None:
    trapped_cost = inventory.get(
        "estimated_trapped_inventory_cost"
    )

    overstock = inventory.get(
        "overstock_positions"
    )

    below_reorder = inventory.get(
        "below_reorder_positions"
    )

    if (
        trapped_cost is None
        or trapped_cost <= 0
    ):
        return None

    severity = (
        InvestigationSeverity.critical
        if trapped_cost >= 25_000_000
        else InvestigationSeverity.warning
    )

    title = (
        "Inventory Working Capital Is Trapped"
    )

    return Investigation(
        investigation_id=(
            _investigation_id(
                month,
                "inventory",
                title,
            )
        ),
        title=title,
        category="inventory",
        severity=severity,
        confidence=(
            InvestigationConfidence.high
        ),
        month=month,
        summary=(
            "Excess and slow-moving inventory "
            "is tying up meaningful working capital."
        ),
        estimated_impact=(
            trapped_cost
        ),
        formatted_impact=(
            _format_currency(
                trapped_cost
            )
        ),
        primary_metric_id=(
            "estimated_trapped_inventory_cost"
        ),
        drivers=[
            InvestigationDriver(
                driver_id="overstock",
                label=(
                    "Overstock Positions"
                ),
                evidence=(
                    [
                        (
                            "Overstock positions: "
                            f"{overstock}"
                        )
                    ]
                    if overstock is not None
                    else []
                ),
            ),
            InvestigationDriver(
                driver_id=(
                    "reorder_risk"
                ),
                label=(
                    "Reorder Risk"
                ),
                evidence=(
                    [
                        (
                            "Below-reorder positions: "
                            f"{below_reorder}"
                        )
                    ]
                    if below_reorder is not None
                    else []
                ),
            ),
        ],
        evidence=[
            InvestigationEvidence(
                evidence_id=(
                    "trapped_inventory"
                ),
                label=(
                    "Trapped Inventory Cost"
                ),
                value=(
                    trapped_cost
                ),
                formatted_value=(
                    _format_currency(
                        trapped_cost
                    )
                ),
                metric_id=(
                    "estimated_trapped_inventory_cost"
                ),
                source_engine=(
                    "d2c_inventory_engine"
                ),
            ),
        ],
        recommended_actions=[
            InvestigationAction(
                action_id=(
                    "review_excess_stock"
                ),
                label=(
                    "Review high-value excess "
                    "SKUs for markdown, redistribution "
                    "or procurement reduction."
                ),
                priority=1,
                related_page=(
                    "/inventory"
                ),
            ),
            InvestigationAction(
                action_id=(
                    "review_reorders"
                ),
                label=(
                    "Prioritize below-reorder SKUs "
                    "with the highest revenue at risk."
                ),
                priority=2,
                related_page=(
                    "/inventory"
                ),
            ),
        ],
        related_metrics=[
            "inventory_cost_value",
            "realized_revenue",
        ],
        related_pages=[
            "/inventory",
        ],
    )


# ============================================================
# MAIN ENGINE
# ============================================================


def generate_investigations(
    month: str,
) -> list[
    Investigation
]:
    """
    Generate deterministic ProfitLens investigations.

    The engine does not use an LLM to decide whether
    a business issue exists.

    AI may later explain or summarize these objects,
    but financial and operational truth remains
    deterministic.
    """

    overview = get_d2c_overview(
        month
    )

    logistics = (
        get_logistics_summary(
            month
        )
    )

    marketing = (
        get_marketing_summary(
            month
        )
    )

    inventory = (
        get_inventory_summary()
    )

    # Loaded now so the engine has the customer
    # domain available for future rules.
    get_customer_summary(
        month
    )

    investigations = []

    builders = [
        (
            _build_revenue_investigation,
            overview,
        ),
        (
            _build_logistics_investigation,
            logistics,
        ),
        (
            _build_marketing_investigation,
            marketing,
        ),
        (
            _build_inventory_investigation,
            inventory,
        ),
    ]

    for builder, context in builders:

        investigation = builder(
            month,
            context,
        )

        if investigation:
            investigations.append(
                investigation
            )

    severity_rank = {
        InvestigationSeverity.critical:
            0,

        InvestigationSeverity.warning:
            1,

        InvestigationSeverity.info:
            2,
    }

    investigations.sort(
        key=lambda item: (
            severity_rank[
                item.severity
            ],
            -abs(
                item.estimated_impact
                or 0
            ),
            item.title,
        )
    )

    return investigations
