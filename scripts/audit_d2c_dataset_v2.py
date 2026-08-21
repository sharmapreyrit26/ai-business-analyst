from pathlib import Path

import pandas as pd


BASE_DIR = Path(
    "data/demo_india_d2c/"
    "indian_d2c_synthetic_dataset"
)

OUTPUT_FILE = Path(
    "data/demo_india_d2c/"
    "d2c_data_audit_v2_report.txt"
)


def add(lines, text=""):
    lines.append(str(text))


def section(lines, title):
    add(lines)
    add(lines, "=" * 70)
    add(lines, title)
    add(lines, "=" * 70)


def pct(num, den):
    if not den:
        return 0.0

    return (
        num
        / den
        * 100
    )


def money(value):
    return (
        f"₹{float(value):,.2f}"
    )


def to_bool(series):
    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(
            [
                "1",
                "true",
                "yes",
                "y",
            ]
        )
    )


def main():
    lines = []

    # ========================================================
    # LOAD
    # ========================================================

    orders = pd.read_csv(
        BASE_DIR / "orders.csv",
        low_memory=False,
    )

    items = pd.read_csv(
        BASE_DIR / "order_items.csv",
        low_memory=False,
    )

    payments = pd.read_csv(
        BASE_DIR / "payments.csv",
        low_memory=False,
    )

    customers = pd.read_csv(
        BASE_DIR / "customers.csv",
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


    # ========================================================
    # DATE PARSING
    # ========================================================

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

    customers[
        "first_order_date"
    ] = pd.to_datetime(
        customers[
            "first_order_date"
        ],
        errors="coerce",
    )

    marketing[
        "date"
    ] = pd.to_datetime(
        marketing[
            "date"
        ],
        errors="coerce",
    )


    # ========================================================
    # NORMALIZED FLAGS
    # ========================================================

    is_cod = to_bool(
        orders["is_cod"]
    )

    is_rto = to_bool(
        orders["is_rto"]
    )

    is_returned = to_bool(
        orders["is_returned"]
    )

    ndr_flag = to_bool(
        orders["ndr_flag"]
    )


    # ========================================================
    # ORDER STATUS CONSISTENCY
    # ========================================================

    section(
        lines,
        "1. ORDER STATUS CONSISTENCY",
    )

    status_counts = (
        orders[
            "order_status"
        ]
        .value_counts(
            dropna=False
        )
    )

    for status, count in (
        status_counts.items()
    ):
        add(
            lines,
            f"{status}: {count:,}"
        )

    delivered_mask = (
        orders[
            "order_status"
        ]
        .astype(str)
        .str.lower()
        .eq("delivered")
    )

    cancelled_mask = (
        orders[
            "order_status"
        ]
        .astype(str)
        .str.lower()
        .isin(
            [
                "cancelled",
                "canceled",
            ]
        )
    )

    delivered_missing_date = int(
        (
            delivered_mask
            & orders[
                "order_delivered_date"
            ].isna()
        ).sum()
    )

    cancelled_with_delivery = int(
        (
            cancelled_mask
            & orders[
                "order_delivered_date"
            ].notna()
        ).sum()
    )

    rto_and_delivered = int(
        (
            is_rto
            & delivered_mask
        ).sum()
    )

    returned_without_delivery = int(
        (
            is_returned
            & orders[
                "order_delivered_date"
            ].isna()
        ).sum()
    )

    add(
        lines,
        (
            "Delivered orders missing delivered date: "
            f"{delivered_missing_date:,}"
        )
    )

    add(
        lines,
        (
            "Cancelled orders with delivered date: "
            f"{cancelled_with_delivery:,}"
        )
    )

    add(
        lines,
        (
            "RTO orders marked delivered: "
            f"{rto_and_delivered:,}"
        )
    )

    add(
        lines,
        (
            "Returned orders missing delivered date: "
            f"{returned_without_delivery:,}"
        )
    )


    # ========================================================
    # TIMESTAMP CONSISTENCY
    # ========================================================

    section(
        lines,
        "2. TIMESTAMP CONSISTENCY",
    )

    first_before_order = int(
        (
            orders[
                "first_attempt_delivery"
            ].notna()
            & (
                orders[
                    "first_attempt_delivery"
                ]
                < orders[
                    "order_date"
                ]
            )
        ).sum()
    )

    delivered_before_order = int(
        (
            orders[
                "order_delivered_date"
            ].notna()
            & (
                orders[
                    "order_delivered_date"
                ]
                < orders[
                    "order_date"
                ]
            )
        ).sum()
    )

    promised_before_order = int(
        (
            orders[
                "promised_delivery_date"
            ].notna()
            & (
                orders[
                    "promised_delivery_date"
                ]
                < orders[
                    "order_date"
                ]
            )
        ).sum()
    )

    first_after_delivery = int(
        (
            orders[
                "first_attempt_delivery"
            ].notna()
            & orders[
                "order_delivered_date"
            ].notna()
            & (
                orders[
                    "first_attempt_delivery"
                ]
                > orders[
                    "order_delivered_date"
                ]
            )
        ).sum()
    )

    add(
        lines,
        (
            "First attempt before order date: "
            f"{first_before_order:,}"
        )
    )

    add(
        lines,
        (
            "Delivered before order date: "
            f"{delivered_before_order:,}"
        )
    )

    add(
        lines,
        (
            "Promised date before order date: "
            f"{promised_before_order:,}"
        )
    )

    add(
        lines,
        (
            "First attempt after delivered date: "
            f"{first_after_delivery:,}"
        )
    )


    # ========================================================
    # REFUND CONSISTENCY
    # ========================================================

    section(
        lines,
        "3. REFUND CONSISTENCY",
    )

    payment_order = (
        payments.merge(
            orders[
                [
                    "order_id",
                    "order_status",
                    "is_returned",
                    "is_rto",
                ]
            ],
            on="order_id",
            how="left",
        )
    )

    refund_positive = (
        payment_order[
            "refund_amount"
        ]
        .fillna(0)
        > 0
    )

    returned_payment = to_bool(
        payment_order[
            "is_returned"
        ]
    )

    rto_payment = to_bool(
        payment_order[
            "is_rto"
        ]
    )

    refund_without_return_or_rto = int(
        (
            refund_positive
            & ~returned_payment
            & ~rto_payment
        ).sum()
    )

    returned_without_refund = int(
        (
            returned_payment
            & (
                payment_order[
                    "refund_amount"
                ]
                .fillna(0)
                <= 0
            )
        ).sum()
    )

    add(
        lines,
        (
            "Refund > 0 without return/RTO: "
            f"{refund_without_return_or_rto:,}"
        )
    )

    add(
        lines,
        (
            "Returned order without refund: "
            f"{returned_without_refund:,}"
        )
    )

    add(
        lines,
        (
            "Total refunds: "
            f"{money(payment_order['refund_amount'].fillna(0).sum())}"
        )
    )


    # ========================================================
    # CUSTOMER REPEAT BEHAVIOR
    # ========================================================

    section(
        lines,
        "4. CUSTOMER REPEAT BEHAVIOR",
    )

    unique_customers = (
        customers[
            "customer_unique_id"
        ]
        .nunique()
    )

    customer_map = (
        orders[
            [
                "order_id",
                "customer_id",
            ]
        ]
        .merge(
            customers[
                [
                    "customer_id",
                    "customer_unique_id",
                ]
            ],
            on="customer_id",
            how="left",
        )
    )

    orders_per_unique_customer = (
        customer_map.groupby(
            "customer_unique_id"
        )[
            "order_id"
        ]
        .nunique()
    )

    repeat_customers = int(
        (
            orders_per_unique_customer
            > 1
        ).sum()
    )

    repeat_rate = pct(
        repeat_customers,
        len(
            orders_per_unique_customer
        ),
    )

    avg_orders_per_customer = (
        orders_per_unique_customer
        .mean()
    )

    max_orders_per_customer = (
        orders_per_unique_customer
        .max()
    )

    add(
        lines,
        (
            "Unique customer identities: "
            f"{unique_customers:,}"
        )
    )

    add(
        lines,
        (
            "Repeat customers: "
            f"{repeat_customers:,}"
        )
    )

    add(
        lines,
        (
            "Repeat customer rate: "
            f"{repeat_rate:.2f}%"
        )
    )

    add(
        lines,
        (
            "Average orders per customer: "
            f"{avg_orders_per_customer:.2f}"
        )
    )

    add(
        lines,
        (
            "Maximum orders for one customer: "
            f"{int(max_orders_per_customer):,}"
        )
    )


    # ========================================================
    # CUSTOMER FIRST ORDER CONSISTENCY
    # ========================================================

    section(
        lines,
        "5. CUSTOMER FIRST ORDER CONSISTENCY",
    )

    earliest_observed = (
        orders.groupby(
            "customer_id"
        )[
            "order_date"
        ]
        .min()
        .rename(
            "earliest_observed_order"
        )
        .reset_index()
    )

    first_order_check = (
        customers[
            [
                "customer_id",
                "first_order_date",
            ]
        ]
        .merge(
            earliest_observed,
            on="customer_id",
            how="left",
        )
    )

    first_order_after_actual = int(
        (
            first_order_check[
                "first_order_date"
            ].notna()
            & first_order_check[
                "earliest_observed_order"
            ].notna()
            & (
                first_order_check[
                    "first_order_date"
                ]
                > first_order_check[
                    "earliest_observed_order"
                ]
            )
        ).sum()
    )

    add(
        lines,
        (
            "Customer first_order_date after earliest observed order: "
            f"{first_order_after_actual:,}"
        )
    )


    # ========================================================
    # COURIER ECONOMICS
    # ========================================================

    section(
        lines,
        "6. COURIER ECONOMICS",
    )

    courier_orders = (
        orders.merge(
            couriers,
            on="courier_id",
            how="left",
        )
    )

    courier_orders[
        "rto_cost"
    ] = (
        courier_orders[
            "rto_fee"
        ]
        .fillna(0)
        * is_rto.astype(int)
    )

    courier_orders[
        "forward_shipping_cost"
    ] = (
        courier_orders[
            "base_shipping_cost"
        ]
        .fillna(0)
    )

    courier_orders[
        "expected_cod_fee"
    ] = (
        courier_orders[
            "cod_fee"
        ]
        .fillna(0)
        * is_cod.astype(int)
    )

    courier_summary = (
        courier_orders.groupby(
            "courier_name"
        )
        .agg(
            orders=(
                "order_id",
                "nunique",
            ),
            forward_cost=(
                "forward_shipping_cost",
                "sum",
            ),
            rto_cost=(
                "rto_cost",
                "sum",
            ),
            expected_cod_fee=(
                "expected_cod_fee",
                "sum",
            ),
        )
        .reset_index()
    )

    for _, row in (
        courier_summary.iterrows()
    ):
        add(
            lines,
            (
                f"{row['courier_name']}: "
                f"{int(row['orders']):,} orders | "
                f"forward={money(row['forward_cost'])} | "
                f"RTO={money(row['rto_cost'])} | "
                f"expected COD fee={money(row['expected_cod_fee'])}"
            )
        )


    # ========================================================
    # CONTRIBUTION PROFIT BEFORE MARKETING
    # ========================================================

    section(
        lines,
        "7. CONTRIBUTION PROFIT BEFORE MARKETING",
    )

    order_item_financials = (
        items.groupby(
            "order_id"
        )
        .agg(
            net_revenue=(
                "net_revenue",
                "sum",
            ),
            cogs=(
                "cogs",
                "sum",
            ),
        )
        .reset_index()
    )

    order_financials = (
        orders[
            [
                "order_id",
                "shipping_charge",
                "courier_id",
                "is_cod",
                "is_rto",
            ]
        ]
        .merge(
            order_item_financials,
            on="order_id",
            how="left",
        )
        .merge(
            payments[
                [
                    "order_id",
                    "payment_fee",
                    "cod_fee",
                    "refund_amount",
                ]
            ],
            on="order_id",
            how="left",
        )
        .merge(
            couriers[
                [
                    "courier_id",
                    "base_shipping_cost",
                    "rto_fee",
                ]
            ],
            on="courier_id",
            how="left",
        )
    )

    rto_bool = to_bool(
        order_financials[
            "is_rto"
        ]
    )

    order_financials[
        "forward_shipping_cost"
    ] = (
        order_financials[
            "base_shipping_cost"
        ]
        .fillna(0)
    )

    order_financials[
        "rto_cost"
    ] = (
        order_financials[
            "rto_fee"
        ]
        .fillna(0)
        * rto_bool.astype(int)
    )

    order_financials[
        "contribution_profit_before_marketing"
    ] = (
        order_financials[
            "net_revenue"
        ]
        + order_financials[
            "shipping_charge"
        ]
        .fillna(0)
        - order_financials[
            "cogs"
        ]
        - order_financials[
            "forward_shipping_cost"
        ]
        - order_financials[
            "cod_fee"
        ]
        .fillna(0)
        - order_financials[
            "payment_fee"
        ]
        .fillna(0)
        - order_financials[
            "rto_cost"
        ]
        - order_financials[
            "refund_amount"
        ]
        .fillna(0)
    )

    total_customer_revenue = (
        order_financials[
            "net_revenue"
        ].sum()
        + order_financials[
            "shipping_charge"
        ].fillna(0).sum()
    )

    total_contribution = (
        order_financials[
            "contribution_profit_before_marketing"
        ].sum()
    )

    contribution_margin = pct(
        total_contribution,
        total_customer_revenue,
    )

    loss_making_orders = int(
        (
            order_financials[
                "contribution_profit_before_marketing"
            ]
            < 0
        ).sum()
    )

    add(
        lines,
        (
            "Customer revenue: "
            f"{money(total_customer_revenue)}"
        )
    )

    add(
        lines,
        (
            "Contribution profit before marketing: "
            f"{money(total_contribution)}"
        )
    )

    add(
        lines,
        (
            "Contribution margin before marketing: "
            f"{contribution_margin:.2f}%"
        )
    )

    add(
        lines,
        (
            "Loss-making orders before marketing: "
            f"{loss_making_orders:,}"
        )
    )


    # ========================================================
    # COD VS PREPAID ECONOMICS
    # ========================================================

    section(
        lines,
        "8. COD VS PREPAID ECONOMICS",
    )

    order_financials[
        "payment_group"
    ] = (
        to_bool(
            order_financials[
                "is_cod"
            ]
        )
        .map(
            {
                True: "COD",
                False: "Prepaid",
            }
        )
    )

    payment_group_summary = (
        order_financials.groupby(
            "payment_group"
        )
        .agg(
            orders=(
                "order_id",
                "nunique",
            ),
            revenue=(
                "net_revenue",
                "sum",
            ),
            contribution_profit=(
                "contribution_profit_before_marketing",
                "sum",
            ),
        )
        .reset_index()
    )

    for _, row in (
        payment_group_summary.iterrows()
    ):
        margin = pct(
            row[
                "contribution_profit"
            ],
            row[
                "revenue"
            ],
        )

        add(
            lines,
            (
                f"{row['payment_group']}: "
                f"{int(row['orders']):,} orders | "
                f"revenue={money(row['revenue'])} | "
                f"contribution={money(row['contribution_profit'])} | "
                f"margin={margin:.2f}%"
            )
        )


    # ========================================================
    # RTO LOSS
    # ========================================================

    section(
        lines,
        "9. RTO ECONOMICS",
    )

    rto_financials = (
        order_financials[
            rto_bool
        ]
    )

    non_rto_financials = (
        order_financials[
            ~rto_bool
        ]
    )

    add(
        lines,
        (
            "RTO orders: "
            f"{len(rto_financials):,}"
        )
    )

    add(
        lines,
        (
            "RTO fee cost: "
            f"{money(rto_financials['rto_cost'].sum())}"
        )
    )

    add(
        lines,
        (
            "Average contribution on RTO orders: "
            f"{money(
                rto_financials[
                    'contribution_profit_before_marketing'
                ].mean()
            )}"
        )
    )

    add(
        lines,
        (
            "Average contribution on non-RTO orders: "
            f"{money(
                non_rto_financials[
                    'contribution_profit_before_marketing'
                ].mean()
            )}"
        )
    )


    # ========================================================
    # MONTHLY ECONOMICS
    # ========================================================

    section(
        lines,
        "10. MONTHLY REVENUE AND CONTRIBUTION",
    )

    order_financials = (
        order_financials.merge(
            orders[
                [
                    "order_id",
                    "order_date",
                ]
            ],
            on="order_id",
            how="left",
        )
    )

    order_financials[
        "month"
    ] = (
        order_financials[
            "order_date"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        order_financials.groupby(
            "month"
        )
        .agg(
            orders=(
                "order_id",
                "nunique",
            ),
            revenue=(
                "net_revenue",
                "sum",
            ),
            contribution_profit=(
                "contribution_profit_before_marketing",
                "sum",
            ),
        )
        .reset_index()
    )

    monthly[
        "contribution_margin_percent"
    ] = (
        monthly[
            "contribution_profit"
        ]
        / monthly[
            "revenue"
        ]
        * 100
    )

    for _, row in (
        monthly.iterrows()
    ):
        add(
            lines,
            (
                f"{row['month']}: "
                f"{int(row['orders']):,} orders | "
                f"revenue={money(row['revenue'])} | "
                f"contribution={money(row['contribution_profit'])} | "
                f"margin={row['contribution_margin_percent']:.2f}%"
            )
        )


    # ========================================================
    # MARKETING SANITY
    # ========================================================

    section(
        lines,
        "11. MARKETING SANITY",
    )

    total_business_revenue = (
        items[
            "net_revenue"
        ].sum()
    )

    marketing_spend = (
        marketing[
            "spend"
        ].sum()
    )

    attributed_revenue = (
        marketing[
            "attributed_revenue"
        ].sum()
    )

    attributed_orders = (
        marketing[
            "orders"
        ].sum()
    )

    attributed_new_customers = (
        marketing[
            "new_customers"
        ].sum()
    )

    roas = (
        attributed_revenue
        / marketing_spend
        if marketing_spend
        else 0
    )

    attributed_vs_business = (
        attributed_revenue
        / total_business_revenue
        if total_business_revenue
        else 0
    )

    add(
        lines,
        (
            "Business net revenue: "
            f"{money(total_business_revenue)}"
        )
    )

    add(
        lines,
        (
            "Marketing spend: "
            f"{money(marketing_spend)}"
        )
    )

    add(
        lines,
        (
            "Attributed revenue: "
            f"{money(attributed_revenue)}"
        )
    )

    add(
        lines,
        (
            "Blended ROAS: "
            f"{roas:.2f}x"
        )
    )

    add(
        lines,
        (
            "Attributed revenue / total business revenue: "
            f"{attributed_vs_business:.2f}x"
        )
    )

    add(
        lines,
        (
            "Attributed campaign orders: "
            f"{attributed_orders:,.0f}"
        )
    )

    add(
        lines,
        (
            "Actual business orders: "
            f"{orders['order_id'].nunique():,}"
        )
    )

    add(
        lines,
        (
            "Attributed new customers: "
            f"{attributed_new_customers:,.0f}"
        )
    )

    marketing_status = (
        "PASS"
        if (
            roas <= 15
            and attributed_vs_business <= 1.5
        )
        else "FAIL"
    )

    add(
        lines,
        (
            "Marketing sanity status: "
            f"{marketing_status}"
        )
    )


    # ========================================================
    # FINAL
    # ========================================================

    section(
        lines,
        "12. AUDIT V2 CONCLUSION",
    )

    critical_flags = {
        "delivered_missing_date":
            delivered_missing_date,

        "cancelled_with_delivery":
            cancelled_with_delivery,

        "rto_and_delivered":
            rto_and_delivered,

        "delivered_before_order":
            delivered_before_order,

        "marketing_sanity_failure":
            int(
                marketing_status
                == "FAIL"
            ),
    }

    for key, value in (
        critical_flags.items()
    ):
        add(
            lines,
            (
                f"{key}: "
                f"{value:,}"
            )
        )

    total_critical = sum(
        int(
            value > 0
        )
        for value in (
            critical_flags.values()
        )
    )

    add(lines)

    add(
        lines,
        (
            "OVERALL V2 STATUS: "
            + (
                "PASS"
                if total_critical == 0
                else "REVIEW REQUIRED"
            )
        )
    )


    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(
        f"Audit V2 complete: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()