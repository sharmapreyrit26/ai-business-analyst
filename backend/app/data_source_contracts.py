from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# ENUMS
# ============================================================


class DataSourceType(
    str,
    Enum,
):
    shopify = "shopify"
    woocommerce = "woocommerce"
    meta_ads = "meta_ads"
    google_ads = "google_ads"
    shiprocket = "shiprocket"
    delhivery = "delhivery"
    razorpay = "razorpay"
    unicommerce = "unicommerce"
    klaviyo = "klaviyo"
    csv = "csv"
    xlsx = "xlsx"


class DataSourceCategory(
    str,
    Enum,
):
    commerce = "commerce"
    marketing = "marketing"
    logistics = "logistics"
    payments = "payments"
    customer = "customer"
    inventory = "inventory"
    file = "file"


class DataSourceStatus(
    str,
    Enum,
):
    disconnected = "disconnected"
    connecting = "connecting"
    connected = "connected"
    syncing = "syncing"
    error = "error"
    paused = "paused"


class SyncStatus(
    str,
    Enum,
):
    never = "never"
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class DatasetType(
    str,
    Enum,
):
    orders = "orders"
    order_items = "order_items"
    customers = "customers"
    products = "products"
    payments = "payments"
    marketing = "marketing"
    logistics = "logistics"
    couriers = "couriers"
    inventory = "inventory"
    unknown = "unknown"


class MappingStatus(
    str,
    Enum,
):
    mapped = "mapped"
    review = "review"
    unmapped = "unmapped"


# ============================================================
# DATA SOURCE
# ============================================================


class DataSource(BaseModel):
    data_source_id: str

    workspace_id: str

    brand_id: str

    source_type: DataSourceType

    category: DataSourceCategory

    name: str

    status: DataSourceStatus = (
        DataSourceStatus.disconnected
    )

    sync_status: SyncStatus = (
        SyncStatus.never
    )

    last_synced_at: Optional[str] = None

    row_count: Optional[int] = None

    error_message: Optional[str] = None

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


# ============================================================
# CREATE SOURCE
# ============================================================


class CreateDataSourceRequest(
    BaseModel
):
    workspace_id: str

    brand_id: str

    source_type: DataSourceType

    name: Optional[str] = None

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


# ============================================================
# UPLOADED FILE
# ============================================================


class UploadedDataset(BaseModel):
    dataset_id: str

    workspace_id: str

    brand_id: str

    filename: str

    detected_type: DatasetType = (
        DatasetType.unknown
    )

    row_count: int = 0

    confidence_percent: float = 0.0

    columns: list[str] = Field(
        default_factory=list
    )

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


# ============================================================
# COLUMN MAPPING
# ============================================================


class ColumnMapping(BaseModel):
    source_column: str

    target_field: Optional[str] = None

    status: MappingStatus = (
        MappingStatus.unmapped
    )

    confidence_percent: float = 0.0

    required: bool = False


class DatasetMapping(BaseModel):
    dataset_id: str

    dataset_type: DatasetType

    mappings: list[
        ColumnMapping
    ] = Field(
        default_factory=list
    )

    mapped_count: int = 0

    review_count: int = 0

    unmapped_count: int = 0

    progress_percent: float = 0.0
