from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# ENUMS
# ============================================================


class WorkspaceType(
    str,
    Enum,
):
    brand = "brand"
    agency = "agency"
    portfolio = "portfolio"


class BrandStatus(
    str,
    Enum,
):
    active = "active"
    paused = "paused"
    archived = "archived"


class WorkspaceRole(
    str,
    Enum,
):
    owner = "owner"
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


# ============================================================
# USER MEMBERSHIP
# ============================================================


class WorkspaceMember(BaseModel):
    user_id: str

    role: WorkspaceRole

    email: Optional[str] = None

    display_name: Optional[str] = None

    active: bool = True


# ============================================================
# BRAND
# ============================================================


class Brand(BaseModel):
    brand_id: str

    workspace_id: str

    name: str

    status: BrandStatus = (
        BrandStatus.active
    )

    country: str = "India"

    currency: str = "INR"

    timezone: str = "Asia/Kolkata"

    business_type: Optional[str] = None

    financial_year_start_month: int = 4

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


# ============================================================
# WORKSPACE
# ============================================================


class Workspace(BaseModel):
    workspace_id: str

    name: str

    workspace_type: WorkspaceType = (
        WorkspaceType.brand
    )

    owner_user_id: str

    members: list[
        WorkspaceMember
    ] = Field(
        default_factory=list
    )

    brand_ids: list[str] = Field(
        default_factory=list
    )

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


# ============================================================
# CREATE REQUESTS
# ============================================================


class CreateWorkspaceRequest(BaseModel):
    name: str

    owner_user_id: str

    workspace_type: WorkspaceType = (
        WorkspaceType.brand
    )

    owner_email: Optional[str] = None

    owner_display_name: Optional[str] = None

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


class CreateBrandRequest(BaseModel):
    workspace_id: str

    name: str

    country: str = "India"

    currency: str = "INR"

    timezone: str = "Asia/Kolkata"

    business_type: Optional[str] = None

    financial_year_start_month: int = 4

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )
