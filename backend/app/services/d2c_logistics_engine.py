from functools import lru_cache

import pandas as pd

from backend.app.services.d2c_data_loader import (
    load_couriers,
    load_d2c_orders,
)


# ============================================================
# LOGISTICS BASE
# ============================================================


@lru_cache(maxsize=1)
def _get_logistics_base_cached():
    """
    Build canonical order-level logistics data.
    """

    orders = (
        load_d2c_orders()
        .copy()
    )

    couriers = (
        load_couriers()
        .copy()
    )

    required_order_columns = {
        "order_id",
        "order_date",
        "order_status",
        "payment_method",
        "courier_id",
        "pincode",
        "city",
        "state",
        "zone",
        "is_cod",
        "is_rto",
        "is_returned",
        "ndr_flag",
        "first_attempt_delivery",
        "order_delivered_date",
        "promised_delivery_date",
    }

    missing_orders = (
        required_order_columns
        - set(orders.columns)
    )

    if missing_orders:
        raise ValueError(
            "Missing required order columns: "
            + ", ".join(
                sorted(
                    missing_orders
                )
            )
        )

    required_courier_columns = {
        "courier_id",
        "courier_name",
        "base_shipping_cost",
        "cod_fee",
        "rto_fee",
        "delivery_sla_days",
    }

    missing_couriers = (
        required_courier_columns
        - set(couriers.columns)
    )

    if missing_couriers:
        raise ValueError(
            "Missing required courier columns: "
            + ", ".join(
                sorted(
                    missing_couriers
                )
            )
        )

    for column in [
        "order_date",
        "first_attempt_delivery",
        "order_delivered_date",
        "promised_delivery_date",
    ]:
        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce",
        )

    orders["month"] = (
        orders["order_date"]
        .dt.to_period("M")
        .astype(str)
    )

    df = (
        orders.merge(
            couriers[
                [
                    "courier_id",
                    "courier_name",
                    "base_shipping_cost",
                    "cod_fee",
                    "rto_fee",
                    "delivery_sla_days",
                ]
            ],
            on="courier_id",
            how="left",
            validate="many_to_one",
        )
    )

    # --------------------------------------------------------
    # DELIVERY TAT
    # --------------------------------------------------------

    df[
        "delivery_tat_days"
    ] = (
        df[
            "order_delivered_date"
        ]
        - df[
            "order_date"
        ]
    ).dt.total_seconds() / 86400

    df[
        "first_attempt_tat_days"
    ] = (
        df[
            "first_attempt_delivery"
        ]
        - df[
            "order_date"
        ]
    ).dt.total_seconds() / 86400

    # --------------------------------------------------------
    # PROMISE PERFORMANCE
    # --------------------------------------------------------

    df[
        "days_vs_promise"
    ] = (
        df[
            "order_delivered_date"
        ]
        - df[
            "promised_delivery_date"
        ]
    ).dt.total_seconds() / 86400

    df[
        "is_late_delivery"
    ] = (
        df[
            "order_delivered_date"
        ].notna()
        & df[
            "promised_delivery_date"
        ].notna()
        & (
            df[
                "order_delivered_date"
            ]
            > df[
                "promised_delivery_date"
            ]
        )
    )

    df[
        "is_on_time_delivery"
    ] = (
        df[
            "order_delivered_date"
        ].notna()
        & df[
            "promised_delivery_date"
        ].notna()
        & (
            df[
                "order_delivered_date"
            ]
            <= df[
                "promised_delivery_date"
            ]
        )
    )

    return df


def get_logistics_base():
    return (
        _get_logistics_base_cached()
        .copy()
    )


# ============================================================
# MONTH SUMMARY
# ============================================================


def get_logistics_summary(
    month: str,
):
    """
    Return headline logistics KPIs for one month.
    """

    df = get_logistics_base()

    month_df = (
        df[
            df["month"]
            == month
        ]
        .copy()
    )

    if month_df.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C logistics data."
        )

    total_orders = int(
        month_df[
            "order_id"
        ]
        .nunique()
    )

    delivered = (
        month_df[
            month_df[
                "order_delivered_date"
            ].notna()
        ]
    )

    delivered_orders = int(
        delivered[
            "order_id"
        ]
        .nunique()
    )

    rto_orders = int(
        month_df[
            "is_rto"
        ]
        .sum()
    )

    returned_orders = int(
        month_df[
            "is_returned"
        ]
        .sum()
    )

    ndr_orders = int(
        month_df[
            "ndr_flag"
        ]
        .sum()
    )

    cod_orders = int(
        month_df[
            "is_cod"
        ]
        .sum()
    )

    tat = (
        delivered[
            "delivery_tat_days"
        ]
        .dropna()
    )

    first_attempt_tat = (
        month_df[
            "first_attempt_tat_days"
        ]
        .dropna()
    )

    measurable_promise = (
        month_df[
            month_df[
                "is_on_time_delivery"
            ]
            | month_df[
                "is_late_delivery"
            ]
        ]
    )

    measured_promise_orders = int(
        measurable_promise[
            "order_id"
        ]
        .nunique()
    )

    on_time_orders = int(
        measurable_promise[
            "is_on_time_delivery"
        ]
        .sum()
    )

    late_orders = int(
        measurable_promise[
            "is_late_delivery"
        ]
        .sum()
    )

    return {
        "month": month,

        "total_orders": total_orders,

        "delivered_orders": (
            delivered_orders
        ),

        "delivery_rate_percent": round(
            (
                delivered_orders
                / total_orders
                * 100
            )
            if total_orders
            else 0.0,
            2,
        ),

        "rto_orders": rto_orders,

        "rto_rate_percent": round(
            (
                rto_orders
                / total_orders
                * 100
            )
            if total_orders
            else 0.0,
            2,
        ),

        "returned_orders": (
            returned_orders
        ),

        "return_rate_percent": round(
            (
                returned_orders
                / total_orders
                * 100
            )
            if total_orders
            else 0.0,
            2,
        ),

        "ndr_orders": ndr_orders,

        "ndr_rate_percent": round(
            (
                ndr_orders
                / total_orders
                * 100
            )
            if total_orders
            else 0.0,
            2,
        ),

        "cod_orders": cod_orders,

        "cod_share_percent": round(
            (
                cod_orders
                / total_orders
                * 100
            )
            if total_orders
            else 0.0,
            2,
        ),

        "average_delivery_tat_days": round(
            float(
                tat.mean()
            )
            if not tat.empty
            else 0.0,
            2,
        ),

        "median_delivery_tat_days": round(
            float(
                tat.median()
            )
            if not tat.empty
            else 0.0,
            2,
        ),

        "p90_delivery_tat_days": round(
            float(
                tat.quantile(
                    0.90
                )
            )
            if not tat.empty
            else 0.0,
            2,
        ),

        "average_first_attempt_tat_days": round(
            float(
                first_attempt_tat.mean()
            )
            if not first_attempt_tat.empty
            else 0.0,
            2,
        ),

        "p90_first_attempt_tat_days": round(
            float(
                first_attempt_tat.quantile(
                    0.90
                )
            )
            if not first_attempt_tat.empty
            else 0.0,
            2,
        ),

        "promise_measured_orders": (
            measured_promise_orders
        ),

        "on_time_orders": (
            on_time_orders
        ),

        "late_orders": (
            late_orders
        ),

        "on_time_delivery_percent": round(
            (
                on_time_orders
                / measured_promise_orders
                * 100
            )
            if measured_promise_orders
            else 0.0,
            2,
        ),

        "late_delivery_percent": round(
            (
                late_orders
                / measured_promise_orders
                * 100
            )
            if measured_promise_orders
            else 0.0,
            2,
        ),
    }


# ============================================================
# COURIER PERFORMANCE
# ============================================================


def get_courier_performance(
    month: str,
):
    """
    Return courier-level logistics performance.
    """

    df = get_logistics_base()

    month_df = (
        df[
            df["month"]
            == month
        ]
        .copy()
    )

    if month_df.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C logistics data."
        )

    rows = []

    for courier_name, group in (
        month_df.groupby(
            "courier_name",
            dropna=False,
        )
    ):

        total_orders = int(
            group[
                "order_id"
            ]
            .nunique()
        )

        rto_orders = int(
            group[
                "is_rto"
            ]
            .sum()
        )

        ndr_orders = int(
            group[
                "ndr_flag"
            ]
            .sum()
        )

        delivered = (
            group[
                group[
                    "order_delivered_date"
                ].notna()
            ]
        )

        delivered_orders = int(
            delivered[
                "order_id"
            ]
            .nunique()
        )

        tat = (
            delivered[
                "delivery_tat_days"
            ]
            .dropna()
        )

        measured = (
            group[
                group[
                    "is_on_time_delivery"
                ]
                | group[
                    "is_late_delivery"
                ]
            ]
        )

        measured_orders = int(
            measured[
                "order_id"
            ]
            .nunique()
        )

        on_time_orders = int(
            measured[
                "is_on_time_delivery"
            ]
            .sum()
        )

        rows.append({
            "courier_name": (
                courier_name
                if pd.notna(
                    courier_name
                )
                else "Unknown"
            ),

            "orders": total_orders,

            "delivered_orders": (
                delivered_orders
            ),

            "delivery_rate_percent": round(
                (
                    delivered_orders
                    / total_orders
                    * 100
                )
                if total_orders
                else 0.0,
                2,
            ),

            "rto_orders": (
                rto_orders
            ),

            "rto_rate_percent": round(
                (
                    rto_orders
                    / total_orders
                    * 100
                )
                if total_orders
                else 0.0,
                2,
            ),

            "ndr_orders": (
                ndr_orders
            ),

            "ndr_rate_percent": round(
                (
                    ndr_orders
                    / total_orders
                    * 100
                )
                if total_orders
                else 0.0,
                2,
            ),

            "average_delivery_tat_days": round(
                float(
                    tat.mean()
                )
                if not tat.empty
                else 0.0,
                2,
            ),

            "p90_delivery_tat_days": round(
                float(
                    tat.quantile(
                        0.90
                    )
                )
                if not tat.empty
                else 0.0,
                2,
            ),

            "on_time_delivery_percent": round(
                (
                    on_time_orders
                    / measured_orders
                    * 100
                )
                if measured_orders
                else 0.0,
                2,
            ),

            "base_shipping_cost": round(
                float(
                    group[
                        "base_shipping_cost"
                    ]
                    .dropna()
                    .iloc[0]
                )
                if group[
                    "base_shipping_cost"
                ].notna().any()
                else 0.0,
                2,
            ),

            "rto_fee": round(
                float(
                    group[
                        "rto_fee"
                    ]
                    .dropna()
                    .iloc[0]
                )
                if group[
                    "rto_fee"
                ].notna().any()
                else 0.0,
                2,
            ),
        })

    result = pd.DataFrame(
        rows
    )

    return (
        result.sort_values(
            [
                "rto_rate_percent",
                "p90_delivery_tat_days",
            ],
            ascending=[
                True,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# COD VS PREPAID LOGISTICS
# ============================================================


def get_payment_logistics_performance(
    month: str,
):
    """
    Compare COD vs prepaid operational performance.
    """

    df = get_logistics_base()

    month_df = (
        df[
            df["month"]
            == month
        ]
        .copy()
    )

    if month_df.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C logistics data."
        )

    month_df[
        "payment_group"
    ] = (
        month_df[
            "is_cod"
        ]
        .map(
            {
                True: "COD",
                False: "Prepaid",
            }
        )
    )

    rows = []

    for payment_group, group in (
        month_df.groupby(
            "payment_group"
        )
    ):

        orders = int(
            group[
                "order_id"
            ]
            .nunique()
        )

        rto_orders = int(
            group[
                "is_rto"
            ]
            .sum()
        )

        ndr_orders = int(
            group[
                "ndr_flag"
            ]
            .sum()
        )

        returned_orders = int(
            group[
                "is_returned"
            ]
            .sum()
        )

        delivered = (
            group[
                group[
                    "order_delivered_date"
                ].notna()
            ]
        )

        tat = (
            delivered[
                "delivery_tat_days"
            ]
            .dropna()
        )

        rows.append({
            "payment_group": (
                payment_group
            ),

            "orders": orders,

            "rto_orders": (
                rto_orders
            ),

            "rto_rate_percent": round(
                (
                    rto_orders
                    / orders
                    * 100
                )
                if orders
                else 0.0,
                2,
            ),

            "ndr_orders": (
                ndr_orders
            ),

            "ndr_rate_percent": round(
                (
                    ndr_orders
                    / orders
                    * 100
                )
                if orders
                else 0.0,
                2,
            ),

            "returned_orders": (
                returned_orders
            ),

            "return_rate_percent": round(
                (
                    returned_orders
                    / orders
                    * 100
                )
                if orders
                else 0.0,
                2,
            ),

            "average_delivery_tat_days": round(
                float(
                    tat.mean()
                )
                if not tat.empty
                else 0.0,
                2,
            ),

            "p90_delivery_tat_days": round(
                float(
                    tat.quantile(
                        0.90
                    )
                )
                if not tat.empty
                else 0.0,
                2,
            ),
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# ZONE RISK
# ============================================================


def get_zone_performance(
    month: str,
):
    """
    Return operational risk by shipping zone.
    """

    df = get_logistics_base()

    month_df = (
        df[
            df["month"]
            == month
        ]
        .copy()
    )

    if month_df.empty:
        raise ValueError(
            f"Month '{month}' not found in D2C logistics data."
        )

    rows = []

    for zone, group in (
        month_df.groupby(
            "zone",
            dropna=False,
        )
    ):

        orders = int(
            group[
                "order_id"
            ]
            .nunique()
        )

        rto_orders = int(
            group[
                "is_rto"
            ]
            .sum()
        )

        ndr_orders = int(
            group[
                "ndr_flag"
            ]
            .sum()
        )

        delivered = (
            group[
                group[
                    "order_delivered_date"
                ].notna()
            ]
        )

        tat = (
            delivered[
                "delivery_tat_days"
            ]
            .dropna()
        )

        rows.append({
            "zone": (
                zone
                if pd.notna(zone)
                else "Unknown"
            ),

            "orders": orders,

            "rto_orders": (
                rto_orders
            ),

            "rto_rate_percent": round(
                (
                    rto_orders
                    / orders
                    * 100
                )
                if orders
                else 0.0,
                2,
            ),

            "ndr_orders": (
                ndr_orders
            ),

            "ndr_rate_percent": round(
                (
                    ndr_orders
                    / orders
                    * 100
                )
                if orders
                else 0.0,
                2,
            ),

            "average_delivery_tat_days": round(
                float(
                    tat.mean()
                )
                if not tat.empty
                else 0.0,
                2,
            ),

            "p90_delivery_tat_days": round(
                float(
                    tat.quantile(
                        0.90
                    )
                )
                if not tat.empty
                else 0.0,
                2,
            ),
        })

    return (
        pd.DataFrame(
            rows
        )
        .sort_values(
            "rto_rate_percent",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )