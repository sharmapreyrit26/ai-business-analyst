import {
  useEffect,
  useState,
} from 'react'

import {
  BarChart3,
  Boxes,
  ChevronLeft,
  ChevronRight,
  FlaskConical,
  Megaphone,
  Menu,
  MessageSquareText,
  PackageCheck,
  UsersRound,
  Warehouse,
} from 'lucide-react'

import {
  NavLink,
} from 'react-router-dom'


const links = [
  {
    to: '/',
    label: 'Overview',
    icon: BarChart3,
  },
  {
    to: '/products',
    label: 'Product Analysis',
    icon: Boxes,
  },
  {
    to: '/customers',
    label: 'Customer Analysis',
    icon: UsersRound,
  },
  {
    to: '/logistics',
    label: 'Logistics',
    icon: PackageCheck,
  },
  {
    to: '/marketing',
    label: 'Marketing',
    icon: Megaphone,
  },
  {
    to: '/inventory',
    label: 'Inventory',
    icon: Warehouse,
  },
  {
    to: '/analyst',
    label: 'Ask ProfitLens',
    icon: MessageSquareText,
  },
  {
    to: '/scenario',
    label: 'Scenario Lab',
    icon: FlaskConical,
  },
]


const STORAGE_KEY =
  'profitlens-sidebar-collapsed'


export function Sidebar() {
  const [
    collapsed,
    setCollapsed,
  ] = useState(
    () =>
      window.localStorage.getItem(
        STORAGE_KEY
      ) === 'true'
  )


  useEffect(
    () => {
      window.localStorage.setItem(
        STORAGE_KEY,
        String(
          collapsed
        )
      )
    },
    [
      collapsed,
    ]
  )


  return (
    <aside
      className={
        collapsed
          ? 'sidebar collapsed'
          : 'sidebar'
      }
    >

      <div className="sidebar-top">

        <button
          type="button"
          className="sidebar-toggle"
          aria-label={
            collapsed
              ? 'Expand sidebar'
              : 'Collapse sidebar'
          }
          title={
            collapsed
              ? 'Expand sidebar'
              : 'Collapse sidebar'
          }
          onClick={() =>
            setCollapsed(
              current =>
                !current
            )
          }
        >
          <Menu size={18} />
        </button>


        <div className="brand">

          <div className="brand-mark">
            PL
          </div>

          <div className="brand-copy">
            <strong>
              ProfitLens
            </strong>

            <span>
              D2C Intelligence
            </span>
          </div>

        </div>

      </div>


      <nav>
        {
          links.map(
            ({
              to,
              label,
              icon: Icon,
            }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                title={
                  collapsed
                    ? label
                    : undefined
                }
                className={({
                  isActive,
                }) =>
                  isActive
                    ? 'nav-link active'
                    : 'nav-link'
                }
              >
                <Icon size={17} />

                <span>
                  {label}
                </span>
              </NavLink>
            )
          )
        }
      </nav>


      <div className="sidebar-note">
        Deterministic analytics first.
        AI interprets, never calculates
        financial truth.
      </div>


      <button
        type="button"
        className="sidebar-collapse-secondary"
        aria-label={
          collapsed
            ? 'Expand navigation'
            : 'Minimize navigation'
        }
        onClick={() =>
          setCollapsed(
            current =>
              !current
          )
        }
      >
        {
          collapsed
            ? (
              <ChevronRight
                size={15}
              />
            )
            : (
              <>
                <ChevronLeft
                  size={15}
                />

                <span>
                  Minimize
                </span>
              </>
            )
        }
      </button>

    </aside>
  )
}
