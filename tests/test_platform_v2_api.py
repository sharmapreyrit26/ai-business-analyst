from fastapi.testclient import (
    TestClient,
)

from backend.app.main import app

from backend.app.services.saved_view_engine import (
    clear_saved_views,
)

from backend.app.services.workspace_engine import (
    clear_workspaces,
)

from backend.app.services.data_source_engine import (
    clear_data_sources,
)


client = TestClient(
    app
)


def setup_function():
    clear_saved_views()
    clear_workspaces()
    clear_data_sources()


def test_platform_health():
    response = client.get(
        "/analytics/v2/health"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()[
            "version"
        ]
        == "v2"
    )


def test_platform_capabilities():
    response = client.get(
        "/analytics/v2/capabilities"
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body[
            "investigations"
        ]
        is True
    )

    assert (
        body[
            "scenario_v2"
        ]
        is True
    )


def test_metric_dictionary_endpoint():
    response = client.get(
        "/analytics/v2/metrics"
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["count"]
        > 0
    )


def test_metric_lineage_endpoint():
    response = client.get(
        (
            "/analytics/v2/metrics/"
            "rto_rate_percent/lineage"
        )
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()[
            "source_engine"
        ]
        == "d2c_logistics_engine"
    )


def test_metric_drilldown_endpoint():
    response = client.post(
        (
            "/analytics/v2/metrics/"
            "rto_rate_percent/drilldown"
        ),
        json={
            "value":
                12.02,

            "previous_value":
                10,

            "component_values": {
                "rto_orders":
                    1142,
                "orders":
                    9501,
            },
        },
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["metric"][
            "metric_id"
        ]
        == "rto_rate_percent"
    )


def test_scenario_v2_endpoint():
    response = client.post(
        "/analytics/v2/scenario/run",
        json={
            "month":
                "2025-11",

            "changes": {
                "orders_change_percent":
                    10,

                "aov_change_percent":
                    5,

                "rto_reduction_percent":
                    20,

                "marketing_spend_change_percent":
                    0,

                "cac_change_percent":
                    0,

                "discount_rate_change_percent":
                    0,
            },
        },
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body[
            "scenario_type"
        ]
        == "d2c_combined_change"
    )


def test_investigation_endpoint():
    response = client.get(
        (
            "/analytics/v2/"
            "investigations/2025-11"
        )
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()[
            "count"
        ]
        > 0
    )


def test_alert_endpoint():
    response = client.get(
        "/analytics/v2/alerts/2025-11"
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body[
            "total_rules"
        ]
        > 0
    )

    assert (
        body[
            "triggered_count"
        ]
        > 0
    )


def test_workspace_brand_source_flow():
    workspace_response = (
        client.post(
            "/analytics/v2/workspaces",
            json={
                "name":
                    "Demo Commerce",

                "owner_user_id":
                    "user_1",

                "workspace_type":
                    "brand",
            },
        )
    )

    assert (
        workspace_response.status_code
        == 200
    )

    workspace = (
        workspace_response.json()
    )

    brand_response = client.post(
        "/analytics/v2/brands",
        json={
            "workspace_id":
                workspace[
                    "workspace_id"
                ],

            "name":
                "Acme Fashion",

            "country":
                "India",

            "currency":
                "INR",

            "business_type":
                "D2C Fashion",
        },
    )

    assert (
        brand_response.status_code
        == 200
    )

    brand = (
        brand_response.json()
    )

    source_response = client.post(
        "/analytics/v2/data-sources",
        json={
            "workspace_id":
                workspace[
                    "workspace_id"
                ],

            "brand_id":
                brand[
                    "brand_id"
                ],

            "source_type":
                "shopify",
        },
    )

    assert (
        source_response.status_code
        == 200
    )

    assert (
        source_response.json()[
            "name"
        ]
        == "Shopify"
    )


def test_export_endpoint():
    response = client.post(
        "/analytics/v2/exports",
        json={
            "export": {
                "report_id":
                    "marketing",

                "month":
                    "2025-11",

                "format":
                    "csv",

                "delivery":
                    "download",
            },

            "data": [
                {
                    "channel":
                        "Meta",

                    "roas":
                        5.32,
                }
            ],
        },
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["status"]
        == "ready"
    )

    assert (
        "Meta"
        in body["content"]
    )
