from __future__ import annotations

from hashlib import sha1

from backend.app.alert_contracts import (
    AlertOperator,
    AlertResult,
    AlertRule,
    AlertSeverity,
    AlertStatus,
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
# DEFAULT RULES
# ============================================================


DEFAULT_ALERT_RULES = [
    AlertRule(
        alert_rule_id="ALERT_RTO_HIGH",
        name="High RTO Rate",
        metric_id="rto_rate_percent",
        operator=AlertOperator.greater_than,
        threshold=15.0,
        severity=AlertSeverity.critical,
        page="/logistics",
        description=(
            "Alert when RTO rises above 15%."
        ),
    ),

    AlertRule(
        alert_rule_id="ALERT_NDR_HIGH",
        name="High NDR Rate",
        metric_id="ndr_rate_percent",
        operator=AlertOperator.greater_than,
        threshold=20.0,
        severity=AlertSeverity.warning,
        page="/logistics",
        description=(
            "Alert when NDR exceeds 20%."
        ),
    ),

    AlertRule(
        alert_rule_id="ALERT_ROAS_LOW",
        name="Low Marketing ROAS",
        metric_id="blended_roas",
        operator=AlertOperator.less_than,
        threshold=3.0,
        severity=AlertSeverity.warning,
        page="/marketing",
        description=(
            "Alert when blended ROAS drops below 3x."
        ),
    ),

    AlertRule(
        alert_rule_id="ALERT_CONTRIBUTION_MARGIN_LOW",
        name="Low Contribution Margin",
        metric_id=(
            "contribution_margin_after_marketing_percent"
        ),
        operator=AlertOperator.less_than,
        threshold=18.0,
        severity=AlertSeverity.critical,
        page="/",
        description=(
            "Alert when contribution margin falls below 18%."
        ),
    ),

    AlertRule(
        alert_rule_id="ALERT_REVENUE_DECLINE",
        name="Revenue Decline",
        metric_id="revenue_growth_percent",
        operator=AlertOperator.less_than,
        threshold=-10.0,
        severity=AlertSeverity.warning,
        page="/",
        description=(
            "Alert when revenue declines more than 10%."
        ),
    ),

    AlertRule(
        alert_rule_id="ALERT_TRAPPED_INVENTORY",
        name="High Trapped Inventory",
        metric_id="estimated_trapped_inventory_cost",
        operator=AlertOperator.greater_than,
        threshold=25_000_000,
        severity=AlertSeverity.critical,
        page="/inventory",
        description=(
            "Alert when trapped inventory cost exceeds ₹2.5 Cr."
        ),
    ),
]


# ============================================================
# HELPERS
# ============================================================


def _rule_id(
    name: str,
    metric_id: str,
) -> str:
    digest = (
        sha1(
            f"{name}|{metric_id}".encode(
                "utf-8"
            )
        )
        .hexdigest()[:10]
        .upper()
    )

    return (
        f"ALERT_{digest}"
    )


def evaluate_condition(
    value: float,
    operator: AlertOperator,
    threshold: float,
) -> bool:
    if operator == AlertOperator.greater_than:
        return value > threshold

    if (
        operator
        == AlertOperator.greater_than_or_equal
    ):
        return value >= threshold

    if operator == AlertOperator.less_than:
        return value < threshold

    if (
        operator
        == AlertOperator.less_than_or_equal
    ):
        return value <= threshold

    if operator == AlertOperator.equal:
        return value == threshold

    raise ValueError(
        f"Unsupported alert operator: {operator}"
    )


def build_alert_rule(
    *,
    name: str,
    metric_id: str,
    operator: AlertOperator,
    threshold: float,
    severity: AlertSeverity,
    page: str | None = None,
    description: str | None = None,
    metadata: dict | None = None,
) -> AlertRule:
    return AlertRule(
        alert_rule_id=(
            _rule_id(
                name,
                metric_id,
            )
        ),
        name=name,
        metric_id=metric_id,
        operator=operator,
        threshold=threshold,
        severity=severity,
        page=page,
        description=description,
        metadata=(
            metadata
            or {}
        ),
    )


# ============================================================
# METRIC SNAPSHOT
# ============================================================


def build_alert_metric_snapshot(
    month: str,
) -> dict[str, float]:
    """
    Build one deterministic metric snapshot used
    by alert evaluation.

    No AI logic is involved.
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

    revenue = overview.get(
        "revenue",
        {},
    )

    profitability = overview.get(
        "profitability",
        {},
    )

    snapshot = {
        "revenue_growth_percent":
            revenue.get(
                "revenue_growth_percent"
            ),

        "contribution_margin_after_marketing_percent":
            profitability.get(
                "contribution_margin_after_marketing_percent"
            ),

        "rto_rate_percent":
            logistics.get(
                "rto_rate_percent"
            ),

        "ndr_rate_percent":
            logistics.get(
                "ndr_rate_percent"
            ),

        "blended_roas":
            marketing.get(
                "blended_roas"
            ),

        "estimated_trapped_inventory_cost":
            inventory.get(
                "estimated_trapped_inventory_cost"
            ),
    }

    return {
        key: float(value)
        for key, value
        in snapshot.items()
        if value is not None
    }


# ============================================================
# RULE EVALUATION
# ============================================================


def evaluate_alert_rule(
    rule: AlertRule,
    metrics: dict[str, float],
) -> AlertResult:
    if not rule.enabled:
        return AlertResult(
            alert_rule_id=(
                rule.alert_rule_id
            ),
            name=rule.name,
            metric_id=(
                rule.metric_id
            ),
            triggered=False,
            severity=rule.severity,
            status=(
                AlertStatus.disabled
            ),
            current_value=None,
            threshold=(
                rule.threshold
            ),
            operator=(
                rule.operator
            ),
            message=(
                "Alert rule is disabled."
            ),
            page=rule.page,
            metadata=rule.metadata,
        )

    value = metrics.get(
        rule.metric_id
    )

    if value is None:
        return AlertResult(
            alert_rule_id=(
                rule.alert_rule_id
            ),
            name=rule.name,
            metric_id=(
                rule.metric_id
            ),
            triggered=False,
            severity=rule.severity,
            status=(
                AlertStatus.active
            ),
            current_value=None,
            threshold=(
                rule.threshold
            ),
            operator=(
                rule.operator
            ),
            message=(
                "Metric is unavailable for "
                "this alert evaluation."
            ),
            page=rule.page,
            metadata=rule.metadata,
        )

    triggered = (
        evaluate_condition(
            value,
            rule.operator,
            rule.threshold,
        )
    )

    return AlertResult(
        alert_rule_id=(
            rule.alert_rule_id
        ),
        name=rule.name,
        metric_id=(
            rule.metric_id
        ),
        triggered=triggered,
        severity=rule.severity,
        status=(
            AlertStatus.triggered
            if triggered
            else AlertStatus.active
        ),
        current_value=value,
        threshold=(
            rule.threshold
        ),
        operator=(
            rule.operator
        ),
        message=(
            (
                f"{rule.name} triggered: "
                f"{rule.metric_id} = {value:.2f}"
            )
            if triggered
            else (
                f"{rule.name} is within "
                "the configured threshold."
            )
        ),
        page=rule.page,
        metadata=rule.metadata,
    )


# ============================================================
# FULL ALERT EVALUATION
# ============================================================


def evaluate_alerts(
    month: str,
    rules: list[
        AlertRule
    ] | None = None,
) -> list[
    AlertResult
]:
    metrics = (
        build_alert_metric_snapshot(
            month
        )
    )

    selected_rules = (
        rules
        if rules is not None
        else DEFAULT_ALERT_RULES
    )

    results = [
        evaluate_alert_rule(
            rule,
            metrics,
        )
        for rule
        in selected_rules
    ]

    severity_rank = {
        AlertSeverity.critical: 0,
        AlertSeverity.warning: 1,
        AlertSeverity.info: 2,
    }

    results.sort(
        key=lambda item: (
            not item.triggered,
            severity_rank[
                item.severity
            ],
            item.name,
        )
    )

    return results
