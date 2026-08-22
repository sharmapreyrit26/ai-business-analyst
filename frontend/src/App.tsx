
import {
  useEffect,
  useRef,
  useState,
} from 'react'

import {
  Route,
  Routes,
} from 'react-router-dom'

import { api } from './api/profitlens'

import {
  useAnalytics,
} from './platform/AnalyticsProvider'
import { Header } from './components/Header'
import { Sidebar } from './components/Sidebar'

import Analyst from './pages/Analyst'
import Customers from './pages/Customers'
import Logistics from './pages/Logistics'
import BusinessHealth from './pages/BusinessHealth'
import RevenueProfit from './pages/RevenueProfit'
import Products from './pages/Products'
import Scenario from './pages/Scenario'
import ScenarioV2 from './pages/ScenarioV2'
import Marketing from './pages/Marketing'
import Inventory from './pages/Inventory'
import Investigations from './pages/Investigations'

export default function App() {
  const {
    month,
    setMonth,
  } = useAnalytics()


  const hasUserSelectedMonth =
    useRef(false)

  const [
    months,
    setMonths,
  ] = useState<string[]>([])

  const [
    partialMonths,
    setPartialMonths,
  ] = useState<string[]>([])

  useEffect(() => {
    api.reportingPeriods()
      .then((data) => {
        setMonths(
          data.months
        )

        setPartialMonths(
          data.partial_months
        )

        const currentMonthIsValid =
          data.months.includes(
            month
          )

        if (
          data.default_month
          && !hasUserSelectedMonth.current
          && !currentMonthIsValid
        ) {
          setMonth(
            data.default_month
          )
        }
      })
      .catch((error) => {
        console.error(
          'Failed to load reporting periods:',
          error
        )
      })
  }, [])

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main">
        <Header
          month={month}
          months={months}
          partialMonths={partialMonths}
          onMonthChange={(nextMonth) => {
            hasUserSelectedMonth.current = true
            setMonth(nextMonth)
          }}
        />

        <div className="content">
          <Routes>
            <Route
              path="/"
              element={
                <BusinessHealth
                  month={month}
                />
              }
            />

            <Route
              path="/revenue-profit"
              element={
                <RevenueProfit
                  month={month}
                />
              }
            />

            <Route
              path="/products"
              element={
                <Products
                  month={month}
                />
              }
            />
             
            <Route
              path="/inventory"
              element={
                <Inventory />
              }
            />
            <Route
              path="/analyst"
              element={
                <Analyst
                  month={month}
                />
              }
            />

            <Route
              path="/marketing"
              element={
                <Marketing
                  month={month}
                />
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
                <Logistics
                  month={month}
                />
              }
            />

            <Route
              path="/analyst"
              element={
                <Analyst
                  month={month}
                />
              }
            />

            <Route
              path="/customers"
              element={
                <Customers
                  month={month}
                />
              }
            />

            <Route
              path="/investigations"
              element={
                <Investigations
                  month={month}
                />
              }
            />

            <Route
              path="/scenario"
              element={
                <ScenarioV2
                  month={month}
                />
              }
            />
          </Routes>
        </div>
      </main>
    </div>
  )
}