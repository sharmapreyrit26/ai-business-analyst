from __future__ import annotations

from typing import Optional

from backend.app.metric_contracts import (
    MetricComparison,
    MetricContract,
    MetricDirection,
    MetricQuality,
    MetricSentiment,
    MetricSource,
    MetricUnit,
)


# ============================================================
# SAFE CALCULATIONS
# ============================================================


def calculate_change(
    value: float | int | None,
    previous_value: float | int | None,
) -> MetricComparison:
    """
    Build deterministic metric comparison values.

    Handles:
    - missing values
    - zero previous value
    - positive/negative movement
    """

    if (
        value is None
        or previous_value is None
    ):
        return MetricComparison()

    current = float(
        value
    )

    previous = float(
        previous_value
    )

    absolute = (
        current - previous
    )

    if previous == 0:
        percent = None

    else:
        percent = (
            absolute
            / abs(previous)
            * 100
        )

    if absolute > 0:
        direction = (
            MetricDirection.up
        )

    elif absolute < 0:
        direction = (
            MetricDirection.down
        )

    else:
        direction = (
            MetricDirection.flat
        )

    return MetricComparison(
        previous_value=previous,
        change_absolute=round(
            absolute,
            2,
        ),
        change_percent=(
            round(
                percent,
                2,
            )
            if percent is not None
            else None
        ),
        direction=direction,
    )


# ============================================================
# VALUE FORMATTERS
# ============================================================


def _format_indian_currency(
    value: float,
) -> str:
    """
    Human-readable INR formatting.

    Examples:
        8500        -> ₹8,500
        125000      -> ₹1.25L
        11000000    -> ₹1.10Cr
    """

    absolute = abs(
        value
    )

    sign = (
        "-"
        if value < 0
        else ""
    )

    if absolute >= 10_000_000:
        return (
            f"{sign}₹"
            f"{absolute / 10_000_000:.2f}Cr"
        )

    if absolute >= 100_000:
        return (
            f"{sign}₹"
            f"{absolute / 100_000:.2f}L"
        )

    if absolute >= 1_000:
        return (
            f"{sign}₹"
            f"{absolute:,.0f}"
        )

    return (
        f"{sign}₹"
        f"{absolute:.2f}"
    )


def format_metric_value(
    value: float | int | None,
    unit: MetricUnit,
) -> Optional[str]:
    """
    Standard metric formatting used by ProfitLens.
    """

    if value is None:
        return None

    numeric = float(
        value
    )

    if unit == MetricUnit.currency:
        return _format_indian_currency(
            numeric
        )

    if unit == MetricUnit.percent:
        return (
            f"{numeric:.2f}%"
        )

    if unit == MetricUnit.ratio:
        return (
            f"{numeric:.2f}x"
        )

    if unit == MetricUnit.days:
        return (
            f"{numeric:.2f} days"
        )

    if unit == MetricUnit.count:
        return (
            f"{int(round(numeric)):,}"
        )

    return (
        f"{numeric:.2f}"
    )


# ============================================================
# SENTIMENT
# ============================================================


def infer_sentiment(
    comparison: MetricComparison,
    *,
    higher_is_better: bool | None = None,
) -> MetricSentiment:
    """
    Infer UI sentiment from metric movement.

    higher_is_better=True:
        Revenue, profit, ROAS

    higher_is_better=False:
        RTO, CAC, NDR, delivery TAT

    higher_is_better=None:
        Neutral / context dependent
    """

    if (
        higher_is_better
        is None
    ):
        return (
            MetricSentiment.neutral
        )

    direction = (
        comparison.direction
    )

    if direction == MetricDirection.flat:
        return (
            MetricSentiment.neutral
        )

    if direction == MetricDirection.unknown:
        return (
            MetricSentiment.unknown
        )

    if higher_is_better:
        return (
            MetricSentiment.positive
            if direction
            == MetricDirection.up
            else MetricSentiment.negative
        )

    return (
        MetricSentiment.positive
        if direction
        == MetricDirection.down
        else MetricSentiment.negative
    )


# ============================================================
# MAIN METRIC BUILDER
# ============================================================


def build_metric(
    *,
    metric_id: str,
    label: str,
    value: float | int | None,
    unit: MetricUnit = MetricUnit.decimal,
    previous_value: float | int | None = None,
    higher_is_better: bool | None = None,
    definition: str | None = None,
    formula: str | None = None,
    data_quality: MetricQuality = (
        MetricQuality.verified
    ),
    source_engine: str | None = None,
    source_tables: list[str] | None = None,
    source_fields: list[str] | None = None,
    metadata: dict | None = None,
) -> MetricContract:
    """
    Build a canonical ProfitLens metric.
    """

    comparison = calculate_change(
        value,
        previous_value,
    )

    sentiment = infer_sentiment(
        comparison,
        higher_is_better=(
            higher_is_better
        ),
    )

    return MetricContract(
        metric_id=metric_id,
        label=label,
        value=value,
        formatted_value=(
            format_metric_value(
                value,
                unit,
            )
        ),
        unit=unit,
        comparison=comparison,
        sentiment=sentiment,
        definition=definition,
        formula=formula,
        data_quality=data_quality,
        source=MetricSource(
            engine=source_engine,
            tables=(
                source_tables
                or []
            ),
            fields=(
                source_fields
                or []
            ),
        ),
        metadata=(
            metadata
            or {}
        ),
    )
