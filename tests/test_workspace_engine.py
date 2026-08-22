import pytest

from backend.app.workspace_contracts import (
    BrandStatus,
    CreateBrandRequest,
    CreateWorkspaceRequest,
    WorkspaceRole,
    WorkspaceType,
)

from backend.app.services.workspace_engine import (
    add_workspace_member,
    clear_workspaces,
    create_brand,
    create_workspace,
    get_brand,
    get_workspace,
    list_workspace_brands,
    list_workspaces_for_user,
    remove_workspace_member,
    update_brand_status,
)


def setup_function():
    clear_workspaces()


def create_demo_workspace():
    return create_workspace(
        CreateWorkspaceRequest(
            name="Demo Commerce",
            owner_user_id="user_1",
            workspace_type=(
                WorkspaceType.brand
            ),
            owner_email=(
                "owner@example.com"
            ),
        )
    )


def test_create_workspace():
    workspace = (
        create_demo_workspace()
    )

    assert (
        workspace.name
        == "Demo Commerce"
    )

    assert (
        workspace.owner_user_id
        == "user_1"
    )

    assert len(
        workspace.members
    ) == 1

    assert (
        workspace.members[0].role
        == WorkspaceRole.owner
    )


def test_workspace_id_is_stable():
    first = (
        create_demo_workspace()
    )

    second = (
        create_demo_workspace()
    )

    assert (
        first.workspace_id
        == second.workspace_id
    )


def test_get_workspace():
    created = (
        create_demo_workspace()
    )

    loaded = get_workspace(
        created.workspace_id
    )

    assert (
        loaded.name
        == "Demo Commerce"
    )


def test_add_workspace_member():
    workspace = (
        create_demo_workspace()
    )

    updated = (
        add_workspace_member(
            workspace.workspace_id,
            user_id="user_2",
            role=(
                WorkspaceRole.analyst
            ),
        )
    )

    assert any(
        member.user_id
        == "user_2"
        for member
        in updated.members
    )


def test_owner_cannot_be_removed():
    workspace = (
        create_demo_workspace()
    )

    with pytest.raises(
        ValueError
    ):
        remove_workspace_member(
            workspace.workspace_id,
            "user_1",
        )


def test_user_workspace_listing():
    workspace = (
        create_demo_workspace()
    )

    add_workspace_member(
        workspace.workspace_id,
        user_id="user_2",
        role=(
            WorkspaceRole.viewer
        ),
    )

    result = (
        list_workspaces_for_user(
            "user_2"
        )
    )

    assert len(
        result
    ) == 1


def test_create_brand():
    workspace = (
        create_demo_workspace()
    )

    brand = create_brand(
        CreateBrandRequest(
            workspace_id=(
                workspace.workspace_id
            ),
            name="Acme Fashion",
            country="India",
            currency="INR",
            business_type=(
                "D2C Fashion"
            ),
        )
    )

    assert (
        brand.name
        == "Acme Fashion"
    )

    assert (
        brand.workspace_id
        == workspace.workspace_id
    )


def test_workspace_can_have_multiple_brands():
    workspace = (
        create_workspace(
            CreateWorkspaceRequest(
                name="Minkee Media",
                owner_user_id=(
                    "agency_owner"
                ),
                workspace_type=(
                    WorkspaceType.agency
                ),
            )
        )
    )

    create_brand(
        CreateBrandRequest(
            workspace_id=(
                workspace.workspace_id
            ),
            name="Brand A",
        )
    )

    create_brand(
        CreateBrandRequest(
            workspace_id=(
                workspace.workspace_id
            ),
            name="Brand B",
        )
    )

    brands = (
        list_workspace_brands(
            workspace.workspace_id
        )
    )

    assert len(
        brands
    ) == 2


def test_brand_id_is_stable():
    workspace = (
        create_demo_workspace()
    )

    request = CreateBrandRequest(
        workspace_id=(
            workspace.workspace_id
        ),
        name="Acme Fashion",
    )

    first = create_brand(
        request
    )

    second = create_brand(
        request
    )

    assert (
        first.brand_id
        == second.brand_id
    )


def test_archive_brand():
    workspace = (
        create_demo_workspace()
    )

    brand = create_brand(
        CreateBrandRequest(
            workspace_id=(
                workspace.workspace_id
            ),
            name="Old Brand",
        )
    )

    archived = (
        update_brand_status(
            brand.brand_id,
            BrandStatus.archived,
        )
    )

    assert (
        archived.status
        == BrandStatus.archived
    )

    visible = (
        list_workspace_brands(
            workspace.workspace_id
        )
    )

    assert len(
        visible
    ) == 0

    all_brands = (
        list_workspace_brands(
            workspace.workspace_id,
            include_archived=True,
        )
    )

    assert len(
        all_brands
    ) == 1


def test_invalid_financial_year_month_rejected():
    workspace = (
        create_demo_workspace()
    )

    with pytest.raises(
        ValueError
    ):
        create_brand(
            CreateBrandRequest(
                workspace_id=(
                    workspace.workspace_id
                ),
                name="Invalid",
                financial_year_start_month=13,
            )
        )


def test_brand_returns_copy():
    workspace = (
        create_demo_workspace()
    )

    brand = create_brand(
        CreateBrandRequest(
            workspace_id=(
                workspace.workspace_id
            ),
            name="Acme",
        )
    )

    loaded = get_brand(
        brand.brand_id
    )

    loaded.name = "Mutated"

    reloaded = get_brand(
        brand.brand_id
    )

    assert (
        reloaded.name
        == "Acme"
    )
