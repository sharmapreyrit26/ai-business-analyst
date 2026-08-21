from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_d2c_overview_endpoint():
    response = client.get(
        "/analytics/d2c/overview/2025-11"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["month"] == "2025-11"

    # Revenue
    assert data["revenue"]["orders"] == 9501
    assert (
        data["revenue"]["realized_revenue"]
        == 11010422.0
    )
    assert (
        data["revenue"]["aov"]
        == 1158.87
    )

    # Profitability
    assert (
        data["profitability"][
            "contribution_profit_after_marketing"
        ]
        == 2282453.47
    )

    assert (
        data["profitability"][
            "contribution_margin_after_marketing_percent"
        ]
        == 20.73
    )

    # Marketing
    assert (
        data["marketing"]["marketing_spend"]
        == 1344648.21
    )

    assert (
        data["marketing"]["roas"]
        == 5.32
    )

    assert (
        data["marketing"]["cac"]
        == 416.43
    )

    assert (
        data["marketing"]["new_customers"]
        == 3229
    )

    # Customers
    assert (
        data["customers"]["active_customers"]
        == 8974
    )

    assert (
        data["customers"]["new_customers"]
        == 3229
    )

    assert (
        data["customers"]["repeat_customers"]
        == 5745
    )

    assert (
        data["customers"][
            "repeat_customer_rate_percent"
        ]
        == 64.02
    )

    # Logistics
    assert (
        data["logistics"]["rto_rate_percent"]
        == 12.02
    )

    assert (
        data["logistics"]["ndr_rate_percent"]
        == 19.05
    )

    assert (
        data["logistics"][
            "p90_delivery_tat_days"
        ]
        == 8.0
    )

    # Products
    assert (
        data["products"]["total_products"]
        == 250
    )

    assert (
        data["products"]["loss_making_products"]
        == 5
    )

    # Inventory
    assert (
        data["inventory"]["total_skus"]
        == 250
    )

    assert (
        data["inventory"]["warehouses"]
        == 3
    )

    assert (
        data["inventory"][
            "total_closing_stock_units"
        ]
        == 510570
    )

    assert (
        data["inventory"][
            "inventory_cost_value"
        ]
        == 177335852.93
    )


def test_d2c_overview_cross_engine_customer_reconciliation():
    response = client.get(
        "/analytics/d2c/overview/2025-11"
    )

    data = response.json()

    assert (
        data["marketing"]["new_customers"]
        == data["customers"]["new_customers"]
    )


def test_d2c_overview_marketing_spend_reconciles():
    response = client.get(
        "/analytics/d2c/overview/2025-11"
    )

    data = response.json()

    assert (
        data["marketing"]["marketing_spend"]
        == data["profitability"]["marketing_spend"]
    )


def test_d2c_overview_product_inventory_sku_reconciliation():
    response = client.get(
        "/analytics/d2c/overview/2025-11"
    )

    data = response.json()

    assert (
        data["products"]["total_products"]
        == data["inventory"]["total_skus"]
    )


def test_d2c_overview_limitations():
    response = client.get(
        "/analytics/d2c/overview/2025-11"
    )

    data = response.json()

    limitations = data["limitations"]

    assert (
        limitations[
            "marketing_attribution_level"
        ]
        == "aggregate_monthly"
    )

    assert (
        limitations[
            "order_level_marketing_allocation_available"
        ]
        is False
    )

    assert (
        limitations[
            "sku_contribution_profit_available"
        ]
        is False
    )

    assert (
        limitations[
            "historical_inventory_available"
        ]
        is False
    )


def test_d2c_overview_invalid_month_returns_404():
    response = client.get(
        "/analytics/d2c/overview/2099-01"
    )

    assert response.status_code == 404