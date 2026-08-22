import pytest

from backend.app.metric_contracts import (
    MetricSentiment,
)

from backend.app.services.metric_dictionary_service import (
    build_registered_metric,
    get_metric_definition,
    get_metric_lineage,
    list_metric_definitions,
    search_metric_definitions,
)


def test_get_metric_definition():
    result = get_metric_definition(
        "rto_rate_percent"
    )

    assert (
        result["label"]
        == "RTO Rate"
    )

    assert (
        result["formula"]
        == (
            "RTO Orders / "
            "Total Orders * 100"
        )
    )

    assert (
        result["source_engine"]
        == "d2c_logistics_engine"
    )


def test_unknown_metric_rejected():
    with pytest.raises(
        ValueError
    ):
        get_metric_definition(
            "does_not_exist"
        )


def test_metric_list_contains_core_metrics():
    metrics = (
        list_metric_definitions()
    )

    ids = {
        metric["metric_id"]
        for metric in metrics
    }

    assert (
        "realized_revenue"
        in ids
    )

    assert (
        "blended_roas"
        in ids
    )

    assert (
        "rto_rate_percent"
        in ids
    )

    assert (
        "estimated_trapped_inventory_cost"
        in ids
    )


def test_metric_search():
    results = (
        search_metric_definitions(
            "inventory"
        )
    )

    assert len(
        results
    ) >= 2

    assert all(
        (
            "inventory"
            in (
                item["metric_id"]
                + " "
                + item["label"]
                + " "
                + item["definition"]
            ).lower()
        )
        for item in results
    )


def test_metric_lineage():
    lineage = (
        get_metric_lineage(
            "contribution_profit_after_marketing"
        )
    )

    assert (
        "marketing"
        in lineage[
            "source_tables"
        ]
    )

    assert (
        lineage[
            "source_engine"
        ]
        == "d2c_profitability_engine"
    )

    assert (
        lineage["grain"]
        == "brand_period"
    )


def test_registered_metric_uses_dictionary_metadata():
    metric = (
        build_registered_metric(
            "rto_rate_percent",
            value=12.02,
            previous_value=10.0,
        )
    )

    assert (
        metric.label
        == "RTO Rate"
    )

    assert (
        metric.formatted_value
        == "12.02%"
    )

    assert (
        metric.sentiment
        == MetricSentiment.negative
    )

    assert (
        metric.source.engine
        == "d2c_logistics_engine"
    )


def test_registered_revenue_metric():
    metric = (
        build_registered_metric(
            "realized_revenue",
            value=11010422,
            previous_value=20556291,
        )
    )

    assert (
        metric.formatted_value
        == "₹1.10Cr"
    )

    assert (
        metric.sentiment
        == MetricSentiment.negative
    )

    assert (
        metric.metadata[
            "grain"
        ]
        == "brand_period"
    )
