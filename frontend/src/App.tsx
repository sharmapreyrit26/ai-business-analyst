import {
  useEffect,
  useState,
} from 'react'

import {
  Route,
  Routes,
} from 'react-router-dom'

import { api } from './api/profitlens'
import { Header } from './components/Header'
import { Sidebar } from './components/Sidebar'
import Analyst from './pages/Analyst'
import Customers from './pages/Customers'
import Logistics from './pages/Logistics'
import Overview from './pages/Overview'
import Products from './pages/Products'
import Scenario from './pages/Scenario'

export default function App() {
  const [month, setMonth] =
    useState('')

  const [months, setMonths] =
    useState<string[]>([])

  const [partialMonths, setPartialMonths] =
    useState<string[]>([])

  const [periodsLoading, setPeriodsLoading] =
    useState(true)

  const [backendConnected, setBackendConnected] =
    useState(true)

  const [periodsError, setPeriodsError] =
    useState('')

  useEffect(() => {
    let active = true

    async function loadReportingPeriods() {
      setPeriodsLoading(true)
      setPeriodsError('')

      try {
        const result =
          await api.reportingPeriods()

        if (!active) return

        setMonths(result.months)
        setPartialMonths(result.partial_months)

        const defaultMonth =
          result.default_month
          || result.complete_months[0]
          || result.months[0]
          || ''

        setMonth(defaultMonth)
        setBackendConnected(true)
      } catch (error) {
        if (!active) return

        setBackendConnected(false)

        setPeriodsError(
          error instanceof Error
            ? error.message
            : 'Unable to load reporting periods.'
        )
      } finally {
        if (active) {
          setPeriodsLoading(false)
        }
      }
    }

    loadReportingPeriods()

    return () => {
      active = false
    }
  }, [])

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main">
        <Header
          month={month}
          months={months}
          partialMonths={partialMonths}
          onMonthChange={setMonth}
          periodsLoading={periodsLoading}
          backendConnected={backendConnected}
        />

        <div className="content">
          {
            periodsError
            && (
              <div className="notice error">
                {periodsError}
              </div>
            )
          }

          {
            periodsLoading
            && (
              <div className="notice info">
                Loading reporting periods…
              </div>
            )
          }

          {
            !periodsLoading
            && month
            && (
              <Routes>
                <Route
                  path="/"
                  element={
                    <Overview month={month} />
                  }
                />

                <Route
                  path="/products"
                  element={
                    <Products month={month} />
                  }
                />

                <Route
                  path="/customers"
                  element={
                    <Customers month={month} />
                  }
                />

                <Route
                  path="/logistics"
                  element={
                    <Logistics month={month} />
                  }
                />

                <Route
                  path="/analyst"
                  element={
                    <Analyst month={month} />
                  }
                />

                <Route
                  path="/scenario"
                  element={
                    <Scenario month={month} />
                  }
                />
              </Routes>
            )
          }
        </div>
      </main>
    </div>
  )
}
