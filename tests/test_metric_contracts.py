from backend.app.metric_contracts import (
    MetricDirection,
    MetricSentiment,
    MetricUnit,
)

from backend.app.services.metric_builder import (
    build_metric,
    calculate_change,
    format_metric_value,
    infer_sentiment,
)


def test_calculate_positive_change():
    result = calculate_change(
        120,
        100,
    )

    assert (
        result.change_absolute
        == 20
    )

    assert (
        result.change_percent
        == 20
    )

    assert (
        result.direction
        == MetricDirection.up
    )


def test_calculate_negative_change():
    result = calculate_change(
        80,
        100,
    )

    assert (
        result.change_absolute
        == -20
    )

    assert (
        result.change_percent
        == -20
    )

    assert (
        result.direction
        == MetricDirection.down
    )


def test_zero_previous_value_has_no_percent_change():
    result = calculate_change(
        100,
        0,
    )

    assert (
        result.change_absolute
        == 100
    )

    assert (
        result.change_percent
        is None
    )


def test_currency_formatting():
    assert (
        format_metric_value(
            11010422,
            MetricUnit.currency,
        )
        == "₹1.10Cr"
    )

    assert (
        format_metric_value(
            1344648,
            MetricUnit.currency,
        )
        == "₹13.45L"
    )


def test_percent_formatting():
    assert (
        format_metric_value(
            12.021,
            MetricUnit.percent,
        )
        == "12.02%"
    )


def test_ratio_formatting():
    assert (
        format_metric_value(
            5.32,
            MetricUnit.ratio,
        )
        == "5.32x"
    )


def test_lower_is_better_sentiment():
    comparison = (
        calculate_change(
            10,
            12,
        )
    )

    sentiment = infer_sentiment(
        comparison,
        higher_is_better=False,
    )

    assert (
        sentiment
        == MetricSentiment.positive
    )


def test_higher_is_better_sentiment():
    comparison = (
        calculate_change(
            120,
            100,
        )
    )

    sentiment = infer_sentiment(
        comparison,
        higher_is_better=True,
    )

    assert (
        sentiment
        == MetricSentiment.positive
    )


def test_build_metric():
    metric = build_metric(
        metric_id=(
            "realized_revenue"
        ),
        label=(
            "Realized Revenue"
        ),
        value=11010422,
        previous_value=20556291,
        unit=MetricUnit.currency,
        higher_is_better=True,
        definition=(
            "Revenue recognized "
            "after cancellations and RTO."
        ),
        source_engine=(
            "d2c_financial_engine"
        ),
        source_tables=[
            "orders",
            "order_items",
        ],
    )

    assert (
        metric.metric_id
        == "realized_revenue"
    )

    assert (
        metric.formatted_value
        == "₹1.10Cr"
    )

    assert (
        metric.comparison.direction
        == MetricDirection.down
    )

    assert (
        metric.sentiment
        == MetricSentiment.negative
    )

    assert (
        metric.source.engine
        == "d2c_financial_engine"
    )
