import math

import pytest

from backend.app.services.financial_analysis import (
    get_monthly_data_quality,
    get_monthly_revenue_analysis,
)

from backend.app.services.kpi_engine import (
    get_kpi_dashboard,
)

from backend.app.services.scenario_engine import (
    simulate_aov_change,
    simulate_combined_change,
    simulate_order_recovery,
)


def test_june_2018_revenue_analysis():
    result = get_monthly_revenue_analysis(
        "2018-06"
    )

    assert result["month"] == "2018-06"
    assert result["previous_month"] == "2018-05"

    assert math.isclose(
        result["revenue"],
        865124.31,
        abs_tol=0.01,
    )

    assert math.isclose(
        result["previous_revenue"],
        996517.68,
        abs_tol=0.01,
    )

    assert math.isclose(
        result["revenue_change_percent"],
        -13.19,
        abs_tol=0.01,
    )

    assert result["orders"] == 6160
    assert result["previous_orders"] == 6853

    assert math.isclose(
        result["order_change_percent"],
        -10.11,
        abs_tol=0.01,
    )

    assert math.isclose(
        result["aov"],
        140.44,
        abs_tol=0.01,
    )

    assert math.isclose(
        result["previous_aov"],
        145.41,
        abs_tol=0.01,
    )

    assert math.isclose(
        result["aov_change_percent"],
        -3.42,
        abs_tol=0.01,
    )


def test_invalid_month_raises_value_error():
    with pytest.raises(
        ValueError,
        match="not found",
    ):
        get_monthly_revenue_analysis(
            "2099-01"
        )


def test_monthly_data_quality_contract():
    result = get_monthly_data_quality()

    assert len(result) > 0

    for item in result:
        assert "month" in item
        assert "data_quality" in item
        assert "status" in item
        assert "is_partial_month" in item
        assert "orders" in item

        assert (
            item["data_quality"]
            == item["status"]
        )

        assert item[
            "data_quality"
        ] in {
            "complete",
            "partial",
        }


def test_june_2018_is_not_partial():
    quality = {
        item["month"]: item
        for item in get_monthly_data_quality()
    }

    june = quality["2018-06"]

    assert (
        june["data_quality"]
        == "complete"
    )

    assert (
        june["is_partial_month"]
        is False
    )


def test_kpi_dashboard_matches_financial_analysis():
    financial = (
        get_monthly_revenue_analysis(
            "2018-06"
        )
    )

    dashboard = (
        get_kpi_dashboard(
            "2018-06"
        )
    )

    assert math.isclose(
        dashboard["revenue"]["value"],
        financial["revenue"],
        abs_tol=0.01,
    )

    assert math.isclose(
        dashboard[
            "revenue"
        ][
            "growth_percent"
        ],
        financial[
            "revenue_change_percent"
        ],
        abs_tol=0.01,
    )

    assert (
        dashboard["orders"]["value"]
        == financial["orders"]
    )

    assert math.isclose(
        dashboard[
            "orders"
        ][
            "growth_percent"
        ],
        financial[
            "order_change_percent"
        ],
        abs_tol=0.01,
    )

    assert math.isclose(
        dashboard["aov"]["value"],
        financial["aov"],
        abs_tol=0.01,
    )

    assert math.isclose(
        dashboard[
            "aov"
        ][
            "growth_percent"
        ],
        financial[
            "aov_change_percent"
        ],
        abs_tol=0.01,
    )


def test_aov_increase_scenario_math():
    result = simulate_aov_change(
        "2018-06",
        12,
    )

    assert (
        result["status"]
        == "complete"
    )

    assert math.isclose(
        result[
            "scenario_result"
        ][
            "aov"
        ],
        157.29,
        abs_tol=0.01,
    )

    assert math.isclose(
        result[
            "scenario_result"
        ][
            "revenue"
        ],
        968923.65,
        abs_tol=0.01,
    )

    assert math.isclose(
        result[
            "difference"
        ][
            "incremental_revenue"
        ],
        103799.34,
        abs_tol=0.01,
    )


def test_order_recovery_scenario_math():
    result = simulate_order_recovery(
        "2018-06",
        50,
    )

    assert (
        result["status"]
        == "complete"
    )

    assert math.isclose(
        result[
            "scenario_result"
        ][
            "orders"
        ],
        6506.5,
        abs_tol=0.01,
    )

    assert math.isclose(
        result[
            "difference"
        ][
            "additional_orders"
        ],
        346.5,
        abs_tol=0.01,
    )

    assert math.isclose(
        result[
            "difference"
        ][
            "incremental_revenue"
        ],
        48662.46,
        abs_tol=0.01,
    )


def test_combined_scenario_math():
    result = simulate_combined_change(
        "2018-06",
        5,
        5,
    )

    assert (
        result["status"]
        == "complete"
    )

    assert math.isclose(
        result[
            "scenario_result"
        ][
            "orders"
        ],
        6468.0,
        abs_tol=0.01,
    )

    assert math.isclose(
        result[
            "scenario_result"
        ][
            "aov"
        ],
        147.46,
        abs_tol=0.01,
    )

    assert math.isclose(
        result[
            "scenario_result"
        ][
            "revenue"
        ],
        953784.22,
        abs_tol=0.01,
    )

    assert math.isclose(
        result[
            "difference"
        ][
            "incremental_revenue"
        ],
        88659.91,
        abs_tol=0.01,
    )
