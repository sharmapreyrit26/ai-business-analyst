import pytest

from backend.app.services.scenario_executor import (
    execute_scenario_question,
)

from backend.app.services.scenario_engine import (
    simulate_d2c_commercial_change,
    simulate_d2c_rto_reduction,
    simulate_d2c_cac_change,
    simulate_d2c_marketing_spend_change,
)


MONTH = "2025-11"


def test_d2c_aov_increase_scenario():

    result = execute_scenario_question(
        question=(
            "What if AOV increases by 10%?"
        ),
        month=MONTH,
    )

    assert result["status"] == "complete"
    assert result["scenario_type"] == "aov_change"

    scenario = result["scenario_result"]

    assert (
        scenario["current"]["aov"]
        == pytest.approx(
            1158.87,
            abs=0.01,
        )
    )

    assert (
        scenario["scenario_result"]["aov"]
        == pytest.approx(
            1274.76,
            abs=0.01,
        )
    )

    assert (
        scenario["difference"]["incremental_revenue"]
        == pytest.approx(
            1101042.20,
            abs=0.01,
        )
    )

    assert (
        scenario["difference"][
            "incremental_contribution_profit_after_marketing"
        ]
        == pytest.approx(
            362710.17,
            abs=0.01,
        )
    )


def test_d2c_order_increase_scenario():

    result = execute_scenario_question(
        question=(
            "What if orders increase by 10%?"
        ),
        month=MONTH,
    )

    assert result["status"] == "complete"

    scenario = result["scenario_result"]

    assert (
        scenario["current"]["orders"]
        == pytest.approx(
            9501.0,
            abs=0.01,
        )
    )

    assert (
        scenario["scenario_result"]["orders"]
        == pytest.approx(
            10451.1,
            abs=0.01,
        )
    )

    assert (
        scenario["difference"]["additional_orders"]
        == pytest.approx(
            950.1,
            abs=0.01,
        )
    )


def test_d2c_combined_orders_and_aov():

    result = execute_scenario_question(
        question=(
            "What if orders increase by 10% "
            "and AOV increases by 5%?"
        ),
        month=MONTH,
    )

    assert result["status"] == "complete"

    assert (
        result["scenario_type"]
        == "d2c_combined_change"
    )

    assert (
        result["parameters"][
            "order_change_percent"
        ]
        == 10.0
    )

    assert (
        result["parameters"][
            "aov_change_percent"
        ]
        == 5.0
    )

    scenario = result["scenario_result"]

    assert (
        scenario["scenario_result"]["orders"]
        == pytest.approx(
            10451.1,
            abs=0.01,
        )
    )

    assert (
        scenario["scenario_result"]["aov"]
        == pytest.approx(
            1216.81,
            abs=0.01,
        )
    )

    assert (
        scenario["scenario_result"]["revenue"]
        == pytest.approx(
            12717037.41,
            abs=0.01,
        )
    )


def test_d2c_order_recovery():

    result = execute_scenario_question(
        question=(
            "What happens if we recover "
            "half of lost orders?"
        ),
        month=MONTH,
    )

    assert result["status"] == "complete"

    assert (
        result["scenario_type"]
        == "order_recovery"
    )

    assert (
        result["parameters"][
            "recovery_percent"
        ]
        == 50.0
    )

    scenario = result["scenario_result"]

    assert (
        scenario["difference"][
            "recovered_orders"
        ]
        == pytest.approx(
            4190.5,
            abs=0.01,
        )
    )

    assert (
        scenario["scenario_result"]["orders"]
        == pytest.approx(
            13691.5,
            abs=0.01,
        )
    )


def test_d2c_rto_reduction():

    result = simulate_d2c_rto_reduction(
        month=MONTH,
        rto_reduction_percent=20.0,
    )

    assert result["status"] == "complete"

    assert (
        result["current"][
            "rto_rate_percent"
        ]
        == pytest.approx(
            12.02,
            abs=0.01,
        )
    )

    assert (
        result["scenario_result"][
            "rto_rate_percent"
        ]
        == pytest.approx(
            9.62,
            abs=0.01,
        )
    )

    assert (
        result["difference"][
            "recovered_rto_orders"
        ]
        == pytest.approx(
            228.4,
            abs=0.01,
        )
    )

    assert (
        result["difference"][
            "incremental_revenue"
        ]
        == pytest.approx(
            327952.84,
            abs=0.01,
        )
    )

    assert (
        result["difference"][
            "incremental_contribution_profit_after_marketing"
        ]
        == pytest.approx(
            174596.72,
            abs=0.01,
        )
    )


def test_d2c_marketing_spend_reduction():

    result = (
        simulate_d2c_marketing_spend_change(
            month=MONTH,
            marketing_spend_change_percent=-15.0,
        )
    )

    assert result["status"] == "complete"

    assert (
        result["scenario_result"][
            "marketing_spend"
        ]
        == pytest.approx(
            1142950.98,
            abs=0.01,
        )
    )

    assert (
        result["difference"][
            "marketing_spend_change"
        ]
        == pytest.approx(
            -201697.23,
            abs=0.01,
        )
    )

    assert (
        result["difference"][
            "incremental_contribution_profit_after_marketing"
        ]
        == pytest.approx(
            201697.23,
            abs=0.01,
        )
    )


def test_d2c_cac_reduction():

    result = simulate_d2c_cac_change(
        month=MONTH,
        cac_change_percent=-10.0,
    )

    assert result["status"] == "complete"

    assert (
        result["current"]["cac"]
        == pytest.approx(
            416.43,
            abs=0.01,
        )
    )

    assert (
        result["scenario_result"]["cac"]
        == pytest.approx(
            374.79,
            abs=0.01,
        )
    )

    assert (
        result["scenario_result"][
            "new_customers"
        ]
        == pytest.approx(
            3587.77,
            abs=0.01,
        )
    )


def test_d2c_combined_orders_aov_and_rto():

    result = execute_scenario_question(
        question=(
            "What if orders increase by 10%, "
            "AOV increases by 5%, "
            "and RTO reduces by 20%?"
        ),
        month=MONTH,
    )

    assert result["status"] == "complete"

    assert (
        result["scenario_type"]
        == "d2c_combined_change"
    )

    assert (
        result["parameters"][
            "order_change_percent"
        ]
        == 10.0
    )

    assert (
        result["parameters"][
            "aov_change_percent"
        ]
        == 5.0
    )

    assert (
        result["parameters"][
            "rto_reduction_percent"
        ]
        == 20.0
    )

    scenario = result["scenario_result"]

    assert (
        scenario["scenario_result"][
            "revenue"
        ]
        == pytest.approx(
            13044990.25,
            abs=0.01,
        )
    )

    assert (
        scenario["scenario_result"][
            "contribution_profit_after_marketing"
        ]
        == pytest.approx(
            3019250.95,
            abs=0.01,
        )
    )

    assert (
        scenario["scenario_result"][
            "contribution_margin_after_marketing_percent"
        ]
        == pytest.approx(
            23.14,
            abs=0.01,
        )
    )


def test_d2c_scenario_never_produces_numpy_scalars():

    result = execute_scenario_question(
        question=(
            "What if RTO reduces by 20%?"
        ),
        month=MONTH,
    )

    scenario = result["scenario_result"]

    values = [
        scenario["scenario_result"]["revenue"],
        scenario["scenario_result"]["aov"],
        scenario["scenario_result"][
            "contribution_profit_after_marketing"
        ],
        scenario["difference"][
            "incremental_revenue"
        ],
    ]

    for value in values:
        assert type(value) in {
            int,
            float,
        }


def test_invalid_rto_reduction_rejected():

    with pytest.raises(
        ValueError
    ):
        simulate_d2c_rto_reduction(
            month=MONTH,
            rto_reduction_percent=120.0,
        )


def test_invalid_negative_order_volume_rejected():

    with pytest.raises(
        ValueError
    ):
        simulate_d2c_commercial_change(
            month=MONTH,
            order_change_percent=-150.0,
        )