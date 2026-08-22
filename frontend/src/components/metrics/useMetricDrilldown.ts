import {
  useState,
} from 'react'

import {
  apiV2,
} from '../../api/v2/profitlens-v2'

import type {
  MetricDrilldown,
} from '../../api/v2/types'


type OpenMetricInput = {
  metricId: string
  value: number

  previousValue?:
    number | null

  componentValues?:
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


export function useMetricDrilldown() {
  const [
    open,
    setOpen,
  ] = useState(false)

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null)

  const [
    data,
    setData,
  ] = useState<
    MetricDrilldown | null
  >(null)


  async function openMetric(
    input:
      OpenMetricInput
  ) {
    setOpen(true)
    setLoading(true)
    setError(null)

    try {
      const result =
        await apiV2
          .metricDrilldown(
            input.metricId,
            {
              value:
                input.value,

              previous_value:
                input.previousValue
                ?? null,

              component_values:
                input.componentValues
                ?? {},

              metadata:
                input.metadata
                ?? {},
            }
          )

      setData(
        result
      )

    } catch (
      requestError
    ) {
      setData(null)

      setError(
        requestError
          instanceof Error
          ? requestError.message
          : (
              'Could not load '
              + 'metric details.'
            )
      )

    } finally {
      setLoading(false)
    }
  }


  function closeMetric() {
    setOpen(false)
  }


  return {
    open,
    loading,
    error,
    data,
    openMetric,
    closeMetric,
  }
}
