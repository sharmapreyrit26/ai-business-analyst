from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_inventory_summary_endpoint():
    response = client.get(
        "/analytics/d2c/inventory/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["inventory_scope"] == "current_snapshot"
    assert data["historical_inventory_available"] is False
    assert data["sku_warehouse_rows"] == 750
    assert data["total_skus"] == 250
    assert data["warehouses"] == 3
    assert data["total_closing_stock_units"] == 510570

    assert (
        data["inventory_cost_value"]
        == 177335852.93
    )

    assert (
        data["inventory_retail_value"]
        == 409909320.0
    )

    assert data["below_reorder_rows"] == 26
    assert data["out_of_stock_rows"] == 0
    assert data["overstock_rows"] == 342
    assert data["slow_moving_rows"] == 434

    assert (
        data["potential_revenue_at_risk"]
        == 1040030.0
    )

    assert (
        data["estimated_trapped_inventory_cost"]
        == 30106548.29
    )


def test_inventory_skus_endpoint():
    response = client.get(
        "/analytics/d2c/inventory/skus"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["inventory_scope"] == "current_snapshot"
    assert payload["historical_inventory_available"] is False

    rows = payload["data"]

    assert len(rows) == 250

    reorder_candidates = [
        row
        for row in rows
        if row["is_reorder_candidate"] is True
    ]

    assert len(reorder_candidates) == 25


def test_inventory_warehouse_endpoint():
    response = client.get(
        "/analytics/d2c/inventory/warehouses"
    )

    assert response.status_code == 200

    rows = response.json()["data"]

    assert len(rows) == 3

    warehouses = {
        row["warehouse"]
        for row in rows
    }

    assert warehouses == {
        "Delhi NCR",
        "Mumbai",
        "Bengaluru",
    }


def test_inventory_category_endpoint():
    response = client.get(
        "/analytics/d2c/inventory/categories"
    )

    assert response.status_code == 200

    rows = response.json()["data"]

    assert len(rows) == 8

    categories = {
        row["category"]
        for row in rows
    }

    assert categories == {
        "Ethnic Wear",
        "Dresses",
        "Footwear",
        "Jeans",
        "T-Shirts",
        "Skincare",
        "Shirts",
        "Accessories",
    }


def test_warehouse_stock_reconciles_to_summary():
    summary = client.get(
        "/analytics/d2c/inventory/summary"
    ).json()

    rows = client.get(
        "/analytics/d2c/inventory/warehouses"
    ).json()["data"]

    total_stock = sum(
        row["closing_stock"]
        for row in rows
    )

    assert (
        total_stock
        == summary[
            "total_closing_stock_units"
        ]
    )


def test_warehouse_inventory_cost_reconciles():
    summary = client.get(
        "/analytics/d2c/inventory/summary"
    ).json()

    rows = client.get(
        "/analytics/d2c/inventory/warehouses"
    ).json()["data"]

    total_cost = round(
        sum(
            row["inventory_cost_value"]
            for row in rows
        ),
        2,
    )

    assert (
        total_cost
        == summary[
            "inventory_cost_value"
        ]
    )


def test_category_inventory_cost_reconciles():
    summary = client.get(
        "/analytics/d2c/inventory/summary"
    ).json()

    rows = client.get(
        "/analytics/d2c/inventory/categories"
    ).json()["data"]

    total_cost = round(
        sum(
            row["inventory_cost_value"]
            for row in rows
        ),
        2,
    )

    assert (
        total_cost
        == summary[
            "inventory_cost_value"
        ]
    )


def test_sku_inventory_cost_reconciles():
    summary = client.get(
        "/analytics/d2c/inventory/summary"
    ).json()

    rows = client.get(
        "/analytics/d2c/inventory/skus"
    ).json()["data"]

    total_cost = round(
        sum(
            row["inventory_cost_value"]
            for row in rows
        ),
        2,
    )

    assert (
        total_cost
        == summary[
            "inventory_cost_value"
        ]
    )