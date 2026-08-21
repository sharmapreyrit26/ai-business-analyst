from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_product_endpoint_valid_month():
    response = client.get(
        "/analytics/products/2018-06"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["month"] == "2018-06"

    assert (
        body["summary"]["status"]
        == "complete"
    )

    assert len(
        body["top_products"]
    ) > 0


def test_product_endpoint_invalid_month_returns_404():
    response = client.get(
        "/analytics/products/2099-01"
    )

    assert response.status_code == 404

    body = response.json()

    assert (
        body["detail"]
        == "Product data not found for month: 2099-01"
    )