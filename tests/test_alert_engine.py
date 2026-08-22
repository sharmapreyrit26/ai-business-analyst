from backend.app.alert_contracts import (
    AlertOperator,
    AlertSeverity,
    AlertStatus,
)

from backend.app.services.alert_engine import (
    DEFAULT_ALERT_RULES,
    build_alert_metric_snapshot,
    build_alert_rule,
    evaluate_alert_rule,
    evaluate_alerts,
    evaluate_condition,
)


def test_greater_than_condition():
    assert (
        evaluate_condition(
            20,
            AlertOperator.greater_than,
            15,
        )
        is True
    )


def test_less_than_condition():
    assert (
        evaluate_condition(
            2.5,
            AlertOperator.less_than,
            3,
        )
        is True
    )


def test_build_custom_rule():
    rule = build_alert_rule(
        name="Custom CAC",
        metric_id="cac",
        operator=(
            AlertOperator.greater_than
        ),
        threshold=600,
        severity=(
            AlertSeverity.warning
        ),
    )

    assert (
        rule.alert_rule_id
        .startswith(
            "ALERT_"
        )
    )

    assert (
        rule.metric_id
        == "cac"
    )


def test_alert_rule_triggers():
    rule = build_alert_rule(
        name="High RTO",
        metric_id=(
            "rto_rate_percent"
        ),
        operator=(
            AlertOperator.greater_than
        ),
        threshold=10,
        severity=(
            AlertSeverity.critical
        ),
    )

    result = evaluate_alert_rule(
        rule,
        {
            "rto_rate_percent":
                12.02
        },
    )

    assert (
        result.triggered
        is True
    )

    assert (
        result.status
        == AlertStatus.triggered
    )


def test_alert_rule_not_triggered():
    rule = build_alert_rule(
        name="High RTO",
        metric_id=(
            "rto_rate_percent"
        ),
        operator=(
            AlertOperator.greater_than
        ),
        threshold=20,
        severity=(
            AlertSeverity.warning
        ),
    )

    result = evaluate_alert_rule(
        rule,
        {
            "rto_rate_percent":
                12.02
        },
    )

    assert (
        result.triggered
        is False
    )

    assert (
        result.status
        == AlertStatus.active
    )


def test_disabled_rule():
    rule = build_alert_rule(
        name="Disabled",
        metric_id="rto_rate_percent",
        operator=(
            AlertOperator.greater_than
        ),
        threshold=10,
        severity=(
            AlertSeverity.warning
        ),
    )

    rule.enabled = False

    result = evaluate_alert_rule(
        rule,
        {
            "rto_rate_percent":
                12
        },
    )

    assert (
        result.status
        == AlertStatus.disabled
    )


def test_missing_metric_does_not_crash():
    rule = build_alert_rule(
        name="Unknown Metric",
        metric_id="missing_metric",
        operator=(
            AlertOperator.greater_than
        ),
        threshold=10,
        severity=(
            AlertSeverity.warning
        ),
    )

    result = evaluate_alert_rule(
        rule,
        {},
    )

    assert (
        result.triggered
        is False
    )

    assert (
        result.current_value
        is None
    )


def test_metric_snapshot_november():
    result = (
        build_alert_metric_snapshot(
            "2025-11"
        )
    )

    assert (
        result[
            "rto_rate_percent"
        ]
        == 12.02
    )

    assert (
        result[
            "revenue_growth_percent"
        ]
        == -46.44
    )

    assert (
        result[
            "blended_roas"
        ]
        == 5.32
    )


def test_default_alert_rules_exist():
    assert len(
        DEFAULT_ALERT_RULES
    ) >= 5


def test_november_alerts():
    result = (
        evaluate_alerts(
            "2025-11"
        )
    )

    assert len(
        result
    ) == len(
        DEFAULT_ALERT_RULES
    )

    triggered = [
        item
        for item in result
        if item.triggered
    ]

    assert len(
        triggered
    ) > 0


def test_revenue_decline_alert_triggers_in_november():
    result = (
        evaluate_alerts(
            "2025-11"
        )
    )

    revenue = next(
        item
        for item in result
        if item.metric_id
        == "revenue_growth_percent"
    )

    assert (
        revenue.triggered
        is True
    )


def test_triggered_alerts_sort_first():
    result = (
        evaluate_alerts(
            "2025-11"
        )
    )

    found_non_triggered = False

    for item in result:

        if not item.triggered:
            found_non_triggered = (
                True
            )

        if found_non_triggered:
            assert (
                item.triggered
                is False
            )
