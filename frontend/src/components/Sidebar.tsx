import {
  BarChart3,
  Boxes,
  FlaskConical,
  MessageSquareText,
  PackageCheck,
  UsersRound,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Overview', icon: BarChart3 },
  { to: '/products', label: 'Product Analysis', icon: Boxes },
  { to: '/customers', label: 'Customer Analysis', icon: UsersRound },
  { to: '/logistics', label: 'Logistics', icon: PackageCheck },
  { to: '/analyst', label: 'Ask ProfitLens', icon: MessageSquareText },
  { to: '/scenario', label: 'Scenario Lab', icon: FlaskConical },
]

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">PL</div>
        <div>
          <strong>ProfitLens</strong>
          <span>D2C Intelligence</span>
        </div>
      </div>

      <nav>
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              isActive ? 'nav-link active' : 'nav-link'
            }
          >
            <Icon size={16} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-note">
        Deterministic analytics first. AI interprets, never calculates financial truth.
      </div>
    </aside>
  )
}
