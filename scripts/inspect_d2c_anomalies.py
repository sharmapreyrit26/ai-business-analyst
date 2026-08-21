from pathlib import Path

import pandas as pd


BASE_DIR = Path(
    "data/demo_india_d2c/"
    "indian_d2c_synthetic_dataset"
)


def main():
    orders = pd.read_csv(
        BASE_DIR / "orders.csv",
        low_memory=False,
    )

    payments = pd.read_csv(
        BASE_DIR / "payments.csv",
        low_memory=False,
    )

    couriers = pd.read_csv(
        BASE_DIR / "couriers.csv",
        low_memory=False,
    )

    marketing = pd.read_csv(
        BASE_DIR / "marketing.csv",
        low_memory=False,
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

    # ========================================================
    # 1. FIRST ATTEMPT AFTER DELIVERY
    # ========================================================

    invalid_attempt = orders[
        orders["first_attempt_delivery"].notna()
        & orders["order_delivered_date"].notna()
        & (
            orders["first_attempt_delivery"]
            > orders["order_delivered_date"]
        )
    ].copy()

    print()
    print("=" * 70)
    print("1. FIRST ATTEMPT AFTER DELIVERY")
    print("=" * 70)

    print(
        "Rows:",
        len(invalid_attempt),
    )

    if not invalid_attempt.empty:

        difference = (
            invalid_attempt["first_attempt_delivery"]
            - invalid_attempt["order_delivered_date"]
        ).dt.days

        print(
            "Median days after delivery:",
            difference.median(),
        )

        print(
            "Maximum days after delivery:",
            difference.max(),
        )

        print()
        print("Order status distribution:")

        print(
            invalid_attempt[
                "order_status"
            ].value_counts()
        )

        print()
        print("Sample:")

        print(
            invalid_attempt[
                [
                    "order_id",
                    "order_status",
                    "order_date",
                    "first_attempt_delivery",
                    "order_delivered_date",
                    "is_rto",
                    "is_returned",
                    "ndr_flag",
                ]
            ]
            .head(10)
            .to_string(
                index=False
            )
        )


    # ========================================================
    # 2. REFUNDS WITHOUT RETURN / RTO
    # ========================================================

    payment_orders = (
        payments.merge(
            orders[
                [
                    "order_id",
                    "order_status",
                    "order_value",
                    "is_rto",
                    "is_returned",
                ]
            ],
            on="order_id",
            how="left",
        )
    )

    anomalous_refunds = payment_orders[
        (
            payment_orders[
                "refund_amount"
            ].fillna(0) > 0
        )
        & (
            payment_orders[
                "is_rto"
            ] == 0
        )
        & (
            payment_orders[
                "is_returned"
            ] == 0
        )
    ].copy()

    print()
    print("=" * 70)
    print("2. REFUNDS WITHOUT RETURN / RTO")
    print("=" * 70)

    print(
        "Rows:",
        len(anomalous_refunds),
    )

    if not anomalous_refunds.empty:

        print()
        print("Status distribution:")

        print(
            anomalous_refunds[
                "order_status"
            ].value_counts()
        )

        anomalous_refunds[
            "refund_pct_of_order"
        ] = (
            anomalous_refunds[
                "refund_amount"
            ]
            / anomalous_refunds[
                "order_value"
            ]
            * 100
        )

        print()
        print(
            "Average refund:",
            round(
                anomalous_refunds[
                    "refund_amount"
                ].mean(),
                2,
            ),
        )

        print(
            "Median refund %:",
            round(
                anomalous_refunds[
                    "refund_pct_of_order"
                ].median(),
                2,
            ),
        )

        print(
            "Max refund %:",
            round(
                anomalous_refunds[
                    "refund_pct_of_order"
                ].max(),
                2,
            ),
        )

        print()
        print("Sample:")

        print(
            anomalous_refunds[
                [
                    "order_id",
                    "order_status",
                    "order_value",
                    "refund_amount",
                    "refund_pct_of_order",
                    "payment_method",
                ]
            ]
            .head(10)
            .to_string(
                index=False
            )
        )


    # ========================================================
    # 3. COURIER / COD PROFILE
    # ========================================================

    courier_orders = orders.merge(
        couriers,
        on="courier_id",
        how="left",
    )

    print()
    print("=" * 70)
    print("3. COURIER COD PROFILE")
    print("=" * 70)

    summary = (
        courier_orders.groupby(
            "courier_name"
        )
        .agg(
            orders=(
                "order_id",
                "nunique",
            ),
            cod_orders=(
                "is_cod",
                "sum",
            ),
        )
        .reset_index()
    )

    summary[
        "cod_share_percent"
    ] = (
        summary["cod_orders"]
        / summary["orders"]
        * 100
    )

    print(
        summary.to_string(
            index=False
        )
    )

    print()
    print("Courier fee table:")

    print(
        couriers[
            [
                "courier_name",
                "base_shipping_cost",
                "cod_fee",
                "rto_fee",
                "delivery_sla_days",
            ]
        ].to_string(
            index=False
        )
    )


    # ========================================================
    # 4. MARKETING SCALE
    # ========================================================

    print()
    print("=" * 70)
    print("4. MARKETING PROFILE BY CHANNEL")
    print("=" * 70)

    channel = (
        marketing.groupby(
            "channel"
        )
        .agg(
            spend=(
                "spend",
                "sum",
            ),
            attributed_revenue=(
                "attributed_revenue",
                "sum",
            ),
            orders=(
                "orders",
                "sum",
            ),
            new_customers=(
                "new_customers",
                "sum",
            ),
            sessions=(
                "sessions",
                "sum",
            ),
        )
        .reset_index()
    )

    channel[
        "roas"
    ] = (
        channel[
            "attributed_revenue"
        ]
        / channel[
            "spend"
        ]
    )

    channel[
        "cac"
    ] = (
        channel[
            "spend"
        ]
        / channel[
            "new_customers"
        ].replace(
            0,
            pd.NA,
        )
    )

    print(
        channel.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()