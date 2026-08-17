from .performance import get_monthly_performance


def detect_trends():
    """
    Detect important business trends from monthly performance data.
    """

    df = get_monthly_performance()

    trends = []

    # ---------------------------------------------------------
    # 1. Revenue trends
    # ---------------------------------------------------------

    for i in range(1, len(df)):
        current = df.iloc[i]
        previous = df.iloc[i - 1]

        revenue_change = current["revenue_growth"]

        if revenue_change <= -10:
            trends.append({
                "type": "revenue_decline",
                "severity": "high",
                "month": current["month"],
                "metric": "revenue",
                "change_percent": round(
                    float(revenue_change), 2
                ),
                "message": (
                    f"Revenue declined by "
                    f"{abs(revenue_change):.2f}% "
                    f"in {current['month']}."
                )
            })

        elif revenue_change >= 20:
            trends.append({
                "type": "revenue_growth",
                "severity": "positive",
                "month": current["month"],
                "metric": "revenue",
                "change_percent": round(
                    float(revenue_change), 2
                ),
                "message": (
                    f"Revenue increased by "
                    f"{revenue_change:.2f}% "
                    f"in {current['month']}."
                )
            })

    # ---------------------------------------------------------
    # 2. Order trends
    # ---------------------------------------------------------

    for i in range(1, len(df)):
        current = df.iloc[i]

        order_change = current["order_growth"]

        if order_change <= -10:
            trends.append({
                "type": "order_decline",
                "severity": "high",
                "month": current["month"],
                "metric": "orders",
                "change_percent": round(
                    float(order_change), 2
                ),
                "message": (
                    f"Orders declined by "
                    f"{abs(order_change):.2f}% "
                    f"in {current['month']}."
                )
            })

    # ---------------------------------------------------------
    # 3. Delivery performance
    # ---------------------------------------------------------

    max_delivery = df.loc[
        df["delivery_rate"].idxmax()
    ]

    min_delivery = df.loc[
        df["delivery_rate"].idxmin()
    ]

    trends.append({
        "type": "best_delivery_rate",
        "severity": "positive",
        "month": max_delivery["month"],
        "metric": "delivery_rate",
        "value": round(
            float(max_delivery["delivery_rate"]), 2
        ),
        "message": (
            f"Highest delivery rate was "
            f"{max_delivery['delivery_rate']:.2f}% "
            f"in {max_delivery['month']}."
        )
    })

    trends.append({
        "type": "worst_delivery_rate",
        "severity": "warning",
        "month": min_delivery["month"],
        "metric": "delivery_rate",
        "value": round(
            float(min_delivery["delivery_rate"]), 2
        ),
        "message": (
            f"Lowest delivery rate was "
            f"{min_delivery['delivery_rate']:.2f}% "
            f"in {min_delivery['month']}."
        )
    })

    # ---------------------------------------------------------
    # 4. Cancellation rate
    # ---------------------------------------------------------

    max_cancellation = df.loc[
        df["cancellation_rate"].idxmax()
    ]

    trends.append({
        "type": "highest_cancellation_rate",
        "severity": "warning",
        "month": max_cancellation["month"],
        "metric": "cancellation_rate",
        "value": round(
            float(max_cancellation["cancellation_rate"]), 2
        ),
        "message": (
            f"Highest cancellation rate was "
            f"{max_cancellation['cancellation_rate']:.2f}% "
            f"in {max_cancellation['month']}."
        )
    })

    # ---------------------------------------------------------
    # 5. AOV
    # ---------------------------------------------------------

    max_aov = df.loc[
        df["aov"].idxmax()
    ]

    min_aov = df.loc[
        df["aov"].idxmin()
    ]

    trends.append({
        "type": "highest_aov",
        "severity": "positive",
        "month": max_aov["month"],
        "metric": "aov",
        "value": round(
            float(max_aov["aov"]), 2
        ),
        "message": (
            f"Highest AOV was "
            f"{max_aov['aov']:.2f} "
            f"in {max_aov['month']}."
        )
    })

    trends.append({
        "type": "lowest_aov",
        "severity": "warning",
        "month": min_aov["month"],
        "metric": "aov",
        "value": round(
            float(min_aov["aov"]), 2
        ),
        "message": (
            f"Lowest AOV was "
            f"{min_aov['aov']:.2f} "
            f"in {min_aov['month']}."
        )
    })

    return trends