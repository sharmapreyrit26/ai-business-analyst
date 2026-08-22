import {
  NavLink,
} from 'react-router-dom'

import {
  ChevronDown,
  Sparkles,
} from 'lucide-react'

import {
  navigation,
} from '../../platform/navigation'


export function NewSidebar() {
  return (
    <aside className="pl-sidebar">

      <div className="pl-sidebar-brand">

        <div className="pl-brand-mark">
          PL
        </div>

        <div>
          <strong>
            ProfitLens
          </strong>

          <span>
            D2C Intelligence
          </span>
        </div>

      </div>


      <button
        type="button"
        className="pl-brand-switcher"
      >
        <div>
          <span>
            Workspace
          </span>

          <strong>
            Demo Commerce
          </strong>
        </div>

        <ChevronDown
          size={16}
        />
      </button>


      <nav className="pl-sidebar-nav">

        {
          navigation.map(
            section => (
              <div
                className="pl-nav-section"
                key={
                  section.section
                }
              >

                <div className="pl-nav-section-label">
                  {
                    section.section
                  }
                </div>

                {
                  section.items.map(
                    item => {
                      const Icon =
                        item.icon

                      return (
                        <NavLink
                          key={
                            item.path
                          }
                          to={
                            item.path
                          }
                          className={
                            ({
                              isActive,
                            }) =>
                              `pl-nav-link ${
                                isActive
                                  ? 'active'
                                  : ''
                              }`
                          }
                        >
                          <Icon
                            size={17}
                          />

                          <span>
                            {
                              item.label
                            }
                          </span>
                        </NavLink>
                      )
                    }
                  )
                }

              </div>
            )
          )
        }

      </nav>


      <div className="pl-sidebar-footer">

        <div className="pl-sidebar-ai-card">

          <Sparkles
            size={18}
          />

          <div>
            <strong>
              ProfitLens AI
            </strong>

            <span>
              Deterministic truth,
              AI interpretation.
            </span>
          </div>

        </div>

      </div>

    </aside>
  )
}
