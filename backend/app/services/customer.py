from backend.app.services.data_loader import (
    load_orders,
)


def get_customer_data_quality():
    """
    Evaluate whether the current dataset can support
    customer-level analytics.

    Important:
    Olist customer_id should not automatically be treated
    as a persistent real-world customer identifier.

    True repeat-purchase analysis requires a persistent
    customer identifier such as customer_unique_id.
    """

    df = load_orders()

    total_orders = len(df)

    missing_customer_ids = int(
        df["customer_id"].isna().sum()
    )

    unique_customer_ids = int(
        df["customer_id"].nunique()
    )

    customer_id_coverage = (
        (
            total_orders
            - missing_customer_ids
        )
        / total_orders
        * 100
        if total_orders
        else 0
    )

    return {
        "status": "partial",

        "total_orders": int(
            total_orders
        ),

        "unique_customer_ids": (
            unique_customer_ids
        ),

        "missing_customer_ids": (
            missing_customer_ids
        ),

        "customer_id_coverage_percent": round(
            customer_id_coverage,
            2
        ),

        "persistent_customer_identifier_available": (
            False
        ),

        "limitations": [
            (
                "The current dataset contains customer_id "
                "but not a persistent customer_unique_id."
            ),
            (
                "Repeat purchase, retention and cohort "
                "analysis cannot be calculated reliably "
                "with the currently connected data."
            ),
        ],
    }


def get_customer_order_summary():
    """
    Return customer-ID coverage information.

    This is NOT a repeat-purchase analysis.
    """

    df = load_orders()

    customer_orders = (
        df.groupby(
            "customer_id"
        )["order_id"]
        .nunique()
    )

    return {
        "customer_records": int(
            df["customer_id"].nunique()
        ),

        "average_orders_per_customer_id": round(
            float(
                customer_orders.mean()
            ),
            4
        )
        if len(customer_orders)
        else 0,

        "maximum_orders_for_single_customer_id": int(
            customer_orders.max()
        )
        if len(customer_orders)
        else 0,

        "interpretation_warning": (
            "These values describe customer_id records only. "
            "They must not be interpreted as true customer "
            "repeat-purchase behaviour without a persistent "
            "customer identifier."
        ),
    }


def get_repeat_purchase_analysis():
    """
    Repeat-purchase analysis cannot currently be
    calculated reliably.
    """

    return {
        "metric": "repeat_purchase_rate",

        "status": "insufficient_data",

        "value": None,

        "reason": (
            "A persistent customer identifier is required "
            "to determine whether orders belong to the "
            "same underlying customer."
        ),

        "required_data": [
            "customer_unique_id",
            "order_id",
            "order_purchase_timestamp",
        ],
    }


def get_retention_analysis():
    """
    Customer retention requires persistent customer identity.
    """

    return {
        "metric": "customer_retention",

        "status": "insufficient_data",

        "value": None,

        "reason": (
            "Retention requires identifying the same "
            "customer across multiple purchase periods."
        ),

        "required_data": [
            "customer_unique_id",
            "order_purchase_timestamp",
        ],
    }


def get_cohort_analysis():
    """
    Cohort analysis cannot yet be calculated.
    """

    return {
        "metric": "customer_cohorts",

        "status": "insufficient_data",

        "value": None,

        "reason": (
            "Customer cohorts require a persistent "
            "customer identifier and purchase history."
        ),

        "required_data": [
            "customer_unique_id",
            "order_purchase_timestamp",
        ],
    }


def get_ltv_analysis():
    """
    LTV cannot currently be calculated reliably.
    """

    return {
        "metric": "ltv",

        "status": "insufficient_data",

        "value": None,

        "reason": (
            "Customer lifetime value requires persistent "
            "customer identity and longitudinal revenue "
            "history. Profit-based LTV additionally requires "
            "customer-level costs."
        ),

        "required_data": [
            "customer_unique_id",
            "customer revenue history",
            "customer purchase history",
            "customer-level costs",
        ],
    }


def get_cac_analysis():
    """
    CAC requires acquisition and marketing cost data.
    """

    return {
        "metric": "cac",

        "status": "insufficient_data",

        "value": None,

        "reason": (
            "Customer acquisition cost requires marketing "
            "or acquisition spend and newly acquired "
            "customer counts."
        ),

        "required_data": [
            "marketing spend",
            "acquisition channel",
            "new customer count",
        ],
    }


def get_customer_analytics():
    """
    Build the complete V1 customer analytics response.

    ProfitLens explicitly separates:
    - what can currently be measured
    - what requires additional data
    """

    return {
        "status": "partial",

        "data_quality": (
            get_customer_data_quality()
        ),

        "available_analysis": {
            "customer_order_summary": (
                get_customer_order_summary()
            ),
        },

        "unavailable_analysis": {
            "repeat_purchase": (
                get_repeat_purchase_analysis()
            ),

            "retention": (
                get_retention_analysis()
            ),

            "cohorts": (
                get_cohort_analysis()
            ),

            "ltv": (
                get_ltv_analysis()
            ),

            "cac": (
                get_cac_analysis()
            ),
        },

        "next_data_requirement": {
            "dataset": (
                "olist_customers_dataset.csv"
            ),

            "critical_field": (
                "customer_unique_id"
            ),

            "reason": (
                "This allows multiple order-level customer "
                "records to be mapped back to the same "
                "underlying customer."
            ),
        },
    }