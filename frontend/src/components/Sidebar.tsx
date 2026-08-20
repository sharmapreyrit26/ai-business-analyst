import { BarChart3, Box, Gauge, Home, MessageSquareText, Route, Settings, Users } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const nav = [
  { to: '/', label: 'Overview', icon: Home },
  { to: '/products', label: 'Product Analysis', icon: Box },
  { to: '/customers', label: 'Customer Analysis', icon: Users },
  { to: '/logistics', label: 'Logistics', icon: Route },
  { to: '/analyst', label: 'Ask ProfitLens', icon: MessageSquareText },
  { to: '/scenario', label: 'Scenario Lab', icon: Gauge },
]

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark"><BarChart3 size={18} /></div>
        <div><strong>ProfitLens</strong><span>Decision Intelligence</span></div>
      </div>

      <nav className="nav-list">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Icon size={17} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="coming-soon"><Settings size={15} /> More integrations later</div>
        <small>V1 • deterministic analytics</small>
      </div>
    </aside>
  )
}
