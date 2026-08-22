import pandas as pd
import pytest

from backend.app.analytics_context import (
    AnalyticsFilters,
)

from backend.app.services.analytics_filter_engine import (
    apply_analytics_filters,
    get_available_filter_options,
    summarize_active_filters,
)


def build_dataframe():
    return pd.DataFrame(
        [
            {
                "order_id": "ORD_1",
                "channel": "Meta",
                "category": "Fashion",
                "sku": "SKU_001",
                "courier": "Delhivery",
                "warehouse": "Delhi",
                "payment_method": "COD",
                "state": "Delhi",
                "zone": "North",
                "revenue": 1000,
            },
            {
                "order_id": "ORD_2",
                "channel": "Google",
                "category": "Fashion",
                "sku": "SKU_002",
                "courier": "Blue Dart",
                "warehouse": "Mumbai",
                "payment_method": "Prepaid",
                "state": "Maharashtra",
                "zone": "West",
                "revenue": 2000,
            },
            {
                "order_id": "ORD_3",
                "channel": "Meta",
                "category": "Beauty",
                "sku": "SKU_003",
                "courier": "Delhivery",
                "warehouse": "Delhi",
                "payment_method": "COD",
                "state": "Uttar Pradesh",
                "zone": "North",
                "revenue": 1500,
            },
        ]
    )


def test_empty_filters_preserve_all_rows():
    dataframe = build_dataframe()

    result = apply_analytics_filters(
        dataframe,
        AnalyticsFilters(),
    )

    assert len(result) == 3

    assert (
        dataframe.equals(
            build_dataframe()
        )
    )


def test_single_filter():
    result = apply_analytics_filters(
        build_dataframe(),
        AnalyticsFilters(
            channels=[
                "Meta"
            ]
        ),
    )

    assert len(result) == 2

    assert set(
        result["order_id"]
    ) == {
        "ORD_1",
        "ORD_3",
    }


def test_multiple_values_inside_filter_use_or_logic():
    result = apply_analytics_filters(
        build_dataframe(),
        AnalyticsFilters(
            channels=[
                "Meta",
                "Google",
            ]
        ),
    )

    assert len(result) == 3


def test_multiple_filter_groups_use_and_logic():
    result = apply_analytics_filters(
        build_dataframe(),
        AnalyticsFilters(
            channels=[
                "Meta"
            ],
            categories=[
                "Fashion"
            ],
            payment_methods=[
                "COD"
            ],
        ),
    )

    assert len(result) == 1

    assert (
        result.iloc[0][
            "order_id"
        ]
        == "ORD_1"
    )


def test_filter_matching_is_case_insensitive():
    result = apply_analytics_filters(
        build_dataframe(),
        AnalyticsFilters(
            channels=[
                "meta"
            ],
            zones=[
                "north"
            ],
        ),
    )

    assert len(result) == 2


def test_filter_alias_resolution():
    dataframe = pd.DataFrame(
        [
            {
                "order_id": "1",
                "acquisition_channel":
                    "Meta",
                "shipping_zone":
                    "North",
            },
            {
                "order_id": "2",
                "acquisition_channel":
                    "Google",
                "shipping_zone":
                    "West",
            },
        ]
    )

    result = apply_analytics_filters(
        dataframe,
        AnalyticsFilters(
            channels=[
                "Meta"
            ],
            zones=[
                "North"
            ],
        ),
    )

    assert len(result) == 1

    assert (
        result.iloc[0][
            "order_id"
        ]
        == "1"
    )


def test_missing_filter_column_is_ignored_by_default():
    dataframe = pd.DataFrame(
        [
            {
                "order_id": "1",
                "revenue": 100,
            }
        ]
    )

    result = apply_analytics_filters(
        dataframe,
        AnalyticsFilters(
            channels=[
                "Meta"
            ]
        ),
    )

    assert len(result) == 1


def test_missing_filter_column_can_be_strict():
    dataframe = pd.DataFrame(
        [
            {
                "order_id": "1",
            }
        ]
    )

    with pytest.raises(
        ValueError
    ):
        apply_analytics_filters(
            dataframe,
            AnalyticsFilters(
                channels=[
                    "Meta"
                ]
            ),
            strict=True,
        )


def test_no_matching_values_returns_empty_dataframe():
    result = apply_analytics_filters(
        build_dataframe(),
        AnalyticsFilters(
            zones=[
                "South"
            ]
        ),
    )

    assert result.empty


def test_available_filter_options():
    result = (
        get_available_filter_options(
            build_dataframe()
        )
    )

    assert (
        result["channels"]
        == [
            "Google",
            "Meta",
        ]
    )

    assert (
        result["payment_methods"]
        == [
            "COD",
            "Prepaid",
        ]
    )

    assert (
        result["zones"]
        == [
            "North",
            "West",
        ]
    )


def test_filter_summary():
    result = summarize_active_filters(
        AnalyticsFilters(
            channels=[
                "Meta",
                "Google",
            ],
            zones=[
                "North",
            ],
        )
    )

    assert (
        result[
            "active_filter_groups"
        ]
        == 2
    )

    assert (
        result[
            "active_filter_values"
        ]
        == 3
    )

    assert (
        result["filters"][
            "zones"
        ]
        == [
            "North"
        ]
    )
