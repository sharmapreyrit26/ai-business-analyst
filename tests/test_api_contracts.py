from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_d2c_product_endpoint_valid_month():
    response = client.get(
        "/analytics/d2c/products/2025-11"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["month"] == "2025-11"

    assert (
        body["summary"]["month"]
        == "2025-11"
    )

    assert (
        body["summary"]["total_products"]
        > 0
    )

    assert len(
        body["products"]
    ) > 0


def test_d2c_product_endpoint_invalid_month_returns_404():
    response = client.get(
        "/analytics/d2c/products/2099-01"
    )

    assert response.status_code == 404

    body = response.json()

    assert "detail" in body

    assert (
        "2099-01"
        in body["detail"]
    )