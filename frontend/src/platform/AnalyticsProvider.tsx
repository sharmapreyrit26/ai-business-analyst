import {
  createContext,
  ReactNode,
  useContext,
  useMemo,
  useState,
} from 'react'

import type {
  AnalyticsContext,
  AnalyticsFilters,
  ComparisonMode,
} from './analytics-context'

import {
  defaultAnalyticsContext,
  emptyFilters,
} from './analytics-context'


type AnalyticsContextValue = {
  analytics: AnalyticsContext

  month: string

  setMonth: (
    month: string
  ) => void

  setPeriod: (
    startDate: string,
    endDate: string
  ) => void

  setComparisonMode: (
    mode: ComparisonMode
  ) => void

  setFilters: (
    filters: AnalyticsFilters
  ) => void

  updateFilter: (
    key: keyof AnalyticsFilters,
    values: string[]
  ) => void

  clearFilters: () => void

  setWorkspace: (
    workspaceId: string | null
  ) => void

  setBrand: (
    brandId: string | null
  ) => void
}


const AnalyticsStateContext =
  createContext<
    AnalyticsContextValue | undefined
  >(
    undefined
  )


type AnalyticsProviderProps = {
  children: ReactNode
}


function monthFromDate(
  startDate: string
) {
  return startDate.slice(
    0,
    7
  )
}


function periodFromMonth(
  month: string
) {
  const [
    year,
    monthNumber,
  ] = month
    .split('-')
    .map(Number)

  const lastDay =
    new Date(
      year,
      monthNumber,
      0
    )
      .getDate()

  return {
    start_date:
      `${month}-01`,

    end_date:
      `${month}-${String(
        lastDay
      ).padStart(
        2,
        '0'
      )}`,
  }
}


const MONTH_STORAGE_KEY =
  'profitlens-reporting-month'


function loadInitialAnalyticsContext():
  AnalyticsContext {
  if (
    typeof window
    === 'undefined'
  ) {
    return defaultAnalyticsContext
  }

  const savedMonth =
    window.localStorage.getItem(
      MONTH_STORAGE_KEY
    )

  if (
    !savedMonth
    || !/^\d{4}-\d{2}$/.test(
      savedMonth
    )
  ) {
    return defaultAnalyticsContext
  }

  return {
    ...defaultAnalyticsContext,

    period:
      periodFromMonth(
        savedMonth
      ),
  }
}


export function AnalyticsProvider({
  children,
}: AnalyticsProviderProps) {
  const [
    analytics,
    setAnalytics,
  ] = useState<AnalyticsContext>(
    () =>
      loadInitialAnalyticsContext()
  )


  const month =
    monthFromDate(
      analytics.period.start_date
    )


  function setMonth(
    nextMonth: string
  ) {
    window.localStorage.setItem(
      MONTH_STORAGE_KEY,
      nextMonth
    )

    setAnalytics(
      current => ({
        ...current,

        period:
          periodFromMonth(
            nextMonth
          ),
      })
    )
  }


  function setPeriod(
    startDate: string,
    endDate: string
  ) {
    setAnalytics(
      current => ({
        ...current,

        period: {
          start_date:
            startDate,

          end_date:
            endDate,
        },
      })
    )
  }


  function setComparisonMode(
    mode: ComparisonMode
  ) {
    setAnalytics(
      current => ({
        ...current,

        comparison: {
          ...current
            .comparison,

          mode,
        },
      })
    )
  }


  function setFilters(
    filters: AnalyticsFilters
  ) {
    setAnalytics(
      current => ({
        ...current,

        filters,
      })
    )
  }


  function updateFilter(
    key: keyof AnalyticsFilters,
    values: string[]
  ) {
    setAnalytics(
      current => ({
        ...current,

        filters: {
          ...current.filters,

          [key]:
            values,
        },
      })
    )
  }


  function clearFilters() {
    setAnalytics(
      current => ({
        ...current,

        filters: {
          ...emptyFilters,
        },
      })
    )
  }


  function setWorkspace(
    workspaceId: string | null
  ) {
    setAnalytics(
      current => ({
        ...current,

        workspace_id:
          workspaceId,
      })
    )
  }


  function setBrand(
    brandId: string | null
  ) {
    setAnalytics(
      current => ({
        ...current,

        brand_id:
          brandId,
      })
    )
  }


  const value =
    useMemo(
      () => ({
        analytics,

        month,

        setMonth,

        setPeriod,

        setComparisonMode,

        setFilters,

        updateFilter,

        clearFilters,

        setWorkspace,

        setBrand,
      }),
      [
        analytics,
        month,
      ]
    )


  return (
    <AnalyticsStateContext.Provider
      value={value}
    >
      {children}
    </AnalyticsStateContext.Provider>
  )
}


export function useAnalytics() {
  const context =
    useContext(
      AnalyticsStateContext
    )

  if (!context) {
    throw new Error(
      'useAnalytics must be used inside AnalyticsProvider.'
    )
  }

  return context
}
