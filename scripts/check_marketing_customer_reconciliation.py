from backend.app.services.d2c_customer_engine import (
    get_customer_summary,
)

from backend.app.services.d2c_profitability_engine import (
    get_monthly_marketing,
)


def main():
    marketing = (
        get_monthly_marketing()
        .copy()
    )

    print(
        "month | actual_new | attributed_new | difference | status"
    )

    print(
        "-" * 70
    )

    total_actual = 0
    total_attributed = 0

    for _, row in marketing.iterrows():

        month = str(
            row["month"]
        )

        customer = (
            get_customer_summary(
                month
            )
        )

        actual_new = int(
            customer[
                "new_customers"
            ]
        )

        attributed_new = int(
            row[
                "new_customers"
            ]
        )

        difference = (
            attributed_new
            - actual_new
        )

        status = (
            "PASS"
            if attributed_new
            <= actual_new
            else "FAIL"
        )

        print(
            f"{month} | "
            f"{actual_new:>10,} | "
            f"{attributed_new:>14,} | "
            f"{difference:>10,} | "
            f"{status}"
        )

        total_actual += (
            actual_new
        )

        total_attributed += (
            attributed_new
        )

    print(
        "-" * 70
    )

    print(
        f"TOTAL | "
        f"{total_actual:>10,} | "
        f"{total_attributed:>14,} | "
        f"{total_attributed - total_actual:>10,}"
    )


if __name__ == "__main__":
    main()