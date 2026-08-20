import pandas as pd

from backend.app.services.data_loader import (
    load_orders,
)


def _prepare_logistics_data(
    month: str = None
):
    """
    Prepare delivered-order logistics data.

    Only orders with the timestamps required for
    each metric are used in that metric.
    """

    df = load_orders().copy()

    df["month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype(str)
    )

    if month is not None:
        df = df[
            df["month"] == month
        ].copy()

    return df


def _hours_between(
    start,
    end
):
    """
    Return elapsed hours between two timestamp columns.
    """

    return (
        end - start
    ).dt.total_seconds() / 3600


def _days_between(
    start,
    end
):
    """
    Return elapsed days between two timestamp columns.
    """

    return (
        end - start
    ).dt.total_seconds() / 86400


def _safe_average(series):
    """
    Return rounded average for valid observations.
    """

    valid = series.dropna()

    if valid.empty:
        return None

    return round(
        float(valid.mean()),
        2
    )


def _safe_median(series):
    """
    Return rounded median.
    """

    valid = series.dropna()

    if valid.empty:
        return None

    return round(
        float(valid.median()),
        2
    )


def _safe_p90(series):
    """
    Return 90th percentile.
    """

    valid = series.dropna()

    if valid.empty:
        return None

    return round(
        float(
            valid.quantile(0.90)
        ),
        2
    )


def get_fulfilment_tat(
    month: str = None
):
    """
    Calculate fulfilment turnaround times.

    Metrics:
    - purchase -> approval
    - approval -> carrier
    - carrier -> customer
    - purchase -> customer
    """

    df = _prepare_logistics_data(
        month
    )

    purchase_to_approval = _hours_between(
        df["order_purchase_timestamp"],
        df["order_approved_at"],
    )

    approval_to_carrier = _days_between(
        df["order_approved_at"],
        df["order_delivered_carrier_date"],
    )

    carrier_to_delivery = _days_between(
        df["order_delivered_carrier_date"],
        df["order_delivered_customer_date"],
    )

    purchase_to_delivery = _days_between(
        df["order_purchase_timestamp"],
        df["order_delivered_customer_date"],
    )

    return {
        "month": month,

        "purchase_to_approval": {
            "unit": "hours",
            "average": _safe_average(
                purchase_to_approval
            ),
            "median": _safe_median(
                purchase_to_approval
            ),
            "p90": _safe_p90(
                purchase_to_approval
            ),
            "sample_size": int(
                purchase_to_approval
                .dropna()
                .shape[0]
            ),
        },

        "approval_to_carrier": {
            "unit": "days",
            "average": _safe_average(
                approval_to_carrier
            ),
            "median": _safe_median(
                approval_to_carrier
            ),
            "p90": _safe_p90(
                approval_to_carrier
            ),
            "sample_size": int(
                approval_to_carrier
                .dropna()
                .shape[0]
            ),
        },

        "carrier_to_delivery": {
            "unit": "days",
            "average": _safe_average(
                carrier_to_delivery
            ),
            "median": _safe_median(
                carrier_to_delivery
            ),
            "p90": _safe_p90(
                carrier_to_delivery
            ),
            "sample_size": int(
                carrier_to_delivery
                .dropna()
                .shape[0]
            ),
        },

        "purchase_to_delivery": {
            "unit": "days",
            "average": _safe_average(
                purchase_to_delivery
            ),
            "median": _safe_median(
                purchase_to_delivery
            ),
            "p90": _safe_p90(
                purchase_to_delivery
            ),
            "sample_size": int(
                purchase_to_delivery
                .dropna()
                .shape[0]
            ),
        },
    }


def get_delivery_promise_performance(
    month: str = None
):
    """
    Compare actual delivery against the estimated
    delivery date.

    Negative variance = delivered early.
    Positive variance = delivered late.
    """

    df = _prepare_logistics_data(
        month
    )

    valid = df[
        df[
            "order_delivered_customer_date"
        ].notna()
        &
        df[
            "order_estimated_delivery_date"
        ].notna()
    ].copy()

    if valid.empty:

        return {
            "month": month,
            "status": "no_data",
        }

    valid[
        "delivery_variance_days"
    ] = _days_between(
        valid[
            "order_estimated_delivery_date"
        ],
        valid[
            "order_delivered_customer_date"
        ],
    )

    valid[
        "on_time"
    ] = (
        valid[
            "delivery_variance_days"
        ] <= 0
    )

    valid[
        "late"
    ] = (
        valid[
            "delivery_variance_days"
        ] > 0
    )

    total = len(valid)

    on_time_orders = int(
        valid["on_time"].sum()
    )

    late_orders = int(
        valid["late"].sum()
    )

    late_days = valid.loc[
        valid["late"],
        "delivery_variance_days",
    ]

    early_days = (
        valid.loc[
            valid[
                "delivery_variance_days"
            ] < 0,
            "delivery_variance_days",
        ]
        .abs()
    )

    return {
        "month": month,

        "status": "complete",

        "measured_orders": int(
            total
        ),

        "on_time_orders": (
            on_time_orders
        ),

        "late_orders": (
            late_orders
        ),

        "on_time_delivery_percent": round(
            on_time_orders
            / total
            * 100,
            2,
        ),

        "late_delivery_percent": round(
            late_orders
            / total
            * 100,
            2,
        ),

        "average_days_late": (
            _safe_average(
                late_days
            )
        ),

        "p90_days_late": (
            _safe_p90(
                late_days
            )
        ),

        "average_days_early": (
            _safe_average(
                early_days
            )
        ),
    }


def get_delivery_status_summary(
    month: str = None
):
    """
    Summarize order statuses for the selected period.
    """

    df = _prepare_logistics_data(
        month
    )

    if df.empty:

        return {
            "month": month,
            "status": "no_data",
        }

    status_counts = (
        df["order_status"]
        .value_counts()
        .to_dict()
    )

    total_orders = len(df)

    return {
        "month": month,

        "total_orders": int(
            total_orders
        ),

        "status_counts": {
            str(status): int(count)
            for status, count
            in status_counts.items()
        },

        "delivered_orders": int(
            (
                df["order_status"]
                == "delivered"
            ).sum()
        ),

        "cancelled_orders": int(
            (
                df["order_status"]
                == "canceled"
            ).sum()
        ),
    }


def get_logistics_data_quality(
    month: str = None
):
    """
    Report timestamp coverage so ProfitLens knows
    how much evidence supports the logistics metrics.
    """

    df = _prepare_logistics_data(
        month
    )

    total = len(df)

    if total == 0:

        return {
            "month": month,
            "status": "no_data",
        }

    fields = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    coverage = {}

    for field in fields:

        available = int(
            df[field]
            .notna()
            .sum()
        )

        coverage[field] = {
            "available": available,

            "missing": int(
                total - available
            ),

            "coverage_percent": round(
                available
                / total
                * 100,
                2,
            ),
        }

    return {
        "month": month,

        "status": "complete",

        "total_orders": int(
            total
        ),

        "field_coverage": coverage,
    }


def get_logistics_analytics(
    month: str = None
):
    """
    Complete V1 logistics and fulfilment analytics.
    """

    return {
        "month": month,

        "fulfilment_tat": (
            get_fulfilment_tat(
                month
            )
        ),

        "delivery_promise": (
            get_delivery_promise_performance(
                month
            )
        ),

        "order_status": (
            get_delivery_status_summary(
                month
            )
        ),

        "data_quality": (
            get_logistics_data_quality(
                month
            )
        ),

        "available_metrics": [
            "purchase-to-approval TAT",
            "approval-to-carrier TAT",
            "carrier-to-delivery TAT",
            "purchase-to-delivery TAT",
            "average TAT",
            "median TAT",
            "P90 TAT",
            "on-time delivery rate",
            "late delivery rate",
            "average days late",
            "P90 days late",
            "average days early",
        ],

        "unavailable_metrics": {
            "courier_performance": {
                "status": (
                    "insufficient_data"
                ),
                "required_data": [
                    "courier identifier",
                ],
            },

            "rto_rate": {
                "status": (
                    "insufficient_data"
                ),
                "required_data": [
                    "RTO status",
                ],
            },

            "ndr_rate": {
                "status": (
                    "insufficient_data"
                ),
                "required_data": [
                    "NDR events",
                ],
            },

            "cod_vs_prepaid": {
                "status": (
                    "insufficient_data"
                ),
                "required_data": [
                    "payment method",
                ],
            },

            "first_attempt_delivery": {
                "status": (
                    "insufficient_data"
                ),
                "required_data": [
                    "delivery attempt events",
                ],
            },

            "zone_performance": {
                "status": (
                    "insufficient_data"
                ),
                "required_data": [
                    "customer location",
                    "shipping zone",
                ],
            },
        },
    }