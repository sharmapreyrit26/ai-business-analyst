from __future__ import annotations

from copy import deepcopy
from hashlib import sha1

from backend.app.workspace_contracts import (
    Brand,
    BrandStatus,
    CreateBrandRequest,
    CreateWorkspaceRequest,
    Workspace,
    WorkspaceMember,
    WorkspaceRole,
)


# ============================================================
# IN-MEMORY STORE
# ============================================================


_WORKSPACES: dict[
    str,
    Workspace,
] = {}

_BRANDS: dict[
    str,
    Brand,
] = {}


# ============================================================
# HELPERS
# ============================================================


def _normalize_name(
    value: str,
    *,
    field_name: str,
) -> str:
    normalized = (
        value
        .strip()
    )

    if not normalized:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return normalized


def _workspace_id(
    request: CreateWorkspaceRequest,
) -> str:
    raw = (
        f"{request.owner_user_id}|"
        f"{request.name.strip()}|"
        f"{request.workspace_type.value}"
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
        f"WS_{digest}"
    )


def _brand_id(
    request: CreateBrandRequest,
) -> str:
    raw = (
        f"{request.workspace_id}|"
        f"{request.name.strip()}"
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
        f"BRAND_{digest}"
    )


def _clone_workspace(
    workspace: Workspace,
) -> Workspace:
    return Workspace(
        **deepcopy(
            workspace.model_dump()
        )
    )


def _clone_brand(
    brand: Brand,
) -> Brand:
    return Brand(
        **deepcopy(
            brand.model_dump()
        )
    )


# ============================================================
# WORKSPACE
# ============================================================


def create_workspace(
    request: CreateWorkspaceRequest,
) -> Workspace:
    name = _normalize_name(
        request.name,
        field_name="Workspace name",
    )

    if not request.owner_user_id.strip():
        raise ValueError(
            "owner_user_id cannot be empty."
        )

    workspace_id = (
        _workspace_id(
            request
        )
    )

    owner = WorkspaceMember(
        user_id=(
            request.owner_user_id
        ),
        role=(
            WorkspaceRole.owner
        ),
        email=(
            request.owner_email
        ),
        display_name=(
            request.owner_display_name
        ),
    )

    workspace = Workspace(
        workspace_id=(
            workspace_id
        ),
        name=name,
        workspace_type=(
            request.workspace_type
        ),
        owner_user_id=(
            request.owner_user_id
        ),
        members=[
            owner
        ],
        metadata=(
            request.metadata
        ),
    )

    _WORKSPACES[
        workspace_id
    ] = workspace

    return _clone_workspace(
        workspace
    )


def get_workspace(
    workspace_id: str,
) -> Workspace:
    workspace = (
        _WORKSPACES.get(
            workspace_id
        )
    )

    if workspace is None:
        raise ValueError(
            "Workspace not found: "
            f"{workspace_id}"
        )

    return _clone_workspace(
        workspace
    )


def list_workspaces_for_user(
    user_id: str,
) -> list[
    Workspace
]:
    result = []

    for workspace in (
        _WORKSPACES.values()
    ):
        if any(
            member.user_id
            == user_id
            and member.active
            for member
            in workspace.members
        ):
            result.append(
                _clone_workspace(
                    workspace
                )
            )

    result.sort(
        key=lambda item:
            item.name.lower()
    )

    return result


# ============================================================
# MEMBERS
# ============================================================


def add_workspace_member(
    workspace_id: str,
    *,
    user_id: str,
    role: WorkspaceRole,
    email: str | None = None,
    display_name: str | None = None,
) -> Workspace:
    workspace = (
        _WORKSPACES.get(
            workspace_id
        )
    )

    if workspace is None:
        raise ValueError(
            "Workspace not found: "
            f"{workspace_id}"
        )

    for member in workspace.members:
        if member.user_id == user_id:
            member.role = role
            member.email = email
            member.display_name = (
                display_name
            )
            member.active = True

            return _clone_workspace(
                workspace
            )

    workspace.members.append(
        WorkspaceMember(
            user_id=user_id,
            role=role,
            email=email,
            display_name=(
                display_name
            ),
        )
    )

    return _clone_workspace(
        workspace
    )


def remove_workspace_member(
    workspace_id: str,
    user_id: str,
) -> Workspace:
    workspace = (
        _WORKSPACES.get(
            workspace_id
        )
    )

    if workspace is None:
        raise ValueError(
            "Workspace not found: "
            f"{workspace_id}"
        )

    if (
        user_id
        == workspace.owner_user_id
    ):
        raise ValueError(
            "Workspace owner cannot be removed."
        )

    for member in workspace.members:
        if member.user_id == user_id:
            member.active = False

            return _clone_workspace(
                workspace
            )

    raise ValueError(
        f"Workspace member not found: {user_id}"
    )


# ============================================================
# BRAND
# ============================================================


def create_brand(
    request: CreateBrandRequest,
) -> Brand:
    workspace = (
        _WORKSPACES.get(
            request.workspace_id
        )
    )

    if workspace is None:
        raise ValueError(
            "Workspace not found: "
            f"{request.workspace_id}"
        )

    name = _normalize_name(
        request.name,
        field_name="Brand name",
    )

    if not (
        1
        <= request.financial_year_start_month
        <= 12
    ):
        raise ValueError(
            "financial_year_start_month must "
            "be between 1 and 12."
        )

    brand_id = (
        _brand_id(
            request
        )
    )

    brand = Brand(
        brand_id=brand_id,
        workspace_id=(
            request.workspace_id
        ),
        name=name,
        country=(
            request.country
        ),
        currency=(
            request.currency
        ),
        timezone=(
            request.timezone
        ),
        business_type=(
            request.business_type
        ),
        financial_year_start_month=(
            request
            .financial_year_start_month
        ),
        metadata=(
            request.metadata
        ),
    )

    _BRANDS[
        brand_id
    ] = brand

    if (
        brand_id
        not in workspace.brand_ids
    ):
        workspace.brand_ids.append(
            brand_id
        )

    return _clone_brand(
        brand
    )


def get_brand(
    brand_id: str,
) -> Brand:
    brand = (
        _BRANDS.get(
            brand_id
        )
    )

    if brand is None:
        raise ValueError(
            "Brand not found: "
            f"{brand_id}"
        )

    return _clone_brand(
        brand
    )


def list_workspace_brands(
    workspace_id: str,
    *,
    include_archived: bool = False,
) -> list[
    Brand
]:
    workspace = (
        _WORKSPACES.get(
            workspace_id
        )
    )

    if workspace is None:
        raise ValueError(
            "Workspace not found: "
            f"{workspace_id}"
        )

    result = []

    for brand_id in (
        workspace.brand_ids
    ):
        brand = (
            _BRANDS.get(
                brand_id
            )
        )

        if brand is None:
            continue

        if (
            not include_archived
            and brand.status
            == BrandStatus.archived
        ):
            continue

        result.append(
            _clone_brand(
                brand
            )
        )

    result.sort(
        key=lambda item:
            item.name.lower()
    )

    return result


def update_brand_status(
    brand_id: str,
    status: BrandStatus,
) -> Brand:
    brand = (
        _BRANDS.get(
            brand_id
        )
    )

    if brand is None:
        raise ValueError(
            "Brand not found: "
            f"{brand_id}"
        )

    brand.status = status

    return _clone_brand(
        brand
    )


# ============================================================
# CLEAR
# ============================================================


def clear_workspaces():
    _WORKSPACES.clear()
    _BRANDS.clear()
