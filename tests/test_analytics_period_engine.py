import pytest

from backend.app.analytics_context import (
    ComparisonPeriod,
    DateRange,
)

from backend.app.services.analytics_period_engine import (
    build_period_context,
    month_to_date_range,
    previous_month,
    previous_period,
    previous_year,
    resolve_comparison_period,
)


def test_month_to_date_range():
    period = month_to_date_range(
        "2025-11"
    )

    assert (
        period.start_date
        == "2025-11-01"
    )

    assert (
        period.end_date
        == "2025-11-30"
    )


def test_month_to_date_range_handles_leap_year():
    period = month_to_date_range(
        "2024-02"
    )

    assert (
        period.end_date
        == "2024-02-29"
    )


def test_previous_period_same_duration():
    result = previous_period(
        DateRange(
            start_date="2025-11-01",
            end_date="2025-11-30",
        )
    )

    assert (
        result.start_date
        == "2025-10-02"
    )

    assert (
        result.end_date
        == "2025-10-31"
    )


def test_previous_month():
    result = previous_month(
        DateRange(
            start_date="2025-11-01",
            end_date="2025-11-30",
        )
    )

    assert (
        result.start_date
        == "2025-10-01"
    )

    assert (
        result.end_date
        == "2025-10-31"
    )


def test_previous_month_crosses_year():
    result = previous_month(
        DateRange(
            start_date="2025-01-01",
            end_date="2025-01-31",
        )
    )

    assert (
        result.start_date
        == "2024-12-01"
    )

    assert (
        result.end_date
        == "2024-12-31"
    )


def test_previous_year():
    result = previous_year(
        DateRange(
            start_date="2025-11-01",
            end_date="2025-11-30",
        )
    )

    assert (
        result.start_date
        == "2024-11-01"
    )

    assert (
        result.end_date
        == "2024-11-30"
    )


def test_custom_comparison():
    result = resolve_comparison_period(
        DateRange(
            start_date="2025-11-01",
            end_date="2025-11-30",
        ),
        ComparisonPeriod(
            mode="custom",
            start_date="2025-08-01",
            end_date="2025-08-31",
        ),
    )

    assert result is not None

    assert (
        result.start_date
        == "2025-08-01"
    )


def test_none_comparison():
    result = resolve_comparison_period(
        DateRange(
            start_date="2025-11-01",
            end_date="2025-11-30",
        ),
        ComparisonPeriod(
            mode="none"
        ),
    )

    assert result is None


def test_invalid_date_range_rejected():
    with pytest.raises(
        ValueError
    ):
        previous_period(
            DateRange(
                start_date="2025-12-01",
                end_date="2025-11-01",
            )
        )


def test_custom_comparison_requires_dates():
    with pytest.raises(
        ValueError
    ):
        resolve_comparison_period(
            DateRange(
                start_date="2025-11-01",
                end_date="2025-11-30",
            ),
            ComparisonPeriod(
                mode="custom"
            ),
        )


def test_build_period_context():
    result = build_period_context(
        DateRange(
            start_date="2025-11-01",
            end_date="2025-11-30",
        ),
        ComparisonPeriod(
            mode="previous_month"
        ),
    )

    assert (
        result["period"]["days"]
        == 30
    )

    assert (
        result[
            "comparison_period"
        ]["start_date"]
        == "2025-10-01"
    )
