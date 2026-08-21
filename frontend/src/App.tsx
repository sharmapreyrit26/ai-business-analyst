
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
import Marketing from './pages/Marketing'
import Inventory from './pages/Inventory'

export default function App() {
  const [
    month,
    setMonth,
  ] = useState('2025-11')

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

        if (
          data.default_month
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
          onMonthChange={setMonth}
        />

        <div className="content">
          <Routes>
            <Route
              path="/"
              element={
                <Overview
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
              path="/scenario"
              element={
                <Scenario
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