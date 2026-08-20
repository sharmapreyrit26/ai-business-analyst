from backend.app.services.financial_analysis import (
    get_monthly_revenue,
    get_monthly_data_quality,
)
from backend.app.services.performance import (
    get_monthly_performance,
)
from backend.app.services.root_cause_engine import (
    analyze_root_causes,
)


def _get_complete_months():
    """
    Return the months considered complete by the
    data-quality layer.
    """

    quality = get_monthly_data_quality()

    return {
        row["month"]
        for row in quality
        if not row["is_partial_month"]
    }


def _severity_from_change(
    change_percent: float,
    warning_threshold: float,
    critical_threshold: float,
):
    """
    Convert percentage movement into anomaly severity.
    """

    magnitude = abs(
        change_percent
    )

    if magnitude >= critical_threshold:
        return "critical"

    if magnitude >= warning_threshold:
        return "warning"

    return None


def detect_revenue_anomalies(
    warning_threshold: float = 10.0,
    critical_threshold: float = 20.0,
):
    """
    Detect unusually large month-over-month
    revenue movements.
    """

    df = get_monthly_revenue().copy()

    complete_months = (
        _get_complete_months()
    )

    df = df[
        df["month"].isin(
            complete_months
        )
    ].copy()

    anomalies = []

    for _, row in df.iterrows():

        change = row[
            "revenue_growth"
        ]

        if change is None:
            continue

        severity = _severity_from_change(
            float(change),
            warning_threshold,
            critical_threshold,
        )

        if severity is None:
            continue

        direction = (
            "increase"
            if change > 0
            else "decrease"
        )

        anomalies.append({
            "type": "revenue_anomaly",
            "metric": "revenue",
            "month": row["month"],
            "severity": severity,
            "direction": direction,
            "value": round(
                float(row["revenue"]),
                2
            ),
            "change_percent": round(
                float(change),
                2
            ),
            "message": (
                f"Revenue showed an unusual "
                f"{direction} of "
                f"{abs(float(change)):.2f}% "
                f"in {row['month']}."
            ),
        })

    return anomalies


def detect_order_anomalies(
    warning_threshold: float = 10.0,
    critical_threshold: float = 20.0,
):
    """
    Detect unusually large month-over-month
    order movements.
    """

    df = get_monthly_revenue().copy()

    complete_months = (
        _get_complete_months()
    )

    df = df[
        df["month"].isin(
            complete_months
        )
    ].copy()

    anomalies = []

    for _, row in df.iterrows():

        change = row[
            "order_growth"
        ]

        if change is None:
            continue

        severity = _severity_from_change(
            float(change),
            warning_threshold,
            critical_threshold,
        )

        if severity is None:
            continue

        direction = (
            "increase"
            if change > 0
            else "decrease"
        )

        anomalies.append({
            "type": "order_anomaly",
            "metric": "orders",
            "month": row["month"],
            "severity": severity,
            "direction": direction,
            "value": int(
                row["orders"]
            ),
            "change_percent": round(
                float(change),
                2
            ),
            "message": (
                f"Orders showed an unusual "
                f"{direction} of "
                f"{abs(float(change)):.2f}% "
                f"in {row['month']}."
            ),
        })

    return anomalies


def detect_aov_anomalies(
    warning_threshold: float = 8.0,
    critical_threshold: float = 15.0,
):
    """
    Detect unusually large AOV movements.
    """

    df = get_monthly_revenue().copy()

    complete_months = (
        _get_complete_months()
    )

    df = df[
        df["month"].isin(
            complete_months
        )
    ].copy()

    anomalies = []

    for _, row in df.iterrows():

        change = row[
            "aov_growth"
        ]

        if change is None:
            continue

        severity = _severity_from_change(
            float(change),
            warning_threshold,
            critical_threshold,
        )

        if severity is None:
            continue

        direction = (
            "increase"
            if change > 0
            else "decrease"
        )

        anomalies.append({
            "type": "aov_anomaly",
            "metric": "aov",
            "month": row["month"],
            "severity": severity,
            "direction": direction,
            "value": round(
                float(row["aov"]),
                2
            ),
            "change_percent": round(
                float(change),
                2
            ),
            "message": (
                f"AOV showed an unusual "
                f"{direction} of "
                f"{abs(float(change)):.2f}% "
                f"in {row['month']}."
            ),
        })

    return anomalies


def detect_delivery_anomalies(
    warning_rate: float = 95.0,
    critical_rate: float = 90.0,
):
    """
    Detect unusually weak delivery performance.
    """

    df = get_monthly_performance().copy()

    complete_months = (
        _get_complete_months()
    )

    df = df[
        df["month"].isin(
            complete_months
        )
    ].copy()

    anomalies = []

    for _, row in df.iterrows():

        rate = float(
            row["delivery_rate"]
        )

        if rate < critical_rate:
            severity = "critical"

        elif rate < warning_rate:
            severity = "warning"

        else:
            continue

        anomalies.append({
            "type": "delivery_anomaly",
            "metric": "delivery_rate",
            "month": row["month"],
            "severity": severity,
            "direction": "weak_performance",
            "value": round(
                rate,
                2
            ),
            "message": (
                f"Delivery rate fell to "
                f"{rate:.2f}% in "
                f"{row['month']}."
            ),
        })

    return anomalies


def detect_cancellation_anomalies(
    warning_rate: float = 1.0,
    critical_rate: float = 2.0,
):
    """
    Detect elevated cancellation rates.

    Thresholds are temporary V1 rules based on
    the available demonstration dataset.
    """

    df = get_monthly_performance().copy()

    complete_months = (
        _get_complete_months()
    )

    df = df[
        df["month"].isin(
            complete_months
        )
    ].copy()

    anomalies = []

    for _, row in df.iterrows():

        rate = float(
            row["cancellation_rate"]
        )

        if rate >= critical_rate:
            severity = "critical"

        elif rate >= warning_rate:
            severity = "warning"

        else:
            continue

        anomalies.append({
            "type": "cancellation_anomaly",
            "metric": "cancellation_rate",
            "month": row["month"],
            "severity": severity,
            "direction": "elevated",
            "value": round(
                rate,
                2
            ),
            "message": (
                f"Cancellation rate increased to "
                f"{rate:.2f}% in "
                f"{row['month']}."
            ),
        })

    return anomalies


def detect_all_anomalies():
    """
    Detect anomalies across all currently
    supported ProfitLens metrics.
    """

    anomalies = []

    anomalies.extend(
        detect_revenue_anomalies()
    )

    anomalies.extend(
        detect_order_anomalies()
    )

    anomalies.extend(
        detect_aov_anomalies()
    )

    anomalies.extend(
        detect_delivery_anomalies()
    )

    anomalies.extend(
        detect_cancellation_anomalies()
    )

    severity_order = {
        "critical": 0,
        "warning": 1,
    }

    anomalies = sorted(
        anomalies,
        key=lambda item: (
            severity_order.get(
                item["severity"],
                99
            ),
            item["month"],
        )
    )

    return anomalies


def investigate_anomaly(
    anomaly: dict
):
    """
    Send an anomaly into the appropriate
    deterministic investigation layer.

    Revenue anomalies can currently use the
    full root-cause engine.

    Other anomaly types are flagged for further
    investigation because their specialized
    root-cause engines have not yet been built.
    """

    metric = anomaly[
        "metric"
    ]

    month = anomaly[
        "month"
    ]

    if metric == "revenue":

        root_cause = (
            analyze_root_causes(
                month
            )
        )

        return {
            "anomaly": anomaly,
            "investigation_status": (
                "root_cause_analysis_complete"
            ),
            "root_cause": root_cause,
        }

    return {
        "anomaly": anomaly,

        "investigation_status": (
            "specialized_analysis_required"
        ),

        "root_cause": None,

        "message": (
            f"A specialized {metric} root-cause "
            f"analysis engine has not yet been built."
        ),
    }


def build_anomaly_report():
    """
    Build the full anomaly report.

    Important anomalies are automatically
    prepared for investigation.
    """

    anomalies = (
        detect_all_anomalies()
    )

    investigations = []

    for anomaly in anomalies:

        if anomaly[
            "severity"
        ] in {
            "critical",
            "warning",
        }:

            investigations.append(
                investigate_anomaly(
                    anomaly
                )
            )

    critical_count = sum(
        1
        for anomaly in anomalies
        if anomaly[
            "severity"
        ] == "critical"
    )

    warning_count = sum(
        1
        for anomaly in anomalies
        if anomaly[
            "severity"
        ] == "warning"
    )

    return {
        "status": "complete",

        "total_anomalies": len(
            anomalies
        ),

        "critical_anomalies": (
            critical_count
        ),

        "warning_anomalies": (
            warning_count
        ),

        "anomalies": anomalies,

        "investigations": (
            investigations
        ),
    }