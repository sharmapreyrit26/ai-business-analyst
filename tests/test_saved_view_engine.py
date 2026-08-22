import pytest

from backend.app.analytics_context import (
    AnalyticsContext,
    AnalyticsFilters,
    ComparisonPeriod,
    DateRange,
)

from backend.app.saved_view_contracts import (
    CreateSavedViewRequest,
    SavedViewScope,
)

from backend.app.services.saved_view_engine import (
    clear_saved_views,
    create_saved_view,
    delete_saved_view,
    get_saved_view,
    list_saved_views,
    update_saved_view,
)


def build_context():
    return AnalyticsContext(
        workspace_id=(
            "workspace_demo"
        ),
        brand_id=(
            "brand_demo"
        ),
        period=DateRange(
            start_date=(
                "2025-11-01"
            ),
            end_date=(
                "2025-11-30"
            ),
        ),
        comparison=(
            ComparisonPeriod(
                mode=(
                    "previous_month"
                )
            )
        ),
        filters=(
            AnalyticsFilters(
                zones=[
                    "North"
                ],
                payment_methods=[
                    "COD"
                ],
            )
        ),
    )


def setup_function():
    clear_saved_views()


def test_create_saved_view():
    view = create_saved_view(
        CreateSavedViewRequest(
            name=(
                "North COD Risk"
            ),
            page=(
                "/logistics"
            ),
            context=(
                build_context()
            ),
            created_by=(
                "user_1"
            ),
        )
    )

    assert (
        view.name
        == "North COD Risk"
    )

    assert (
        view.page
        == "/logistics"
    )

    assert (
        view.context.filters.zones
        == [
            "North"
        ]
    )


def test_saved_view_id_is_stable():
    request = (
        CreateSavedViewRequest(
            name=(
                "North COD Risk"
            ),
            page=(
                "/logistics"
            ),
            context=(
                build_context()
            ),
            created_by=(
                "user_1"
            ),
        )
    )

    first = create_saved_view(
        request
    )

    second = create_saved_view(
        request
    )

    assert (
        first.saved_view_id
        == second.saved_view_id
    )


def test_get_saved_view():
    created = (
        create_saved_view(
            CreateSavedViewRequest(
                name="Meta Efficiency",
                page="/marketing",
                context=(
                    build_context()
                ),
            )
        )
    )

    loaded = get_saved_view(
        created.saved_view_id
    )

    assert (
        loaded.saved_view_id
        == created.saved_view_id
    )


def test_list_saved_views_filters_by_page():
    create_saved_view(
        CreateSavedViewRequest(
            name="Logistics View",
            page="/logistics",
            context=(
                build_context()
            ),
        )
    )

    create_saved_view(
        CreateSavedViewRequest(
            name="Marketing View",
            page="/marketing",
            context=(
                build_context()
            ),
        )
    )

    result = (
        list_saved_views(
            page="/marketing"
        )
    )

    assert len(
        result
    ) == 1

    assert (
        result[0].name
        == "Marketing View"
    )


def test_default_view_is_unique_per_page_and_user():
    first = create_saved_view(
        CreateSavedViewRequest(
            name="First",
            page="/logistics",
            context=(
                build_context()
            ),
            is_default=True,
            created_by=(
                "user_1"
            ),
        )
    )

    second = create_saved_view(
        CreateSavedViewRequest(
            name="Second",
            page="/logistics",
            context=(
                build_context()
            ),
            is_default=True,
            created_by=(
                "user_1"
            ),
        )
    )

    first_loaded = (
        get_saved_view(
            first.saved_view_id
        )
    )

    second_loaded = (
        get_saved_view(
            second.saved_view_id
        )
    )

    assert (
        first_loaded.is_default
        is False
    )

    assert (
        second_loaded.is_default
        is True
    )


def test_update_saved_view():
    created = (
        create_saved_view(
            CreateSavedViewRequest(
                name="Old Name",
                page="/inventory",
                context=(
                    build_context()
                ),
            )
        )
    )

    updated = (
        update_saved_view(
            created.saved_view_id,
            name=(
                "Inventory Watch"
            ),
            metadata={
                "sort":
                    "risk_desc"
            },
        )
    )

    assert (
        updated.name
        == "Inventory Watch"
    )

    assert (
        updated.metadata[
            "sort"
        ]
        == "risk_desc"
    )


def test_delete_saved_view():
    created = (
        create_saved_view(
            CreateSavedViewRequest(
                name="Delete Me",
                page="/marketing",
                context=(
                    build_context()
                ),
            )
        )
    )

    assert (
        delete_saved_view(
            created.saved_view_id
        )
        is True
    )

    with pytest.raises(
        ValueError
    ):
        get_saved_view(
            created.saved_view_id
        )


def test_workspace_scope():
    created = (
        create_saved_view(
            CreateSavedViewRequest(
                name=(
                    "Team Logistics"
                ),
                page="/logistics",
                context=(
                    build_context()
                ),
                scope=(
                    SavedViewScope.workspace
                ),
            )
        )
    )

    assert (
        created.scope
        == SavedViewScope.workspace
    )


def test_empty_name_rejected():
    with pytest.raises(
        ValueError
    ):
        create_saved_view(
            CreateSavedViewRequest(
                name="   ",
                page="/marketing",
                context=(
                    build_context()
                ),
            )
        )


def test_returned_saved_view_is_copy():
    created = (
        create_saved_view(
            CreateSavedViewRequest(
                name="Original",
                page="/marketing",
                context=(
                    build_context()
                ),
            )
        )
    )

    loaded = get_saved_view(
        created.saved_view_id
    )

    loaded.name = (
        "Mutated Outside"
    )

    reloaded = get_saved_view(
        created.saved_view_id
    )

    assert (
        reloaded.name
        == "Original"
    )
