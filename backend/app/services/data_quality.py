from backend.app.services.data_loader import load_orders
from backend.app.services.financial_analysis import (
    get_monthly_data_quality,
)


def check_order_data_quality():
    """
    Check the overall quality of the orders dataset.
    """

    df = load_orders()

    total_rows = len(df)

    missing_order_ids = int(
        df["order_id"].isna().sum()
    )

    missing_customer_ids = int(
        df["customer_id"].isna().sum()
    )

    duplicate_orders = int(
        df["order_id"].duplicated().sum()
    )

    missing_purchase_dates = int(
        df[
            "order_purchase_timestamp"
        ].isna().sum()
    )

    missing_delivery_dates = int(
        df[
            "order_delivered_customer_date"
        ].isna().sum()
    )

    issues = []

    if missing_order_ids > 0:
        issues.append(
            "Missing order IDs detected."
        )

    if duplicate_orders > 0:
        issues.append(
            "Duplicate order IDs detected."
        )

    if missing_purchase_dates > 0:
        issues.append(
            "Missing order purchase timestamps detected."
        )

    if total_rows == 0:

        status = "critical"

    elif (
        missing_order_ids > 0
        or duplicate_orders > 0
    ):

        status = "warning"

    else:

        status = "healthy"

    return {
        "status": status,
        "total_rows": int(total_rows),
        "missing_order_ids": missing_order_ids,
        "missing_customer_ids": missing_customer_ids,
        "duplicate_orders": duplicate_orders,
        "missing_purchase_dates": (
            missing_purchase_dates
        ),
        "missing_delivery_dates": (
            missing_delivery_dates
        ),
        "issues": issues,
    }


def check_monthly_data_quality():
    """
    Return monthly completeness and partial-period information.
    """

    monthly_quality = get_monthly_data_quality()

    partial_months = []

    complete_months = []

    for record in monthly_quality:

        if record["is_partial_month"]:

            partial_months.append(
                record["month"]
            )

        else:

            complete_months.append(
                record["month"]
            )

    return {
        "total_months": len(monthly_quality),
        "complete_months": complete_months,
        "partial_months": partial_months,
        "monthly_quality": monthly_quality,
    }


def get_data_quality_report():
    """
    Generate the complete data quality report.
    """

    order_quality = (
        check_order_data_quality()
    )

    monthly_quality = (
        check_monthly_data_quality()
    )

    return {
        "overall_status": (
            order_quality["status"]
        ),
        "orders": order_quality,
        "monthly": monthly_quality,
    }