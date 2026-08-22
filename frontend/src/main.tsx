import React from 'react'
import ReactDOM from 'react-dom/client'

import {
  BrowserRouter,
} from 'react-router-dom'

import App from './App'

import {
  ThemeProvider,
} from './theme/ThemeProvider'

import {
  AnalyticsProvider,
} from './platform/AnalyticsProvider'

import './theme/tokens.css'
import './styles.css'
import './components/shell/shell.css'


ReactDOM
  .createRoot(
    document.getElementById(
      'root'
    )!
  )
  .render(
    <React.StrictMode>

      <BrowserRouter>

        <ThemeProvider>

          <AnalyticsProvider>

            <App />

          </AnalyticsProvider>

        </ThemeProvider>

      </BrowserRouter>

    </React.StrictMode>
  )
