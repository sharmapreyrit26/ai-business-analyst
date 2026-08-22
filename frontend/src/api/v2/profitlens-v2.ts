import {
  requestV2,
} from './client'

import type {
  AlertListResponse,
  ExportRequest,
  ExportResponse,
  InvestigationListResponse,
  MetricDrilldown,
  MetricLineage,
  MetricListResponse,
  PlatformCapabilities,
  PlatformHealth,
  ScenarioV2Request,
  ScenarioV2Response,
} from './types'


export const apiV2 = {

  health: () =>
    requestV2<
      PlatformHealth
    >(
      '/analytics/v2/health'
    ),


  capabilities: () =>
    requestV2<
      PlatformCapabilities
    >(
      '/analytics/v2/capabilities'
    ),


  metrics: (
    search?: string
  ) => {
    const query =
      search?.trim()

    const suffix =
      query
        ? (
            `?search=${encodeURIComponent(
              query
            )}`
          )
        : ''

    return requestV2<
      MetricListResponse
    >(
      `/analytics/v2/metrics${suffix}`
    )
  },


  metricLineage: (
    metricId: string
  ) =>
    requestV2<
      MetricLineage
    >(
      `/analytics/v2/metrics/${
        encodeURIComponent(
          metricId
        )
      }/lineage`
    ),


  metricDrilldown: (
    metricId: string,
    payload: {
      value: number
      previous_value?: number | null

      component_values?:
        Record<
          string,
          number
        >

      metadata?:
        Record<
          string,
          unknown
        >
    }
  ) =>
    requestV2<
      MetricDrilldown
    >(
      `/analytics/v2/metrics/${
        encodeURIComponent(
          metricId
        )
      }/drilldown`,
      {
        method: 'POST',
        body: payload,
      }
    ),


  scenarioCapabilities: () =>
    requestV2<{
      controls:
        PlatformCapabilities[
          'scenario_controls'
        ]
    }>(
      '/analytics/v2/scenario/capabilities'
    ),


  runScenario: (
    payload:
      ScenarioV2Request
  ) =>
    requestV2<
      ScenarioV2Response
    >(
      '/analytics/v2/scenario/run',
      {
        method: 'POST',
        body: payload,
      }
    ),


  investigations: (
    month: string
  ) =>
    requestV2<
      InvestigationListResponse
    >(
      `/analytics/v2/investigations/${
        encodeURIComponent(
          month
        )
      }`
    ),


  alerts: (
    month: string
  ) =>
    requestV2<
      AlertListResponse
    >(
      `/analytics/v2/alerts/${
        encodeURIComponent(
          month
        )
      }`
    ),


  exportReport: (
    exportRequest:
      ExportRequest,

    data: unknown,

    metadata:
      Record<
        string,
        unknown
      > = {}
  ) =>
    requestV2<
      ExportResponse
    >(
      '/analytics/v2/exports',
      {
        method: 'POST',

        body: {
          export:
            exportRequest,

          data,

          metadata,
        },
      }
    ),
}
