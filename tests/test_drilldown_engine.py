import pytest

from backend.app.services.drilldown_engine import (
    build_metric_drilldown,
)


def test_revenue_drilldown():
    result = (
        build_metric_drilldown(
            metric_id=(
                "realized_revenue"
            ),
            value=11010422,
            previous_value=20556291,
        )
    )

    assert (
        result.metric.metric_id
        == "realized_revenue"
    )

    assert (
        result.metric.formatted_value
        == "₹1.10Cr"
    )

    assert (
        "orders"
        in result.related_metrics
    )

    assert len(
        result.sources
    ) > 0


def test_contribution_profit_components():
    result = (
        build_metric_drilldown(
            metric_id=(
                "contribution_profit_after_marketing"
            ),
            value=2282453.47,
            previous_value=4474421.10,
            component_values={
                "realized_revenue":
                    11010422,
                "recognized_cogs":
                    4200000,
                "forward_shipping":
                    850000,
                "cod_fees":
                    210000,
                "payment_fees":
                    180000,
                "rto_costs":
                    798000,
                "marketing_spend":
                    1344648.21,
            },
        )
    )

    ids = [
        component.component_id
        for component
        in result.calculation_components
    ]

    assert (
        "realized_revenue"
        in ids
    )

    assert (
        "marketing_spend"
        in ids
    )

    marketing = next(
        component
        for component
        in result.calculation_components
        if component.component_id
        == "marketing_spend"
    )

    assert (
        marketing.operator
        == "-"
    )

    assert (
        marketing.value
        == 1344648.21
    )


def test_rto_drilldown():
    result = (
        build_metric_drilldown(
            metric_id=(
                "rto_rate_percent"
            ),
            value=12.02,
            previous_value=10.0,
            component_values={
                "rto_orders":
                    1142,
                "orders":
                    9501,
            },
        )
    )

    assert (
        len(
            result.calculation_components
        )
        == 2
    )

    assert (
        result.calculation_components[
            0
        ].component_id
        == "rto_orders"
    )

    assert (
        "ndr_rate_percent"
        in result.related_metrics
    )

    assert len(
        result.suggested_questions
    ) > 0


def test_marketing_metric_has_lineage():
    result = (
        build_metric_drilldown(
            metric_id="blended_roas",
            value=5.32,
            previous_value=4.9,
            component_values={
                "attributed_revenue":
                    7155250.34,
                "marketing_spend":
                    1344648.21,
            },
        )
    )

    table_names = {
        source.source_name
        for source in result.sources
        if source.source_type
        == "table"
    }

    assert (
        "marketing"
        in table_names
    )


def test_unknown_metric_rejected():
    with pytest.raises(
        ValueError
    ):
        build_metric_drilldown(
            metric_id=(
                "unknown_metric"
            ),
            value=100,
        )


def test_drilldown_does_not_require_components():
    result = (
        build_metric_drilldown(
            metric_id="cac",
            value=416.43,
        )
    )

    assert (
        result.metric.value
        == 416.43
    )

    assert len(
        result.calculation_components
    ) == 2

    assert all(
        component.value
        is None
        for component
        in result.calculation_components
    )
