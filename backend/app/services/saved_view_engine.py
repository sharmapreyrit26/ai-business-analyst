from __future__ import annotations

from copy import deepcopy
from hashlib import sha1

from backend.app.saved_view_contracts import (
    CreateSavedViewRequest,
    SavedView,
)


# ============================================================
# IN-MEMORY STORE
# ============================================================


_SAVED_VIEWS: dict[
    str,
    SavedView,
] = {}


# ============================================================
# HELPERS
# ============================================================


def _normalize_name(
    value: str,
) -> str:
    result = (
        value
        .strip()
    )

    if not result:
        raise ValueError(
            "Saved view name "
            "cannot be empty."
        )

    return result


def _saved_view_id(
    request: CreateSavedViewRequest,
) -> str:
    raw = (
        f"{request.name.strip()}|"
        f"{request.page}|"
        f"{request.created_by}|"
        f"{request.context.model_dump_json()}"
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
        f"VIEW_{digest}"
    )


def _clone(
    view: SavedView,
) -> SavedView:
    return SavedView(
        **deepcopy(
            view.model_dump()
        )
    )


# ============================================================
# CREATE
# ============================================================


def create_saved_view(
    request: CreateSavedViewRequest,
) -> SavedView:
    name = _normalize_name(
        request.name
    )

    if not request.page.strip():
        raise ValueError(
            "Saved view page "
            "cannot be empty."
        )

    saved_view_id = (
        _saved_view_id(
            request
        )
    )

    if request.is_default:
        for view in (
            _SAVED_VIEWS.values()
        ):
            if (
                view.page
                == request.page
                and view.created_by
                == request.created_by
            ):
                view.is_default = False

    view = SavedView(
        saved_view_id=(
            saved_view_id
        ),
        name=name,
        page=(
            request.page.strip()
        ),
        context=(
            request.context
        ),
        scope=(
            request.scope
        ),
        description=(
            request.description
        ),
        is_default=(
            request.is_default
        ),
        created_by=(
            request.created_by
        ),
        metadata=(
            request.metadata
        ),
    )

    _SAVED_VIEWS[
        saved_view_id
    ] = view

    return _clone(
        view
    )


# ============================================================
# GET
# ============================================================


def get_saved_view(
    saved_view_id: str,
) -> SavedView:
    view = (
        _SAVED_VIEWS.get(
            saved_view_id
        )
    )

    if view is None:
        raise ValueError(
            "Saved view not found: "
            f"{saved_view_id}"
        )

    return _clone(
        view
    )


# ============================================================
# LIST
# ============================================================


def list_saved_views(
    *,
    page: str | None = None,
    created_by: str | None = None,
) -> list[
    SavedView
]:
    result = []

    for view in (
        _SAVED_VIEWS.values()
    ):
        if (
            page is not None
            and view.page
            != page
        ):
            continue

        if (
            created_by is not None
            and view.created_by
            != created_by
        ):
            continue

        result.append(
            _clone(
                view
            )
        )

    result.sort(
        key=lambda item: (
            not item.is_default,
            item.name.lower(),
        )
    )

    return result


# ============================================================
# UPDATE
# ============================================================


def update_saved_view(
    saved_view_id: str,
    *,
    name: str | None = None,
    context=None,
    description: str | None = None,
    is_default: bool | None = None,
    metadata: dict | None = None,
) -> SavedView:
    view = (
        _SAVED_VIEWS.get(
            saved_view_id
        )
    )

    if view is None:
        raise ValueError(
            "Saved view not found: "
            f"{saved_view_id}"
        )

    if name is not None:
        view.name = (
            _normalize_name(
                name
            )
        )

    if context is not None:
        view.context = (
            context
        )

    if description is not None:
        view.description = (
            description
        )

    if metadata is not None:
        view.metadata = (
            metadata
        )

    if is_default is not None:

        if is_default:
            for other in (
                _SAVED_VIEWS.values()
            ):
                if (
                    other.saved_view_id
                    != saved_view_id
                    and other.page
                    == view.page
                    and other.created_by
                    == view.created_by
                ):
                    other.is_default = (
                        False
                    )

        view.is_default = (
            is_default
        )

    return _clone(
        view
    )


# ============================================================
# DELETE
# ============================================================


def delete_saved_view(
    saved_view_id: str,
) -> bool:
    if (
        saved_view_id
        not in _SAVED_VIEWS
    ):
        return False

    del _SAVED_VIEWS[
        saved_view_id
    ]

    return True


# ============================================================
# CLEAR - TEST / FUTURE WORKSPACE RESET
# ============================================================


def clear_saved_views():
    _SAVED_VIEWS.clear()
