from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(
    "data/demo_india_d2c/"
    "indian_d2c_synthetic_dataset"
)

OUTPUT_FILE = Path(
    "data/demo_india_d2c/"
    "d2c_data_audit_report.txt"
)

EXPECTED_FILES = {
    "products": "products.csv",
    "customers": "customers.csv",
    "couriers": "couriers.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
    "payments": "payments.csv",
    "marketing": "marketing.csv",
    "inventory": "inventory.csv",
}


# ============================================================
# HELPERS
# ============================================================

report = []


def add(text=""):
    report.append(str(text))


def section(title):
    add()
    add("=" * 70)
    add(title)
    add("=" * 70)


def pct(value, total):
    if total == 0:
        return 0.0

    return round(
        value / total * 100,
        2,
    )


def missing_summary(df):
    result = []

    for column in df.columns:
        missing = int(
            df[column].isna().sum()
        )

        if missing > 0:
            result.append(
                (
                    column,
                    missing,
                    pct(
                        missing,
                        len(df),
                    ),
                )
            )

    return result


# ============================================================
# LOAD DATA
# ============================================================

section("1. FILE AND ROW COUNT AUDIT")

tables = {}

for name, filename in EXPECTED_FILES.items():

    path = BASE_DIR / filename

    if not path.exists():
        add(
            f"FAIL | {filename} missing"
        )
        continue

    df = pd.read_csv(
        path,
        low_memory=False,
    )

    tables[name] = df

    add(
        f"PASS | {filename:<20} "
        f"rows={len(df):,} "
        f"columns={len(df.columns)}"
    )


# ============================================================
# DUPLICATES
# ============================================================

section("2. PRIMARY KEY / DUPLICATE AUDIT")

primary_keys = {
    "products": ["sku_id"],
    "customers": ["customer_id"],
    "couriers": ["courier_id"],
    "orders": ["order_id"],
    "payments": ["order_id"],
}

for table, keys in primary_keys.items():

    if table not in tables:
        continue

    df = tables[table]

    duplicates = int(
        df.duplicated(
            subset=keys
        ).sum()
    )

    status = (
        "PASS"
        if duplicates == 0
        else "FAIL"
    )

    add(
        f"{status} | {table:<15} "
        f"duplicate keys={duplicates:,}"
    )


# ============================================================
# MISSING VALUES
# ============================================================

section("3. MISSING VALUE AUDIT")

for name, df in tables.items():

    add()
    add(
        f"[{name}]"
    )

    missing = missing_summary(
        df
    )

    if not missing:
        add(
            "No missing values."
        )

    else:
        for (
            column,
            count,
            percentage,
        ) in missing:

            add(
                f"{column:<30} "
                f"{count:>8,} "
                f"({percentage:>6.2f}%)"
            )


# ============================================================
# RELATIONSHIP AUDIT
# ============================================================

section("4. FOREIGN KEY / RELATIONSHIP AUDIT")


def foreign_key_check(
    child_table,
    child_key,
    parent_table,
    parent_key,
):

    child = tables[
        child_table
    ]

    parent = tables[
        parent_table
    ]

    child_values = set(
        child[
            child_key
        ]
        .dropna()
        .astype(str)
    )

    parent_values = set(
        parent[
            parent_key
        ]
        .dropna()
        .astype(str)
    )

    missing = (
        child_values
        - parent_values
    )

    status = (
        "PASS"
        if len(missing) == 0
        else "FAIL"
    )

    add(
        f"{status} | "
        f"{child_table}.{child_key} "
        f"-> "
        f"{parent_table}.{parent_key} "
        f"| orphan keys={len(missing):,}"
    )


foreign_key_check(
    "orders",
    "customer_id",
    "customers",
    "customer_id",
)

foreign_key_check(
    "order_items",
    "order_id",
    "orders",
    "order_id",
)

foreign_key_check(
    "payments",
    "order_id",
    "orders",
    "order_id",
)

foreign_key_check(
    "order_items",
    "sku_id",
    "products",
    "sku_id",
)

foreign_key_check(
    "inventory",
    "sku_id",
    "products",
    "sku_id",
)

foreign_key_check(
    "orders",
    "courier_id",
    "couriers",
    "courier_id",
)


# ============================================================
# DATE COVERAGE
# ============================================================

section("5. DATE COVERAGE")

orders = tables["orders"].copy()

orders[
    "order_date"
] = pd.to_datetime(
    orders["order_date"],
    errors="coerce",
)

add(
    "First order date: "
    f"{orders['order_date'].min()}"
)

add(
    "Last order date:  "
    f"{orders['order_date'].max()}"
)

orders[
    "month"
] = (
    orders[
        "order_date"
    ]
    .dt.to_period("M")
    .astype(str)
)

monthly_orders = (
    orders.groupby(
        "month"
    )["order_id"]
    .nunique()
)

add()
add("Orders by month:")

for month, count in monthly_orders.items():

    add(
        f"{month}: {count:,}"
    )


# ============================================================
# FINANCIAL EQUATION AUDIT
# ============================================================

section("6. FINANCIAL LOGIC AUDIT")

items = tables[
    "order_items"
].copy()


# Gross revenue equation

expected_gross = (
    items[
        "selling_price"
    ]
    * items[
        "quantity"
    ]
)

gross_diff = (
    items[
        "gross_revenue"
    ]
    - expected_gross
).abs()

gross_failures = int(
    (
        gross_diff > 0.02
    ).sum()
)

add(
    f"{'PASS' if gross_failures == 0 else 'FAIL'}"
    f" | Gross Revenue = selling_price × quantity"
    f" | mismatches={gross_failures:,}"
)


# Net revenue equation

expected_net = (
    items[
        "gross_revenue"
    ]
    - items[
        "discount"
    ]
)

net_diff = (
    items[
        "net_revenue"
    ]
    - expected_net
).abs()

net_failures = int(
    (
        net_diff > 0.02
    ).sum()
)

add(
    f"{'PASS' if net_failures == 0 else 'FAIL'}"
    f" | Net Revenue = gross_revenue - discount"
    f" | mismatches={net_failures:,}"
)


# Order value equation

item_order_values = (
    items.groupby(
        "order_id"
    )[
        "net_revenue"
    ]
    .sum()
    .rename(
        "calculated_net_revenue"
    )
)

order_check = (
    orders.merge(
        item_order_values,
        on="order_id",
        how="left",
    )
)

order_check[
    "expected_order_value"
] = (
    order_check[
        "calculated_net_revenue"
    ]
    + order_check[
        "shipping_charge"
    ]
)

order_check[
    "difference"
] = (
    order_check[
        "order_value"
    ]
    - order_check[
        "expected_order_value"
    ]
).abs()

order_failures = int(
    (
        order_check[
            "difference"
        ]
        > 0.05
    ).sum()
)

add(
    f"{'PASS' if order_failures == 0 else 'FAIL'}"
    f" | Order Value = net revenue + shipping"
    f" | mismatches={order_failures:,}"
)


# ============================================================
# PAYMENT CONSISTENCY
# ============================================================

section("7. PAYMENT CONSISTENCY")

payments = tables[
    "payments"
].copy()

payment_check = (
    orders[
        [
            "order_id",
            "payment_method",
            "is_cod",
        ]
    ]
    .merge(
        payments[
            [
                "order_id",
                "payment_method",
                "cod_fee",
                "payment_fee",
                "refund_amount",
            ]
        ],
        on="order_id",
        how="left",
        suffixes=(
            "_orders",
            "_payments",
        ),
    )
)

method_mismatch = int(
    (
        payment_check[
            "payment_method_orders"
        ]
        != payment_check[
            "payment_method_payments"
        ]
    ).sum()
)

add(
    f"{'PASS' if method_mismatch == 0 else 'FAIL'}"
    f" | Order/payment method consistency"
    f" | mismatches={method_mismatch:,}"
)

non_cod_with_cod_fee = int(
    (
        (
            payment_check[
                "is_cod"
            ]
            == 0
        )
        & (
            payment_check[
                "cod_fee"
            ]
            .fillna(0)
            > 0
        )
    ).sum()
)

add(
    f"{'PASS' if non_cod_with_cod_fee == 0 else 'WARN'}"
    f" | Non-COD orders with COD fee"
    f" | rows={non_cod_with_cod_fee:,}"
)


# ============================================================
# LOGISTICS / D2C FLAGS
# ============================================================

section("8. D2C LOGISTICS AUDIT")

for column in [
    "is_cod",
    "is_rto",
    "is_returned",
    "ndr_flag",
    "first_attempt_delivery",
]:

    if column not in orders.columns:
        continue

    values = (
        orders[
            column
        ]
        .value_counts(
            dropna=False
        )
    )

    add()
    add(
        f"{column}:"
    )

    for value, count in values.items():

        add(
            f"  {value}: {count:,}"
        )


# COD / RTO rates

cod_orders = orders[
    orders[
        "is_cod"
    ]
    == 1
]

prepaid_orders = orders[
    orders[
        "is_cod"
    ]
    == 0
]

cod_rto_rate = (
    cod_orders[
        "is_rto"
    ]
    .mean()
    * 100
    if len(cod_orders)
    else 0
)

prepaid_rto_rate = (
    prepaid_orders[
        "is_rto"
    ]
    .mean()
    * 100
    if len(prepaid_orders)
    else 0
)

add()
add(
    f"COD orders: {len(cod_orders):,}"
)

add(
    f"Prepaid orders: {len(prepaid_orders):,}"
)

add(
    f"COD RTO rate: {cod_rto_rate:.2f}%"
)

add(
    f"Prepaid RTO rate: {prepaid_rto_rate:.2f}%"
)


# ============================================================
# PRODUCT ECONOMICS
# ============================================================

section("9. PRODUCT ECONOMICS")

items[
    "gross_margin_before_other_costs"
] = (
    items[
        "net_revenue"
    ]
    - items[
        "cogs"
    ]
)

total_net_revenue = (
    items[
        "net_revenue"
    ]
    .sum()
)

total_cogs = (
    items[
        "cogs"
    ]
    .sum()
)

gross_margin = (
    total_net_revenue
    - total_cogs
)

gross_margin_pct = (
    gross_margin
    / total_net_revenue
    * 100
    if total_net_revenue
    else 0
)

add(
    f"Net revenue: {total_net_revenue:,.2f}"
)

add(
    f"COGS: {total_cogs:,.2f}"
)

add(
    f"Gross margin: {gross_margin:,.2f}"
)

add(
    f"Gross margin %: {gross_margin_pct:.2f}%"
)

negative_margin_rows = int(
    (
        items[
            "gross_margin_before_other_costs"
        ]
        < 0
    ).sum()
)

add(
    f"Negative-margin item rows: "
    f"{negative_margin_rows:,}"
)


# ============================================================
# MARKETING AUDIT
# ============================================================

section("10. MARKETING AUDIT")

marketing = tables[
    "marketing"
].copy()

marketing[
    "date"
] = pd.to_datetime(
    marketing["date"],
    errors="coerce",
)

add(
    f"Marketing date range: "
    f"{marketing['date'].min()} "
    f"to "
    f"{marketing['date'].max()}"
)

total_spend = (
    marketing[
        "spend"
    ]
    .sum()
)

attributed_revenue = (
    marketing[
        "attributed_revenue"
    ]
    .sum()
)

roas = (
    attributed_revenue
    / total_spend
    if total_spend
    else 0
)

add(
    f"Total marketing spend: "
    f"{total_spend:,.2f}"
)

add(
    f"Attributed revenue: "
    f"{attributed_revenue:,.2f}"
)

add(
    f"Blended attributed ROAS: "
    f"{roas:.2f}"
)


# ============================================================
# INVENTORY AUDIT
# ============================================================

section("11. INVENTORY AUDIT")

inventory = tables[
    "inventory"
].copy()

negative_stock = int(
    (
        inventory[
            "closing_stock"
        ]
        < 0
    ).sum()
)

below_reorder = int(
    (
        inventory[
            "closing_stock"
        ]
        <= inventory[
            "reorder_point"
        ]
    ).sum()
)

add(
    f"{'PASS' if negative_stock == 0 else 'FAIL'}"
    f" | Negative closing stock"
    f" | rows={negative_stock:,}"
)

add(
    f"SKUs/warehouse rows at or below "
    f"reorder point: {below_reorder:,}"
)


# ============================================================
# DATASET SUMMARY
# ============================================================

section("12. DATASET SUMMARY")

add(
    f"Tables loaded: "
    f"{len(tables)}/{len(EXPECTED_FILES)}"
)

add(
    f"Orders: "
    f"{len(orders):,}"
)

add(
    f"Order items: "
    f"{len(items):,}"
)

add(
    f"Customers: "
    f"{len(tables['customers']):,}"
)

add(
    f"Products: "
    f"{len(tables['products']):,}"
)

add(
    f"Couriers: "
    f"{len(tables['couriers']):,}"
)

add(
    f"Payments: "
    f"{len(payments):,}"
)

add(
    f"Marketing rows: "
    f"{len(marketing):,}"
)

add(
    f"Inventory rows: "
    f"{len(inventory):,}"
)

add()
add(
    "Audit complete."
)


# ============================================================
# WRITE REPORT
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8",
)

print(
    f"Audit complete: {OUTPUT_FILE}"
)