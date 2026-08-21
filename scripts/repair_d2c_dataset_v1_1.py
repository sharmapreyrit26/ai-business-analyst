from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(
    "data/demo_india_d2c/"
    "indian_d2c_synthetic_dataset"
)

BACKUP_DIR = Path(
    "data/demo_india_d2c/"
    "indian_d2c_synthetic_dataset_v1_backup"
)


def main():
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # LOAD
    # ========================================================

    orders = pd.read_csv(
        BASE_DIR / "orders.csv",
        low_memory=False,
    )

    marketing = pd.read_csv(
        BASE_DIR / "marketing.csv",
        low_memory=False,
    )

    # ========================================================
    # BACKUP ORIGINALS
    # ========================================================

    orders.to_csv(
        BACKUP_DIR / "orders.csv",
        index=False,
    )

    marketing.to_csv(
        BACKUP_DIR / "marketing.csv",
        index=False,
    )

    # ========================================================
    # FIX FIRST ATTEMPT TIMESTAMPS
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

    invalid_attempt = (
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
    )

    fixed_rows = int(
        invalid_attempt.sum()
    )

    # For impossible rows, set first attempt
    # equal to delivered date.
    #
    # This preserves chronology without inventing
    # an earlier arbitrary date.
    orders.loc[
        invalid_attempt,
        "first_attempt_delivery",
    ] = orders.loc[
        invalid_attempt,
        "order_delivered_date",
    ]

    # ========================================================
    # REBUILD MARKETING TABLE
    # ========================================================

    marketing["date"] = pd.to_datetime(
        marketing["date"],
        errors="coerce",
    )

    rng = np.random.default_rng(
        42
    )

    # Keep original:
    # - dates
    # - channels
    # - campaigns
    #
    # Rebuild commercial metrics into sane scale.

    paid_mask = (
        marketing["channel"]
        .astype(str)
        .str.lower()
        != "organic"
    )

    # --------------------------------------------------------
    # Spend
    # --------------------------------------------------------

    # Keep existing spend for paid channels.
    # Organic remains zero.

    marketing.loc[
        ~paid_mask,
        "spend",
    ] = 0.0

    # --------------------------------------------------------
    # Sessions
    # --------------------------------------------------------

    # Reasonable daily/campaign session volumes.
    marketing["sessions"] = (
        rng.integers(
            400,
            4500,
            size=len(marketing),
        )
    )

    # Organic can have higher natural traffic.
    organic_rows = (
        ~paid_mask
    )

    marketing.loc[
        organic_rows,
        "sessions",
    ] = rng.integers(
        900,
        6000,
        size=int(
            organic_rows.sum()
        ),
    )

    # --------------------------------------------------------
    # Clicks
    # --------------------------------------------------------

    ctr = rng.uniform(
        0.015,
        0.055,
        size=len(marketing),
    )

    marketing["clicks"] = (
        marketing["sessions"]
        * ctr
    ).round().astype(int)

    # --------------------------------------------------------
    # Orders
    # --------------------------------------------------------

    conversion_rate = rng.uniform(
        0.012,
        0.038,
        size=len(marketing),
    )

    marketing["orders"] = (
        marketing["sessions"]
        * conversion_rate
    ).round().astype(int)

    # --------------------------------------------------------
    # New Customers
    # --------------------------------------------------------

    new_customer_share = rng.uniform(
        0.42,
        0.72,
        size=len(marketing),
    )

    marketing["new_customers"] = (
        marketing["orders"]
        * new_customer_share
    ).round().astype(int)

    # Never more new customers than orders.
    marketing[
        "new_customers"
    ] = np.minimum(
        marketing[
            "new_customers"
        ],
        marketing[
            "orders"
        ],
    )

    # --------------------------------------------------------
    # Attributed Revenue
    # --------------------------------------------------------

    # Use plausible campaign-level AOV.
    attributed_aov = rng.uniform(
        1100,
        1700,
        size=len(marketing),
    )

    marketing[
        "attributed_revenue"
    ] = (
        marketing[
            "orders"
        ]
        * attributed_aov
    ).round(2)

    # --------------------------------------------------------
    # Scale attributed orders to business reality
    # --------------------------------------------------------

    actual_orders = (
        orders[
            "order_id"
        ]
        .nunique()
    )

    target_attributed_orders = int(
        actual_orders
        * 0.72
    )

    current_attributed_orders = int(
        marketing[
            "orders"
        ].sum()
    )

    if current_attributed_orders > 0:
        scale = (
            target_attributed_orders
            / current_attributed_orders
        )

        marketing[
            "orders"
        ] = (
            marketing[
                "orders"
            ]
            * scale
        ).round().astype(int)

        marketing[
            "orders"
        ] = (
            marketing[
                "orders"
            ]
            .clip(
                lower=0
            )
        )

        marketing[
            "new_customers"
        ] = np.minimum(
            (
                marketing[
                    "new_customers"
                ]
                * scale
            )
            .round()
            .astype(int),
            marketing[
                "orders"
            ],
        )

    # Recalculate attributed revenue after scaling.
    marketing[
        "attributed_revenue"
    ] = (
        marketing[
            "orders"
        ]
        * attributed_aov
    ).round(2)

    # --------------------------------------------------------
    # Paid-channel ROAS sanity adjustment
    # --------------------------------------------------------

    paid_spend = (
        marketing.loc[
            paid_mask,
            "spend",
        ].sum()
    )

    paid_revenue = (
        marketing.loc[
            paid_mask,
            "attributed_revenue",
        ].sum()
    )

    # Target blended paid ROAS ~4.0x.
    target_paid_roas = 4.0

    if (
        paid_spend > 0
        and paid_revenue > 0
    ):
        revenue_scale = (
            paid_spend
            * target_paid_roas
            / paid_revenue
        )

        marketing.loc[
            paid_mask,
            "attributed_revenue",
        ] = (
            marketing.loc[
                paid_mask,
                "attributed_revenue",
            ]
            * revenue_scale
        ).round(2)

    # Organic remains naturally attributed
    # without paid spend.
    marketing.loc[
        organic_rows,
        "attributed_revenue",
    ] = (
        marketing.loc[
            organic_rows,
            "orders",
        ]
        * rng.uniform(
            1150,
            1650,
            size=int(
                organic_rows.sum()
            ),
        )
    ).round(2)

    # ========================================================
    # SAVE
    # ========================================================

    orders.to_csv(
        BASE_DIR / "orders.csv",
        index=False,
        date_format="%Y-%m-%d",
    )

    marketing.to_csv(
        BASE_DIR / "marketing.csv",
        index=False,
        date_format="%Y-%m-%d",
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    total_marketing_spend = (
        marketing["spend"]
        .sum()
    )

    total_attributed_revenue = (
        marketing[
            "attributed_revenue"
        ].sum()
    )

    attributed_orders = int(
        marketing[
            "orders"
        ].sum()
    )

    paid_revenue = (
        marketing.loc[
            paid_mask,
            "attributed_revenue",
        ].sum()
    )

    paid_spend = (
        marketing.loc[
            paid_mask,
            "spend",
        ].sum()
    )

    paid_roas = (
        paid_revenue
        / paid_spend
        if paid_spend
        else 0
    )

    print()
    print(
        "ProfitLens D2C Dataset Repair Complete"
    )
    print(
        "=" * 50
    )

    print(
        "First-attempt timestamps fixed:",
        f"{fixed_rows:,}",
    )

    print(
        "Actual business orders:",
        f"{actual_orders:,}",
    )

    print(
        "Attributed marketing orders:",
        f"{attributed_orders:,}",
    )

    print(
        "Marketing spend:",
        f"₹{total_marketing_spend:,.2f}",
    )

    print(
        "Attributed revenue:",
        f"₹{total_attributed_revenue:,.2f}",
    )

    print(
        "Paid blended ROAS:",
        f"{paid_roas:.2f}x",
    )

    print()
    print(
        "Original orders.csv and marketing.csv backed up to:"
    )

    print(
        BACKUP_DIR
    )


if __name__ == "__main__":
    main()