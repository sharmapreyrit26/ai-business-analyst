from pathlib import Path

import pandas as pd

from backend.app.services.d2c_customer_engine import (
    get_customer_summary,
)


BASE_DIR = Path(
    "data/demo_india_d2c/"
    "indian_d2c_synthetic_dataset"
)

MARKETING_FILE = (
    BASE_DIR
    / "marketing.csv"
)


def main():
    marketing = pd.read_csv(
        MARKETING_FILE,
        low_memory=False,
    )

    marketing[
        "date"
    ] = pd.to_datetime(
        marketing[
            "date"
        ],
        errors="coerce",
    )

    marketing[
        "month"
    ] = (
        marketing[
            "date"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    adjusted_months = []

    for month in sorted(
        marketing[
            "month"
        ]
        .dropna()
        .unique()
    ):
        actual_new = int(
            get_customer_summary(
                month
            )[
                "new_customers"
            ]
        )

        month_mask = (
            marketing[
                "month"
            ]
            == month
        )

        attributed_new = int(
            marketing.loc[
                month_mask,
                "new_customers",
            ].sum()
        )

        if (
            attributed_new
            <= actual_new
            or attributed_new
            == 0
        ):
            continue

        scale = (
            actual_new
            / attributed_new
        )

        scaled_values = (
            marketing.loc[
                month_mask,
                "new_customers",
            ]
            * scale
        )

        marketing.loc[
            month_mask,
            "new_customers",
        ] = (
            scaled_values
            .round()
            .astype(int)
        )

        # Rounding can leave the total slightly off.
        new_total = int(
            marketing.loc[
                month_mask,
                "new_customers",
            ].sum()
        )

        difference = (
            actual_new
            - new_total
        )

        if difference != 0:
            month_indices = (
                marketing.loc[
                    month_mask
                ]
                .sort_values(
                    "new_customers",
                    ascending=False,
                )
                .index
                .tolist()
            )

            step = (
                1
                if difference > 0
                else -1
            )

            remaining = abs(
                difference
            )

            for index in month_indices:
                if remaining == 0:
                    break

                current = int(
                    marketing.at[
                        index,
                        "new_customers",
                    ]
                )

                if (
                    step < 0
                    and current <= 0
                ):
                    continue

                marketing.at[
                    index,
                    "new_customers",
                ] = (
                    current
                    + step
                )

                remaining -= 1

        final_total = int(
            marketing.loc[
                month_mask,
                "new_customers",
            ].sum()
        )

        adjusted_months.append(
            (
                month,
                attributed_new,
                actual_new,
                final_total,
            )
        )

    marketing = (
        marketing.drop(
            columns=[
                "month",
            ]
        )
    )

    marketing.to_csv(
        MARKETING_FILE,
        index=False,
        date_format="%Y-%m-%d",
    )

    print(
        "Marketing new-customer repair complete."
    )

    for (
        month,
        before,
        actual,
        after,
    ) in adjusted_months:
        print(
            f"{month}: "
            f"before={before:,}, "
            f"actual={actual:,}, "
            f"after={after:,}"
        )


if __name__ == "__main__":
    main()