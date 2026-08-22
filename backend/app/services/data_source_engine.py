from __future__ import annotations

from copy import deepcopy
from hashlib import sha1

from backend.app.data_source_contracts import (
    ColumnMapping,
    CreateDataSourceRequest,
    DataSource,
    DataSourceCategory,
    DataSourceStatus,
    DataSourceType,
    DatasetMapping,
    DatasetType,
    MappingStatus,
    SyncStatus,
    UploadedDataset,
)


# ============================================================
# SOURCE REGISTRY
# ============================================================


SOURCE_CATEGORIES = {
    DataSourceType.shopify:
        DataSourceCategory.commerce,

    DataSourceType.woocommerce:
        DataSourceCategory.commerce,

    DataSourceType.meta_ads:
        DataSourceCategory.marketing,

    DataSourceType.google_ads:
        DataSourceCategory.marketing,

    DataSourceType.shiprocket:
        DataSourceCategory.logistics,

    DataSourceType.delhivery:
        DataSourceCategory.logistics,

    DataSourceType.razorpay:
        DataSourceCategory.payments,

    DataSourceType.unicommerce:
        DataSourceCategory.inventory,

    DataSourceType.klaviyo:
        DataSourceCategory.customer,

    DataSourceType.csv:
        DataSourceCategory.file,

    DataSourceType.xlsx:
        DataSourceCategory.file,
}


SOURCE_LABELS = {
    DataSourceType.shopify:
        "Shopify",

    DataSourceType.woocommerce:
        "WooCommerce",

    DataSourceType.meta_ads:
        "Meta Ads",

    DataSourceType.google_ads:
        "Google Ads",

    DataSourceType.shiprocket:
        "Shiprocket",

    DataSourceType.delhivery:
        "Delhivery",

    DataSourceType.razorpay:
        "Razorpay",

    DataSourceType.unicommerce:
        "Unicommerce",

    DataSourceType.klaviyo:
        "Klaviyo",

    DataSourceType.csv:
        "CSV Upload",

    DataSourceType.xlsx:
        "Excel Upload",
}


# ============================================================
# IN-MEMORY STORE
# ============================================================


_DATA_SOURCES: dict[
    str,
    DataSource,
] = {}


# ============================================================
# IDS
# ============================================================


def _source_id(
    request: CreateDataSourceRequest,
) -> str:
    raw = (
        f"{request.workspace_id}|"
        f"{request.brand_id}|"
        f"{request.source_type.value}|"
        f"{request.name or ''}"
    )

    digest = (
        sha1(
            raw.encode(
                "utf-8"
            )
        )
        .hexdigest()[:12]
        .upper()
    )

    return (
        f"SRC_{digest}"
    )


def _dataset_id(
    workspace_id: str,
    brand_id: str,
    filename: str,
) -> str:
    raw = (
        f"{workspace_id}|"
        f"{brand_id}|"
        f"{filename}"
    )

    digest = (
        sha1(
            raw.encode(
                "utf-8"
            )
        )
        .hexdigest()[:12]
        .upper()
    )

    return (
        f"DATASET_{digest}"
    )


# ============================================================
# SOURCE MANAGEMENT
# ============================================================


def create_data_source(
    request: CreateDataSourceRequest,
) -> DataSource:
    source_id = (
        _source_id(
            request
        )
    )

    name = (
        request.name.strip()
        if request.name
        else SOURCE_LABELS[
            request.source_type
        ]
    )

    if not name:
        raise ValueError(
            "Data source name cannot be empty."
        )

    source = DataSource(
        data_source_id=(
            source_id
        ),
        workspace_id=(
            request.workspace_id
        ),
        brand_id=(
            request.brand_id
        ),
        source_type=(
            request.source_type
        ),
        category=(
            SOURCE_CATEGORIES[
                request.source_type
            ]
        ),
        name=name,
        metadata=(
            request.metadata
        ),
    )

    _DATA_SOURCES[
        source_id
    ] = source

    return DataSource(
        **deepcopy(
            source.model_dump()
        )
    )


def update_source_status(
    data_source_id: str,
    *,
    status: DataSourceStatus,
    sync_status: SyncStatus | None = None,
    last_synced_at: str | None = None,
    row_count: int | None = None,
    error_message: str | None = None,
) -> DataSource:
    source = (
        _DATA_SOURCES.get(
            data_source_id
        )
    )

    if source is None:
        raise ValueError(
            "Data source not found: "
            f"{data_source_id}"
        )

    source.status = status

    if sync_status is not None:
        source.sync_status = (
            sync_status
        )

    if last_synced_at is not None:
        source.last_synced_at = (
            last_synced_at
        )

    if row_count is not None:
        source.row_count = (
            row_count
        )

    source.error_message = (
        error_message
    )

    return DataSource(
        **deepcopy(
            source.model_dump()
        )
    )


def list_brand_data_sources(
    brand_id: str,
) -> list[
    DataSource
]:
    result = [
        DataSource(
            **deepcopy(
                source.model_dump()
            )
        )
        for source
        in _DATA_SOURCES.values()
        if source.brand_id
        == brand_id
    ]

    result.sort(
        key=lambda item:
            item.name.lower()
    )

    return result


# ============================================================
# DATASET DETECTION
# ============================================================


def detect_dataset_type(
    filename: str,
    columns: list[str],
) -> tuple[
    DatasetType,
    float,
]:
    normalized = {
        column
        .strip()
        .lower()
        for column
        in columns
    }

    filename_lower = (
        filename.lower()
    )

    rules = [
        (
            DatasetType.order_items,
            {
                "order_id",
                "product_id",
            },
            [
                "order_item",
                "items",
            ],
        ),

        (
            DatasetType.orders,
            {
                "order_id",
                "customer_id",
            },
            [
                "orders",
            ],
        ),

        (
            DatasetType.customers,
            {
                "customer_id",
            },
            [
                "customer",
            ],
        ),

        (
            DatasetType.products,
            {
                "product_id",
            },
            [
                "product",
            ],
        ),

        (
            DatasetType.payments,
            {
                "order_id",
                "payment_method",
            },
            [
                "payment",
            ],
        ),

        (
            DatasetType.marketing,
            {
                "channel",
                "spend",
            },
            [
                "marketing",
                "campaign",
            ],
        ),

        (
            DatasetType.inventory,
            {
                "sku",
                "stock",
            },
            [
                "inventory",
                "stock",
            ],
        ),

        (
            DatasetType.couriers,
            {
                "courier_id",
            },
            [
                "courier",
            ],
        ),
    ]

    best_type = (
        DatasetType.unknown
    )

    best_score = 0.0

    for (
        dataset_type,
        required_columns,
        filename_hints,
    ) in rules:

        column_score = (
            len(
                required_columns
                & normalized
            )
            / len(
                required_columns
            )
        )

        filename_score = (
            1.0
            if any(
                hint
                in filename_lower
                for hint
                in filename_hints
            )
            else 0.0
        )

        score = (
            column_score
            * 0.8
            + filename_score
            * 0.2
        )

        if score > best_score:
            best_score = score
            best_type = (
                dataset_type
            )

    return (
        best_type,
        round(
            best_score * 100,
            2,
        ),
    )


def build_uploaded_dataset(
    *,
    workspace_id: str,
    brand_id: str,
    filename: str,
    columns: list[str],
    row_count: int,
) -> UploadedDataset:
    dataset_type, confidence = (
        detect_dataset_type(
            filename,
            columns,
        )
    )

    return UploadedDataset(
        dataset_id=(
            _dataset_id(
                workspace_id,
                brand_id,
                filename,
            )
        ),
        workspace_id=(
            workspace_id
        ),
        brand_id=(
            brand_id
        ),
        filename=filename,
        detected_type=(
            dataset_type
        ),
        row_count=(
            row_count
        ),
        confidence_percent=(
            confidence
        ),
        columns=columns,
    )


# ============================================================
# COLUMN MAPPING
# ============================================================


FIELD_ALIASES = {
    "order_id": [
        "order_id",
        "orderid",
        "order_number",
    ],

    "customer_id": [
        "customer_id",
        "customerid",
    ],

    "order_date": [
        "order_date",
        "created_at",
        "date",
    ],

    "order_status": [
        "order_status",
        "status",
    ],

    "payment_method": [
        "payment_method",
        "payment_type",
    ],

    "order_value": [
        "order_value",
        "total_amount",
        "amount",
    ],

    "courier_id": [
        "courier_id",
        "delivery_partner",
        "courier",
    ],

    "pincode": [
        "pincode",
        "postal_code",
        "zip",
    ],

    "sku": [
        "sku",
        "product_sku",
    ],

    "product_id": [
        "product_id",
        "productid",
    ],
}


def suggest_column_mapping(
    *,
    dataset_id: str,
    dataset_type: DatasetType,
    columns: list[str],
) -> DatasetMapping:
    mappings = []

    normalized_aliases = {
        alias.lower():
            target
        for target, aliases
        in FIELD_ALIASES.items()
        for alias in aliases
    }

    for column in columns:
        normalized = (
            column
            .strip()
            .lower()
        )

        target = (
            normalized_aliases.get(
                normalized
            )
        )

        if target:
            status = (
                MappingStatus.mapped
            )

            confidence = 100.0

        else:
            status = (
                MappingStatus.review
            )

            confidence = 0.0

        mappings.append(
            ColumnMapping(
                source_column=column,
                target_field=target,
                status=status,
                confidence_percent=(
                    confidence
                ),
            )
        )

    mapped_count = sum(
        item.status
        == MappingStatus.mapped
        for item in mappings
    )

    review_count = sum(
        item.status
        == MappingStatus.review
        for item in mappings
    )

    unmapped_count = sum(
        item.status
        == MappingStatus.unmapped
        for item in mappings
    )

    total = len(
        mappings
    )

    progress = (
        mapped_count
        / total
        * 100
        if total
        else 0
    )

    return DatasetMapping(
        dataset_id=(
            dataset_id
        ),
        dataset_type=(
            dataset_type
        ),
        mappings=mappings,
        mapped_count=(
            mapped_count
        ),
        review_count=(
            review_count
        ),
        unmapped_count=(
            unmapped_count
        ),
        progress_percent=round(
            progress,
            2,
        ),
    )


# ============================================================
# CLEAR
# ============================================================


def clear_data_sources():
    _DATA_SOURCES.clear()
