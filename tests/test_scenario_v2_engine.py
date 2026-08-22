import pytest

from backend.app.scenario_v2_contracts import (
    ScenarioChanges,
    ScenarioV2Request,
)

from backend.app.services.scenario_v2_engine import (
    get_scenario_v2_capabilities,
    run_scenario_v2,
)


def test_scenario_capabilities():
    result = (
        get_scenario_v2_capabilities()
    )

    ids = {
        item["control_id"]
        for item in result
    }

    assert (
        "orders_change_percent"
        in ids
    )

    assert (
        "rto_reduction_percent"
        in ids
    )

    assert (
        "discount_rate_change_percent"
        in ids
    )

    discount = next(
        item
        for item in result
        if item["control_id"]
        == "discount_rate_change_percent"
    )

    assert (
        discount["enabled"]
        is False
    )


def test_combined_scenario_v2():
    result = (
        run_scenario_v2(
            ScenarioV2Request(
                month="2025-11",
                name="Growth + RTO",
                changes=(
                    ScenarioChanges(
                        orders_change_percent=10,
                        aov_change_percent=5,
                        rto_reduction_percent=20,
                        marketing_spend_change_percent=0,
                    )
                ),
            )
        )
    )

    assert (
        result.status
        == "complete"
    )

    assert (
        result.scenario_type
        == "d2c_combined_change"
    )

    assert (
        result.current[
            "orders"
        ]
        == 9501.0
    )

    assert (
        result.projected[
            "revenue"
        ]
        > result.current[
            "revenue"
        ]
    )

    assert (
        result.difference[
            "incremental_revenue"
        ]
        > 0
    )

    assert len(
        result.waterfall
    ) > 0

    assert len(
        result.explanations
    ) > 0

    assert len(
        result.assumptions
    ) > 0


def test_rto_scenario_v2():
    result = (
        run_scenario_v2(
            ScenarioV2Request(
                month="2025-11",
                changes=(
                    ScenarioChanges(
                        rto_reduction_percent=20
                    )
                ),
            )
        )
    )

    assert (
        result.projected[
            "rto_rate_percent"
        ]
        < 12.02
    )

    assert (
        result.difference[
            "recovered_rto_orders"
        ]
        > 0
    )


def test_marketing_reduction_v2():
    result = (
        run_scenario_v2(
            ScenarioV2Request(
                month="2025-11",
                changes=(
                    ScenarioChanges(
                        marketing_spend_change_percent=-10
                    )
                ),
            )
        )
    )

    assert (
        result.difference[
            "marketing_spend_change"
        ]
        < 0
    )


def test_cac_scenario_v2():
    result = (
        run_scenario_v2(
            ScenarioV2Request(
                month="2025-11",
                changes=(
                    ScenarioChanges(
                        cac_change_percent=-10
                    )
                ),
            )
        )
    )

    assert (
        result.scenario_type
        == "cac_change"
    )


def test_cac_cannot_be_combined_yet():
    with pytest.raises(
        ValueError
    ):
        run_scenario_v2(
            ScenarioV2Request(
                month="2025-11",
                changes=(
                    ScenarioChanges(
                        orders_change_percent=10,
                        cac_change_percent=-10,
                    )
                ),
            )
        )


def test_discount_scenario_rejected_until_model_exists():
    with pytest.raises(
        ValueError
    ):
        run_scenario_v2(
            ScenarioV2Request(
                month="2025-11",
                changes=(
                    ScenarioChanges(
                        discount_rate_change_percent=-5
                    )
                ),
            )
        )


def test_invalid_rto_reduction_rejected():
    with pytest.raises(
        ValueError
    ):
        run_scenario_v2(
            ScenarioV2Request(
                month="2025-11",
                changes=(
                    ScenarioChanges(
                        rto_reduction_percent=120
                    )
                ),
            )
        )


def test_scenario_v2_contains_no_numpy_values():
    result = (
        run_scenario_v2(
            ScenarioV2Request(
                month="2025-11",
                changes=(
                    ScenarioChanges(
                        orders_change_percent=5,
                        aov_change_percent=5,
                    )
                ),
            )
        )
    )

    dumped = result.model_dump()

    def walk(value):

        if isinstance(
            value,
            dict,
        ):
            for item in value.values():
                walk(item)

        elif isinstance(
            value,
            list,
        ):
            for item in value:
                walk(item)

        else:
            module = (
                type(value)
                .__module__
            )

            assert not (
                module.startswith(
                    "numpy"
                )
            )

    walk(
        dumped
    )
