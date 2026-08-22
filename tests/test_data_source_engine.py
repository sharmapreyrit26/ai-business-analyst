from backend.app.data_source_contracts import (
    CreateDataSourceRequest,
    DataSourceStatus,
    DataSourceType,
    DatasetType,
    MappingStatus,
    SyncStatus,
)

from backend.app.services.data_source_engine import (
    build_uploaded_dataset,
    clear_data_sources,
    create_data_source,
    detect_dataset_type,
    list_brand_data_sources,
    suggest_column_mapping,
    update_source_status,
)


def setup_function():
    clear_data_sources()


def test_create_shopify_source():
    source = create_data_source(
        CreateDataSourceRequest(
            workspace_id="ws_1",
            brand_id="brand_1",
            source_type=(
                DataSourceType.shopify
            ),
        )
    )

    assert (
        source.name
        == "Shopify"
    )

    assert (
        source.status
        == DataSourceStatus.disconnected
    )


def test_source_id_is_stable():
    request = CreateDataSourceRequest(
        workspace_id="ws_1",
        brand_id="brand_1",
        source_type=(
            DataSourceType.meta_ads
        ),
    )

    first = create_data_source(
        request
    )

    second = create_data_source(
        request
    )

    assert (
        first.data_source_id
        == second.data_source_id
    )


def test_update_source_status():
    source = create_data_source(
        CreateDataSourceRequest(
            workspace_id="ws_1",
            brand_id="brand_1",
            source_type=(
                DataSourceType.shopify
            ),
        )
    )

    updated = update_source_status(
        source.data_source_id,
        status=(
            DataSourceStatus.connected
        ),
        sync_status=(
            SyncStatus.success
        ),
        row_count=100000,
        last_synced_at=(
            "2026-08-21T12:00:00"
        ),
    )

    assert (
        updated.status
        == DataSourceStatus.connected
    )

    assert (
        updated.row_count
        == 100000
    )


def test_list_brand_sources():
    create_data_source(
        CreateDataSourceRequest(
            workspace_id="ws_1",
            brand_id="brand_1",
            source_type=(
                DataSourceType.shopify
            ),
        )
    )

    create_data_source(
        CreateDataSourceRequest(
            workspace_id="ws_1",
            brand_id="brand_1",
            source_type=(
                DataSourceType.meta_ads
            ),
        )
    )

    result = (
        list_brand_data_sources(
            "brand_1"
        )
    )

    assert len(
        result
    ) == 2


def test_detect_orders_dataset():
    dataset_type, confidence = (
        detect_dataset_type(
            "orders.csv",
            [
                "order_id",
                "customer_id",
                "order_date",
            ],
        )
    )

    assert (
        dataset_type
        == DatasetType.orders
    )

    assert (
        confidence
        >= 80
    )


def test_detect_marketing_dataset():
    dataset_type, confidence = (
        detect_dataset_type(
            "marketing.csv",
            [
                "channel",
                "spend",
                "campaign",
            ],
        )
    )

    assert (
        dataset_type
        == DatasetType.marketing
    )


def test_uploaded_dataset():
    result = (
        build_uploaded_dataset(
            workspace_id="ws_1",
            brand_id="brand_1",
            filename="orders.csv",
            columns=[
                "order_id",
                "customer_id",
            ],
            row_count=100000,
        )
    )

    assert (
        result.detected_type
        == DatasetType.orders
    )

    assert (
        result.row_count
        == 100000
    )


def test_column_mapping():
    mapping = (
        suggest_column_mapping(
            dataset_id="dataset_1",
            dataset_type=(
                DatasetType.orders
            ),
            columns=[
                "order_id",
                "customer_id",
                "created_at",
                "status",
                "total_amount",
                "postal_code",
                "delivery_partner",
            ],
        )
    )

    assert (
        mapping.mapped_count
        == 7
    )

    assert (
        mapping.review_count
        == 0
    )

    assert (
        mapping.progress_percent
        == 100
    )


def test_unknown_column_requires_review():
    mapping = (
        suggest_column_mapping(
            dataset_id="dataset_1",
            dataset_type=(
                DatasetType.orders
            ),
            columns=[
                "order_id",
                "mystery_field",
            ],
        )
    )

    mystery = next(
        item
        for item in mapping.mappings
        if item.source_column
        == "mystery_field"
    )

    assert (
        mystery.status
        == MappingStatus.review
    )


def test_file_source_category():
    source = create_data_source(
        CreateDataSourceRequest(
            workspace_id="ws_1",
            brand_id="brand_1",
            source_type=(
                DataSourceType.csv
            ),
        )
    )

    assert (
        source.name
        == "CSV Upload"
    )
