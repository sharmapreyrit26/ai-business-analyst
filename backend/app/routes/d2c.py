from backend.app.services.d2c_overview_engine import (
    get_d2c_overview,
)
from backend.app.services.d2c_inventory_engine import (
    get_inventory_summary,
    get_sku_inventory_performance,
    get_warehouse_inventory_performance,
    get_category_inventory_performance,
)
from backend.app.services.d2c_marketing_engine import (
    get_marketing_summary,
    get_channel_performance,
    get_campaign_performance,
    get_monthly_marketing_trend,
    get_marketing_insights,
)
from backend.app.services.d2c_logistics_engine import (
    get_courier_performance,
    get_logistics_summary,
    get_payment_logistics_performance,
    get_zone_performance,
)
from backend.app.services.d2c_customer_engine import (
    get_acquisition_channel_performance,
    get_customer_cohorts,
    get_customer_summary,
)
from backend.app.services.d2c_product_engine import (
    get_category_performance,
    get_product_performance,
    get_product_summary,
)
from fastapi import APIRouter, HTTPException

from backend.app.services.d2c_data_loader import (
    get_d2c_dataset_summary,
    load_d2c_orders,
)

from backend.app.services.d2c_financial_engine import (
    get_d2c_financial_summary,
    get_monthly_d2c_financials,
)

from backend.app.services.d2c_profitability_engine import (
    get_monthly_profitability,
    get_profitability_summary,
)


router = APIRouter(
    prefix="/analytics/d2c",
    tags=["D2C Analytics"],
)


# ============================================================
# HELPERS
# ============================================================


def _raise_http_error(
    error: Exception,
):
    if isinstance(
        error,
        ValueError,
    ):
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    raise HTTPException(
        status_code=500,
        detail=(
            "ProfitLens D2C analytics failed."
        ),
    )


def _records(
    dataframe,
):
    """
    Convert a Pandas DataFrame into
    JSON-safe Python records.
    """

    safe = (
        dataframe
        .where(
            dataframe.notna(),
            None,
        )
    )

    return (
        safe.to_dict(
            orient="records"
        )
    )


# ============================================================
# DATASET SUMMARY
# ============================================================


@router.get(
    "/dataset-summary",
)
def dataset_summary():
    """
    Return metadata about the connected
    ProfitLens India D2C demo dataset.
    """

    try:
        return (
            get_d2c_dataset_summary()
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# REPORTING PERIODS
# ============================================================


@router.get(
    "/reporting-periods",
)
def reporting_periods():
    """
    Return available D2C reporting periods.

    January and December are intentionally
    partial in the synthetic dataset.

    The latest complete month becomes the
    default reporting period.
    """

    try:
        orders = (
            load_d2c_orders()
        )

        monthly = (
            orders.groupby(
                "month"
            )
            .agg(
                orders=(
                    "order_id",
                    "nunique",
                ),
            )
            .reset_index()
            .sort_values(
                "month",
                ascending=False,
            )
            .reset_index(
                drop=True
            )
        )

        if monthly.empty:
            return {
                "months": [],
                "complete_months": [],
                "partial_months": [],
                "default_month": None,
            }

        # Synthetic dataset contract:
        # January and December are intentionally partial.
        partial_months = []

        for month in (
            monthly["month"]
            .astype(str)
            .tolist()
        ):

            month_number = (
                int(
                    month.split(
                        "-"
                    )[1]
                )
            )

            if month_number in {
                1,
                12,
            }:
                partial_months.append(
                    month
                )

        months = (
            monthly["month"]
            .astype(str)
            .tolist()
        )

        complete_months = [
            month
            for month in months
            if month
            not in partial_months
        ]

        default_month = (
            complete_months[0]
            if complete_months
            else (
                months[0]
                if months
                else None
            )
        )

        return {
            "months": months,
            "complete_months": (
                complete_months
            ),
            "partial_months": (
                partial_months
            ),
            "default_month": (
                default_month
            ),
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# MONTHLY FINANCIAL SUMMARY
# ============================================================


@router.get(
    "/financials/{month}",
)
def financials(
    month: str,
):
    """
    Return deterministic financial metrics
    for one D2C reporting month.
    """

    try:
        return (
            get_d2c_financial_summary(
                month
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# MONTHLY PROFITABILITY SUMMARY
# ============================================================


@router.get(
    "/profitability/{month}",
)
def profitability(
    month: str,
):
    """
    Return full ProfitLens profitability
    metrics for one D2C reporting month.
    """

    try:
        return (
            get_profitability_summary(
                month
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# MONTHLY FINANCIAL HISTORY
# ============================================================


@router.get(
    "/monthly-financials",
)
def monthly_financials():
    """
    Return deterministic monthly financial
    history for the D2C dataset.
    """

    try:
        dataframe = (
            get_monthly_d2c_financials()
        )

        return {
            "data": _records(
                dataframe
            )
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# MONTHLY PROFITABILITY HISTORY
# ============================================================


@router.get(
    "/monthly-profitability",
)
def monthly_profitability():
    """
    Return monthly ProfitLens profitability
    including aggregate marketing economics.
    """

    try:
        dataframe = (
            get_monthly_profitability()
        )

        return {
            "data": _records(
                dataframe
            )
        }

    except Exception as error:
        _raise_http_error(
            error
        )

# ============================================================
# PRODUCT ANALYTICS
# ============================================================


@router.get(
    "/products/{month}",
)
def products(
    month: str,
):
    """
    Return D2C product-level commercial
    performance for one reporting month.
    """

    try:
        summary = (
            get_product_summary(
                month
            )
        )

        products_df = (
            get_product_performance(
                month
            )
        )

        return {
            "month": month,
            "summary": summary,
            "products": _records(
                products_df
            ),
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# CATEGORY ANALYTICS
# ============================================================


@router.get(
    "/categories/{month}",
)
def categories(
    month: str,
):
    """
    Return category-level commercial
    performance for one reporting month.
    """

    try:
        category_df = (
            get_category_performance(
                month
            )
        )

        return {
            "month": month,
            "categories": _records(
                category_df
            ),
        }

    except Exception as error:
        _raise_http_error(
            error
        )
        
# ============================================================
# CUSTOMER ANALYTICS
# ============================================================


@router.get(
    "/customers/{month}",
)
def customers(
    month: str,
):
    """
    Return customer KPIs for one D2C reporting month.
    """

    try:
        return (
            get_customer_summary(
                month
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# ACQUISITION CHANNEL ANALYTICS
# ============================================================


@router.get(
    "/acquisition-channels/{month}",
)
def acquisition_channels(
    month: str,
):
    """
    Return customer and placed-order performance
    by acquisition channel.

    Order value metrics represent placed-order
    economics rather than realized revenue.
    """

    try:
        dataframe = (
            get_acquisition_channel_performance(
                month
            )
        )

        return {
            "month": month,
            "metric_basis": (
                "placed_order_value"
            ),
            "data": _records(
                dataframe
            ),
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# CUSTOMER COHORTS
# ============================================================


@router.get(
    "/customer-cohorts",
)
def customer_cohorts():
    """
    Return observed monthly customer retention cohorts.
    """

    try:
        dataframe = (
            get_customer_cohorts()
        )

        return {
            "retention_type": (
                "observed_historical"
            ),
            "predictive": False,
            "data": _records(
                dataframe
            ),
        }

    except Exception as error:
        _raise_http_error(
            error
        )

# ============================================================
# LOGISTICS SUMMARY
# ============================================================


@router.get(
    "/logistics/{month}",
)
def logistics(
    month: str,
):
    """
    Return headline D2C logistics metrics
    for one reporting month.
    """

    try:
        summary = (
            get_logistics_summary(
                month
            )
        )

        return {
            "month": month,
            "summary": summary,
            "definitions": {
                "delivery_rate_percent": (
                    "Share of orders with a recorded "
                    "customer-delivery timestamp."
                ),
                "on_time_delivery_percent": (
                    "Share of measurable delivered orders "
                    "delivered on or before promised date."
                ),
            },
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# COURIER PERFORMANCE
# ============================================================


@router.get(
    "/couriers/{month}",
)
def courier_performance(
    month: str,
):
    """
    Return courier-level operational performance.
    """

    try:
        dataframe = (
            get_courier_performance(
                month
            )
        )

        return {
            "month": month,
            "data": _records(
                dataframe
            ),
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# COD VS PREPAID LOGISTICS
# ============================================================


@router.get(
    "/payment-logistics/{month}",
)
def payment_logistics(
    month: str,
):
    """
    Compare COD and prepaid logistics outcomes.
    """

    try:
        dataframe = (
            get_payment_logistics_performance(
                month
            )
        )

        return {
            "month": month,
            "data": _records(
                dataframe
            ),
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# ZONE PERFORMANCE
# ============================================================


@router.get(
    "/zones/{month}",
)
def zone_performance(
    month: str,
):
    """
    Return logistics risk and TAT by zone.
    """

    try:
        dataframe = (
            get_zone_performance(
                month
            )
        )

        return {
            "month": month,
            "data": _records(
                dataframe
            ),
        }

    except Exception as error:
        _raise_http_error(
            error
        )

# ============================================================
# MARKETING ANALYTICS
# ============================================================


@router.get("/marketing/monthly-trend")
def marketing_monthly_trend():
    """
    Return monthly marketing performance and MoM changes.
    """

    try:
        dataframe = get_monthly_marketing_trend()

        return {
            "data": _records(dataframe),
        }

    except Exception as error:
        _raise_http_error(error)


@router.get("/marketing/{month}")
def marketing_summary(month: str):
    """
    Return headline marketing performance for one month.
    """

    try:
        return get_marketing_summary(month)

    except Exception as error:
        _raise_http_error(error)


@router.get("/marketing/channels/{month}")
def marketing_channels(month: str):
    """
    Return acquisition-channel marketing performance.
    """

    try:
        dataframe = get_channel_performance(month)

        return {
            "month": month,
            "data": _records(dataframe),
        }

    except Exception as error:
        _raise_http_error(error)


@router.get("/marketing/campaigns/{month}")
def marketing_campaigns(month: str):
    """
    Return campaign-level marketing performance.
    """

    try:
        dataframe = get_campaign_performance(month)

        return {
            "month": month,
            "data": _records(dataframe),
        }

    except Exception as error:
        _raise_http_error(error)




@router.get("/marketing/insights/{month}")
def marketing_insights(month: str):
    """
    Return deterministic marketing performance signals.
    """

    try:
        return get_marketing_insights(month)

    except Exception as error:
        _raise_http_error(error)

# ============================================================
# INVENTORY ANALYTICS
# ============================================================


@router.get("/inventory/summary")
def d2c_inventory_summary():
    """
    Current inventory snapshot summary.

    Inventory data is not historical/monthly.
    """

    try:
        return get_inventory_summary()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/inventory/skus")
def d2c_inventory_skus():
    """
    SKU-level inventory health across warehouses.
    """

    try:
        df = get_sku_inventory_performance()

        return {
            "inventory_scope": "current_snapshot",
            "historical_inventory_available": False,
            "data": df.to_dict(
                orient="records"
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/inventory/warehouses")
def d2c_inventory_warehouses():
    """
    Warehouse-level inventory health.
    """

    try:
        df = (
            get_warehouse_inventory_performance()
        )

        return {
            "inventory_scope": "current_snapshot",
            "historical_inventory_available": False,
            "data": df.to_dict(
                orient="records"
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/inventory/categories")
def d2c_inventory_categories():
    """
    Category-level inventory health.
    """

    try:
        df = (
            get_category_inventory_performance()
        )

        return {
            "inventory_scope": "current_snapshot",
            "historical_inventory_available": False,
            "data": df.to_dict(
                orient="records"
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.get("/overview/{month}")
def d2c_overview(month: str):
    """
    Return the canonical executive D2C overview
    for the requested reporting month.
    """

    try:
        return get_d2c_overview(month)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc