from calendar import monthrange
from datetime import date, timedelta

from backend.app.analytics_context import (
    ComparisonPeriod,
    DateRange,
)


# ============================================================
# HELPERS
# ============================================================


def _parse_iso_date(
    value: str,
) -> date:
    try:
        return date.fromisoformat(
            value
        )

    except ValueError as error:
        raise ValueError(
            f"Invalid date '{value}'. "
            "Expected YYYY-MM-DD."
        ) from error


def _to_iso(
    value: date,
) -> str:
    return value.isoformat()


def _validate_range(
    period: DateRange,
) -> tuple[
    date,
    date,
]:
    start = _parse_iso_date(
        period.start_date
    )

    end = _parse_iso_date(
        period.end_date
    )

    if start > end:
        raise ValueError(
            "start_date cannot be after end_date."
        )

    return (
        start,
        end,
    )


# ============================================================
# MONTH TO DATE RANGE
# ============================================================


def month_to_date_range(
    month: str,
) -> DateRange:
    """
    Convert YYYY-MM into an inclusive calendar
    month date range.

    Example:
    2025-11
        ->
    2025-11-01 to 2025-11-30
    """

    try:
        year_text, month_text = (
            month.split(
                "-"
            )
        )

        year = int(
            year_text
        )

        month_number = int(
            month_text
        )

        if (
            month_number < 1
            or month_number > 12
        ):
            raise ValueError

    except (
        ValueError,
        TypeError,
    ) as error:
        raise ValueError(
            f"Invalid month '{month}'. "
            "Expected YYYY-MM."
        ) from error

    last_day = monthrange(
        year,
        month_number,
    )[1]

    return DateRange(
        start_date=(
            date(
                year,
                month_number,
                1,
            )
            .isoformat()
        ),
        end_date=(
            date(
                year,
                month_number,
                last_day,
            )
            .isoformat()
        ),
    )


# ============================================================
# PREVIOUS PERIOD
# ============================================================


def previous_period(
    period: DateRange,
) -> DateRange:
    """
    Return the immediately preceding range
    with the same number of inclusive days.

    Example:
    Nov 01 - Nov 30
        ->
    Oct 02 - Oct 31
    """

    start, end = (
        _validate_range(
            period
        )
    )

    duration = (
        end - start
    ).days + 1

    comparison_end = (
        start
        - timedelta(
            days=1
        )
    )

    comparison_start = (
        comparison_end
        - timedelta(
            days=duration - 1
        )
    )

    return DateRange(
        start_date=_to_iso(
            comparison_start
        ),
        end_date=_to_iso(
            comparison_end
        ),
    )


# ============================================================
# PREVIOUS CALENDAR MONTH
# ============================================================


def previous_month(
    period: DateRange,
) -> DateRange:
    """
    Return the full calendar month immediately
    before the period's start month.
    """

    start, _ = (
        _validate_range(
            period
        )
    )

    if start.month == 1:
        year = (
            start.year - 1
        )
        month_number = 12

    else:
        year = start.year
        month_number = (
            start.month - 1
        )

    last_day = monthrange(
        year,
        month_number,
    )[1]

    return DateRange(
        start_date=(
            date(
                year,
                month_number,
                1,
            )
            .isoformat()
        ),
        end_date=(
            date(
                year,
                month_number,
                last_day,
            )
            .isoformat()
        ),
    )


# ============================================================
# PREVIOUS YEAR
# ============================================================


def previous_year(
    period: DateRange,
) -> DateRange:
    """
    Shift the requested period one calendar year
    backwards.

    Leap-day values are normalized safely.
    """

    start, end = (
        _validate_range(
            period
        )
    )

    def shift_year(
        value: date,
    ) -> date:
        try:
            return value.replace(
                year=value.year - 1
            )

        except ValueError:
            # Feb 29 -> Feb 28
            return value.replace(
                year=value.year - 1,
                day=28,
            )

    shifted_start = (
        shift_year(
            start
        )
    )

    shifted_end = (
        shift_year(
            end
        )
    )

    return DateRange(
        start_date=_to_iso(
            shifted_start
        ),
        end_date=_to_iso(
            shifted_end
        ),
    )


# ============================================================
# COMPARISON RESOLVER
# ============================================================


def resolve_comparison_period(
    period: DateRange,
    comparison: ComparisonPeriod,
) -> DateRange | None:
    """
    Resolve the comparison configuration into
    a concrete date range.
    """

    _validate_range(
        period
    )

    mode = (
        comparison.mode
    )

    if mode == "none":
        return None

    if mode == "previous_period":
        return previous_period(
            period
        )

    if mode == "previous_month":
        return previous_month(
            period
        )

    if mode == "previous_year":
        return previous_year(
            period
        )

    if mode == "custom":

        if (
            not comparison.start_date
            or not comparison.end_date
        ):
            raise ValueError(
                "Custom comparison requires "
                "start_date and end_date."
            )

        result = DateRange(
            start_date=(
                comparison.start_date
            ),
            end_date=(
                comparison.end_date
            ),
        )

        _validate_range(
            result
        )

        return result

    raise ValueError(
        f"Unsupported comparison mode: {mode}"
    )


# ============================================================
# SERIALIZABLE PERIOD CONTEXT
# ============================================================


def build_period_context(
    period: DateRange,
    comparison: ComparisonPeriod,
) -> dict:
    """
    Return the normalized period information used
    by ProfitLens API responses.
    """

    current_start, current_end = (
        _validate_range(
            period
        )
    )

    comparison_range = (
        resolve_comparison_period(
            period,
            comparison,
        )
    )

    result = {
        "period": {
            "start_date": (
                _to_iso(
                    current_start
                )
            ),
            "end_date": (
                _to_iso(
                    current_end
                )
            ),
            "days": (
                current_end
                - current_start
            ).days + 1,
        },
        "comparison_mode": (
            comparison.mode
        ),
        "comparison_period": None,
    }

    if comparison_range:
        result[
            "comparison_period"
        ] = {
            "start_date": (
                comparison_range
                .start_date
            ),
            "end_date": (
                comparison_range
                .end_date
            ),
        }

    return result
