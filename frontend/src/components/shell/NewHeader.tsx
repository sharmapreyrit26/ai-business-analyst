import {
  useState,
} from 'react'

import {
  Bell,
  CalendarDays,
  Download,
  Filter,
  Moon,
  Search,
  Sun,
} from 'lucide-react'

import {
  useAnalytics,
} from '../../platform/AnalyticsProvider'

import {
  activeFilterCount,
} from '../../platform/analytics-serialization'

import {
  useTheme,
} from '../../theme/ThemeProvider'

import {
  FilterDrawer,
} from './FilterDrawer'


export function NewHeader() {
  const {
    mode,
    toggleTheme,
  } = useTheme()

  const {
    analytics,
  } = useAnalytics()

  const [
    filtersOpen,
    setFiltersOpen,
  ] = useState(false)


  const filterCount =
    activeFilterCount(
      analytics.filters
    )


  return (
    <>

      <header className="pl-header">

        <div className="pl-header-left">

          <button
            type="button"
            className="pl-period-control"
          >
            <CalendarDays
              size={16}
            />

            <div>
              <span>
                Reporting period
              </span>

              <strong>
                {
                  analytics
                    .period
                    .start_date
                }
                {' → '}
                {
                  analytics
                    .period
                    .end_date
                }
              </strong>
            </div>
          </button>


          <button
            type="button"
            className="pl-compare-control"
          >
            Compare:
            <strong>
              {
                analytics
                  .comparison
                  .mode
              }
            </strong>
          </button>

        </div>


        <div className="pl-header-right">

          <button
            type="button"
            className="pl-icon-button"
            aria-label="Search"
          >
            <Search
              size={18}
            />
          </button>


          <button
            type="button"
            className="pl-header-action"
            onClick={() =>
              setFiltersOpen(
                true
              )
            }
          >
            <Filter
              size={16}
            />

            Filters

            {
              filterCount > 0
              && (
                <span className="pl-filter-count">
                  {
                    filterCount
                  }
                </span>
              )
            }
          </button>


          <button
            type="button"
            className="pl-header-action"
          >
            <Download
              size={16}
            />

            Export
          </button>


          <button
            type="button"
            className="pl-icon-button"
            aria-label="Notifications"
          >
            <Bell
              size={18}
            />

            <span className="pl-alert-dot" />
          </button>


          <button
            type="button"
            className="pl-icon-button"
            aria-label="Toggle theme"
            onClick={
              toggleTheme
            }
          >
            {
              mode === 'dark'
                ? (
                  <Sun
                    size={18}
                  />
                )
                : (
                  <Moon
                    size={18}
                  />
                )
            }
          </button>


          <div className="pl-user-avatar">
            PS
          </div>

        </div>

      </header>


      <FilterDrawer
        open={filtersOpen}
        onClose={() =>
          setFiltersOpen(
            false
          )
        }
      />

    </>
  )
}
