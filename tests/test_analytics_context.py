from backend.app.analytics_context import (
    AnalyticsContext,
    AnalyticsFilters,
    ComparisonPeriod,
    DateRange,
)


def test_default_analytics_context():
    context = AnalyticsContext(
        period=DateRange(
            start_date="2025-11-01",
            end_date="2025-11-30",
        )
    )

    assert (
        context.period.start_date
        == "2025-11-01"
    )

    assert (
        context.period.end_date
        == "2025-11-30"
    )

    assert (
        context.comparison.mode
        == "previous_period"
    )

    assert (
        context.filters.channels
        == []
    )

    assert (
        context.filters.categories
        == []
    )


def test_analytics_context_accepts_filters():
    context = AnalyticsContext(
        workspace_id="workspace_demo",
        brand_id="brand_demo",
        period=DateRange(
            start_date="2025-10-01",
            end_date="2025-10-31",
        ),
        comparison=ComparisonPeriod(
            mode="previous_month"
        ),
        filters=AnalyticsFilters(
            channels=[
                "Meta",
                "Google",
            ],
            categories=[
                "Ethnic Wear",
            ],
            payment_methods=[
                "COD",
            ],
            zones=[
                "North",
            ],
        ),
    )

    assert (
        context.workspace_id
        == "workspace_demo"
    )

    assert (
        context.brand_id
        == "brand_demo"
    )

    assert (
        context.filters.channels
        == [
            "Meta",
            "Google",
        ]
    )

    assert (
        context.filters.payment_methods
        == [
            "COD",
        ]
    )

    assert (
        context.filters.zones
        == [
            "North",
        ]
    )
