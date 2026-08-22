from typing import Any, Optional

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from pydantic import BaseModel, Field

from backend.app.alert_contracts import (
    AlertRule,
)

from backend.app.data_source_contracts import (
    CreateDataSourceRequest,
    DataSourceStatus,
    SyncStatus,
)

from backend.app.export_contracts import (
    ExportRequest,
)

from backend.app.saved_view_contracts import (
    CreateSavedViewRequest,
)

from backend.app.scenario_v2_contracts import (
    ScenarioV2Request,
)

from backend.app.workspace_contracts import (
    BrandStatus,
    CreateBrandRequest,
    CreateWorkspaceRequest,
    WorkspaceRole,
)

from backend.app.services.alert_engine import (
    evaluate_alerts,
)

from backend.app.services.data_source_engine import (
    create_data_source,
    list_brand_data_sources,
    update_source_status,
)

from backend.app.services.drilldown_engine import (
    build_metric_drilldown,
)

from backend.app.services.export_engine import (
    build_export,
)

from backend.app.services.investigation_engine import (
    generate_investigations,
)

from backend.app.services.metric_dictionary_service import (
    get_metric_definition,
    get_metric_lineage,
    list_metric_definitions,
    search_metric_definitions,
)

from backend.app.services.saved_view_engine import (
    create_saved_view,
    delete_saved_view,
    get_saved_view,
    list_saved_views,
)

from backend.app.services.scenario_v2_engine import (
    get_scenario_v2_capabilities,
    run_scenario_v2,
)

from backend.app.services.workspace_engine import (
    add_workspace_member,
    create_brand,
    create_workspace,
    get_brand,
    get_workspace,
    list_workspace_brands,
    list_workspaces_for_user,
    update_brand_status,
)


router = APIRouter(
    prefix="/analytics/v2",
    tags=[
        "ProfitLens Platform V2"
    ],
)


# ============================================================
# ERROR HANDLING
# ============================================================


def _raise_http_error(
    error: Exception,
):
    if isinstance(
        error,
        ValueError,
    ):
        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        )

    raise HTTPException(
        status_code=500,
        detail=(
            "ProfitLens platform error."
        ),
    )


# ============================================================
# HEALTH / CAPABILITIES
# ============================================================


@router.get(
    "/health"
)
def platform_health():
    return {
        "status": "healthy",
        "version": "v2",
        "architecture":
            "deterministic-first",
    }


@router.get(
    "/capabilities"
)
def platform_capabilities():
    return {
        "analytics_context": True,
        "global_filters": True,
        "metric_contracts": True,
        "metric_dictionary": True,
        "drilldowns": True,
        "scenario_v2": True,
        "investigations": True,
        "alerts": True,
        "exports": True,
        "saved_views": True,
        "workspaces": True,
        "brands": True,
        "data_sources": True,
        "data_quality": True,

        "scenario_controls":
            get_scenario_v2_capabilities(),
    }


# ============================================================
# METRIC DICTIONARY
# ============================================================


@router.get(
    "/metrics"
)
def metrics(
    search: Optional[str] = Query(
        default=None
    ),
):
    try:
        if (
            search is not None
            and search.strip()
        ):
            data = (
                search_metric_definitions(
                    search
                )
            )

        else:
            data = (
                list_metric_definitions()
            )

        return {
            "count": len(
                data
            ),
            "data": data,
        }

    except Exception as error:
        _raise_http_error(
            error
        )


@router.get(
    "/metrics/{metric_id}"
)
def metric_definition(
    metric_id: str,
):
    try:
        return (
            get_metric_definition(
                metric_id
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


@router.get(
    "/metrics/{metric_id}/lineage"
)
def metric_lineage(
    metric_id: str,
):
    try:
        return (
            get_metric_lineage(
                metric_id
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# DRILLDOWN
# ============================================================


class DrilldownRequest(
    BaseModel
):
    value: float | int

    previous_value: Optional[
        float | int
    ] = None

    component_values: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


@router.post(
    "/metrics/{metric_id}/drilldown"
)
def metric_drilldown(
    metric_id: str,
    request: DrilldownRequest,
):
    try:
        result = (
            build_metric_drilldown(
                metric_id=(
                    metric_id
                ),
                value=(
                    request.value
                ),
                previous_value=(
                    request.previous_value
                ),
                component_values=(
                    request.component_values
                ),
                metadata=(
                    request.metadata
                ),
            )
        )

        return result.model_dump(
            mode="json"
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# SCENARIO LAB V2
# ============================================================


@router.get(
    "/scenario/capabilities"
)
def scenario_capabilities():
    return {
        "controls":
            get_scenario_v2_capabilities()
    }


@router.post(
    "/scenario/run"
)
def scenario_run(
    request: ScenarioV2Request,
):
    try:
        result = (
            run_scenario_v2(
                request
            )
        )

        return result.model_dump(
            mode="json"
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# INVESTIGATIONS
# ============================================================


@router.get(
    "/investigations/{month}"
)
def investigations(
    month: str,
):
    try:
        result = (
            generate_investigations(
                month
            )
        )

        return {
            "month": month,
            "count": len(
                result
            ),
            "data": [
                item.model_dump(
                    mode="json"
                )
                for item
                in result
            ],
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# ALERTS
# ============================================================


@router.get(
    "/alerts/{month}"
)
def alerts(
    month: str,
):
    try:
        result = (
            evaluate_alerts(
                month
            )
        )

        triggered = [
            item
            for item
            in result
            if item.triggered
        ]

        return {
            "month": month,

            "triggered_count":
                len(
                    triggered
                ),

            "total_rules":
                len(
                    result
                ),

            "data": [
                item.model_dump(
                    mode="json"
                )
                for item
                in result
            ],
        }

    except Exception as error:
        _raise_http_error(
            error
        )


class CustomAlertEvaluationRequest(
    BaseModel
):
    month: str

    rules: list[
        AlertRule
    ]


@router.post(
    "/alerts/evaluate"
)
def custom_alert_evaluation(
    request:
        CustomAlertEvaluationRequest,
):
    try:
        result = (
            evaluate_alerts(
                request.month,
                rules=(
                    request.rules
                ),
            )
        )

        return {
            "month":
                request.month,

            "data": [
                item.model_dump(
                    mode="json"
                )
                for item
                in result
            ],
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# EXPORTS
# ============================================================


class ExportBuildRequest(
    BaseModel
):
    export: ExportRequest

    data: Any

    metadata: dict[
        str,
        Any
    ] = Field(
        default_factory=dict
    )


@router.post(
    "/exports"
)
def create_export(
    request: ExportBuildRequest,
):
    try:
        result = build_export(
            request.export,
            data=request.data,
            metadata=(
                request.metadata
            ),
        )

        return result.model_dump(
            mode="json"
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# SAVED VIEWS
# ============================================================


@router.post(
    "/saved-views"
)
def saved_view_create(
    request:
        CreateSavedViewRequest,
):
    try:
        return (
            create_saved_view(
                request
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


@router.get(
    "/saved-views"
)
def saved_view_list(
    page: Optional[str] = None,
    created_by: Optional[
        str
    ] = None,
):
    try:
        result = (
            list_saved_views(
                page=page,
                created_by=(
                    created_by
                ),
            )
        )

        return {
            "count": len(
                result
            ),

            "data": [
                item.model_dump(
                    mode="json"
                )
                for item
                in result
            ],
        }

    except Exception as error:
        _raise_http_error(
            error
        )


@router.get(
    "/saved-views/{saved_view_id}"
)
def saved_view_get(
    saved_view_id: str,
):
    try:
        return (
            get_saved_view(
                saved_view_id
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


@router.delete(
    "/saved-views/{saved_view_id}"
)
def saved_view_delete(
    saved_view_id: str,
):
    try:
        deleted = (
            delete_saved_view(
                saved_view_id
            )
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Saved view not found."
                ),
            )

        return {
            "deleted": True,
            "saved_view_id":
                saved_view_id,
        }

    except HTTPException:
        raise

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# WORKSPACES
# ============================================================


@router.post(
    "/workspaces"
)
def workspace_create(
    request:
        CreateWorkspaceRequest,
):
    try:
        return (
            create_workspace(
                request
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


@router.get(
    "/workspaces/{workspace_id}"
)
def workspace_get(
    workspace_id: str,
):
    try:
        return (
            get_workspace(
                workspace_id
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


@router.get(
    "/users/{user_id}/workspaces"
)
def user_workspaces(
    user_id: str,
):
    try:
        result = (
            list_workspaces_for_user(
                user_id
            )
        )

        return {
            "count": len(
                result
            ),

            "data": [
                item.model_dump(
                    mode="json"
                )
                for item
                in result
            ],
        }

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# MEMBERS
# ============================================================


class AddWorkspaceMemberRequest(
    BaseModel
):
    user_id: str

    role: WorkspaceRole

    email: Optional[
        str
    ] = None

    display_name: Optional[
        str
    ] = None


@router.post(
    "/workspaces/{workspace_id}/members"
)
def workspace_member_add(
    workspace_id: str,
    request:
        AddWorkspaceMemberRequest,
):
    try:
        return (
            add_workspace_member(
                workspace_id,
                user_id=(
                    request.user_id
                ),
                role=(
                    request.role
                ),
                email=(
                    request.email
                ),
                display_name=(
                    request.display_name
                ),
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# BRANDS
# ============================================================


@router.post(
    "/brands"
)
def brand_create(
    request:
        CreateBrandRequest,
):
    try:
        return (
            create_brand(
                request
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


@router.get(
    "/brands/{brand_id}"
)
def brand_get(
    brand_id: str,
):
    try:
        return (
            get_brand(
                brand_id
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


@router.get(
    "/workspaces/{workspace_id}/brands"
)
def workspace_brands(
    workspace_id: str,
    include_archived: bool = False,
):
    try:
        result = (
            list_workspace_brands(
                workspace_id,
                include_archived=(
                    include_archived
                ),
            )
        )

        return {
            "count": len(
                result
            ),

            "data": [
                item.model_dump(
                    mode="json"
                )
                for item
                in result
            ],
        }

    except Exception as error:
        _raise_http_error(
            error
        )


class UpdateBrandStatusRequest(
    BaseModel
):
    status: BrandStatus


@router.patch(
    "/brands/{brand_id}/status"
)
def brand_status_update(
    brand_id: str,
    request:
        UpdateBrandStatusRequest,
):
    try:
        return (
            update_brand_status(
                brand_id,
                request.status,
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


# ============================================================
# DATA SOURCES
# ============================================================


@router.post(
    "/data-sources"
)
def data_source_create(
    request:
        CreateDataSourceRequest,
):
    try:
        return (
            create_data_source(
                request
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )


@router.get(
    "/brands/{brand_id}/data-sources"
)
def brand_data_sources(
    brand_id: str,
):
    try:
        result = (
            list_brand_data_sources(
                brand_id
            )
        )

        return {
            "count": len(
                result
            ),

            "data": [
                item.model_dump(
                    mode="json"
                )
                for item
                in result
            ],
        }

    except Exception as error:
        _raise_http_error(
            error
        )


class UpdateDataSourceStatusRequest(
    BaseModel
):
    status: DataSourceStatus

    sync_status: Optional[
        SyncStatus
    ] = None

    last_synced_at: Optional[
        str
    ] = None

    row_count: Optional[
        int
    ] = None

    error_message: Optional[
        str
    ] = None


@router.patch(
    "/data-sources/{data_source_id}/status"
)
def data_source_status_update(
    data_source_id: str,
    request:
        UpdateDataSourceStatusRequest,
):
    try:
        return (
            update_source_status(
                data_source_id,
                status=(
                    request.status
                ),
                sync_status=(
                    request.sync_status
                ),
                last_synced_at=(
                    request.last_synced_at
                ),
                row_count=(
                    request.row_count
                ),
                error_message=(
                    request.error_message
                ),
            )
            .model_dump(
                mode="json"
            )
        )

    except Exception as error:
        _raise_http_error(
            error
        )
