import {
  X,
} from 'lucide-react'

import {
  useAnalytics,
} from '../../platform/AnalyticsProvider'

import type {
  AnalyticsFilters,
} from '../../platform/analytics-context'


type FilterDrawerProps = {
  open: boolean
  onClose: () => void
}


type FilterConfig = {
  key: keyof AnalyticsFilters
  label: string
  options: string[]
}


const FILTERS: FilterConfig[] = [
  {
    key: 'channels',
    label: 'Channel',
    options: [
      'Meta',
      'Google',
      'Organic',
      'Direct',
    ],
  },
  {
    key: 'categories',
    label: 'Category',
    options: [
      'Fashion',
      'Beauty',
      'Electronics',
      'Home',
    ],
  },
  {
    key: 'couriers',
    label: 'Courier',
    options: [
      'Delhivery',
      'Xpressbees',
      'DTDC',
      'Bluedart',
    ],
  },
  {
    key: 'payment_methods',
    label: 'Payment Method',
    options: [
      'COD',
      'Prepaid',
    ],
  },
  {
    key: 'zones',
    label: 'Zone',
    options: [
      'North',
      'South',
      'East',
      'West',
    ],
  },
]


export function FilterDrawer({
  open,
  onClose,
}: FilterDrawerProps) {
  const {
    analytics,
    updateFilter,
    clearFilters,
  } = useAnalytics()


  if (!open) {
    return null
  }


  function toggleValue(
    key: keyof AnalyticsFilters,
    value: string
  ) {
    const current =
      analytics.filters[key]

    const exists =
      current.includes(
        value
      )

    const next =
      exists
        ? current.filter(
            item =>
              item !== value
          )
        : [
            ...current,
            value,
          ]

    updateFilter(
      key,
      next
    )
  }


  return (
    <>

      <button
        type="button"
        className="pl-drawer-backdrop"
        onClick={onClose}
        aria-label="Close filters"
      />

      <aside className="pl-filter-drawer">

        <div className="pl-filter-drawer-header">

          <div>
            <span>
              Global filters
            </span>

            <h2>
              Filter analytics
            </h2>
          </div>

          <button
            type="button"
            className="pl-icon-button"
            onClick={onClose}
            aria-label="Close filter drawer"
          >
            <X size={18} />
          </button>

        </div>


        <div className="pl-filter-drawer-body">

          {
            FILTERS.map(
              filter => (
                <section
                  key={filter.key}
                  className="pl-filter-section"
                >

                  <div className="pl-filter-label">
                    {filter.label}
                  </div>

                  <div className="pl-filter-option-list">

                    {
                      filter.options.map(
                        option => {
                          const checked =
                            analytics
                              .filters[
                                filter.key
                              ]
                              .includes(
                                option
                              )

                          return (
                            <label
                              key={option}
                              className="pl-filter-option"
                            >
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={() =>
                                  toggleValue(
                                    filter.key,
                                    option
                                  )
                                }
                              />

                              <span>
                                {option}
                              </span>
                            </label>
                          )
                        }
                      )
                    }

                  </div>

                </section>
              )
            )
          }

        </div>


        <div className="pl-filter-drawer-footer">

          <button
            type="button"
            className="pl-secondary-button"
            onClick={clearFilters}
          >
            Clear all
          </button>

          <button
            type="button"
            className="pl-primary-button"
            onClick={onClose}
          >
            Apply filters
          </button>

        </div>

      </aside>

    </>
  )
}
